#!/usr/bin/env python3
"""Read frozen scores; derive post-hoc diagnostics without inference or refitting.

Run from any directory with Python >=3.10 and numpy. All writes are confined to
this experiment's results directory. Historical paths are resolved through the
archive move, never recreated. No bootstrap intervals are generated here.
"""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import platform
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'py_src/cert_judge').is_dir() and (p / 'pyproject.toml').is_file())
HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "results"
ARCHIVE = ROOT / "experiments/archive/04_veribench_validation"
INPUTS = {}
PASSES = ("avg", "pass1", "pass2")
FAMILIES = {
    "Codex": ("codex", "gpt-5.3-codex", "_newindex"),
    "Claude Opus": ("opus", "claude-opus-4-7", "_newindex"),
    "Qwen3-Coder": ("qwen", "Qwen/Qwen3-Coder-30B-A3B-Instruct", ""),
    "Leanstral": ("leanstral", "labs-leanstral-2603", ""),
}
SEMANTIC_PROMPTS = ("P1_BASELINE", "P4_CHECKLIST", "P8_STRICT_B")


def read(path: Path) -> str:
    raw = path.read_bytes()
    INPUTS[str(path.relative_to(ROOT))] = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
    return raw.decode()


def obj(path: Path):
    return json.loads(read(path))


def csvrows(path: Path):
    return list(csv.DictReader(read(path).splitlines()))


def relocated(path: str) -> Path:
    current = ROOT / path
    if current.is_file():
        return current
    archived = ROOT / path.replace("experiments/", "experiments/archive/", 1)
    assert archived.is_file(), archived
    return archived


def rank2(values):
    """Twice the average ranks, exactly integral even with tied observations."""
    assert all(math.isfinite(v) for v in values)
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0] * len(values)
    a = 0
    while a < len(values):
        b = a + 1
        while b < len(values) and values[order[b]] == values[order[a]]:
            b += 1
        for k in order[a:b]:
            ranks[k] = a + b + 1
        a = b
    return ranks


def rho(x, y):
    if len(x) < 2:
        return None
    a = [r - (len(x) + 1) for r in rank2(x)]
    b = [r - (len(y) + 1) for r in rank2(y)]
    denom = math.sqrt(sum(v*v for v in a) * sum(v*v for v in b))
    return sum(u*v for u, v in zip(a, b)) / denom if denom else None


def exact_test(x, y):
    """Two-sided absolute rank-correlation statistic; all n! label assignments.

    All labeled permutations are counted, including repeats of tied values.
    The denominator is invariant; integer centered rank products permit an
    exact >= comparison with no floating tolerance or Monte Carlo correction.
    """
    n = len(x)
    a = [r - (n + 1) for r in rank2(x)]
    b = [r - (n + 1) for r in rank2(y)]
    assert any(a) and any(b)
    observed = abs(sum(u*v for u, v in zip(a, b)))
    exceed = sum(abs(sum(u*v for u, v in zip(a, perm))) >= observed
                 for perm in itertools.permutations(b))
    return exceed, math.factorial(n), exceed / math.factorial(n)


def close(a, b, atol=1e-12):
    assert a is not None and b is not None and math.isclose(a, b, rel_tol=0, abs_tol=atol), (a, b)


