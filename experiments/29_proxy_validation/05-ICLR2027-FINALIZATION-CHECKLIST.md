# ICLR 2027 manuscript finalization checklist

## Target

Edit only the active tree:

`paper_latex/ICLR_2027_submission/main.tex`

Do not re-port TMLR and do not edit historical workshop/submission directories except for an explicitly requested backport.

## Terminology

- `TW_m`: scoped trustworthiness construct/predicate.
- `TI_m`: human-grounded criterion.
- `PTI_p`: label-free behavioral proxy family.
- `PTI_v0`: exact frozen implementation used in the new experiment.
- `TI_var`/legacy JTI: historical result only; label every retained number `LEGACY — NOT PTI-v0`.

## Claims

- The paper studies amortized human validation, not elimination of humans.
- The bridge is population-scoped and judge-indexed.
- Passing a behavioral screen is not proof of trustworthiness.
- Necessity language is Route-A-definitional or Route-B-conditional.
- The registered 32-judge negative and criterion drift remain disclosed.
- An underpowered interval is called inconclusive, not a negative effect.

## PTI-v0 methods

Include:

- typed indices `f=(i,a,q)`, repeat `r`, human pass/rater `u`, ladder level `ell`;
- local median over repeats;
- Spearman primary, Kendall tau-b robustness;
- `C=(1-rho)/2` with parentheses;
- `2*sd(ddof=0)` repeat instability;
- `K_aj=1 => mu=C`;
- structural-invalid exclusion versus behavioral constant `C=0`;
- log-domain zero-first GM with no headline epsilon floor;
- missingness/coverage policy;
- alpha-only top-level invariance factor;
- exact metric-version field and reproducibility commands.

## Results hierarchy

1. Probe and coverage audit.
2. Per-property PTI-v0 table with uncertainty.
3. Main outer bridge over judges.
4. Role/family and three-vs-four-property sensitivity.
5. Exp27 item-level criterion diagnostic.
6. SESOI/power analysis.
7. Decision utility only if thresholds were frozen before results; otherwise future protocol, not a claimed deployment result.

## Figure audit

- no `y=x` on PTI-vs-TI_m1;
- no PTI/TI level MAE;
- no smoothed 2D density used as evidence of pairing;
- every axis states its index unit and range;
- every headline figure has a source-data table and generator command.

## Submission hygiene

- main text within the current ICLR page limit;
- double-blind author and repository-link audit;
- required AI-use statement;
- reproducibility statement and ethics/broader-impact material as required by the live template;
- no unresolved references, citations, `TODO`, `TBD`, or result placeholders in the submitted PDF;
- exact abstract and paper deadline checked from the current official CFP immediately before submission.
