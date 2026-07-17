# TMLR 2026 Submission Prompt — CertJudge

**TLDR:** Transform the accepted ICML 2026 AI4Math workshop paper (CertJudge) into a submission-ready TMLR paper at `paper_latex/TMLR_2026/`, following https://jmlr.org/tmlr/submissions.html: TMLR stylefile, double-anonymous, reviewer feedback incorporated, every number traceable to a local experiment artifact, and the held-out story told honestly (the existing Exp23 held-out result is negative and must never be spun as confirmatory).

ref: OpenReview reviews — `experiments/18_open_revievew_feedback_ICML_2026_mathai_ws/pre_prompt.md`
ref: action plan — `experiments/18_open_revievew_feedback_ICML_2026_mathai_ws/agent_prompt.md`
ref: TMLR instructions — https://jmlr.org/tmlr/submissions.html and https://jmlr.org/tmlr/author-guide.html

## Goal

Produce a TMLR submission the user can upload to OpenReview (https://openreview.net/group?id=TMLR) immediately: `paper_latex/TMLR_2026/main.pdf` built clean from source, anonymized, with the ICML AI4Math reviewer feedback addressed and results from experiments 00–20 incorporated where local artifacts support them.

## Inputs

- **Base (use this as the primary source):** `paper_latex/TMLR_2026/main.tex` — an existing TMLR-format draft with the AI-measurement-science framing, anonymous author block, Ethics + Reproducibility statements, `tmlr.sty`/`tmlr.bst`, and `figures/` staged with exp38–43 subdirectories.
- **Freshest content lineage:** `paper_latex/ICML_2026_AI4Math/main.tex` — the post-review camera-ready (commits `8caa7dc`, `4dfc415`, Jul 10–11 2026). Sync any content improvements the TMLR draft lacks.
- **Reviews:** all three reviewers + meta-review in `pre_prompt.md` (accept-poster; main asks: held-out validation, annotation-protocol clarity, uncertainty, TI_var justification, alpha-renaming, VeriBench judge-family consistency, citation hygiene, readability).
- **Evidence artifacts:** `experiments/04_veribench_validation/results_*` (exp16 r9 median, exp18 reliability + alpha, exp21 index sweep, exp23 held-out, exp24 alpha canonicalized, exp29/exp30 index variants, exp38–43 five-human/train-test/honest/proper-transfer/held-out), plus top-level `experiments/00–20`. The compiled evidence map lives at `experiments/21_tmlr_submission/evidence_map.md`.

## TMLR requirements (verified 2026-07-17 from jmlr.org)

1. **Stylefile mandatory** — TMLR LaTeX template unmodified (`\usepackage{tmlr}`; no `[accepted]`/`[preprint]` option for submission → anonymous mode, "Under review as submission to TMLR" header).
2. **Double-anonymous** — no author names/affiliations; cite own prior published work (VeriBench workshop paper) in third person with its real citation; do not link to any named version of *this* paper.
3. **Length** — no hard limit, but justified by content; appendices go after references.
4. **Broader Impact Statement** — required if the work carries harm risk; keep a short one (adapted from the ICML Impact Statement).
5. **Acceptance criteria** — claims must match evidence; audience-interest. Calibration-scoped claims (not generalization claims) are exactly the right register.
6. **Supplementary** — up to 100MB zip/pdf, anonymized, optional.
7. **After submission** — OpenReview asks the authors to recommend Action Editors; user does this manually.

## Required edits

1. **Held-out honesty (highest stakes):** The paper mentions a 5-reviewer / 343-label / 78-pair independent pool "reserved for locked testing." Local artifacts already contain the held-out analyses: the exp38–43 suite — exp42 zero-leakage transfer and exp43 frozen-TIvar held-out on the five-reviewer pool, both null/negative (see `evidence_map.md`). Report the locked/frozen analysis with its actual sign and uncertainty, framed as a stress test. Never claim held-out confirmation without a positive locked artifact. *Historical note:* the exp23 numbers previously quoted in `../18_open_revievew_feedback_ICML_2026_mathai_ws/agent_prompt.md` (−0.238, p=0.5821, path `results_exp23_heldout_human_labels`) match no artifact on disk — phantom values, superseded by exp42/43.
2. **Citation hygiene:** replace `anonymous2026veribench` with the real `miranda2026veribench` (published AI4Math workshop paper, OpenReview lkL0qnUv3p), cited in third person; remove "Our VeriBench" possessives; drop or repair anonymous/future-dated entries (`anonymous2025formaljudge` is cited only in comments — delete); add arXiv/DOI URLs where missing.
3. **Sync camera-ready deltas** from `ICML_2026_AI4Math/main.tex` where the TMLR draft is thinner (protocol details, R9 rerun CIs/permutation values, cross-model status table, Leanstral negative control, naive blind baseline, human-ceiling table).
4. **Incorporate pre-21 experiments** where artifacts have final summaries (exp38 five-human isotonic, exp40 train/test, exp41 honest, exp42 proper transfer, exp43 held-out; plus top-level 05–20 status). Anything without a summary artifact is listed as future work, not fabricated.
5. **Writing quality:** follow `~/agents-config/writing/ml_research/ml_research_writing.md` (sentence budget, active voice, audience translation "specification" → "theorem formulation" where ML readers would misread, no CS197 jargon in prose, no stale echoes — grep every changed number across all .tex).

## Safety / evidence rules

- No new LLM-provider API calls, no scripts reading `~/keys/*` LLM keys, no new judge scoring (Hard Rule 9 in `~/agents-config/INDEX_RULES.md`). All paper numbers come from existing local artifacts; missing numbers are reported as missing, never generated.
- Every numeric claim traces to a path (+ JSON field / CSV row). Spot-check with the evidence map.

## Build + QA

- Build: `cd paper_latex/TMLR_2026 && latexmk -pdf main.tex` (TeX Live 2024). Zero errors; no undefined citations/references; skim PDF for breakage.
- Anonymization grep: no `Miranda|Hersch|Obbad|Daruru|Acharya|Wang|Zhou|Dillmann|Denisov|Koyejo|Stanford|Harvard|HKBU` outside references; no acknowledgments; no links to the named workshop version of this paper.
- **Mega QA (Trigger Rule 10):** sequential chain Codex → Claude Code → Antigravity, each with authority to fix. Codex dispatch per Hard Rule 8: `codex exec --full-auto -m gpt-5.6-sol -c 'model_reasoning_effort="xhigh"' "$QA_PROMPT"` (GPT-5.6 "Sol" tier, released 2026-07-09). On 2026-07-17 the Codex account was usage-capped (resets Jul 22) and Antigravity was not installed, so this round ran the approved per-stage fallbacks: fresh `clauded` context → Claude Code builder pass → fresh Claude subagent.
- After QA passes: commit + push (Trigger Rule 8), then one completion email to brando.science@gmail.com (Trigger Rule 14).

## Manual submission checklist (Brando, ~5 min)

1. Open https://openreview.net/group?id=TMLR → "Submit".
2. Upload `paper_latex/TMLR_2026/main.pdf`.
3. Confirm OpenReview profile is current (affiliation, conflicts, publications).
4. Certify the submission meets TMLR criteria; dual-submission: the AI4Math workshop version is non-archival (workshop poster), which TMLR permits — disclose it if the form asks.
5. After the confirmation email, recommend 3+ Action Editors working on evaluation/LLM-as-judge/formal methods.
