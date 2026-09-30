# CKPT: proxy-index search (experiment 39)

Created: 09-30-2026 16:35 UTC
Last updated: 09-30-2026 17:35 UTC

Task: run experiments/39_label_free_proxy_index_train_val_test_over_judge_families end to end on SNAP skampere1 per cc.md.

State:
- Phase: DESIGNED, not dispatched. No judge call made. Nothing spent.
- Code: scripts/ complete; `python3 -m pytest scripts/test_e39.py -q` -> 19 passed (cloud container, 09-30-2026). Theorem finder widened to same-line `@[attr] theorem` heads after the PR #48 review (181/181 gold theorems found, was 60). Agent-judge family (Terminus2 + Luna val; Terminus2 + Sonnet 5 and + Qwen test; H2, D0) added the same day at Brando's request ("the proxy metric should work for multiple agents").
- Dry run (cloud container, local VeriBench checkout, no Lean): panel 60 units; probes constructed (unvalidated); 56 configurations rendered; quote 51,500 calls / $1,421 expected (cap $2,000); pack round-trip PASS for opus55x (transport flavor) and t2_luna (agent flavor); controls scored.
- Coordination: a sibling cloud session ("Sir Judge validation setup") read PR #48 on 09-30-2026 and chose not to duplicate; it is reviewing (noted the legacy prompts' last-theorem reference makes gold-deletion ladders one-step for P1/P4/P8/LEX — recorded in PROTOCOL.md as a known configuration property). No shared checkout; it should post findings on PR #48. Outputs kept under results/planning_dryrun/ (superseded on SNAP).
- Branch: ccr-a2f6f115-a9zq3m (cert-judge). Worker branch on SNAP: e39-proxy-index-search.

Next command (on skampere1, in the node-local clone, inside tmux `cj-e39-proxy-index-search`):
  export E39_VERIBENCH_REPO=/lfs/skampere1/0/brando9/veribench_e39 E39_LAKE_DIR=/lfs/skampere1/0/brando9/vb90_grading/lean_project E39_LAKE_BIN=$HOME/.elan/bin/lake E39_PYTHON=/lfs/skampere1/0/brando9/vb103_venv/bin/python PATH=$HOME/.elan/bin:$PATH
  cd experiments/39_label_free_proxy_index_train_val_test_over_judge_families
  $E39_PYTHON -m pytest scripts/test_e39.py -q && $E39_PYTHON scripts/build_panel.py && $E39_PYTHON scripts/build_probes.py --jobs 6

Blockers: none known. Cannot dispatch from the cloud container (no SNAP access); dispatch from a laptop master session.
