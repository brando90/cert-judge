# CKPT: proxy-index search (experiment 39)

Created: 09-30-2026 16:35 UTC
Last updated: 09-30-2026 16:35 UTC

Task: run experiments/39_label_free_proxy_index_train_val_test_over_judge_families end to end on SNAP skampere1 per cc.md.

State:
- Phase: DESIGNED, not dispatched. No judge call made. Nothing spent.
- Code: scripts/ complete; `python3 -m pytest scripts/test_e39.py -q` -> 16 passed (cloud container, 09-30-2026).
- Dry run (cloud container, local VeriBench checkout, no Lean): panel 54 units; probes constructed (unvalidated); 50 configurations rendered; quote 45,136 calls / $1,084 expected; pack round-trip PASS for opus55x; controls scored. Outputs kept under results/planning_dryrun/ (superseded on SNAP).
- Branch: ccr-a2f6f115-a9zq3m (cert-judge). Worker branch on SNAP: e39-proxy-index-search.

Next command (on skampere1, in the node-local clone, inside tmux `cj-e39-proxy-index-search`):
  export E39_VERIBENCH_REPO=/lfs/skampere1/0/brando9/veribench_e39 E39_LAKE_DIR=/lfs/skampere1/0/brando9/vb90_grading/lean_project E39_LAKE_BIN=$HOME/.elan/bin/lake E39_PYTHON=/lfs/skampere1/0/brando9/vb103_venv/bin/python PATH=$HOME/.elan/bin:$PATH
  cd experiments/39_label_free_proxy_index_train_val_test_over_judge_families
  $E39_PYTHON -m pytest scripts/test_e39.py -q && $E39_PYTHON scripts/build_panel.py && $E39_PYTHON scripts/build_probes.py --jobs 6

Blockers: none known. Cannot dispatch from the cloud container (no SNAP access); dispatch from a laptop master session.
