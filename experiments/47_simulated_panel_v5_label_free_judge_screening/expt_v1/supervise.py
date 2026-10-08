#!/usr/bin/env python3
"""Durable, serial CLI executor with process receipts and bounded continuation.

This makes no provider API calls. Its configuration is a locally verified argv
array, never text from a worker log. Active scientific jobs prevent replacement.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import time


def atomic_json(path: Path, obj: dict) -> None:
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(obj, indent=2) + '\n')
    tmp.replace(path)


def process_group_alive(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', type=Path, required=True)
    args = ap.parse_args()
    cfg = json.loads(args.config.read_text())
    cwd = Path(cfg['cwd']).resolve()
    runtime = Path(cfg['runtime']).resolve()
    runtime.mkdir(parents=True, exist_ok=True)
    lock = (runtime / 'supervisor.lock').open('a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return 73
    state_path = runtime / 'supervisor.json'
    previous = json.loads(state_path.read_text()) if state_path.exists() else {}
    if previous.get('run_id') not in (None, cfg['run_id']):
        raise ValueError('A different run owns the state directory')
    if previous.get('pgid') and process_group_alive(previous['pgid']):
        raise RuntimeError('Previous writer or child remains alive; adoption required')
    start_attempt = int(previous.get('attempt', 0)) + 1
    state = {'run_id': cfg['run_id'], 'supervisor_pid': os.getpid(),
             'host': os.uname().nodename, 'started_epoch': time.time(),
             'cwd': str(cwd), 'maximum_attempts': cfg['maximum_attempts']}
    prompt = Path(cfg['prompt']).read_text()
    for attempt in range(start_attempt, cfg['maximum_attempts'] + 1):
        for marker in ('COMPLETE.json', 'BLOCKED.json'):
            path = runtime / marker
            if path.exists():
                receipt = json.loads(path.read_text())
                if receipt.get('run_id') == cfg['run_id']:
                    state.update(state='worker_terminal_receipt', marker=marker,
                                 receipt=receipt, heartbeat_epoch=time.time())
                    atomic_json(state_path, state)
                    return 0
        active = runtime / 'active_jobs.json'
        if active.exists() and json.loads(active.read_text()).get('jobs'):
            state.update(state='adoption_required', heartbeat_epoch=time.time())
            atomic_json(state_path, state)
            return 75
        log_path = runtime / f'executor_attempt_{attempt}.log'
        with log_path.open('wb') as log:
            follow = ('\nThis is a serial continuation. Read your checkpoint and reconcile existing '
                      'cells/processes first. Do not repeat completed calls.\n' if attempt > 1 else '')
            proc = subprocess.Popen(cfg['argv'], cwd=cwd, stdin=subprocess.PIPE,
                                    stdout=log, stderr=subprocess.STDOUT,
                                    start_new_session=True)
            proc.stdin.write((prompt + follow + '\nRun identity: ' + cfg['run_id'] + '\n').encode())
            proc.stdin.close()
            state.update(attempt=attempt, pid=proc.pid, pgid=proc.pid,
                         argv=cfg['argv'], state='executor_running', log=str(log_path))
            while proc.poll() is None:
                state.update(heartbeat_epoch=time.time(), log_bytes=log_path.stat().st_size)
                atomic_json(state_path, state)
                time.sleep(cfg.get('heartbeat_seconds', 30))
            state.update(exit_code=proc.returncode, heartbeat_epoch=time.time())
            atomic_json(state_path, state)
        if process_group_alive(proc.pid):
            state.update(state='child_alive_adoption_required')
            atomic_json(state_path, state)
            return 75
        tail = log_path.read_text(errors='replace')[-20000:].lower()
        if any(s in tail for s in ('refresh_token_reused', 'token_expired',
                                   'usage limit', 'quota exceeded',
                                   'not supported when using codex', '401 unauthorized')):
            state.update(state='provider_recovery_required')
            atomic_json(state_path, state)
            return 77
        state.update(state='executor_exited')
        atomic_json(state_path, state)
    state.update(state='attempt_budget_reached', heartbeat_epoch=time.time())
    atomic_json(state_path, state)
    return 78


if __name__ == '__main__':
    raise SystemExit(main())
