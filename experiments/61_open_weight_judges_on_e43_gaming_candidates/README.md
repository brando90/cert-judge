# Experiment 61: do the edits an attacker optimized against Claude Sonnet 5 also inflate open-weight judges?
Protocol `PROTOCOL.md` (frozen before any judge call). Scripts `scripts/` (render61, fetch61, run61, e61_lane.sh, analyze61). Results `results/`.
Re-scores experiment 43's saved start and final candidates (77 unique texts, prompts D0, H2, P1) with Qwen3-4B, Qwen2.5-14B-Instruct-AWQ and Qwen3-8B on free RTX A4000 cards (mercury2). Free hardware, no paid API.
Independent of experiment 58 (frozen) and of the protocol dry-run of its analysis.
