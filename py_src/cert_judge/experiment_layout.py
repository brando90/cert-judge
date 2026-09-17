"""Check experiment lifecycle layout and preserve obsolete local leftovers.

Uses only the standard library; never reads credentials or invokes inference.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def inventory(root: Path) -> dict:
    return json.loads((root / 'experiments/archive/layout.json').read_text())


def check(root: Path) -> list[str]:
    config = inventory(root)
    errors = []
    allowed = set(config['active']) | set(config['support'])
    for path in sorted((root / 'experiments').iterdir()):
        if path.is_dir() or path.is_symlink():
            if path.name not in allowed:
                errors.append(f'Unregistered or retired experiment directory: {path.relative_to(root)}')
    for name, task in config['active'].items():
        if not task.strip() or not (root / 'experiments' / name).is_dir():
            errors.append(f'Active experiment needs a directory and current task: {name}')
    for name, destination in config['retired'].items():
        if name in allowed:
            errors.append(f'Retired name also registered as active/support: {name}')
        target = root / destination
        if not target.exists() and not target.is_symlink():
            errors.append(f'Missing canonical archived home: {destination}')
    return errors


def reconcile(root: Path) -> list[dict[str, str]]:
    """Move obsolete local files without overwriting any existing destination.

    Does not follow symlinks. Every collision, including an identical duplicate,
    is kept in a separate ignored recovery directory. Only empty directories
    are removed. Re-running after completion is a no-op.
    """
    receipts = []
    config = inventory(root)
    recovery = root / 'experiments/archive/.local_leftovers'

    def merge(source: Path, target: Path, old_name: str) -> None:
        # Treat symlinks as files, including dangling links; never traverse them.
        if source.is_dir() and not source.is_symlink() and target.is_dir() and not target.is_symlink():
            for child in sorted(source.iterdir()):
                merge(child, target / child.name, old_name)
            source.rmdir()
            return
        dest = target
        if target.exists() or target.is_symlink():
            dest = recovery / old_name / source.relative_to(root / 'experiments' / old_name)
            candidate = dest
            serial = 1
            while dest.exists() or dest.is_symlink():
                dest = candidate.with_name(candidate.name + f'.preserved-{serial}')
                serial += 1
        # Never follow a destination ancestor symlink.
        if any(p.is_symlink() for p in dest.parents if p != root.parent):
            raise ValueError(f'Refusing destination with symlink ancestor: {dest}')
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(dest))
        receipts.append({'source':str(source.relative_to(root)), 'destination':str(dest.relative_to(root))})

    for name, destination in config['retired'].items():
        source = root / 'experiments' / name
        target = root / destination
        if not source.exists() and not source.is_symlink():
            continue
        if not target.exists() and not target.is_symlink():
            raise ValueError(f'Canonical destination missing; refusing to guess: {destination}')
        merge(source, target, name)
    if receipts:
        recovery.mkdir(parents=True, exist_ok=True)
        receipt = recovery / 'reconciliation.jsonl'
        with receipt.open('a') as stream:
            for row in receipts:
                stream.write(json.dumps(row) + '\n')
    return receipts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--reconcile', action='store_true')
    args = parser.parse_args()
    if args.reconcile:
        moved = reconcile(ROOT)
        print(f'Preserved and relocated {len(moved)} local entries.')
    errors = check(ROOT)
    for error in errors:
        print(error)
    if not errors:
        config = inventory(ROOT)
        print(f'Layout OK: {len(config["active"])} active experiments; no retired directories at the active level.')
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
