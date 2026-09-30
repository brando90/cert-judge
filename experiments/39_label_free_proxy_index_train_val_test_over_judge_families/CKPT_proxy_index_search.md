# CKPT: proxy-index search (experiment 39)

Created: 09-30-2026 16:35 UTC
Last updated: 09-30-2026 12:09 PDT

Task: run experiments/39_label_free_proxy_index_train_val_test_over_judge_families end to end on SNAP skampere1 per cc.md.

State:
- Phase: DISPATCHED on skampere1, cc.md step 1 done (checkpoint + ledger). No judge call made. Nothing spent.
- Worker: tmux `cj-e39-proxy-index-search` on skampere1; clauded (personal profile, --dangerously-skip-permissions), model claude-fable-5-1, effort max; SNAP pre-approval in force.
- Clone: /lfs/skampere1/0/brando9/cert-judge_e39, branch `e39-proxy-index-search` cut from origin/main 0be32d7 (the runbook landing 2d5b16a / PR #48 is on main, so no fallback branch was needed).
- VeriBench read-only clone: /lfs/skampere1/0/brando9/veribench_e39 (git clone started during step 1).
- Health check: `snap_health.sh --node skampere1` -> one FAIL, shared DFS 96% used (3264 GiB free); not relevant, every experiment file lives on node-local /lfs (15 TiB free). WARN rows are dirty shared DFS checkouts this task does not touch.
- Prerequisites verified: ~/.config/valkyrie/valkyrie.yaml mode 600 (never printed); lake 5.0.0 (Lean 4.22.0); Lean project /lfs/skampere1/0/brando9/vb90_grading/lean_project (toolchain leanprover/lean4:v4.22.0); valk; cloudflared; ports 8990-8998 free; `gh auth status` OK as brando90.
- Decision (Rule 57): the $2,000 hold rule from cc.md / PROTOCOL.md (APPROVED_SPEND_USD restated by the dispatcher) stays in force even though the repo CLAUDE.md (commit 0be32d7, "Valkyrie runs have no automatic caps") discourages adding caps: it is pre-registered in the locked protocol, no new cap is being added, and the planning estimate ($1,421) is under it.
- Open item: `uutils` is not importable from /lfs/skampere1/0/brando9/vb103_venv/bin/python or /usr/bin/python3 (needed only for the step-11 landing email); resolve before landing. numpy is not needed by any script (verified by grep of imports).
- LANDED (earlier, docs only): 2d5b16a74170b4f03ebc78ebaf3f4e16dcb26506 https://github.com/brando90/cert-judge/pull/48 09-30-2026 17:53 UTC (rebase-merge of PR #48; 19 tests; QA: not requested).

Next command (skampere1, this clone, inside tmux `cj-e39-proxy-index-search`):
  export E39_VERIBENCH_REPO=/lfs/skampere1/0/brando9/veribench_e39 E39_LAKE_DIR=/lfs/skampere1/0/brando9/vb90_grading/lean_project E39_LAKE_BIN=$HOME/.elan/bin/lake E39_PYTHON=/lfs/skampere1/0/brando9/vb103_venv/bin/python PATH=$HOME/.elan/bin:$PATH
  cd /lfs/skampere1/0/brando9/cert-judge_e39/experiments/39_label_free_proxy_index_train_val_test_over_judge_families
  $E39_PYTHON -m pytest scripts/test_e39.py -q && $E39_PYTHON scripts/build_panel.py && $E39_PYTHON scripts/build_probes.py --jobs 6

Blockers: none.
