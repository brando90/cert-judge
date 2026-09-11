# OPEN QUESTIONS — human decisions needed for the ICLR 2027 submission

**TLDR:** The remaining author decisions concern the panel scope, title, decision utility, residual
legacy appendix figures, and the submission bundle. Experiment 29 resolved the prior PTI recompute,
Ethics-statement, and headline-figure questions.

1. **72-vs-75, Option B (memo §6.1 recommends it; requires approval because it changes headline
   numbers).** Rename the 3 stale `0_unsafeMultiply_safe` label rows to `1_unsafeMultiply_safe` and
   regenerate EXP16/EXP18-family outputs so n=75 / 25 problems becomes literally true. This re-runs
   LLM judges on the 3 restored pairs × all bridge judges (API-priced) and shifts every inter-round
   and bridge statistic by small amounts. The draft currently uses Option A wording (75 rated / 72
   analyzed), which is correct as-is. **Decide: stay with A, or approve B + budget.**

2. **Title.** Working title = memo shortlist #1 (*The Surrogate Gap: …*, graded 9/10). #2 (*Do
   Behavioral Stress Tests Predict Human Agreement? …*, also 9/10) names the formal-code domain in
   the title, which #1 does not. One-line change.

3. **Resolved by Experiment 29 — three-property sensitivity.** The frozen v5 run computes all four
   properties separately and reports both four-property `PTI_v0` and the labeled
   `PTI_{eq,bm,ms}` sensitivity. Their primary judge-level rank statistics coincide because they
   retain the same tie pattern; neither result supports a positive bridge.

4. **Decision-utility measurement** (screen's headline number: % human validations avoided at
   false-pass tolerance α). Framework + metrics are in §5; no value is claimed. Needs ~40 judge
   configurations (API-priced) per the memo. **Decide: pre-register + run before ICLR, or keep as
   registered-next-analysis (current draft).**

5. **Resolved — Ethics statement.** The Ethics statement is active before the references and states
   that annotators were consenting research-team members and no sensitive data was used.

6. **Residual legacy appendix figures.** Experiment 29 removed the old raster overview and regenerated
   the new outer-bridge figures from audited source data. Some historical appendix PNGs still embed
   `TI_var`/`cert index`/`pass1`/`pass2`; their captions disclose the legacy names. **Decide: regenerate
   the remaining historical appendix figures before submission or keep the explicit caption notes.**

7. **Supplementary anonymized archive.** The Reproducibility statement promises: tidy panel TSV,
   audit scripts, probe/prompt definitions, cached bridge statistics, pre-registration docs.
   Assemble the zip (strip git metadata + names) close to the deadline. Also verify
   `refs.bib`'s `anonymous2025formaljudge` entry still matches how the workshop version should be
   cited (currently "NeurIPS (to appear), 2025" — update venue/year if that's stale).

8. **Two notational threads deliberately left open** (memo §6.7): the "IS" benchmark-subset label is
   unidentified in the working archive, and the prompt dimension `k_x` is deferred. Neither appears
   in the draft; resolve only if a future section needs them.

9. **JS/KL rows** were dropped from the human-ceiling table (unreproducible from raw files —
   plug-in KL infinite on disjoint support; derived JS 0.1035 bits ≠ draft's 0.081). If you want
   them back, regenerate with the exp18 script's exact smoothing convention and re-insert with a
   stated convention.

10. **Codex/`gpt-4o-mini` naming in App. E table** retains the draft's judge-panel composition
    labels. If the panel is expanded toward ~40 configurations (memo §6.5), the cross-model status
    table should be regenerated from the new run rather than edited by hand.
