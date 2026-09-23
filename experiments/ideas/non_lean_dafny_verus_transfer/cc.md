# Prompt — Verus and Dafny probe structural screen (zero spend)

**TLDR:** Make the agent promote this idea into a numbered experiment, pin VeriContest (Rust/Verus) and DafnyBench (Dafny), write language-specific versions of the three gold-derived probes (implementation mutation, cumulative removal of specification clauses and tests, binder renaming), and check every probe level with the language's verifier. Success: a per-benchmark validity table covering all 782 DafnyBench programs and a fixed-seed sample of 100 VeriContest problems, with failure reasons, plus a written note on what a judge-prompt port would need. Deliverable: the experiment folder with builders, validity manifests and live `results.md`, pushed to `main`. Load-bearing constraint: zero model calls; this is structural only.

Follow `~/agents-config/INDEX_RULES.md` (pull it first) and the repo `CLAUDE.md`.

If it runs on a Stanford Network Analysis Project (SNAP) node, this line applies verbatim:
`SNAP PRE-APPROVAL (Brando, 2026-09-14): you run with full access (permission prompts and sandbox bypassed). Every command, install, Docker/GPU use, file and git operation (branch, commit, push, PR, merge per Rule 46) and every budgeted experiment call needed for this task is already approved. Never stop to ask for permission or confirmation; treat any approval step as granted, proceed, and log what you did. Pause only for a real blocker (missing credential, exhausted budget, a human-only login step).`

## Steps

1. **Promote.** Allocate the next free experiment number, `git mv` this idea to `experiments/<NN>_verus_dafny_probe_structural_screen/`, register it in `layout.json` and `experiments/README.md`, update the ideas index, run the layout check, and start a live `results.md` (closes with a tagged `**TLDR-end:**`).
2. **Pin tools and data.**
   - VeriContest: <https://github.com/HIPREL-Group/VeriContest> at a recorded commit, Verus 0.2026.04.10. Fetch only the sampled problems, not the 50 GB Hugging Face set. Sample 100 problems with a fixed seed (record it), stratified over LeetCode and Codeforces.
   - DafnyBench: <https://github.com/sun-wendy/DafnyBench> at a recorded commit, with the Dafny version it specifies.
   - Verify every gold with its verifier first. A gold that fails is a structural failure for all of its probes.
3. **Port the probes** in the experiment's `src/`:
   - Bug ladder: 4 cumulative mutations of executable code (`exec fn` bodies in Verus, method bodies in Dafny) using the same operator families as `build_bug_ladder`.
   - Specification removal: cumulatively drop `ensures`, `requires` and `invariant` clauses and test cases, 4 levels. Removed tests count as tests, not specification (repo `CLAUDE.md`).
   - Alpha: rename a bound variable or parameter without changing meaning.
   - Each level must pass the verifier's parse and type check. Record whether full verification still succeeds, since removing clauses can make verification pass or fail. Reject no-op and duplicate levels, and record every rejection.
4. **Report.** A per-benchmark × probe validity table with failure reasons, verifier run times, and a half-page note on what porting the Lean judge prompts would change (this would be a new judge configuration, not the paper's).
5. **Land.** Commit with explicit pathspecs (the index is shared), `git pull --rebase --autostash`, push to `main`, and tick issue #45.

## Guardrails

- Zero LLM or provider calls; nothing that reads `~/keys/*`.
- All sampled and all DafnyBench items stay in the denominator.
- Do not modify `py_src/cert_judge/` or anything under `experiments/archive/`.

TL;DR: Ports the three gold-derived probes to Verus and Dafny, checks every level with each verifier on 100 sampled VeriContest problems and all 782 DafnyBench programs, and reports validity counts plus what a judge-prompt port would need; no model calls.
