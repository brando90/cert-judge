#!/usr/bin/env python3
"""Passive, zero-inference callback observer. Never restart or redeploy a service."""
import argparse
import concurrent.futures
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.request

RUN = 'cj-e47-v5-10-08-2026-a1'
MODELS = ('opus55x', 'qwen36', 't2_qwen', 't2_sonnet5')
BOOT = Path('/proc/sys/kernel/random/boot_id')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic(path, value):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, indent=2) + '\n')
    os.chmod(tmp, 0o600)
    tmp.replace(path)


def process(pid, proc=Path('/proc'), boot=BOOT):
    p = proc / str(int(pid))
    stat = (p / 'stat').read_text().rsplit(')', 1)[1].split()
    if stat[0] in ('Z', 'X'):
        raise RuntimeError('dead_process')
    start = stat[19]
    result = dict(pid=int(pid), boot_id=boot.read_text().strip(), start_ticks=start,
                  cwd=str((p / 'cwd').resolve(strict=True)),
                  argv=(p / 'cmdline').read_bytes().decode().rstrip('\0').split('\0'))
    if (p / 'stat').read_text().rsplit(')', 1)[1].split()[19] != start:
        raise RuntimeError('process_changed_during_observation')
    return result


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def health(url, bearer=None):
    # Reject redirects so the bearer cannot be forwarded to a different host.
    headers = {'Authorization': 'Bearer ' + bearer} if bearer else {}
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(urllib.request.Request(url, headers=headers), timeout=6) as r:
            return r.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception:
        return 0


def healthy_codes(codes):
    return codes == {'local_authenticated': 200, 'local_unauthenticated': 401,
                     'tunnel_authenticated': 200, 'tunnel_unauthenticated': 401}


def inspect_model(e, model, index, expected=None):
    private = e / 'private/probes'
    path = private / ('deployment_' + model + '.json')
    receipt = json.loads(path.read_text())
    port = 9044 + index
    assert receipt['model_key'] == model
    assert receipt['benchmark'] == 'certjudge47-v5-a1-probes-' + model.replace('_', '-')
    assert receipt['port'] == port
    url = receipt['tunnel_url']
    assert re.fullmatch(r'https://[a-z0-9-]+\.trycloudflare\.com', url)
    service_dir = Path(receipt['service_dir']).resolve(strict=True)
    assert service_dir.is_relative_to((e / 'private/dependencies').resolve())
    assert service_dir.name == 'vb_service_single_call'
    assert Path(receipt['pack_dir']).resolve(strict=True) == (private / 'packs' / model).resolve(strict=True)
    assert Path(receipt['valkyrie_config']).resolve(strict=True) == (private / 'valkyrie.yaml').resolve(strict=True)
    files = receipt['service_files_sha256']
    assert files and set(files) == {p.name for p in service_dir.glob('*.py')}
    for name, digest in files.items():
        assert Path(name).name == name and sha(service_dir / name) == digest
    service, tunnel = process(receipt['service_pid']), process(receipt['tunnel_pid'])
    assert service['cwd'] == str(service_dir)
    assert any(Path(a).name == 'uvicorn' for a in service['argv'][:2])
    assert service['argv'][-5:] == ['main:app', '--host', '127.0.0.1', '--port', str(port)]
    assert tunnel['cwd'] == str(e.parents[2].resolve())
    assert len(tunnel['argv']) == 5 and Path(tunnel['argv'][0]).name == 'cloudflared'
    assert tunnel['argv'][1:] == ['tunnel', '--no-autoupdate', '--url', 'http://127.0.0.1:' + str(port)]
    # Inspect only the four required nonsecret environment values, never emit the environment.
    wanted = {'VB_TASK_PACK': str(private / 'packs' / model),
              'VB_SERVICE_KEY_FILE': str(private / 'service_bearer'), 'VB_COLLECT_ONLY': '1', 'VB_NO_COMPILER': '1'}
    found = {}
    for entry in (Path('/proc') / str(service['pid']) / 'environ').read_bytes().split(b'\0'):
        key, _, value = entry.partition(b'=')
        name = key.decode(errors='replace')
        if name in wanted:
            found[name] = value.decode()
    assert found == wanted
    identity = dict(deployment_sha256=sha(path), service=service, tunnel=tunnel)
    if expected is not None:
        assert identity == expected
    bearer = (private / 'service_bearer').read_text().strip()
    assert bearer
    codes = {}
    for place, endpoint in [('local', 'http://127.0.0.1:' + str(port)), ('tunnel', url)]:
        codes[place + '_authenticated'] = health(endpoint + '/health', bearer)
        codes[place + '_unauthenticated'] = health(endpoint + '/health')
    assert process(service['pid']) == service and process(tunnel['pid']) == tunnel
    return {'model': model, 'healthy': healthy_codes(codes), 'codes': codes, 'identity': identity}


def observe(e, binding=None):
    def one(index_model):
        index, model = index_model
        try:
            return inspect_model(e, model, index, binding['models'][model] if binding else None)
        except Exception as exc:
            return {'model': model, 'healthy': False, 'error_type': type(exc).__name__}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(one, enumerate(MODELS)))
    return rows


def verdict(binding, rows, file_hashes):
    identities_ok = set(r['model'] for r in rows) == set(MODELS) and len(rows) == 4
    stable = file_hashes == binding['files']
    return 'HEALTHY' if identities_ok and stable and all(r['healthy'] for r in rows) else 'CALLBACK_ATTENTION'


