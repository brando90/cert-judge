# CKPT: proxy-index search (experiment 39)

Created: 09-30-2026 16:35 UTC
Last updated: 09-30-2026 13:27 PDT

Task: run experiments/39_label_free_proxy_index_train_val_test_over_judge_families end to end on SNAP skampere1 per cc.md.

State:
- Phase: cc.md step 6 DONE (nine services up: ports 8990-8998, benchmarks certjudge39-{sol6h,sonnet5m,luna6h,gem31h,opus55x,qwen36,t2-luna,t2-sonnet5,t2-qwen}; agent-judge names use hyphens because Valkyrie rejects underscores); next: step 8 worker loop. No judge call made. Nothing spent.
- Services: pids in private/service_<key>.pid and private/tunnel_<key>.pid; receipts private/deployment_<key>.json (tunnel URL) and results/deployment_<key>.json (public); `deploy_service.py --model <key> --status` re-checks. Never redeploy a model with a live run (the tunnel URL would change).
- Step 4 final: results/probe_manifest.json (mirror project, 677 rows): ident 24/1, ms_gold 76/4, bm_gold 37/60, crit 75, ms_cand 3/72, alpha 3/72, reorder 0/75, sorry 3/72, spam 3/72 valid/invalid.
- Step 5: render 56 configs -> 28,591 calls (+504 deterministic, 81 unmeasured extraction); QUOTE 28,591 calls, expected $790.59 (train 129.49, val 127.01, test 534.13), worst case $11,945, within cap; packs PASS (9 packs under private/packs, 793 MB); controls -> results/harvest/ctl__*.json (521 cells each, editdist = exact Levenshtein.ratio).
- Step 4 finding: first build (vb90_grading project) -> 72/75 candidates and gold 1_MyAdd do not elaborate; 9 candidates fail only at `import VeriBench*`. Fix (Rule 57 decision, recorded in results.md deviations): private mirror project `private/lean_mirror` (same lakefile/manifest/toolchain, symlinked packages) + the three empty prelude modules compiled with cert-judge's LeanCompiler.compile_module (sources byte-identical to the archived PTI-v0 run). `private/env.sh` now sets E39_LAKE_DIR to the mirror. First manifest kept at private/probe_manifest_no_prelude_09-30-2026.json. Shared Lean project untouched.
- Step 2: `$E39_PYTHON -m pytest scripts/test_e39.py -q` -> 19 passed in 1.22 s (skampere1, vb103_venv Python 3.12.14).
- Step 3: `scripts/build_panel.py` -> results/panel.json, 60 units (train 18 LLM + 4 controls, val 20, test 18); prompt fingerprints unchanged from the dry run (H2 469a2ac3875c..., D0 c0da49bbe86d...).
- Step 4: `nohup $E39_PYTHON scripts/build_probes.py --jobs 6 > private/logs/build_probes.log` started 09-30-2026 ~12:20 PDT (pid 40593); `lake env lean` on gold 0_bisect_right: exit 0 in 3.6 s (sorry warnings only). Expect 1-2 h.
- Step 6 (zero-call part, run early because it needs no pack): `verify_bundle.py` PASS and `verify_agent_harness.py` PASS (agent `brando_terminus_gateway`, secret_env null = the contract maps fellows/brandoModelGatewayApiKey itself, so no `-s` flag); receipts committed as 2c816b8. `private/valkyrie.yaml` was seeded as a mode-600 copy of the host config (deploy_service.py adds the benchmark entries to it).
- Valkyrie CLI verified read-only: `valk agent list --all` shows vb103_judge (2026-09-29), terminus2, brando_terminus_gateway, brando_terminus_astra_smoke. (`valk run list` needs a tty pager; the controller uses `run status --format json`.)
- Worker: tmux `cj-e39-proxy-index-search` on skampere1; clauded (personal profile, --dangerously-skip-permissions), model claude-fable-5-1, effort max; SNAP pre-approval in force.
- Clone: /lfs/skampere1/0/brando9/cert-judge_e39, branch `e39-proxy-index-search` cut from origin/main 0be32d7 (the runbook landing 2d5b16a / PR #48 is on main, so no fallback branch was needed).
- VeriBench read-only clone: /lfs/skampere1/0/brando9/veribench_e39 at d7d36c319 (experiments 75, 100, 103, 105 and scripts/scsc present).
- Health check: `snap_health.sh --node skampere1` -> one FAIL, shared DFS 96% used (3264 GiB free); not relevant, every experiment file lives on node-local /lfs (15 TiB free). WARN rows are dirty shared DFS checkouts this task does not touch.
- Prerequisites verified: ~/.config/valkyrie/valkyrie.yaml mode 600 (never printed); lake 5.0.0 (Lean 4.22.0); Lean project /lfs/skampere1/0/brando9/vb90_grading/lean_project (toolchain leanprover/lean4:v4.22.0); valk; cloudflared; ports 8990-8998 free; `gh auth status` OK as brando90.
- Decision (Rule 57): the $2,000 hold rule from cc.md / PROTOCOL.md (APPROVED_SPEND_USD restated by the dispatcher) stays in force even though the repo CLAUDE.md (commit 0be32d7, "Valkyrie runs have no automatic caps") discourages adding caps: it is pre-registered in the locked protocol, no new cap is being added, and the planning estimate ($1,421) is under it.
- Landing email route: `PYTHONPATH=/dfs/scratch0/brando9/ultimate-utils/py_src /usr/bin/python3 -c 'from uutils.emailing import send_email_smtp'` imports OK (vb103_venv lacks dill); ~/keys/gmail_app_password.txt present (mode 600). numpy is not needed by any script.
- LANDED (earlier, docs only): 2d5b16a74170b4f03ebc78ebaf3f4e16dcb26506 https://github.com/brando90/cert-judge/pull/48 09-30-2026 17:53 UTC (rebase-merge of PR #48; 19 tests; QA: not requested).

Next command (skampere1, this clone, inside tmux `cj-e39-proxy-index-search`):
  export E39_VERIBENCH_REPO=/lfs/skampere1/0/brando9/veribench_e39 E39_LAKE_DIR=/lfs/skampere1/0/brando9/vb90_grading/lean_project E39_LAKE_BIN=$HOME/.elan/bin/lake E39_PYTHON=/lfs/skampere1/0/brando9/vb103_venv/bin/python PATH=$HOME/.elan/bin:$PATH
  cd /lfs/skampere1/0/brando9/cert-judge_e39/experiments/39_label_free_proxy_index_train_val_test_over_judge_families
  source private/env.sh   # the exports above
  for k in sol6h sonnet5m luna6h gem31h opus55x qwen36 t2_luna t2_sonnet5 t2_qwen; do $E39_PYTHON scripts/deploy_service.py --model $k --status || $E39_PYTHON scripts/deploy_service.py --model $k; done   # step 6
  tmux new-window -t cj-e39-proxy-index-search -n worker 'cd $PWD && source private/env.sh && E39_CONCURRENCY=20 bash scripts/worker_loop.sh'   # step 8

Blockers: none.
