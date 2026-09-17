from pathlib import Path
import json

from cert_judge.experiment_layout import check, reconcile


def fixture_root(tmp_path):
    archived = tmp_path / 'experiments/archive/01_done'
    archived.mkdir(parents=True)
    (archived.parent / 'layout.json').write_text(json.dumps({
        'active': {}, 'support': {'archive':'finished work'},
        'retired': {'01_done':'experiments/archive/01_done'},
    }))
    return archived


def test_repository_layout():
    assert check(Path(__file__).resolve().parents[1]) == []


def test_leftovers_preserve_conflicts_and_are_idempotent(tmp_path):
    archived = fixture_root(tmp_path)
    old = tmp_path / 'experiments/01_done'
    old.mkdir()
    (old / 'score.json').write_text('local result')
    (archived / 'score.json').write_text('frozen result')
    (old / 'cache').mkdir()
    (old / 'cache/entry').write_bytes(b'\x00unique')
    assert check(tmp_path)
    receipts = reconcile(tmp_path)
    assert (archived / 'score.json').read_text() == 'frozen result'
    assert (archived.parent / '.local_leftovers/01_done/score.json').read_text() == 'local result'
    assert (archived / 'cache/entry').read_bytes() == b'\x00unique'
    assert receipts and not old.exists()
    assert check(tmp_path) == []
    assert reconcile(tmp_path) == []


def test_leftover_symlink_does_not_move_external_contents(tmp_path):
    archived = fixture_root(tmp_path)
    outside = tmp_path / 'outside'
    outside.mkdir()
    (outside / 'keep').write_text('untouched')
    old = tmp_path / 'experiments/01_done'
    old.symlink_to(outside, target_is_directory=True)
    reconcile(tmp_path)
    assert archived.is_dir() and not archived.is_symlink()
    assert (outside / 'keep').read_text() == 'untouched'
    assert (archived.parent / '.local_leftovers/01_done').is_symlink()