def write_json(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def audit_panel(family, summary):
    source = relocated(summary["inputs"]["exp16_summary"])
    detail = relocated(summary["inputs"]["detail_rows"])
    meta, rows = obj(source), csvrows(detail)
    assert len(rows) == 2304
    ids = sorted({r["judge_id"] for r in rows})
    assert len(ids) == 8 and len({(r['judge_id'], r['row_type'], r['item_key']) for r in rows}) == len(rows)
    audited = []
    components = {}
    for jid in ids:
        jr = [r for r in rows if r["judge_id"] == jid]
        by_type = Counter(r["row_type"] for r in jr)
        assert by_type == {"human_eval_union": 72, "property_bug": 120, "property_identity": 96}
        lengths = defaultdict(Counter)
        repeat_sds = defaultdict(list)
        ladders, rewrites = defaultdict(dict), defaultdict(set)
        for row in jr:
            rep = json.loads(row["repeat_scores"])
            assert rep and all(math.isfinite(v) and 0 <= v <= 1 for v in rep)
            lengths[row["row_type"]][len(rep)] += 1
            repeat_sds[row["row_type"]].append(statistics.pstdev(rep))
            # Historical score_mean is named for an older aggregator, but its
            # recorded value here is the median (checked with CSV precision).
            close(float(row["score_mean"]), statistics.median(rep), atol=5.1e-7)
            if row["row_type"] == "property_bug":
                file, level = row["item_key"].rsplit("::", 1)
                ladders[file][int(level[1:])] = rep
            elif row["row_type"] == "property_identity":
                file, kind = row["item_key"].rsplit("::", 1)
                rewrites[file].add(kind)
        assert len(ladders) == len(rewrites) == 24
        assert all(set(v) == set(range(5)) for v in ladders.values())
        assert all(v == {"ALPHA", "RENAME", "REORDER", "STYLE"} for v in rewrites.values())
        expected_repeats = 9 if family == "Codex" and jid in {"editdist_e1", "random_r1"} else 3
        assert all(set(v) == {expected_repeats} for v in lengths.values())
        cf, within = [], []
        for ladder in ladders.values():
            lvls = sorted(ladder)
            corr = rho(lvls, [statistics.median(ladder[l]) for l in lvls])
            if corr is None:
                continue
            cf.append((1-corr)/2)
            within.extend(statistics.pvariance(ladder[l]) for l in lvls)
        components[jid] = {"C_f_mean": statistics.mean(cf) if cf else 0,
                           "VarCorr_V_f": statistics.pvariance(cf) if cf else 1,
                           "VarScore_V_s": statistics.mean(within) if within else 1,
                           "n_files_with_corr": len(cf)}
        audited.append({"judge_id": jid, "row_counts": dict(by_type),
                        "repeat_lengths_by_row_type": {k: dict(v) for k,v in lengths.items()},
                        "mean_within_row_population_sd_by_type": {k: statistics.mean(v) for k,v in repeat_sds.items()},
                        "ladders": len(ladders), "levels_per_ladder": 5,
                        "identity_rows": 96, "literal_self_comparison_identity_rows": 0,
                        "unedited_self_comparison_bug_level_0_rows": len(ladders),
                        "bug_level_0_median_scores": [statistics.median(ladders[k][0]) for k in sorted(ladders)],
                        "identity_types": sorted(next(iter(rewrites.values()))),
                        "included_ladders": len(cf)})
    return {"family": family, "summary_path": str(source.relative_to(ROOT)),
            "detail_path": str(detail.relative_to(ROOT)), "rows": len(rows),
            "summary_repeat_setting": meta["judge_repeats"], "repeat_aggregation": meta["repeat_agg"],
            "configurations": audited}, components


def cross_pass():
    source = obj(ARCHIVE / "results_exp16_final_robust_r9_median/summary.json")
    read(ARCHIVE / "exp23_cross_pass_calibration.py")
    order = ["ident", "mono", "weak", "stab", "anti", "subtle"]
    components = {}
    for r in source["judge_rows"]:
        components[r["judge_id"]] = np.clip([r["identity_mean"], (1-r["bug_spearman_r"])/2,
          r["bug_weak_mono_pct"]/100, 1-r["flip_rate"], r["anti_string_score"], r["subtle_bug_sensitivity"]], 0, 1)
    output = []
    for view in ["pass1", "pass2"]:
        path = ARCHIVE / f"results_exp23_cross_pass_calibration/summary_fit_{view}.json"
        saved = obj(path)
        weights = np.asarray([saved["weights"][k] for k in order])
        close(float(sum(weights)), 1)
        exact, rounded = [], []
        for r in saved["per_judge"]:
            logs = np.log(np.clip(components[r["judge_id"]], 1e-6, 1))
            score = float(np.exp(np.dot(weights, logs)))
            close(score, r["cert_index"])
            exact.append(score)
            rounded.append(float(np.exp(np.dot(np.round(weights,6), logs))))
        fit = [r["human_corr_fit"] for r in saved["per_judge"]]
        other = [r["human_corr_test"] for r in saved["per_judge"]]
        close(rho(exact,fit),saved["fit_corr_spearman"])
        close(rho(exact,other),saved["test_corr_spearman"])
        output.append({"source": str(path.relative_to(ROOT)), "fit_on": view, "report_on": saved['report_on'],
           "component_order": order, "weights": saved["weights"], "display_weights_rounded_6dp": [round(float(w),6) for w in weights],
           "fit_rho": rho(exact,fit), "other_pass_rho": rho(exact,other), "n_configurations": len(exact), "n_pairs": saved['n_overlap_pairs'],
           "exact_saved_weights_reproduce_saved_scores_atol": 1e-12,
           "rounded_6dp_max_abs_score_error": max(abs(x-y) for x,y in zip(exact,rounded)),
           "rounded_6dp_same_ranking": rank2(exact)==rank2(rounded),
           "historical_seed": None, "historical_iterations": None,
           "search_settings_status": "not recorded in saved fit summaries; no run invocation recovered",
           "script_defaults_not_run_facts": {"seed":42,"iters":200000,"eps":1e-6}})
    return {"objective": "maximize judge-level Spearman association on the fitting pass",
       "procedure_in_source": "four fixed starting vectors, then Dirichlet(1,1,1,1,1,1) draws; replace best only on strict improvement",
       "no_search_rerun": True, "fits": output}


def main():
    OUT.mkdir(exist_ok=True)
    # Independent known cases check ties, reversal, constants and exact tails.
    close(rho([1,1,2],[1,2,3]), math.sqrt(3)/2)
    close(rho([1,2,3],[3,2,1]), -1)
    assert rho([1,1,1],[1,2,3]) is None
    assert exact_test([1,2,3],[1,2,3]) == (2,6,1/3)
    assert exact_test([1,1,2],[1,2,3]) == (4,6,2/3)
    audits, diagnostics, membership = [], [], []
    for family, (slug, model, suffix) in FAMILIES.items():
        avg_summary = obj(ARCHIVE / f"results_exp28_varaware_{slug}_avg{suffix}/summary.json")
        audit, components = audit_panel(family, avg_summary)
        audits.append(audit)
        for view in PASSES:
            directory = ARCHIVE / f"results_exp28_varaware_{slug}_{view}{suffix}"
            summary, rows = obj(directory/'summary.json'), csvrows(directory/'judge_trust_vector.csv')
            ids = [r['judge_id'] for r in rows]
            assert len(ids)==len(set(ids))==8
            target = [f"{model}|{prompt}" for prompt in SEMANTIC_PROMPTS]
            semantic = target + [f"gpt-4o-mini|{p}" for p in ("P4_CHECKLIST","P8_STRICT_B")]
            assert set(ids)==set(semantic+[f"{model}|BAD_STRINGY","editdist_e1","random_r1"])
            for r in rows:
                for k,v in components[r['judge_id']].items():
                    close(float(r[k]),v)
                cf, vc, vs = [float(r[k]) for k in ('C_f_mean','VarCorr_stability_1_minus','VarScore_stability_1_minus')]
                close(math.exp(sum(math.log(max(v,1e-6)) for v in [cf,vc,vs])/3),float(r['TI_variance_aware']))
            # Validate variance normalization on the ORIGINAL EIGHT rows only.
            for raw, norm in [('VarCorr_V_f','VarCorr_norm'),('VarScore_V_s','VarScore_norm')]:
                values=[float(r[raw]) for r in rows]; lo, hi=min(values),max(values)
                for r,v in zip(rows,values):
                    close(float(r[norm]),0 if hi<=lo+1e-12 else (v-lo)/(hi-lo))
            for name, members in [('full_panel_8',ids),('semantic_5',semantic),('target_semantic_3',target)]:
                selected=[r for r in rows if r['judge_id'] in members]
                x=[float(r['TI_variance_aware']) for r in selected]; y=[float(r['human_spearman']) for r in selected]
                cf=[float(r['C_f_mean']) for r in selected]
                rti,rcf=rho(x,y),rho(cf,y)
                # Independent numpy correlation over separately calculated ranks.
                def independent_rank(v):
                    return [1+sum(z<t for z in v)+(sum(z==t for z in v)-1)/2 for t in v]
                close(rti,float(np.corrcoef(independent_rank(x),independent_rank(y))[0,1]))
                extreme=total=pvalue=None
                if name=='full_panel_8':
                    close(rti,summary['correlations']['rho_TI_vs_human'])
                    close(rcf,summary['correlations']['rho_Cf_vs_human'])
                    if family!='Leanstral':
                        extreme,total,pvalue=exact_test(x,y)
                diagnostics.append({'family':family,'label_view':view,'subset':name,'n_configurations':len(selected),
                   'rho_TI_vs_human':rti,'rho_Cf_vs_human':rcf,'rho_difference_descriptive':rti-rcf,
                   'exact_two_sided_p':pvalue,'extreme_permutations':extreme,'total_permutations':total,
                   'n_unique_TI':len(set(x)),'n_unique_human':len(set(y)),'n_unique_Cf':len(set(cf)),
                   'undefined_reason':None if rti is not None else 'constant or insufficient observations'})
                membership.append({'family':family,'label_view':view,'subset':name,'n_configurations':len(selected),
                    'members':[r['judge_id'] for r in selected], 'excluded':[j for j in ids if j not in members],
                    'normalization':'unchanged frozen original eight-configuration family panel',
                    'observations':[{'judge_id':r['judge_id'],'TI':float(r['TI_variance_aware']),
                        'human_spearman':float(r['human_spearman']),'C_f_mean':float(r['C_f_mean'])} for r in selected]})
    assert len(diagnostics)==36 and len(membership)==36
    tested=[r for r in diagnostics if r['exact_two_sided_p'] is not None]
    assert len(tested)==9 and all(r['total_permutations']==40320 for r in tested)
    assert len({(r['family'],r['label_view'],r['subset']) for r in diagnostics})==36
    with (OUT/'diagnostics.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(diagnostics[0])); writer.writeheader(); writer.writerows(diagnostics)
    write_json('subset_membership.json',membership)
    write_json('panel_audit.json',audits)
    write_json('cross_pass_audit.json',cross_pass())
    threshold_dir=ROOT/'experiments/archive/02_neurips_reviews/results/threshold_calibration_sweep'
    threshold_meta=obj(threshold_dir/'summary.json'); threshold_rows=csvrows(threshold_dir/'threshold_metrics.csv')
    best=min(threshold_rows,key=lambda r:float(r['threshold_flip_rate']))
    assert float(best['threshold'])==0.85
    overlaps=all(max(float(r['threshold_flip_rate_ci_lo']),float(best['threshold_flip_rate_ci_lo']))<=
                 min(float(r['threshold_flip_rate_ci_hi']),float(best['threshold_flip_rate_ci_hi'])) for r in threshold_rows)
    assert overlaps and len(threshold_rows)==6
    write_json('threshold_audit.json',{'source_summary':threshold_meta,'rows':threshold_rows,
        'minimum_observed_threshold':0.85,'minimum_interval_overlaps_all_six':overlaps,
        'paired_difference_test':'not performed; overlap is not a test of differences','unique_optimality':'not established'})
    read(ARCHIVE/'exp28_variance_aware_trust_index.py')
    generator=read(ROOT/'experiments/archive/02_neurips_reviews/utils/veribench_variance_utils.py')
    assert 'ladder = [code]' in generator.split('def build_bug_ladder')[1].split('def local_prompt_judge')[0]
    probe_driver=read(ARCHIVE/'exp16_multi_judge_human_sets.py')
    assert 'enumerate(build_bug_ladder(gold))' in probe_driver
    assert '_score_once(spec, gold, cand, repeats=args.judge_repeats, seed=args.seed)' in probe_driver
    write_json('diagnostic_provenance.json',{'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'runtime':{'python':platform.python_version(),'numpy':np.__version__},'inputs':INPUTS,
        'interpretation':'post-hoc descriptive diagnostics on reused validation labels; no causal or independent validation claim',
        'tie_handling':'average ranks; exact float equality on saved full-precision values; no rounded ranks',
        'normalization':'never refit; frozen original eight-configuration family panels',
        'permutation':'two-sided |rho|; all 8! labeled permutations; inclusive tail; integer rank products; no random seed',
        'multiplicity':'nine primary-family/pass descriptive tests, unadjusted; shared controls and reused labels',
        'missing_intervals':'historical Opus and Qwen bootstrap intervals unavailable; no replacement procedure computed',
        'expected_rows':36,'observed_rows':len(diagnostics),'primary_family_rows':27,'additional_Leanstral_rows':9,
        'exact_tests':len(tested),'undefined_correlations':sum(r['undefined_reason'] is not None for r in diagnostics),
        'primary_full_panel_point_increases_over_Cf':sum(r['rho_difference_descriptive']>0 for r in tested)})
    for r in diagnostics:
        print(r['family'],r['label_view'],r['subset'],f"rho={r['rho_TI_vs_human']:.6f}",f"Cf={r['rho_Cf_vs_human']:.6f}",r['exact_two_sided_p'])


if __name__=='__main__':
    main()
