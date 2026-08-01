# TMLR resubmission kit (or ICLR 2027 pivot) — form fields + checklist

**TLDR:** Everything that goes into the OpenReview FORM (not the PDF) for the next submission, pre-checked so the landing page cannot sabotage triage again. The abstract below is PLAIN TEXT with `$...$` math only (OpenReview MathJax renders `$...$`, NOT `\(...\)`), and no internal section/appendix references.

## Root cause of 10994 desk reject (for the record)

EiC discretionary triage ("unlikely to meet TMLR acceptance criteria... extremely limited reviewer capacity"), 31 Jul 2026. NOT anonymity / stylefile / length / overlap / quota (all verified compliant). Self-inflicted contributors: (1) form-field abstract had `\(\mathrm{TI}_{\mathrm{var}}\)` stripped by OpenReview → landing page read "a variance-aware trust index, ," + internal refs "(Appendix G)"; (2) abstract skim-reads as "n=8 correlations + held-out test failed" — triage bait when the disclosure is appended to a workshop-poster framing instead of positioned as the contribution.

## Form-field abstract (plain text, paste EXACTLY; adjust only after the base version is finalized)

When a language-model judge scores AI-generated Lean 4 theorems and specifications against gold references, how much should we trust the judge itself? Re-validating every new judge, prompt, model, or threshold with fresh human ratings does not scale, so we study whether judge validation can be amortized through behavioral checks that are automatic and falsifiable. Our protocol, CertJudge, treats judge reliability as a measurement target: it tests judges under controlled perturbations measuring identity, bug monotonicity, specification monotonicity, and stability, and combines these diagnostics into a variance-aware trust index $TI_{var}$. On a human-labeled validation suite, $TI_{var}$ predicts judge-level human alignment with validation-set Spearman correlations of $0.833$ (averaged labels), $0.905$ (pass 1), and $0.738$ (pass 2) across $n=8$ judge configurations. We then report what happened when we tested the boundary of this calibration evidence: an independent five-reviewer annotation pool ($343$ labels, $78$ pairs) collected as a held-out test was confounded by an annotation-protocol revision (cross-protocol label correlation $\approx 0.13$), and a pre-registered screen over $32$ judge configurations found no label-free property signal meeting its registered success bar. We disclose the full audit: the calibration evidence is valid relative to the original annotation protocol, cross-protocol transfer is bounded but unsettled, and label-lineage verification belongs in judge-certification protocols alongside behavioral properties.

RULES for this field: no `\(...\)` delimiters; no "(Section X)" / "(Appendix Y)" references; paste into OpenReview and PREVIEW the rendered MathJax before submitting.

## Form checklist

- [ ] Submission type: Regular (main content ≤ 12 pages — verify page where References starts in the final PDF).
- [ ] Resubmission declaration: link previous submission 10994 + change summary (required by TMLR policy for resubmissions): metadata rendering corrected; exposition restructured around the certification protocol + pre-registered transfer analysis; title differentiated from the non-archival workshop version; format overrides removed.
- [ ] Author list: reconcile with the workshop version (10994 listed: Hersch, Miranda, Obbad, Daruru, Zhou, Acharya, **Bo Han**, Koyejo; workshop camera-ready tex also had Zixiao Jolene Wang, Steven Dillmann, Yegor Denisov-Blanch, no Bo Han). Confirm the intended list with co-authors BEFORE submitting; quota is computed from it.
- [ ] Quota: confirm with Sanmi/co-authors that nobody is over the TMLR harmonic quota (desk rejects also spend budget).
- [ ] Human-subjects field: reuse 10994 text (verify "no external participants" is accurate for the five-reviewer pool).
- [ ] PDF: anonymized (`\usepackage{tmlr}` review mode), unmodified stylefile, NO global format overrides in preamble.
- [ ] Candidate bases: A′ = `paper_latex/TMLR_2026_resubmission/` (workshop+caveat, cleaned, retitled — human-read content); B = `paper_latex/TMLR_2026/` (full audit rewrite — stronger triage profile, REQUIRES Brando's read + co-author window). Mega QA stage-1 report will recommend; final call is Brando's.
- [ ] Venue decision: TMLR retry (fast, but same EiC triage risk) vs ICLR 2027 (abstract deadline ~mid-Sept 2026; full review, no discretionary triage). One at a time — TMLR forbids parallel archival submission.
