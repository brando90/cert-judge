# Prompt 02 — Address every ledger complaint in the ICLR 2027 manuscript

**TLDR:** Make the agent apply the edits listed under "Edits applied in this pass" in `experiments/33_openreview_complaints_all_venues_to_iclr2027_paper/complaints_ledger.md` (E1–E9) to `paper_latex/ICLR_2027_submission/main.tex` and `refs.bib`, with every new number copied from the artifact named in the ledger, then rebuild the PDF in a scratch copy and commit. Success: `latexmk` builds with zero undefined citations or references, `python3 ~/agents-config/scripts/latex_sentence_lines.py --check` passes, every ledger row marked `Partial → E#` becomes `Addressed` or `Disclosed`, and `git diff` contains nothing outside the listed edits. Deliverable: one commit on `main` touching `main.tex`, `main.pdf`, `refs.bib`, the ledger, and `results.md`. Load-bearing constraints: no new experiments or model calls, no number without an artifact path, and coordinate with the concurrent sessions editing `main.tex`.

Follow `~/agents-config/INDEX_RULES.md` and read `~/agents-config/writing/ml_research/ml_research_writing.md` (one sentence per line; ≤25 words per abstract/intro sentence; active voice; train/validation/test names only) before editing.

## Concurrency protocol (mandatory)

1. `git -C /Users/brandomiranda/cert-judge status --short paper_latex/ICLR_2027_submission/main.tex` must be clean before you edit; if a peer has uncommitted hunks, hand them the sentence instead of committing over it.
2. `ListAgents`, then `SendMessage` every busy `cert-judge-*` / "paper writing certjudge" peer the exact lines you will change.
3. Never run `latexmk` inside `paper_latex/ICLR_2027_submission`; copy the directory to the scratchpad, build there, copy `main.pdf` back, commit `main.tex` + `main.pdf` together.
4. Stage explicit paths only; `git pull --rebase --autostash` before pushing; never force-push.

## Edits (numbers must match the artifacts; re-verify each before writing)

- **E1** §4 "Properties": P2 and P3 become "scores do not increase as …" (weak monotonicity); add one sentence that each ladder level extends the previous one, so later levels are more damaged by construction and the target ordering does not depend on the severity of any single edit.
- **E2** Fig. 1 subcaptions (b),(c): "vs." → "w.r.t.".
- **E3** §5.3 after the Pearson/Kendall sentence: bootstrap 95% CIs and permutation p for the Codex trio from `experiments/archive/21_tmlr_submission/ci_provenance/headline_cis.json` (avg [0.24, 1.00] p=0.017; pass1 [0.41, 1.00] p=0.005; pass2 [0.11, 1.00] p=0.045; seed 42; 10,000 resamples).
- **E4** §5.2 alpha paragraph, last sentence: post-hoc canonicalization proxy from `results_exp24_alpha_canonicalized_identity/summary.json` (within-item std 0.250 → 0.070; median reduction 64%; eight Codex configurations; a real fix rescores canonicalized text).
- **E5** §6, replace the `% TODO(internal-review)` comment with one or two sentences disclosing the pre-registered screens: n=14 underpowered (`23_reanchored_calibration/REPORT.md`, verdict c); n=32 no candidate met the registered bar, strongest Spearman −0.39, Holm p=0.25, leave-one-out transfer ρ=0.24, p=0.49 (`24_expanded_panel_cli/results/pass2_full_screen_results.json`, verdict b).
- **E6** §6 "What certification does not cover": name vacuous, weakened, over-constrained statements, formatting-only edits beyond Table 1, and non-Lean proof assistants as untested.
- **E7** §5.3 first paragraph: Codex-panel scores are medians over repeated calls per pair, three for the LLM judges and nine for the edit-distance and random controls (`results_exp16_final_robust_r9_median/detail_rows.csv`: `repeat_scores` lengths; `summary.json` records `repeat_agg` median and a configured `judge_repeats` of 9 that the judge-call cache did not fill for LLM judges). Do not write "nine repeated calls" for the LLM judges.
- **E8** Appendix "Human-Human Agreement Ceiling Context": the agreement statistics use the 72 overlapping pairs (`exp18_human_label_reliability/summary.json`: `n_overlap_pairs` 72), not 75; leave the histogram caption (its counts sum to 75) alone.
- **E9** `refs.bib`: delete `anonymous2025formaljudge` (uncited); `bach2022trusthci` → authors Bach, Tita Alissa and Khan, Amna and Hallock, Harry and Beltrão, Gabriela and Sousa, Sonia, DOI 10.1080/10447318.2022.2138826, arXiv 2304.08795; `ding2025citations` → Ding, Yifan and Facciani, Matthew and Joyce, Ellen and Poudel, Amrit and Bhattacharya, Sanmitra and Veeramani, Balaji and Weninger, Tim, Proceedings of the AAAI Conference on Artificial Intelligence 39(22):23787–23795, arXiv 2501.01303; `bowman2022scalable` → add `URL = {https://arxiv.org/abs/2211.03540}`.

## Do not touch

- §5.4 and Table 5 (experiment 32 is re-scoring the VeriBench ranking with a certified judge).
- The abstract and intro prose beyond E-list items (experiment 31 owns them).
- Anything in `experiments/archive/` (frozen evidence).

## Verification and closing

1. Build in the scratch copy: `latexmk -pdf main.tex`; grep the log for `undefined`; record the page count.
2. `python3 ~/agents-config/scripts/latex_sentence_lines.py --check paper_latex/ICLR_2027_submission/main.tex`.
3. `git diff --stat`; `git diff --check`.
4. Update the ledger statuses and `results.md` (phase table, numbers, `**TLDR-end:**`), commit with explicit paths, rebase, push.

TL;DR: Applies the nine artifact-traced edits E1–E9 to the ICLR 2027 `main.tex`/`refs.bib`, rebuilds the PDF in a scratch copy, updates the ledger and `results.md`, and pushes one commit; it runs no model calls and stays off §5.4, the abstract, and the archive.
