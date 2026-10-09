"""Publish aggregate descriptive evidence; never include private raw ratings."""
from collections import Counter
from pathlib import Path
import statistics
from e47_adapter import ROOT,RESULTS,read,write,sha,RUN_ID

def fmt(stat):
    value=stat['estimate'];ci=stat['interval_95']
    if value is None:return 'undefined'
    return f'{value:.3f} [{ci[0]:.3f}, {ci[1]:.3f}]' if ci else f'{value:.3f} [undefined]'

def table_row(label,result,link):
    metrics=result['metrics'];label=label.replace('|',' / ')
    return '| '+f'[{label}]({link}) | {result["observed"]}/{result["declared"]}; {result["tasks"]}'+' | '+' | '.join(fmt(metrics[k]) for k in ('spearman','pearson','kendall','mae','bias','judge_mean','panel_mean','judge_sd','panel_sd'))+' |'

HEADER='| Procedure / target | Observed/declared; tasks | Spearman | Pearson | Kendall tau-b | Absolute error | Bias | Judge mean | Panel mean | Judge standard deviation | Panel standard deviation |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|'

def main():
    existing=read(RESULTS/'existing_descriptive_index.json');controls=read(RESULTS/'controls_diagnostics_index.json')
    if existing['completed']!=existing['declared'] or controls['completed']!=controls['expected']:raise ValueError('descriptive analyses still running')
    lines=['# Cached procedures, structural controls and simulated-panel diagnostics','',
           '**Doc link:** [Frozen protocol](PROTOCOL.md)',
           '**TLDR:** All 90 distinct cached procedures and 90 structural-control/panel-diagnostic views are analyzed. These descriptive simulated-panel results do not establish full-pool selection utility or agreement with people.','',
           'All intervals below are 95% percentile intervals from 10,000 paired task-bootstrap draws, seed 47; p-val=n/a (no hypothesis test). Correlations and score metrics are reported individually. Scores lie in [0,1]; bias is judge/control minus simulated panel, so positive values mean higher scores. Each machine-readable result retains finite/undefined draw counts. Coverage must be at least 90% of the declared nonblank scope, as fixed in the protocol.','',
           'Every learned fold remains its own evaluation procedure. The late ALL procedures were built from the original groups with late items excluded; no undeclared original-group ALL scores were invented. Ensembles remain separate from their members. Source run identifiers, exact model/harness settings, parser and fitting scope are in the [inventory](expt_v1/results/existing_v5_inventory.json).','',
           'File-byte length uses length/(1+length). The theorem-count control uses the capped candidate/reference count ratio from the frozen parser; a zero reference count or absent file is missing. These controls cannot rank judges because their predictions are identical across judge configurations. Panel diagnostics compare each family/persona with both the primary target and the target excluding that family. Raw panel ratings remain private.','',
           'Intervals condition on the existing simulated panel and frozen procedures; they omit new human-rater and new model-family uncertainty. Primary/common-target correlations among cached procedures may be optimistic because prompts and the simulated panel are related.','',HEADER]
    for proc,path in sorted(existing['procedures'].items()):
        data=read(ROOT/path)
        for view,result in data['views'].items():lines.append(table_row(proc+' / '+view,result,'expt_v1/'+path))
    lines.extend(['','## Deterministic controls and panel diagnostics','',HEADER])
    for label,path in sorted(controls['results'].items()):
        data=read(ROOT/path);lines.append(table_row(label,data['result'],'expt_v1/'+path))
    scores=read(RESULTS/'existing_v5_scores.json');variability={}
    for proc,items in scores.items():
        rows=[r for r in items.values() if not r.get('structural_blank')];sds=[r['raw_repeat_sample_sd'] for r in rows if r.get('raw_repeat_sample_sd') is not None]
        variability[proc]={'units':len(rows),'accepted_repeat_counts':dict(Counter(r.get('complete_repeats','not_a_repeated_member') for r in rows)),
                           'mean_within_item_sample_sd':statistics.mean(sds) if sds else None,'units_with_at_least_two_repeats':len(sds),
                           'note':'Ensemble repeat variability is undefined; member repeats are retained separately. Aggregate repeatability cannot be estimated from a single median per item.'}
    write(RESULTS/'existing_repeat_variability.json',variability)
    lines.extend(['','## Raw-repeat variability','',
                  'The [repeat-variability table with task-bootstrap intervals](expt_v1/results/existing_repeat_variability_intervals.json) records accepted repeat counts and mean within-item sample standard deviations for every distinct member procedure. Raw repeat values and identifiers are preserved in private storage; sanitized hashes, aggregate scores and counts are public. A single median per item does not estimate repeated-median reliability.','',
                  '**TLDR-end:** [cert-judge: 47_simulated_panel_v5_label_free_judge_screening] Descriptive cached, structural and simulated-panel analyses are complete; the full frozen twelve-judge scoring and selection campaign remains running.','',
                  '**Snapshot:**','```text',f'cached procedures: {existing["completed"]}/{existing["declared"]}',f'control/panel views: {controls["completed"]}/{controls["expected"]}','draws per view: 10000','seed: 47','resampling unit: task','whole experiment: RUNNING','```',''])
    report=ROOT.parent/'RESULTS_existing_and_controls.md';report.write_text('\n'.join(lines))
    write(RESULTS/'descriptive_report_receipt.json',{'run_id':RUN_ID,'report_sha256':sha(report.read_bytes()),'existing_procedures':existing['completed'],'controls_panel_views':controls['completed'],'new_judge_calls':0,'whole_experiment_complete':False})
    print('Wrote',report.name)

if __name__=='__main__':main()
