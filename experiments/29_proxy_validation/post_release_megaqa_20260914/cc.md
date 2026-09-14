# Experiment 29 post-release advisory review

You are the single review worker for the Experiment 29 release closeout. Work only in the dedicated checkout and branch named below. The release is already published; do not rerun the experiment, republish any artifact, delete any Weights & Biases report, or touch Experiment 30.

SNAP PRE-APPROVAL (Brando, 2026-09-14): you run with full access (permission prompts and sandbox bypassed). Every command, install, Docker/GPU use, file and git operation (branch, commit, push, PR, merge per Rule 46) and every budgeted experiment call needed for this task is already approved. Never stop to ask for permission or confirmation; treat any approval step as granted, proceed, and log what you did. Pause only for a real blocker (missing credential, exhausted budget, a human-only login step).

## Immutable review target

- Original base commit: `03946b83d85af2530971322ec6dfcdba80e0bacd`
- Published release commit: `c20027dc2b10758b8128adca5d5b93eeacba2653`
- Release-patch Secure Hash Algorithm 256-bit digest: `e720c9042bc65b0c7179fb7b1aeffdc67e9b1c1dc00aa8c6b6ea63627f00dc64`
- Dispatch base on current `origin/main`: `0fa83475fc0f8e147ca281b7bfbc6a2f8652990c`
- Task branch: `codex/exp29-release-megaqa-20260914`
- Historical path: `experiments/29_pti_v0_cli_bridge/`
- Current renamed path: `experiments/29_proxy_validation/`
- Review record directory: `experiments/29_proxy_validation/post_release_megaqa_20260914/`

The release commit changed exactly these 12 paths:

1. `.gitignore`
2. `experiments/29_pti_v0_cli_bridge/MEGA_QA_REPORT.md`
3. `experiments/29_pti_v0_cli_bridge/PR_BODY.md`
4. `experiments/29_pti_v0_cli_bridge/README.md`
5. `experiments/29_pti_v0_cli_bridge/README_FOR_BRANDO.md`
6. `experiments/29_pti_v0_cli_bridge/STATUS_PTI_V0_V4.md`
7. `experiments/29_pti_v0_cli_bridge/expt_v5/push_to_wandb.py`
8. `experiments/29_pti_v0_cli_bridge/results.md`
9. `experiments/29_pti_v0_cli_bridge/results/wandb_report.json`
10. `pyproject.toml`
11. `tests/test_experiment29_wandb_publisher.py`
12. `uv.lock`

## Reviewer identity and acceptance status

- Requested executor: `clauded-vals --model claude-opus-5 --effort max`
- Role: advisory review of a critical scientific release.
- This invocation is not an accepted Mega quality assurance stage. The repository policy currently names `claude-fable-5-1` at `max` as the mandatory strongest Claude tier. Do not describe Opus 5 as Fable 5.1, do not claim it fulfills stage 1, and do not declare the three-stage chain complete.
- The still-required accepted chain for this Codex-built closeout is fresh Claude Fable 5.1/max, Codex GPT-6 Astra/ultra, then fresh Claude Fable 5.1/max.

## Work

1. Read the project `AGENTS.md`, the current global rules loaded by Claude Code, this runbook, `dispatch_manifest.json`, `results.md`, and `CKPT_post_release_megaqa.md`.
2. Verify the checkout branch, clean starting state, base/release commits, and release-patch digest before reviewing.
3. Review the complete historical diff `03946b83d85af2530971322ec6dfcdba80e0bacd..c20027dc2b10758b8128adca5d5b93eeacba2653`, then verify that the corresponding behavior and release evidence survived on the dispatch branch after path renames.
4. Check correctness and structural quality, especially:
   - safe default behavior of the Weights & Biases publisher;
   - entity/project/report identity and fail-closed publication controls;
   - dependency and lock consistency;
   - scientific-result, hash, coverage, cost, and negative-result wording consistency;
   - whether historical Mega quality assurance wording incorrectly claims review of the later closeout;
   - secret exposure, path/link breakage, reproducibility, and tests that could pass without exercising the intended behavior.
5. Use existing committed evidence and deterministic tests. Do not make provider-inference calls, rerun the 774-task measurement, republish to Weights & Biases or the Python Package Index, send email, or delete the known duplicate report.
6. Do not edit release code, manuscript files, Experiment 30, or anything outside the review record directory. Report concrete findings with file/line evidence for the root coordinator to reconcile. You may update only `results.md` and `CKPT_post_release_megaqa.md` in this review directory.
7. Run proportionate non-networking checks. At minimum verify the historical patch digest, `git diff --check`, JSON parsing, publisher syntax/formatting, the two publisher tests with the exact locked Weights & Biases versions if the environment supports them, and the relevant scientific unit tests without downloading dependencies. Clearly separate code failures from environment-only limitations.
8. Update the live review `results.md` after meaningful milestones. Set the final advisory verdict and issue counts, record the actual model evidence from the Claude result/session metadata, and state explicitly that accepted Mega quality assurance remains `0/3` unless a separately eligible reviewer satisfies a required stage.
9. Update the checkpoint with the exact process/session identity, observed timestamps, completed checks, blocker, and resume step. Commit the two record updates to the task branch and push that branch. Do not open or merge a pull request; the root coordinator owns reconciliation because the mandatory acceptance chain remains incomplete.

End your response with exactly this block:

```text
ROLE: ADVISORY
REQUESTED_MODEL: claude-opus-5
REQUESTED_EFFORT: max
ACTUAL_MODEL: <verified model identifier or UNVERIFIED>
ACTUAL_EFFORT: <verified effort or UNVERIFIED>
VERDICT: PASS | FAIL
CRITICAL_ISSUES: <count>
MAJOR_ISSUES: <count>
STRUCTURAL: PASS | IMPROVED | SKIP
ACCEPTED_MEGA_QA_STAGES: 0/3
SUMMARY: <one or two sentences>
```

TL;DR: Independently review the fixed Experiment 29 release patch and its survival on current main, update and push only the advisory review records, never rerun or republish the experiment, and preserve the mandatory Fable 5.1/Codex/Fable 5.1 acceptance gate as incomplete.
