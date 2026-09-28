# Anonymous score-level supplement preparation

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/34_iclr_mega_rewrite_astra/submission/RESULTS_anonymous_supplement.md>

**TLDR:** A 270,577-byte anonymous archive reproduces the current manuscript's five regenerated figures and eight numerical tables from 28 frozen inputs. It is a bounded score-level artifact, not the complete experiment repository; this receipt and the builder are not part of the upload.

Prepared 09-24-2026. The document address above is the intended publication destination; this worker did not commit or publish it.

## Deliverable and verification

- Upload artifact: `anonymous_supplement.zip`, 50 files, 270,577 bytes.
- SHA-256 checksum: `4caf85a29f522c46321ccdcdbf3c2792b69ff2186bf91ecad974bb284f100f43`.
- Input set: 28 files, each verified against the frozen manuscript manifest before packaging.
- Source preservation: all original files unchanged; one nonnumeric absolute-path field changed only in the anonymous copy.
- Numerical reconstruction: all eight derived comma-separated-value tables match current evidence byte-for-byte; all five checked summary groups match exactly.
- Standalone execution: extracted into an independent temporary directory, then ran the included calculation with exit status 0 and no repository or Git dependency.
- Archive integrity: Python's archive validation returned `Done testing`.
- Identity scans: zero matches in included text, filenames, or extracted figure text for the configured author names, account/host paths, repository host links, email addresses, and credential prefixes.
- Figure metadata: five Portable Document Format figures contain only Matplotlib creator/producer metadata, with no author, creation/modification dates, JavaScript or encryption; two raster figures contain only Matplotlib software metadata and resolution.
- The exact current prompt/model/repetition appendix is included as `PROMPTS_AND_MODELS.tex`.

## Scope for manuscript wording

The package reconstructs fixed-index associations from recorded component vectors, the local weight sensitivity, and the recorded score/property diagnostics.
It includes stored comparison and confidence summaries but does not rerun their original analyses.
It does not reproduce model inference, recover the original human rubric, reconstruct every appendix study, or supply all original task/gold/candidate files and human labels.
The anonymous package README states these limitations explicitly.
There is no new inference or scientific result in this packaging work.

The numerical verifier used Python 3.11 with NumPy 2.2.6, SciPy 1.16.3 and Matplotlib 3.10.7.
`build_anonymous_supplement.py` is the local reproducible packaging procedure; `supplement_build_receipt.json` contains machine-readable verification counts.
Only `anonymous_supplement.zip` is the intended supplementary upload, not its parent directory, builder, or this internal receipt.

**TLDR-end:** [cert-judge: anonymous supplement] The artifact under `experiments/34_iclr_mega_rewrite_astra/submission/` is ready for the coordinator's submission workflow, with bounded reproduction coverage and zero configured identity-scan matches.
