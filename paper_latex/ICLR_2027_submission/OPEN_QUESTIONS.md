# OPEN QUESTIONS — human decisions needed for the ICLR 2027 submission

TLDR: seven decisions the agent could not (or must not) make alone; nothing here blocks reading the
draft, but #1–#4 should be settled before the Sep 18 abstract deadline.

1. **72-vs-75, Option B (memo §6.1 recommends it; requires approval because it changes headline
   numbers).** Rename the 3 stale `0_unsafeMultiply_safe` label rows to `1_unsafeMultiply_safe` and
   regenerate EXP16/EXP18-family outputs so n=75 / 25 problems becomes literally true. This re-runs
   LLM judges on the 3 restored pairs × all bridge judges (API-priced) and shifts every inter-round
   and bridge statistic by small amounts. The draft currently uses Option A wording (75 rated / 72
   analyzed), which is correct as-is. **Decide: stay with A, or approve B + budget.**

2. **Title.** Working title = memo shortlist #1 (*The Surrogate Gap: …*, graded 9/10). #2 (*Do
   Behavioral Stress Tests Predict Human Agreement? …*, also 9/10) names the formal-code domain in
   the title, which #1 does not. One-line change.

3. **`PTI_{1,2,3}` headline recompute.** The memo (§2.4) wants the primary bridge to be
   `PTI_{1,2,3}` vs `TI_{m1}` with P4 standalone. Cached per-judge artifacts store only the
   aggregated quality term (`C_f`) — not the four properties separately — so this needs a rerun of
   the property pipeline over cached detail rows (no new judge calls if detail rows suffice, else
   API-priced). The draft defines `PTI_{1,2,3}` as the going-forward object, reports the documented
   `PTI_var` numbers, and explains why that does not put stability on both sides at m1. **Decide:
   ship as-is, or schedule the recompute before submission.**

4. **Decision-utility measurement** (screen's headline number: % human validations avoided at
   false-pass tolerance α). Framework + metrics are in §5; no value is claimed. Needs ~40 judge
   configurations (API-priced) per the memo. **Decide: pre-register + run before ICLR, or keep as
   registered-next-analysis (current draft).**

5. **Ethics statement.** Commented stub in `main.tex` (annotators were consenting research-team
   members; no sensitive data). ICLR treats it as optional. **Decide: uncomment or leave out.**

6. **Figure regeneration** (CHANGES §7 list): embedded "TI_var"/"cert index"/"pass1/pass2" labels in
   7 PNGs. Regenerating is mechanical (matplotlib scripts listed) but touches cached results
   packages; captions currently bridge the naming. **Decide: regenerate before submission or ship
   with caption notes.**

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