def notify(state, runtime):
    # Existing authorized internal SMTP route; no collaborator mail or new credentials.
    sys.path[:0] = ['/lfs/skampere1/0/brando9/.local/lib/python3.12/site-packages',
                   '/dfs/scratch0/brando9/ultimate-utils/py_src']
    from uutils.emailing import send_email_smtp
    send_email_smtp(to='brando.science@gmail.com',
        subject='[cert-judge] Experiment 47 probe callback health changed',
        body='Experiment 47_simulated_panel_v5_label_free_judge_screening has a changed probe callback health failure. '
             'The passive monitor has preserved all services, tunnel URLs and admitted run identities. '
             'No inference, restart or redeployment was attempted. State: ' + state['state'] +
             '. Receipt: ' + str(runtime / 'callback_observation.json') +
             '\nThe desktop master heartbeat remains responsible for recovery.\n\n-----\nBrando Miranda\n'
             'Ph.D. Student\nComputer Science, Stanford University\nEDGE Scholar, Stanford University\n'
             'brando9@stanford.edu\nwebsite: https://brando90.github.io/brandomiranda/',
        smtp_user='brandojazz@gmail.com', smtp_pass_file='/dfs/scratch0/brando9/keys/gmail_app_password.txt')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--experiment', type=Path, required=True, help='Owned expt_v1 path')
    ap.add_argument('--bind', action='store_true', help='Bind once after separate scientific admission checks')
    ap.add_argument('--admission', type=Path, help='Frozen probe admission manifest, required for bind')
    ap.add_argument('--notify', action='store_true', help='Send one authorized internal email per changed failure')
    args = ap.parse_args()
    os.umask(0o077)
    e = args.experiment.resolve(strict=True)
    runtime = e / 'runtime'
    assert e.name == 'expt_v1' and e.parent.name == '47_simulated_panel_v5_label_free_judge_screening'
    with (runtime / 'callback_monitor.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0
        try:
            bp = runtime / 'callback_binding.json'
            if not args.bind and not bp.exists():
                return 2  # Not yet deployed; never infer a healthy gate.
            if args.bind:
                assert not bp.exists(), 'binding already exists; no silent rebinding'
                assert args.admission and args.admission.resolve(strict=True).is_relative_to(e)
                files = {str(args.admission.resolve()): sha(args.admission),
                         str(e / 'private/probes/valkyrie.yaml'): sha(e / 'private/probes/valkyrie.yaml')}
                binding = {'run_id': RUN, 'phase': 'probes', 'bound_epoch': time.time(),
                           'files': files, 'models': {}, 'observer_sha256': sha(__file__)}
            else:
                binding = json.loads(bp.read_text())
                assert binding['run_id'] == RUN and binding['phase'] == 'probes'
                assert binding['observer_sha256'] == sha(__file__), 'bound observer code changed'
            rows = observe(e, None if args.bind else binding)
            try:
                current_files = {p: sha(p) for p in binding['files']}
            except OSError:
                current_files = {}
            state = {'run_id': RUN, 'phase': 'probes', 'observed_epoch': time.time(),
                     'state': verdict(binding, rows, current_files), 'models': rows,
                     'measured_calls': 0, 'restarts': 0, 'whole_experiment_complete': False}
            if args.bind and state['state'] == 'HEALTHY':
                binding['models'] = {r['model']: r['identity'] for r in rows}
                binding['initial_observed_epoch'] = state['observed_epoch']
                atomic(bp, binding)
            state['bound'] = bp.exists()
            state['binding_sha256'] = sha(bp) if bp.exists() else None
            state['observer_sha256'] = sha(__file__)
            state['observation_kind'] = 'bind' if args.bind else 'monitor'
            state['observer_pid'] = os.getpid()
            state['observer_parent_pid'] = os.getppid()
        except Exception as exc:
            state = {'run_id': RUN, 'phase': 'probes', 'observed_epoch': time.time(),
                     'state': 'CALLBACK_MONITOR_ERROR', 'models': [], 'error_type': type(exc).__name__,
                     'bound': (runtime / 'callback_binding.json').exists(), 'measured_calls': 0,
                     'restarts': 0, 'whole_experiment_complete': False}
            rows, current_files = [], {}
        # Neither public state nor events includes a bearer or callback URL.
        signature = hashlib.sha256(json.dumps([state['state'], state.get('error_type'), rows, current_files,
                                               state.get('binding_sha256'), state.get('observer_sha256')], sort_keys=True).encode()).hexdigest()
        previous_path = runtime / 'callback_observation.json'
        try:
            previous = json.loads(previous_path.read_text()) if previous_path.exists() else {}
        except (OSError, ValueError):
            previous = {}
        state['signature'] = signature
        if previous.get('signature') == signature:
            for key in ('notification_attempted_epoch', 'notification_sent_epoch', 'notification_failed_epoch', 'notification_error_type'):
                if key in previous:
                    state[key] = previous[key]
        else:
            with (runtime / 'callback_events.jsonl').open('a') as log:
                log.write(json.dumps(state, sort_keys=True) + '\n')
            if args.notify and state['state'] != 'HEALTHY':
                # Persist before sending: an uncertain delivery never causes duplicate retries.
                state['notification_attempted_epoch'] = time.time()
                atomic(previous_path, state)
                try:
                    notify(state, runtime)
                    state['notification_sent_epoch'] = time.time()
                except Exception as exc:
                    state.update(notification_failed_epoch=time.time(), notification_error_type=type(exc).__name__)
        atomic(previous_path, state)
        print(json.dumps({'state': state['state'], 'bound': state['bound'], 'observed_epoch': state['observed_epoch'],
                          'processes_verified': sum(2 for r in rows if 'identity' in r), 'measured_calls': 0}))
        return 0 if state['state'] == 'HEALTHY' and state['bound'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
