#!/usr/bin/env python3
"""One frozen Vals-gateway call; no direct provider client or fallback.

Runtime settings are private and supplied by the execution host. This program
never reads a personal provider key or imports a provider SDK.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone


def stamp():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')
    os.chmod(tmp, 0o600)
    tmp.replace(path)


def parse_score(text):
    text = text.strip()
    if text.startswith('```'):
        lines = text.splitlines()
        if lines[-1].startswith('```'):
            text = '\n'.join(lines[1:-1])
    obj = json.loads(text)
    score = obj.get('score')
    if isinstance(score, bool) or not isinstance(score, (float, int)):
        raise ValueError('score must be numeric')
    if not math.isfinite(score) or not 0 <= score <= 1:
        raise ValueError('score outside [0,1]')
    if not isinstance(obj.get('reasoning'), str) or not obj['reasoning'].strip():
        raise ValueError('missing reasoning')
    return {'score': float(score), 'reasoning': obj['reasoning']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--settings', type=Path, required=True)
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest_bytes = (root / 'manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    cell = manifest['cells'][0]
    assert manifest['expected_cells'] == len(manifest['cells']) == 1
    prompt_bytes = (root / cell['prompt']).read_bytes()
    assert sha(prompt_bytes) == cell['prompt_sha256']
    assert sha((root / 'data/my_add.lean').read_bytes()) == manifest['source_sha256']
    settings = json.loads(args.settings.read_text())
    url = settings['gateway_url'].rstrip('/')
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.scheme != 'https' or not parsed_url.hostname.endswith('.vals.ai'):
        raise ValueError('Only HTTPS Vals-hosted gateways are permitted')
    if parsed_url.username or parsed_url.password or parsed_url.query or parsed_url.fragment:
        raise ValueError('Invalid gateway URL')
    import boto3
    import yaml
    config = yaml.safe_load(Path(settings['valkyrie_config']).read_text())
    session = boto3.Session(aws_access_key_id=config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=config['AWS_SECRET_ACCESS_KEY'],
        aws_session_token=config.get('AWS_SESSION_TOKEN'), region_name=settings['region'])
    raw = session.client('secretsmanager').get_secret_value(
        SecretId=settings['gateway_key_secret'])['SecretString']
    try:
        secret = json.loads(raw)
    except json.JSONDecodeError:
        secret = raw
    key = next(secret[k] for k in ['MODEL_GATEWAY_API_KEY', 'api_key', 'key']
        if k in secret) if isinstance(secret, dict) else secret
    headers = {'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}
    secrets = [raw, key, str(config['AWS_ACCESS_KEY_ID']), str(config['AWS_SECRET_ACCESS_KEY'])]

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            raise ValueError('Gateway redirects are not permitted')

    opener = urllib.request.build_opener(NoRedirect())
    def request(route, body=None, timeout=30):
        req = urllib.request.Request(url + route, headers=headers,
            data=json.dumps(body).encode() if body is not None else None)
        with opener.open(req, timeout=timeout) as response:
            data = response.read()
            return json.loads(data), response.status, data

    registry, _, _ = request('/registry')
    model = registry['models'][settings['model_selector']]
    assert model['provider_endpoint'] == manifest['model']
    assert model['default_parameters']['reasoning_effort'] == manifest['reasoning_effort']
    assert not model.get('provider_properties', {}).get('fallback_models')
    assert model['provider_name'] == 'openai'
    prices = model['costs_per_million_token']
    input_bound = len(prompt_bytes) + 1024
    estimate = (input_bound * prices['input'] + manifest['max_tokens'] * prices['output']) / 1e6
    assert estimate <= manifest['admission_cost_ceiling_usd']
    preflight = {'timestamp': stamp(), 'host': socket.gethostname(),
        'model': manifest['model'], 'reasoning_effort': manifest['reasoning_effort'],
        'manifest_sha256': sha(manifest_bytes), 'prompt_sha256': sha(prompt_bytes),
        'input_token_upper_bound': input_bound, 'output_token_limit': manifest['max_tokens'],
        'input_usd_per_million': prices['input'], 'output_usd_per_million': prices['output'],
        'admission_estimate_usd': estimate, 'funding_route': 'Vals-hosted gateway with server-held provider credentials',
        'custom_provider_credential': False, 'custom_provider_endpoint': False,
        'configured_fallbacks': False, 'invoice_account_independently_visible': False}
    save(root / 'results/preflight.json', preflight)
    if args.preflight_only:
        print(json.dumps(preflight)); return
    # Exclusive reservation prevents accidental duplicate calls on rerun.
    reservation = root / 'results/attempt-reserved.json'
    with reservation.open('x') as stream:
        json.dump({'started': stamp(), 'cell_id': cell['cell_id'], 'pid': os.getpid()}, stream)
    os.chmod(reservation, 0o600)
    run_id = 'cert-judge-36-vals-smoke-09-24-2026-v1'
    query = {'model': settings['model_selector'],
        'config': {'max_tokens': manifest['max_tokens'], 'reasoning_effort': manifest['reasoning_effort']},
        'inputs': [{'kind': 'text', 'text': prompt_bytes.decode()}], 'tools': [],
        'run_id': run_id, 'question_id': cell['cell_id'], 'query_id': run_id + '-' + cell['cell_id'],
        'identity': {'benchmark_name': 'cert-judge-smoke', 'agent_name': 'P1_BASELINE'}, 'in_agent': False}
    save(root / 'private/request.json', query)
    result = {'started': stamp(), 'host': socket.gethostname(), 'cell_id': cell['cell_id'],
        'run_id': run_id, 'query_id': query['query_id'], 'expected_cells': 1, 'client_inference_calls': 1,
        'model_requested': manifest['model'], 'reasoning_effort_requested': manifest['reasoning_effort'],
        'manifest_sha256': sha(manifest_bytes), 'prompt_sha256': sha(prompt_bytes),
        'status': 'RUNNING', 'transport_success': False, 'valid_score': False,
        'identity_sanity_pass': False, 'scientific_judge_validity_established': False}
    save(root / 'results/receipt.json', result)
    begin = time.monotonic()
    try:
        response, status, raw_response = request('/query', query, manifest['client_timeout_seconds'])
        save(root / 'results/raw/response.json', response)
        result.update(http_status=status, response_sha256=sha(raw_response), response_bytes=len(raw_response))
        if response.get('error'):
            result['status'] = 'PROVIDER_ERROR'
            result['error_type'] = response['error'].get('exception_type', response['error'].get('type'))
        else:
            result['transport_success'] = True
            result['finish_reason'] = response.get('finish_reason')
            meta = response.get('metadata', {})
            result['usage'] = {k: meta.get(k) for k in ['in_tokens', 'out_tokens', 'reasoning_tokens',
                'cache_read_tokens', 'cache_write_tokens', 'duration_seconds', 'cost', 'fallback']}
            result['provider_receipt'] = response.get('extras', {})
            result['output_sha256'] = sha((response.get('output_text') or '').encode())
            score = parse_score(response.get('output_text') or '')
            result.update(score)
            result['valid_score'] = True
            result['identity_sanity_pass'] = score['score'] == 1.0
            result['status'] = 'COMPLETE' if not meta.get('fallback') else 'UNEXPECTED_FALLBACK'
            if isinstance(result['finish_reason'], dict) and result['finish_reason'].get('reason') in ['length', 'max_tokens']:
                result['status'] = 'BUDGET_EXHAUSTED'
    except Exception as exc:
        result['status'] = 'INFRASTRUCTURE_OR_PARSE_ERROR'
        result['error_type'] = type(exc).__name__
        # Errors may carry request details. Keep only scrubbed text in private evidence.
        message = str(exc)
        for value in secrets:
            if value: message = message.replace(value, '[REDACTED]')
        save(root / 'private/error.json', {'type': type(exc).__name__, 'message': message})
    finally:
        result.update(ended=stamp(), wall_seconds=round(time.monotonic()-begin, 3), terminal_cells=1)
        save(root / 'results/receipt.json', result)
        print(json.dumps(result))


if __name__ == '__main__':
    main()
