"""Read-only callback gate for new probe admissions; no transport or recovery."""
import math
from pathlib import Path
import time

from e47_adapter import POOL, RUN_ID, read, sha, write
from callback_watch import MODELS, healthy_codes, process


def require_callback_ready(root, admission_digest, now=None):
    root = Path(root).resolve()
    now = time.time() if now is None else now
    runtime = root/'runtime'
    bp, op = runtime/'callback_binding.json', runtime/'callback_observation.json'
    binding_bytes, observation_bytes = bp.read_bytes(), op.read_bytes()
    import json
    binding, observation = json.loads(binding_bytes), json.loads(observation_bytes)
    for record in (binding, observation):
        if (record.get('run_id'), record.get('phase')) != (RUN_ID, 'probes'):
            raise ValueError('callback run/phase differs')
    age = now-observation['observed_epoch']
    if not math.isfinite(age) or not 0 <= age <= 150:
        raise ValueError('callback observation is stale or future')
    if (observation.get('state') != 'HEALTHY' or observation.get('bound') is not True
            or observation.get('observation_kind') != 'monitor'
            or not binding['initial_observed_epoch'] < observation['observed_epoch']):
        raise ValueError('subsequent healthy callback observation required')
    observer_digest = sha((root/'callback_watch.py').read_bytes())
    if (binding.get('observer_sha256') != observer_digest
            or observation.get('observer_sha256') != observer_digest
            or observation.get('binding_sha256') != sha(binding_bytes)):
        raise ValueError('callback binding/observer bytes differ')
    admission_path = root/'results/probes/admission_manifest.json'
    expected_files = {str(admission_path): admission_digest,
                      str(root/'private/probes/valkyrie.yaml'): sha((root/'private/probes/valkyrie.yaml').read_bytes())}
    if binding['files'] != expected_files or any(sha(Path(p).read_bytes()) != d for p,d in expected_files.items()):
        raise ValueError('callback frozen admission/config bytes differ')
    admission = read(admission_path)
    if ((admission.get('run_id'), admission.get('phase'), admission.get('state')) != (RUN_ID, 'probes', 'FROZEN')
            or sorted(admission.get('configurations', [])) != sorted(POOL)):
        raise ValueError('callback admission population differs')
    models = observation['models']
    if (set(binding['models']) != set(MODELS) or len(models) != 4
            or {r['model'] for r in models} != set(MODELS)):
        raise ValueError('callback model universe differs')
    for row in models:
        expected = binding['models'][row['model']]
        if row.get('healthy') is not True or not healthy_codes(row['codes']) or row['identity'] != expected:
            raise ValueError('callback endpoint/identity differs')
        deployment = root/'private/probes'/('deployment_'+row['model']+'.json')
        if sha(deployment.read_bytes()) != expected['deployment_sha256']:
            raise ValueError('callback deployment changed')
        for kind in ('service', 'tunnel'):
            if process(expected[kind]['pid']) != expected[kind]:
                raise ValueError('callback process changed')
    if bp.read_bytes() != binding_bytes:
        raise ValueError('callback binding changed during gate')
    return {'run_id': RUN_ID, 'phase': 'probes', 'state': 'PASS', 'verified_epoch': now,
            'admission_manifest_sha256': admission_digest, 'binding_sha256': sha(binding_bytes),
            'observation_sha256': sha(observation_bytes), 'observer_sha256': observer_digest,
            'observation_age_seconds': age, 'processes_verified': 8, 'transport_called': False}


def before_probe_transport(ctl, root, admission_digest, original_command):
    """A late gate failure is proven pretransport, never ambiguous admission."""
    try:
        return require_callback_ready(root, admission_digest)
    except Exception as exc:
        state = ctl.load_state()
        for entry in state['runs'].values():
            if entry.get('phase') == 'admitting' and entry.get('command') == original_command:
                entry.update(phase='admission_blocked_before_transport', transport_called=False,
                             callback_error_type=type(exc).__name__, callback_blocked_epoch=time.time())
        ctl.save_state(state)
        raise


def admit_probe(ctl, root, admission_digest, config, part, suffix=''):
    key = config+'@'+part+suffix
    runs = ctl.load_state()['runs']
    if runs.get(key, {}).get('phase') == 'admission_blocked_before_transport':
        raise RuntimeError('preserved callback gate rejection requires explicit pretransport recovery: '+config)
    if key not in runs:
        gate = require_callback_ready(root, admission_digest)
        write(Path(root)/'runtime/callback_admission_gates'/f"{config.replace('|','__')}__{part}.json", gate)
    # Frozen admit adopts an existing key without issuing another start. This
    # remains available under an unhealthy callback, as do polling/harvesting.
    return ctl.admit(config, part, concurrency=20, suffix=suffix)
