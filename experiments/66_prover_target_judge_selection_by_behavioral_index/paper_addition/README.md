# Experiment 66 proposed paper addition

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/66_prover_target_judge_selection_by_behavioral_index/paper_addition/README.md>

**TLDR:** A proposed appendix reporting the retrospective prover-outcome criterion, kept outside the active paper's `\input` list because the paper's framing is Brando's call after the new human-rating round. The PDF here is a scratch build of the active paper with this appendix appended as section G (21 pages, 0 undefined references).

- `999_appendix_prover_target_criterion.tex`: the fragment, one sentence per line, with numbers from [the results](../RESULTS_prover_target_selection.md).
- `main_with_proposed_prover_appendix.pdf`: a scratch build of `paper_latex/ICLR_2027_submission` at `e13b133` plus `\input{999_appendix_prover_target_criterion}` after the last appendix.

To adopt it, copy the fragment into `paper_latex/ICLR_2027_submission/`, add the `\input` line to `main.tex`, rebuild in a scratch copy and commit the fresh PDF.

**TLDR-end:** [cj: experiments/66_prover_target_judge_selection_by_behavioral_index paper addition] Proposed, built and checked; not merged into the paper.
