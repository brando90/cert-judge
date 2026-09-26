#!/usr/bin/env python3
"""Save and apply-check the complete nonignored task patch in private scratch.

Does not modify the real repository index, commit, or write outside this
checkout. Incoming consultation/launcher artifacts are included as delivered.
The patch and receipt are ignored scratch artifacts to avoid self-reference.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'py_src/cert_judge').is_dir() and (p / 'pyproject.toml').is_file())
HERE = Path(__file__).resolve().parents[1]
BASE = 'f73228a9350b59001fb4ed187ef7351d73503e30'


def run(args, cwd=ROOT, accepted=(0,)):
    result = subprocess.run(args, cwd=cwd, capture_output=True)
    assert result.returncode in accepted, result.stderr.decode(errors='replace')
    return result.stdout


def main():
    verification = json.loads((HERE / 'results/verification.json').read_text())
    assert verification['result'] == 'PASS'
    assert run(['git', 'rev-parse', 'HEAD']).decode().strip() == BASE
    run(['git', 'diff', '--cached', '--quiet'])
    changed = run(['git', 'diff', '--name-only', BASE]).decode().splitlines()
    added = run(['git', 'ls-files', '--others', '--exclude-standard']).decode().splitlines()
    paths = sorted(changed + added)
    assert len(paths) == len(set(paths))
    for path in paths:
        assert path.startswith(('paper_latex/ICLR_2027_submission/',
                               str(HERE.parent.relative_to(ROOT)) + '/')), path
    patch = run(['git', 'diff', '--binary', BASE, '--', *changed])
    for path in sorted(added):
        patch += run(['git', 'diff', '--no-index', '--binary', '--', '/dev/null', path], accepted=(1,))
    tmp = HERE / 'tmp'
    tmp.mkdir(exist_ok=True)
    patch_path = tmp / 'feedback_revision.patch'
    patch_path.write_bytes(patch)
    scratch = Path(tempfile.mkdtemp(prefix='patch-check-', dir=tmp))
    # A new local repository prevents Git from discovering the shared parent.
    run(['git', 'init', '--quiet'], scratch)
    for path in changed:
        target = scratch / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(run(['git', 'show', BASE + ':' + path]))
    run(['git', 'apply', '--check', str(patch_path)], scratch)
    run(['git', 'apply', str(patch_path)], scratch)
    matched = {}
    for path in paths:
        assert (scratch / path).read_bytes() == (ROOT / path).read_bytes(), path
        matched[path] = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
    run(['git', 'diff', '--cached', '--quiet'])
    receipt = {'base_commit': BASE, 'patch': str(patch_path.relative_to(ROOT)),
               'patch_sha256': hashlib.sha256(patch).hexdigest(), 'bytes': len(patch),
               'check_directory': str(scratch.relative_to(ROOT)),
               'apply_check_exit_code': 0, 'scratch_apply_exit_code': 0,
               'all_applied_files_byte_equal_to_working_tree': True,
               'files': len(paths), 'tracked_changed_files': len(changed),
               'new_files': len(added), 'file_sha256': matched,
               'real_repository_index_unchanged': True, 'commits_created': 0}
    (tmp / 'patch_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: receipt[k] for k in ['patch', 'patch_sha256', 'bytes', 'files',
                     'apply_check_exit_code', 'all_applied_files_byte_equal_to_working_tree']}, indent=2))


if __name__ == '__main__':
    main()
