"""Offline reconciliation of original archives, never a fabricated server final view.

Only the pinned single-call writer's certified file bytes may become scores.
Terminus trajectories certify accounting, not submission. No transport is used.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import ExitStack
import fcntl
import io
import json
import math
from pathlib import Path, PurePosixPath
import tarfile
from unittest.mock import patch

from e47_adapter import (ROOT, RESULTS, PRIVATE, RUN_ID, POOL, DEPENDENCIES,
                         read, write, sha, verify_dependencies, phase_context,
                         prompts, panel, module)
from receipt_validation import accepted

COLLECTION = Path('/dfs/scratch0/brando9/cj-e47-original-output-collection-10-08-2026')
WRITER = DEPENDENCIES/'experiments/103_single_call_baselines_all_models_vbv1_vbv2_valkyrie_validated_fsc_judge/scripts/valkyrie_judge_agent/judge_call.py'
WRITER_SHA = '9314c8107eef1c940a98a5f0dfba84546bc315aef5637405c97987f34a02b061'
IDENTITY_FIELDS = ('cell', 'kind', 'key', 'task', 'item', 'level', 'repeat', 'prompt_sha256')


class InvalidEvidence(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise InvalidEvidence(reason)


def unique(rows, key):
    result = {}
    for row in rows:
        require(row[key] not in result, 'DUPLICATE_'+key.upper())
        result[row[key]] = row
    return result


def json_bytes(data):
    def pairs(values):
        out = {}
        for key, value in values:
            require(key not in out, 'DUPLICATE_JSON_KEY:'+key)
            out[key] = value
        return out
    return json.loads(data, object_pairs_hook=pairs)


def archive_members(data):
    """Inspect bytes without extraction; reject aliases, links and duplicates."""
    contents, names = {}, set()
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        for member in archive:
            name = member.name
            path = PurePosixPath(name)
            require(not path.is_absolute() and '..' not in path.parts and str(path) == name,
                    'UNSAFE_ARCHIVE_MEMBER')
            require(name not in names, 'DUPLICATE_ARCHIVE_MEMBER:'+name)
            names.add(name)
            require(member.isfile() or member.isdir(), 'UNSUPPORTED_ARCHIVE_MEMBER:'+name)
            if member.isfile():
                contents[name] = archive.extractfile(member).read()
                require(len(contents[name]) == member.size, 'TRUNCATED_ARCHIVE_MEMBER')
    return contents


def verify_request(meta, cell, unit, instruction, rendered, pack, writer, phase='criterion'):
    """Bind every local identity to frozen cells, header and exact prompt bytes."""
    for field in IDENTITY_FIELDS:
        require(meta.get(field) == cell.get(field), 'CELL_BINDING:'+field)
    require(meta['task_id'] == pack.task_id_of('cj47', unit['prompt_key'],
            f"q{meta['queue_index']:05d}__{cell['cell']}"), 'TASK_ID_BINDING')
    if phase == 'criterion':
        require(cell['cell'] == f"crit__{cell['item']}__L{cell['level']}__r{cell['repeat']}"
                and cell['kind'] == 'crit' and cell['repeat'] in (1, 2, 3), 'CELL_IDENTITY')
    else:
        require(phase == 'probes', 'UNKNOWN_PHASE')
        e, renderer, _, _ = phase_context(phase)
        kind = cell['kind']
        require(kind in e.KINDS and kind != 'crit', 'PROBE_KIND')
        repeats = 2 if kind == 'ms_gold' else e.KINDS[kind]['repeats']
        require(type(cell['repeat']) is int and cell['repeat'] in range(1, repeats+1)
                and cell['cell'] == renderer.cell_id(kind, cell['key'], cell['level'], cell['repeat'])
                and cell.get('status') == 'render' and cell.get('valid') is True, 'PROBE_CELL_IDENTITY')
    require(len(instruction) == meta['instruction_bytes'] and sha(instruction) == meta['instruction_sha256'],
            'INSTRUCTION_BYTES')
    text = instruction.decode('utf-8')
    header, system, user = writer.parse_task_file(text)
    require(system == rendered['system'] and user == rendered['user'], 'RENDERED_PROMPT_BYTES')
    maker = pack.agent_task_file if unit['pack_flavor'] == 'agent' else pack.task_file
    expected = maker(cell['cell'], cell.get('item') or cell['key'], cell['repeat'],
                     cell['kind'], unit['rubric'], system, user).encode('utf-8')
    require(instruction == expected, 'HEADER_OR_INSTRUCTION_BINDING')
    hashes = {'system': sha(system.encode()), 'user': sha(user.encode()),
              'prompt': sha((system+'\n\n'+user).encode())}
    for name, digest in hashes.items():
        require(header.get(name+'_sha256') == digest, 'HEADER_HASH:'+name)
    require(hashes['prompt'] == meta['prompt_sha256'], 'PROMPT_HASH_BINDING')
    return header, hashes


def preserved_receipt_fields(receipt):
    # Preserve errors/attempts/costs even when no verdict can be accepted.
    fields = ('status', 'requests_sent', 'attempt', 'http_status', 'error_kind',
              'error_type', 'reason', 'finish_reason', 'usage', 'cost_usd',
              'fallback', 'response_sha256', 'output_text_sha256',
              'output_text_bytes', 'written_file', 'started', 'ended')
    return {k: receipt[k] for k in fields if k in receipt}


def recover_single(meta, unit, entry, header, hashes, outer_bytes, members, parse):
    """Require request and writer evidence before invoking the original parser."""
    require('logs/vb103/receipt.json' in members, 'MISSING_INNER_RECEIPT')
    require(outer_bytes == members['logs/vb103/receipt.json'], 'OUTER_INNER_RECEIPT_CONFLICT')
    receipt = json_bytes(outer_bytes)
    expected = {'condition': 'expt103-judge-transport-v1', 'task_id': meta['task_id'],
                'selector': entry['selector'], 'judge_config': unit['config'],
                'benchmark': entry['benchmark'], 'cell': meta['cell'],
                'output_path': header['output_path'], 'expected': hashes,
                **{key+'_sha256': value for key, value in hashes.items()}}
    for key, value in expected.items():
        require(receipt.get(key) == value, 'RECEIPT_BINDING:'+key)
    config = {'max_tokens': unit['max_tokens']}
    config.update({k: v for k, v in unit['kwargs'].items() if k in ('compute_effort', 'reasoning_effort')})
    require(receipt.get('config') == config, 'REQUEST_CONFIG_BINDING')
    requests = receipt.get('requests_sent')
    require(type(requests) is int and 1 <= requests <= 2, 'MISSING_OR_EXCESS_REQUESTS')
    require(type(receipt.get('attempt')) is int and receipt['attempt'] == requests, 'ATTEMPT_BINDING')
    if requests == 2:
        require(receipt.get('http_status') in (429, 500, 502, 503, 504)
                and receipt.get('error_kind') == 'HTTPError', 'UNSUPPORTED_SECOND_REQUEST')
    elif receipt.get('status') == 'measured':
        require('http_status' not in receipt and 'error_kind' not in receipt, 'CONFLICTING_FIRST_REQUEST_SUCCESS')
    require(not receipt.get('fallback'), 'UNEXPECTED_FALLBACK')
    require('logs/vb103/response.txt' in members, 'MISSING_RESPONSE_BYTES')
    response = members['logs/vb103/response.txt']
    require(len(response) == receipt.get('output_text_bytes')
            and sha(response) == receipt.get('output_text_sha256'), 'RESPONSE_BYTES_BINDING')
    completion = response.decode('utf-8')
    # EXACT pinned judge_call.py writer: append LF only if not already present.
    submitted = (completion if completion.endswith('\n') else completion+'\n').encode('utf-8')
    require(receipt.get('written_file') == {'path': header['output_path'],
            'bytes': len(submitted), 'sha256': sha(submitted)}, 'WRITTEN_FILE_BINDING')
    result = {'agent_status': receipt.get('status'), 'prompt_sha256_delivered': hashes['prompt'],
              'raw_transport_receipt_sha256': sha(outer_bytes), 'verdict_sha256': sha(submitted),
              'verdict_bytes': len(submitted), 'submission_evidence': 'pinned writer and original written_file path/size/hash; server submission status unavailable',
              'original_transport': preserved_receipt_fields(receipt),
              **{k: receipt[k] for k in ('requests_sent', 'attempt', 'http_status', 'error_kind',
                                        'error_type', 'finish_reason', 'cost_usd', 'usage') if k in receipt}}
    try:
        raw, normalized, verdict = parse(unit, submitted.decode('utf-8'))
        result.update(status='measured', score_raw=raw, score=normalized,
                      rationale=str(verdict.get('rationale') or verdict.get('reasoning') or verdict.get('reason') or '')[:300])
    except ValueError as exc:
        result.update(status='parse_error', error=str(exc)[:200])
    ok, reason = accepted(result, meta['prompt_sha256'])
    finish = receipt.get('finish_reason') or {}
    clean = str(finish.get('reason') or finish or '').lower() in {'stop', 'stop_sequence', 'end_turn'} if isinstance(finish, dict) else False
    if receipt.get('status') != 'measured' or not clean:
        ok, reason = False, 'UNCLEAN_TRANSPORT_STATUS'
    if receipt.get('http_status') == 429:
        ok, reason = False, 'HTTP_429_INFRASTRUCTURE_FAILURE'
    result.update(accepted=ok, acceptance_reason=reason)
    if not ok and result.get('status') == 'measured':
        result['status'] = 'unmeasured_infra'
    return result


def recover_trajectory(task_id, entry, raw):
    trajectory = json_bytes(raw)
    require(trajectory.get('session_id') == task_id and
            trajectory.get('trajectory_id') == task_id+':terminus-offline', 'TRAJECTORY_TASK_BINDING')
    agent = trajectory.get('agent', {})
    require(agent.get('name') == 'terminus-2' and agent.get('model_name') == entry['selector'],
            'TRAJECTORY_AGENT_BINDING')
    metrics = trajectory.get('final_metrics') or {}
    cost = metrics.get('total_cost_usd')
    require(cost is None or (type(cost) in (int, float) and math.isfinite(cost) and cost >= 0), 'INVALID_REPORTED_COST')
    availability = metrics.get('extra', {}).get('metric_availability', {}).get('cost_usd', {})
    certified_cost = (cost if availability.get('total_responses', 0) > 0 and
                      availability.get('reported_responses') == availability.get('total_responses') else None)
    return {'trajectory_sha256': sha(raw), 'original_final_metrics': metrics,
            'cost_usd': certified_cost, 'known_reported_cost_usd': cost,
            'agent_steps': metrics.get('total_steps'), 'agent_prompt_tokens': metrics.get('total_prompt_tokens'),
            'agent_completion_tokens': metrics.get('total_completion_tokens'),
            'agent_cached_tokens': metrics.get('total_cached_tokens'),
            'accepted': False, 'status': 'unmeasured_infra',
            'acceptance_reason': 'SUBMITTED_VERDICT_BYTES_UNCERTIFIED'}


def verify_collection(collection, ledger_path, packs_path):
    completion = read(collection/'collection_completion_receipt.json')
    require(completion['scientific_run_id'] == RUN_ID and completion['new_inference_calls'] == 0, 'COLLECTION_IDENTITY')
    for key, name in (('manifest_sha256', 'collection_manifest.json'), ('progress_sha256', 'progress.json'),
                      ('metadata_summary_sha256', 'metadata_summary.json')):
        require(sha((collection/name).read_bytes()) == completion[key], 'COLLECTION_HASH:'+name)
    manifest = read(collection/'collection_manifest.json')
    require(manifest['scientific_run_id'] == RUN_ID and manifest['new_measured_calls'] == 0, 'MANIFEST_IDENTITY')
    require(sha(ledger_path.read_bytes()) == manifest['source_ledger_sha256'], 'ORIGINAL_LEDGER_CHANGED')
    require(sha(packs_path.read_bytes()) == manifest['frozen_packs_sha256'], 'FROZEN_PACKS_CHANGED')
    runs = unique(manifest['runs'], 'run_id')
    unique(manifest['runs'], 'key'); unique(manifest['runs'], 'config')
    progress = read(collection/'progress.json')
    require(progress['scientific_run_id'] == RUN_ID and progress['stage'] ==
            'RAW_COLLECTION_COMPLETE_STRICT_HARVEST_PENDING_NOT_EXPERIMENT_COMPLETE', 'COLLECTION_INCOMPLETE')
    completed = unique(progress['completed'], 'run_id')
    snapshots = unique(read(collection/'metadata_summary.json')['rows'], 'run_id')
    require(set(runs) == set(completed) == set(snapshots) and len(runs) == completion['runs'], 'COLLECTION_RUN_MASK')
    return manifest, completion, completed, snapshots


def verified_files(directory):
    inventory = read(directory/'files_sha256.json')
    indexed = unique(inventory, 'path')
    for name, record in indexed.items():
        relative = PurePosixPath(name)
        require(not relative.is_absolute() and '..' not in relative.parts, 'UNSAFE_FILE_PATH')
        path = directory/name
        require(path.is_file() and not path.is_symlink(), 'MISSING_OR_LINKED_COLLECTION_FILE:'+name)
        data = path.read_bytes()
        require(len(data) == record['bytes'] and sha(data) == record['sha256'], 'COLLECTED_FILE_HASH:'+name)
    actual = {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
    require(actual == set(indexed) | {'files_sha256.json', 'identity_receipt.json'}, 'UNINDEXED_COLLECTION_FILE')
    return indexed


def harvest_run(source, entry, unit, metas, cells, packed, pack, writer, parse, directory, indexed, phase='criterion'):
    wanted = source['frozen_task_ids']
    require(len(wanted) == len(set(wanted)) and set(wanted) == set(metas), 'TASK_MASK_OR_DUPLICATE')
    require(entry['expected_cells'] == len(wanted), 'EXPECTED_TASK_COUNT')
    require(set(p.name for p in directory.iterdir() if p.is_dir()) <= set(wanted), 'UNEXPECTED_TASK_ARTIFACT')
    result = []
    for task_id in wanted:
        meta = metas[task_id]
        row = {k: meta[k] for k in ('task_id', *IDENTITY_FIELDS)}
        row.update(config=unit['config'], run_id=entry['run_id'], phase=phase, part='main',
                   accepted=False, status='unmeasured_infra', cost_usd=None,
                   acceptance_reason='ARTIFACT_ABSENT_UNRESOLVED', prior_verdict_absence_established=False,
                   server_submission_status=None, source_collection_path=str(directory/task_id))
        task = directory/task_id
        try:
            cell = cells[meta['cell']]
            instruction = (Path(packed['pack'])/task_id/'instruction.md').read_bytes()
            rendered = read(PRIVATE/phase/'cells'/unit['config'].replace('|', '__')/(meta['cell']+'.json'))
            header, hashes = verify_request(meta, cell, unit, instruction, rendered, pack, writer, phase)
            row['frozen_instruction_sha256'] = sha(instruction)
            row['frozen_header_sha256'] = sha(json.dumps(header, sort_keys=True).encode())
            if not task.is_dir():
                result.append(row); continue
            files = {name: (directory/name).read_bytes() for name in indexed if name.startswith(task_id+'/')}
            receipt_paths = [name for name in files if Path(name).name == 'receipt.json']
            require(receipt_paths in ([], [task_id+'/receipt.json']), 'DUPLICATE_OR_UNSUPPORTED_OUTER_RECEIPT')
            require(task_id+'/agent_output.tar.gz' in files, 'MISSING_TASK_ARCHIVE')
            members = archive_members(files[task_id+'/agent_output.tar.gz'])
            inner_receipts = [name for name in members if PurePosixPath(name).name == 'receipt.json']
            require(inner_receipts in ([], ['logs/vb103/receipt.json']), 'DUPLICATE_OR_UNSUPPORTED_INNER_RECEIPT')
            row['archive_sha256'] = sha(files[task_id+'/agent_output.tar.gz'])
            row['archive_member_sha256'] = {name: sha(data) for name, data in members.items()}
            if unit['pack_flavor'] == 'agent':
                trajectory = files.get(task_id+'/atif/trajectory.json')
                require(trajectory is not None, 'MISSING_TRAJECTORY_ACCOUNTING')
                row.update(recover_trajectory(task_id, entry, trajectory))
            else:
                outer = files.get(task_id+'/receipt.json')
                require(outer is not None, 'MISSING_OUTER_RECEIPT')
                receipt = json_bytes(outer)
                row['original_transport'] = preserved_receipt_fields(receipt)
                row.update({k: receipt[k] for k in ('requests_sent', 'attempt', 'http_status', 'finish_reason', 'error_kind', 'error_type') if k in receipt})
                # Accounting is retained but marked uncertified until the pair and identity agree.
                row['reported_cost_usd_unverified'] = receipt.get('cost_usd')
                row.update(recover_single(meta, unit, entry, header, hashes, outer, members, parse))
        except (InvalidEvidence, ValueError, KeyError, OSError, tarfile.TarError, AssertionError) as exc:
            row.update(accepted=False, status='unmeasured_infra', acceptance_reason=str(exc)[:250])
        result.append(row)
    require(len(result) == len(wanted), 'INCOMPLETE_RECONCILIATION')
    return result


def offline_only(*args, **kwargs):
    raise RuntimeError('OFFLINE_ADAPTER_FORBIDS_TRANSPORT')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--collection', type=Path, default=COLLECTION)
    args = ap.parse_args(); collection = args.collection.resolve()
    dependencies = verify_dependencies()
    e, _, pack, ctl = phase_context('criterion')
    # Block even an accidental call into the unchanged vendor transport.
    with ExitStack() as stack:
        for name in ('cli', 'admit', 'poll', 'download', 'harvest', 'save_state'):
            stack.enter_context(patch.object(ctl, name, offline_only))
        lock = stack.enter_context((ROOT/'runtime/judge_criterion.lock').open('a'))
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifest, completion, completed, snapshots = verify_collection(collection, ctl.STATE, e.RESULTS/'packs.json')
        admission = read(e.RESULTS/'admission_manifest.json'); quote = read(e.RESULTS/'QUOTE.json')
        require(admission['run_id'] == RUN_ID and admission['phase'] == 'criterion' and admission['state'] == 'FROZEN'
                and set(admission['configurations']) == set(POOL), 'ADMISSION_IDENTITY')
        require(sha((e.RESULTS/'admission_manifest.json').read_bytes()) == quote['admission_manifest_sha256']
                and sha((e.RESULTS/'packs.json').read_bytes()) == quote['packs_sha256'], 'ADMISSION_QUOTE_BINDING')
        for name, digest in admission['contract_hashes'].items():
            require(sha((ROOT.parent/name).read_bytes()) == digest, 'CONTRACT_CHANGED:'+name)
        require(sha((e.RESULTS/'transport_policy.json').read_bytes()) == admission['transport_policy_sha256'], 'TRANSPORT_POLICY_CHANGED')
        require(sha(WRITER.read_bytes()) == WRITER_SHA, 'PINNED_WRITER_CHANGED')
        writer = module('e47_offline_original_writer', WRITER)
        for name in ('gateway_request', 'registry_entry'):
            stack.enter_context(patch.object(writer, name, offline_only))
        prompt_module = prompts()
        parse = lambda unit, text: ctl.parse_verdict(unit, text, prompt_module)
        units = unique(read(e.RESULTS/'panel.json')['units'], 'config')
        require(units == unique(panel(), 'config'), 'PANEL_DIFFERS_FROM_FROZEN_SOURCE')
        # panel() resets paths; restore criterion context before any reads.
        e, _, pack, ctl = phase_context('criterion')
        state = ctl.load_state(); packs = read(e.RESULTS/'packs.json')['packs']
        actual_runs = {k: v for k, v in state['runs'].items() if v['part'] == 'main' and v.get('run_id')}
        require(set(actual_runs) == {r['key'] for r in manifest['runs']}, 'ORIGINAL_RUN_MASK')
        summaries, outputs = [], {}
        file_count = byte_count = 0
        for source in manifest['runs']:
            entry = actual_runs[source['key']]; cfg = source['config']; unit = units[cfg]
            require(all(entry.get(k) == source.get(k) for k in ('run_id', 'benchmark', 'config', 'part', 'task_ids')), 'LEDGER_RUN_IDENTITY')
            require(entry['selector'] == unit['selectors'][0] and entry['harness'] == unit['harness'], 'LEDGER_MODEL_HARNESS')
            packed = packs[unit['model_key']]; per = packed['per_config'][cfg]
            require(source['benchmark'] == packed['benchmark'] and per['rubric'] == unit['rubric']
                    and per['flavor'] == unit['pack_flavor'] and per['harness'] == unit['harness'], 'PACK_CONFIG_IDENTITY')
            expected_kwargs = dict(unit['kwargs'])
            if unit['pack_flavor'] != 'agent':
                expected_kwargs.update(judge_config=cfg, max_tokens=str(unit['max_tokens']), benchmark=entry['benchmark'])
            require(entry['kwargs'] == expected_kwargs, 'LEDGER_KWARGS')
            harness = read(e.RESULTS/('agent_harness.json' if unit['pack_flavor'] == 'agent' else 'agent_bundle_check.json'))
            expected_agent = harness['agent']
            digest = harness['contract_sha256'] if unit['pack_flavor'] == 'agent' else WRITER_SHA
            require(harness['verdict'] == 'PASS' and entry['agent'] == expected_agent and entry['judge_agent_sha256'] == digest, 'HARNESS_CERTIFICATE')
            cell_path = e.RESULTS/'cells'/(cfg.replace('|', '__')+'.json')
            require(sha(cell_path.read_bytes()) == admission['cells_sha256'][cfg], 'FROZEN_CELLS_CHANGED')
            cells = unique(read(cell_path)['cells'], 'cell'); metas = unique(per['cells'], 'task_id')
            require({m['cell'] for m in metas.values()} == {c['cell'] for c in cells.values() if c['status'] == 'render'} and
                    len({m['cell'] for m in metas.values()}) == len(metas), 'PACK_CELL_MASK')
            run_dir = collection/source['run_id']; directory = run_dir/'original_archive_attempt_1'
            indexed = verified_files(directory); file_count += len(indexed); byte_count += sum(r['bytes'] for r in indexed.values())
            command = read(directory/'collection_command.json')
            require(command['scientific_run_id'] == RUN_ID and command['run_id'] == source['run_id']
                    and command['returncode'] == 0 and command['command'] == ['/dfs/scratch0/brando9/bin/valk', 'run', 'output', source['run_id'], '-o', str(directory)], 'ORIGINAL_COLLECTION_COMMAND')
            require(len(indexed) == completed[source['run_id']]['files'] and sum(r['bytes'] for r in indexed.values()) == completed[source['run_id']]['bytes'], 'COLLECTION_TOTALS')
            snapshot_path = run_dir/'fetch_snapshot_attempt_1.json'
            require(sha(snapshot_path.read_bytes()) == snapshots[source['run_id']]['snapshot_sha256'], 'SNAPSHOT_HASH')
            snapshot = read(snapshot_path)
            require(snapshot['run_id'] == entry['run_id'] and snapshot['benchmark_name'] == entry['benchmark'] and
                    snapshot['label'] == entry['actual_label'] and snapshot['status'] == 'ERROR' and
                    snapshot['total_tasks'] == len(metas), 'ORIGINAL_METADATA_BINDING')
            rows = harvest_run(source, entry, unit, metas, cells, packed, pack, writer, parse, directory, indexed)
            known = sum(r.get('cost_usd') or 0 for r in rows)
            blob = {'run_id': entry['run_id'], 'scientific_run_id': RUN_ID, 'config': cfg, 'part': 'main',
                    'phase': 'criterion', 'selector': entry['selector'], 'kwargs': entry['kwargs'],
                    'n_cells': len(rows), 'accepted_count': sum(r['accepted'] for r in rows),
                    'status_counts': dict(Counter(r['status'] for r in rows)), 'charges_usd': known,
                    'cells': rows, 'evidence_kind': 'original_artifacts_only',
                    'server_run_status': snapshot['status'], 'server_task_state_counts': snapshot['task_state_counts'],
                    'server_final_callback_error': snapshots[source['run_id']]['error_summary'],
                    'collection_inventory_sha256': sha((directory/'files_sha256.json').read_bytes()),
                    'collection_command_sha256': sha((directory/'collection_command.json').read_bytes())}
            outputs[cfg] = blob
            summary = {k: blob[k] for k in ('run_id', 'config', 'n_cells', 'accepted_count', 'status_counts', 'charges_usd')}
            summary.update(reasons=dict(Counter(r['acceptance_reason'] for r in rows)),
                           unknown_charge_cells=sum(r.get('cost_usd') is None for r in rows))
            summaries.append(summary); print(json.dumps(summary), flush=True)
        require(file_count == completion['hashed_files'] and byte_count == completion['bytes'], 'COMPLETE_COLLECTION_TOTALS')
        # Only publish derived local harvests after every global binding passes.
        for cfg, blob in outputs.items():
            path = ctl.JUDGE/'strict_harvests'/(cfg.replace('|', '__')+'__main.json')
            if path.exists():
                require(read(path) == blob, 'EXISTING_HARVEST_DIFFERS; preserve and resolve explicitly')
            else:
                write(path, blob)
        from campaign_driver import merge_phase
        merge_phase(ctl, 'criterion')
        evidence = {'run_id': RUN_ID, 'phase': 'criterion', 'state': 'RECONCILED', 'route': 'offline original artifacts',
                    'admission_manifest_sha256': quote['admission_manifest_sha256'],
                    'collection_completion_sha256': sha((collection/'collection_completion_receipt.json').read_bytes()),
                    'source_ledger_sha256': manifest['source_ledger_sha256'], 'verified_files': file_count,
                    'verified_bytes': byte_count, 'frozen_dependency_count': len(dependencies),
                    'adapter_sha256': sha(Path(__file__).read_bytes()), 'runs': summaries,
                    'new_inference_calls': 0, 'transport_commands': 0, 'whole_experiment_complete': False,
                    'missing_artifacts_do_not_establish_absent_verdict': True}
        write(e.RESULTS/'original_artifact_reconciliation.json', evidence)
        charges = []
        for path in sorted((ctl.JUDGE/'strict_harvests').glob('*.json')):
            blob = read(path)
            charges.append({'config': blob['config'], 'part': blob['part'], 'run_id': blob['run_id'],
                            'known_reported_sum_usd': blob['charges_usd'],
                            'unknown_charge_cells': sum(r.get('cost_usd') is None for r in blob['cells']),
                            'cells': blob['n_cells'], 'accepted': blob['accepted_count']})
        unknown = sum(r['unknown_charge_cells'] for r in charges); known = sum(r['known_reported_sum_usd'] for r in charges)
        write(e.RESULTS/'charges.json', {'route': 'Vals-funded Valkyrie', 'runs': charges,
              'reported_total_usd': None if unknown else known, 'known_reported_sum_usd': known,
              'unknown_charge_cells': unknown, 'source': 'original receipt/trajectory accounting; missing cost unknown'})
        write(ROOT/'runtime/judge_criterion_RECONCILED.json', evidence)


if __name__ == '__main__':
    main()
