# Search Judge remote deterministic receipt

**TLDR:** The owned `skampere2` worktree ran the five-test EFG regression suite in a named tmux session and passed without a provider call.

- Session: `cj-search-smoke-10-21-2026: 1 windows (created Wed Oct 21 08:36:12 2026)`.
- Worktree: `/lfs/skampere2/0/brando9/cert-judge-search-judge-smoke-10-21-2026` at `04ceea558576f0ae0534c517087ab0397ba0c15e`.
- Command: `PYTHONPATH=py_src /lfs/skampere2/0/brando9/.local/bin/uv run --isolated --no-project --with pytest --python 3.11 python -m pytest -q tests/test_efg_judge.py`.
- Result: `5 passed in 0.02s`; exit 0.
- Preserved artifacts: `remote-efg.log` (SHA-256 `ef0e7ef49e71fa999842be0cb8d22ec1058d3a384ed5c0a2ec6efb8f434975ac`) and `remote-efg.status` (SHA-256 `19eaf43821a7660ec323a87c8457bf74823beb296c39f5e01aa8a683aa50f061`).
- Cleanup: the task-owned remote worktree and bare clone were removed after artifact transfer; no `cj-search-smoke-10-21-2026` tmux session remained.
