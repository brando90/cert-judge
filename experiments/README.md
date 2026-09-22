# Experiments

Only currently pursued experiments belong directly in this directory.
| Active experiment | Current task |
|---|---|
| [31_final_iclr_paper_writing](31_final_iclr_paper_writing/notes.md) | Targeted main-text rewrite of the ICLR 2027 submission: replace development-set "predicts"/"fit" framing for the fixed-weight TI_var, label the exp23 tuned-weight cross-pass table as a separate variant, reconcile the 0.881 quote, cut to 9 pages. Started 2026-09-22. |

The completed proxy studies are archived; the suggested new-family follow-up
has not started and is not an active run. This is a repository classification,
not a claim about processes on remote machines.

| Location | Purpose |
|---|---|
| [archive/](archive/README.md) | Completed, superseded, or parked studies, including recent results. |
| [human_labels/](human_labels/) | Shared human-label data; not an experiment. |
| [ethan_hand_labels/](ethan_hand_labels/) | Shared human-label data; not an experiment. |

The ignored local `keys/` directory is credential storage, not an experiment.

## Recent completed work

- [29_proxy_validation](archive/29_proxy_validation/README.md): completed behavioral-proxy validation; negative/inconclusive finding.
- [30_proxy_trust_index_held_out_validity](archive/30_proxy_trust_index_held_out_validity/README.md): completed combined-target and within-problem diagnostics; new-family validation remains unstarted.
- [27_trust_plots](archive/27_trust_plots/README.md): completed figures from existing scores; reusable plotting functions remain in `py_src/cert_judge/`.

## Layout maintenance

Register new active work in [the inventory](archive/layout.json) with a concrete
current task, and add it here. Archive finished or parked work promptly; a future
idea or a paper citation does not make a finished experiment active.

Git moves tracked files but leaves ignored caches and local outputs behind. After
a pull, check and reconcile those leftovers without deleting unique evidence:

```bash
python3 py_src/cert_judge/experiment_layout.py --check
python3 py_src/cert_judge/experiment_layout.py --reconcile
```

Reconciliation never overwrites existing files; collisions are preserved under
`archive/.local_leftovers/` and remain ignored. Frozen records retain their original
provenance paths; executable consumers use the current archive locations.
