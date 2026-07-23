# EXP46 Decision — Submit the Measurement-Lessons Paper (Outcome b)

**TLDR:** Submit CertJudge to TMLR as the **measurement-lessons paper**. The pre-registered powered test (n=26) settled the open question: the pass-1 identity lead is **not a stable, population-independent signal** — it replicates strongly negative on the diverse original panel (−0.62) but flips positive on a narrow homogeneous panel (+0.85), pooling to null (+0.146, p=0.47). A signal whose sign depends on the judge population can't anchor a methods/transfer claim. The publishable, honest contribution is the falsifiable protocol + the two-stage audit (protocol-drift discovery) + the pre-registered result that no stable label-free transfer signal exists. Legitimate, rigorous TMLR submission — TMLR judges claim-evidence fit, not positive results.

## Recommendation

**Ship outcome (b).** Frame the paper as: (1) a falsifiable property-certification protocol for LLM judges; (2) an audit that caught our own calibration construct drifting lexical→semantic (dir 22); (3) a pre-registered, powered test showing the property signals do **not** predict the semantic-protocol target (dir 23 → dir 24), with the pass-1 lead explicitly shown to be underpowered noise. Calibration-scoped positive results stay; no generalization/transfer claim is made.

## Rationale

1. **The data is pre-registered and decisive against (a).** Verdict (b) came from criteria fixed before results (PREREG c5a621c). The pooled primary fails the (a) bar, and the subgroup analysis is the real story: the effect is sign-heterogeneous (−0.62 diverse panel vs +0.85 narrow pseudo-replicated panel), so no stable certification law holds. Submitting a methods/transfer claim on a sign-unstable signal would be exactly the overreach the whole audit arc has been correcting.
2. **TMLR fit.** No significance bar; the acceptance test is whether claims match evidence. A rigorous negative-transfer result with a pre-registered protocol, an audit trail, and an honest scope is publishable and useful to the AI-evaluation measurement community.
3. **Every alternative is worse.** Claiming (a) contradicts the powered data. Waiting for more configs is unlikely to revive a signal that reversed sign (the morning Sol panel n≈32 is confirmation, not a lottery ticket). Not submitting wastes a complete, honest result.

## What to do

- **Paper:** update §5.5 to add the pass-2 powered result (identity lead did not replicate; property signals null against the semantic target at n=26) and keep the honest calibration framing. No transfer claim. (Being applied + mega-QA'd tonight.)
- **Submit:** TMLR OpenReview, `paper_latex/TMLR_2026/main.pdf`, once the §5.5 update passes QA. Tonight or morning per your call.
- **Morning confirmation (optional, non-blocking):** full 9-candidate screen + LOO on the n≈32 panel (with GPT-5.6-Sol configs) as a robustness appendix + the CLI-vs-metered cross-method sign check. Does not change the (b) decision; strengthens it.

## Cost / provenance

Metered spend ~$31 (OpenAI only; **no Opus, no anthropic_bm_key_koyejolab** — the $17k-incident key never loaded). CLI (Fable/Sol) free. All numbers trace to `results/pass2_results.json`; drift gate 0.9985 validates the pipeline.
