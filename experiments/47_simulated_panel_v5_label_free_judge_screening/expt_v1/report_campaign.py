"""Publish only computed campaign statistics; never infer success from launch."""
import argparse
from collections import Counter
import math
from pathlib import Path
import re
from e47_adapter import ROOT,RESULTS,RUN_ID,POOL,read,write,sha
from statistics_v5 import PROPERTIES,METRICS

E=ROOT.parent
VIEWS=('T_all','T_C0','T_common_excluding_Anthropic_Alibaba')
NAMES={'T_all':'Primary persona target','T_C0':'Instructions-only target','T_common_excluding_Anthropic_Alibaba':'Common Anthropic/Alibaba-excluded target'}

def num(value):
    return f'{value:.4f}' if isinstance(value,(int,float)) and math.isfinite(value) else 'undefined'

def interval(value):
    point=num(value.get('estimate'));bounds=value.get('interval_95')
    band=' ['+', '.join(map(num,bounds))+']' if bounds else ' [undefined]'
    return point+band+f"; {value.get('finite_draws',0)}/{value.get('draws',10000)} finite"

def link(path):
    path=Path(path);return f'[{path.name}]({path.relative_to(E).as_posix()})'

def text_file(name,lines):
    path=E/name;path.write_text('\n'.join(lines)+'\n');return path

def verified_reconciliation(phase):
    receipt=read(ROOT/'runtime'/f'judge_{phase}_RECONCILED.json')
    if receipt.get('run_id')!=RUN_ID or receipt.get('phase')!=phase or receipt.get('state')!='RECONCILED':raise ValueError('phase not reconciled '+phase)
    if receipt.get('admission_manifest_sha256')!=sha((RESULTS/phase/'admission_manifest.json').read_bytes()):raise ValueError('reconciliation does not bind current admission '+phase)

def criterion_report():
    verified_reconciliation('criterion')
    index=read(RESULTS/'criterion_descriptive_index.json')
    if index['completed']!=192 or index['expected']!=192 or len(index['results'])!=192:raise ValueError('all 192 criterion views are required')
    lines=['# Criterion agreement with the simulated panel','',
           '**Doc link:** [Frozen protocol](PROTOCOL.md)',
           '**TLDR:** These are agreement estimates against simulated ratings, conditional on the existing panel and frozen judge procedures. They do not measure judge–human agreement.','',
           'All intervals are percentile 95% intervals from 10,000 task bootstrap draws with seed 47. Repeated task multiplicity and paired score/target rows are preserved. Finite-draw counts accompany every estimate; undefined draws are excluded from interval quantiles and remain explicitly counted. No hypothesis test is performed (p-val=n/a). A configuration requires at least 90% item coverage in each reported view and bootstrap sample.','',
           'Primary nonblank population: 691 of 750 declared candidates over 50 tasks; the remaining 59 are source-declared blank candidates. The all-declared sensitivity applies only the frozen deterministic blank rule. Own-family exclusions are judge-specific sensitivities and do not provide a common cross-judge target.','']
    sources=[]
    for target in (*VIEWS,'own_family_excluded'):
        for scope in ('pooled','original_G01_G13','late_G16_G17','all_declared_blank_zero'):
            lines += ['## '+target+' / '+scope,'',
                      '| Configuration | Observed/declared | Tasks | Status | Spearman | Pearson | Kendall tau-b | Mean absolute error | Signed bias | Judge mean | Panel mean | Judge standard deviation | Panel standard deviation |',
                      '|---|---:|---:|---|---|---|---|---|---|---|---|---|---|']
            for cfg in POOL:
                path=ROOT/index['results'][cfg+'|'+target+'|'+scope];b=read(path)
                if b['run_id']!=RUN_ID or b['draws']!=10000 or b['seed']!=47:raise ValueError('criterion analysis identity mismatch')
                sources.append(path);r=b['result']
                lines.append('| '+' | '.join([cfg.replace('|',' / '),f"{r['observed']}/{r['declared']}",str(r['tasks']),r['status']]+[interval(r['metrics'][m]) for m in METRICS])+' |')
            lines.append('')
    variability=read(RESULTS/'repeat_variability_criterion.json')
    lines += ['## Accepted criterion repeat variability','',
              'This measures within-item dispersion of accepted repeat scores, not the repeatability of the median aggregate. A single median aggregate per item does not identify aggregate-level repeatability. Blank rules are deterministic and excluded from stochastic repeat information.','',
              '| Configuration | Units | Accepted repeat scores | Repeat-count distribution | Mean within-unit sample standard deviation |','|---|---:|---:|---|---:|']
    for cfg in POOL:
        r=variability[cfg].get('crit',{})
        lines.append('| '+' | '.join([cfg.replace('|',' / '),str(r.get('units',0)),str(r.get('accepted_raw_repeats',0)),str(r.get('repeat_count_distribution',{})),interval(r['mean_within_unit_sample_sd_interval'])])+' |')
    lines += ['', 'Historical fold-specific learned judges, separately named ensembles, item structural controls, and persona/provider-family diagnostics are reported in [the existing-procedure report](RESULTS_existing_and_controls.md).',
              'Machine-readable per-view estimates and input hashes: '+link(RESULTS/'criterion_descriptive_index.json')+'.']
    path=text_file('RESULTS_criterion_campaign.md',lines)
    return [path],sources+[RESULTS/'repeat_variability_criterion.json']

def selection_rows(lines,result):
    configs=result.get('configs',[])
    if 'support' in result:
        r=result['support'];lines += [f"Common support: {r['observed']}/{r['declared']} items ({r['status']}); {result['base_model_count']} base-model clusters and {result['provider_family_count']} provider families.",'']
    for prop,p in result['properties'].items():
        lines += ['### '+prop,'']
        if 'weights' in p:
            selected=[f'{cfg} ({w:.6g})' for cfg,w in zip(configs,p['weights']) if w>0]
            lines += [f"Computable property configurations: {p['eligible_configurations']}/{len(configs)}. Selector: "+(', '.join(selected) if selected else 'abstains')+'.',
                      f"Finite association: {p['finite_association_configurations']} configurations, {p['finite_association_base_models']} base-model clusters, {p['finite_association_provider_families']} provider families.",'']
            lines += ['| Association | Estimate [95% interval]; finite draws |','|---|---|']
            lines += [f'| {key} | {interval(value)} |' for key,value in p['association'].items()]
            lines.append('')
        lines += ['| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |','|---|---|---|']
        for key,value in p['unconditional_selection'].items():lines.append(f"| {key} | {interval(value)} | {interval(p['conditional_fixed_selection'][key])} |")
        lines.append('')
    if 'controls' in result:
        lines += ['### Exact control expectations','', '| Control | Estimate [95% interval]; finite draws |','|---|---|']
        lines += [f'| {k} | {interval(v)} |' for k,v in result['controls']['exact_expectations'].items()]
        lines += ['', 'Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.','']

def figures(analyses):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    folder=E/'figures';folder.mkdir(exist_ok=True)
    fig,axes=plt.subplots(1,2,figsize=(12,5.6),sharey=True)
    for ax,key in zip(axes,(VIEWS[0],VIEWS[2])):
        for i,prop in enumerate(PROPERTIES):
            r=analyses[key]['properties'][prop]['unconditional_selection']['gain_vs_H2'];point=r['estimate'];ci=r['interval_95']
            if point is not None:
                ax.plot(point,i,'o',color='#2459a6')
                if ci:ax.plot(ci,[i,i],color='#2459a6',linewidth=1.6)
            else:ax.text(.02,i,'Not computable',transform=ax.get_yaxis_transform(),va='center',color='#666666',fontsize=8)
        ax.axvline(0,color='#777777',linestyle='--',linewidth=.8);ax.set_title('Primary target' if key==VIEWS[0] else 'Common family-excluded target')
        ax.set_xlabel('Paired Spearman gain over fixed H2');ax.grid(axis='x',alpha=.2)
    axes[0].set_yticks(range(len(PROPERTIES)),PROPERTIES);axes[0].invert_yaxis()
    fig.suptitle('Selection gain with unconditional task-bootstrap 95% intervals')
    fig.text(.5,.01,'50 observed tasks; fixed pool of 12 configurations, 3 base models, 2 provider families. Simulated-panel criterion.',ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.04,1,.96));paths=[]
    for ext in ('png','pdf'):
        path=folder/f'selection_gain.{ext}';fig.savefig(path,dpi=180);paths.append(path)
    plt.close(fig);return paths

def full_report(manifest):
    for phase in ('criterion','probes'):verified_reconciliation(phase)
    probe=read(manifest);compile_path=Path(manifest).with_name('compile_summary.json');compilation=read(compile_path)
    if compilation['probe_manifest_sha256']!=sha(Path(manifest).read_bytes()):raise ValueError('compiler summary does not bind final structural manifest')
    analyses=read(RESULTS/'selection_association.json');recommendations=read(RESULTS/'recommendations.json')
    if set(analyses)!=set(VIEWS) or set(recommendations)!=set(PROPERTIES):raise ValueError('full required analyses not complete')
    sources=[Path(manifest),compile_path,RESULTS/'semantic_audit_availability.json',RESULTS/'selection_association.json',RESULTS/'recommendations.json']
    details=['# Full property, transfer and planning estimates','',
             '**Doc link:** [Main scientific report](RESULTS_full_campaign.md)','',
             'All reported intervals are 95%. Task bootstrap draws use seed 47 and 10,000 draws; task multiplicity and pairings are retained. Association additionally resamples the three observed base-model clusters with all their variants. Conditional fixed-selection intervals answer a narrower question than unconditional selection intervals. No p-value test is performed.','']
    for key in VIEWS:
        details += ['## '+NAMES[key]+' / pooled','',link(RESULTS/'selection_association.json')+' contains the exact common-support and component-coverage denominators.',''];selection_rows(details,analyses[key])
        for kind in ('sensitivity','transfers'):
            path=RESULTS/(kind+'_'+key+'.json');b=read(path);sources.append(path)
            for view,r in (b['results'] if kind=='transfers' else b).items():
                details += ['## '+NAMES[key]+' / '+view,'',link(path),'']
                if 'properties' in r:selection_rows(details,r)
                else:details += [str(r),'']
        path=RESULTS/('planning_'+key+'.json');planning=read(path);sources.append(path)
        details += ['## '+NAMES[key]+' / conditional power planning','',
                    'A +0.10 alternative shifts a gain distribution centered separately within each observed subpool. The one-sided threshold is its 97.5th percentile; target rejection probability is 80%. These agent-chosen planning assumptions condition on observed tasks and judges. Monte Carlo intervals quantify simulation error, not new-human or new-family uncertainty. New independent model-family requirements are NOT_IDENTIFIABLE.','']
        for prop,rows in planning.items():
            details += ['### '+prop,'']
            if isinstance(rows,dict):details += [str(rows),''];continue
            details += ['| Pool size | Resampled tasks | Subpools | Finite/draws | Rejections | Power [Monte Carlo 95% interval] | Null threshold | Independent base-model counts |','|---:|---:|---:|---:|---:|---|---:|---|']
            for r in rows:
                ci=r.get('mc_interval_95');power=num(r.get('power'))+(' ['+', '.join(map(num,ci))+']' if ci else '')
                details.append('| '+' | '.join(map(str,[r['pool_size'],r['tasks'],r['subset_count'],f"{r['finite_draws']}/{r['draws']}",r.get('rejections','undefined'),power,num(r.get('centered_null_threshold_975')),r.get('base_model_counts',{})]))+' |')
            details.append('')
    detail_path=text_file('RESULTS_full_analysis_details.md',details)
    lines=['# Full simulated-panel judge-screening campaign','',
           '**Doc link:** [Frozen protocol and additive amendments](README.md)',
           '**TLDR:** This exploratory campaign evaluates frozen judge-screening properties against simulated-panel agreement. Recommendations concern a later prospective test and establish no judge–human validation or deployment guarantee.','',
           '## Recommendations','', '| Property | Frozen screening-rule result | Primary gain over H2 [95% interval] | Common-family-excluded gain over H2 [95% interval] |','|---|---|---|---|']
    for prop in PROPERTIES:lines.append('| '+' | '.join([prop,recommendations[prop]]+[interval(analyses[key]['properties'][prop]['unconditional_selection']['gain_vs_H2']) for key in (VIEWS[0],VIEWS[2])])+' |')
    strong=[p for p in PROPERTIES if recommendations[p]=='STRONG_FOLLOWUP']
    lines += ['', ('Properties satisfying the strong follow-up rule: '+', '.join(strong)+'.') if strong else 'No property satisfies the strong follow-up rule. Positive point estimates without positive lower bounds remain inconclusive; absence of evidence is not equivalence.',
              'The fixed rule requires at least 11 of 12 computable property configurations, nonconstant values, positive association and positive paired H2 gain in both required targets. Strong follow-up additionally requires both gain interval lower bounds above zero. Constants, uncomputable properties, or a nonpositive gain upper bound in either required target are dropped from this sandbox shortlist. The threshold is an agent-chosen screen, not a universal validated standard.','',
              '## Population, evidence and missingness','',
              'The frozen universe contains 750 candidates over 50 tasks: 691 source-declared nonblank and 59 blank. The 650 original-group target rows reproduce saved targets to six decimals. The 100 late rows have no saved target file; their evidence is the frozen aggregation tests and rating provenance. All six authorized source recovery streams are included. Historical fold-specific learned judges remain separate evaluation procedures; ensembles remain distinct from members.','',
              '| Probe kind | Declared structural rows | Verified valid | Invalid/unverified |','|---|---:|---:|---:|']
    counts={kind:Counter(r.get('valid') for r in probe['rows'] if r['kind']==kind) for kind in sorted({r['kind'] for r in probe['rows']})}
    for kind,c in counts.items():lines.append(f'| {kind} | {sum(c.values())} | {c[True]} | {c[False]} |')
    lines += ['', f"Unique compilation receipts: {compilation['unique_compilations']}; successful: {compilation['ok']}; failed or unverified: {compilation['failed']}. These counts concern unique source hashes, not independent tasks. Evidence: "+link(compile_path)+'.','', '| Compiler receipt class | Count |','|---|---:|']
    lines += [f'| {key} | {value} |' for key,value in sorted(compilation['error_classes'].items())]
    lines += ['', 'Criterion rows remain declared even when the candidate fails Lean compilation. Structural validity is determined independently of judge outcomes. Complete invalidity and compiler diagnostics are retained in '+link(Path(manifest))+'.',
              'Per-judge coverage and all nine criterion metrics, including original/late and explicit blank-zero sensitivities, appear in [the criterion report](RESULTS_criterion_campaign.md). Full common-support counts, component coverage, selectors, tied weights, paired regret and gains, and conditional/unconditional intervals are in '+link(detail_path)+' and their linked machine-readable sources.','',
              '## What the properties and uncertainty mean','',
              'The geometric-mean monotonicity property GM_mono2 combines reference deletion and candidate deletion, as Amendment02 and the exact frozen owner function specify. Historical reference-deletion quality uses its original first repeat; the second-repeat supplement serves only the owner deletion information property. The repeat total-variation-distance property requires at least two candidates with all three accepted repeats within a task, rather than requiring every candidate. Bin-label permutations preserve its value.','',
              'semantic_auc is NOT_COMPUTABLE: none of the50 fresh reference hashes matches the25 owner historical audited source hashes. The exact frozen source-manifest hash matches the owner input inventory; '+link(RESULTS/'semantic_audit_availability.json')+' records the availability check. Ordinary compile-valid deletion does not establish strict weakening or formatting equivalence, and no substitute semantic evidence was invented.','',
              'Three base-model clusters are Opus, Qwen and Sonnet. Qwen single-call and Terminus2 variants share one cluster; the four harness/model identities and 12 configurations are not independent models. Only two provider families are observed, so population association inference is fragile. Provider/base exclusions are sensitivities, and single-family results do not establish transfer to unseen families.','',
              'Group-transfer selection excludes held-out candidate contributions, including reconstruction of the repeat-information joint distribution. It conditions on shared known references and is not task transfer. Five task folds instead select using four task folds and evaluate the fifth. Equal-group results weight each of the 15 groups equally and retain paired task uncertainty.','',
              'The common target excludes Anthropic and Alibaba for comparable cross-judge quality. Own-family targets use different criteria and are sensitivity results only. The intervals condition on existing simulated ratings and omit new human-rater and model-family uncertainty. Reusing task information, exploratory protocol development and known historical failures limit confirmatory interpretation. Compilation establishes elaboration, not semantic weakening or bug relevance. A compiler timeout means nonverification within the frozen time bound, not proof of Lean invalidity; timeout diagnostics remain separately classified.','',
              '## Costs, infrastructure and provenance','']
    for phase in ('criterion','probes'):
        path=RESULTS/phase/'charges.json';charges=read(path);sources.append(path)
        lines += [f"{phase}: reported total USD {num(charges.get('reported_total_usd'))}; known reported sum USD {num(charges.get('known_reported_sum_usd'))}; {charges.get('unknown_charge_cells',0)} cells with unknown charges. Evidence: "+link(path)+'.']
    lines += ['', 'All measured inference used Vals-funded Valkyrie with frozen named model selectors, prompts, parsers and harnesses. Provider backend revision identity was not established. Failed transport/admission conditions and original run identifiers remain preserved. Collection recovery reads original artifacts and does not repeat measured verdicts. Missing charges are unavailable, never interpreted as zero. No provider keys or purchased subscription credits were used.','',
              'Cached and structural controls: [existing procedure report](RESULTS_existing_and_controls.md). Conditional power planning, all transfers and all unfavorable/undefined results: '+link(detail_path)+'. Raw provider-private outputs remain in ignored owned storage; published evidence is sanitized.']
    figure_paths=figures(analyses);lines += ['', '![Selection gains](figures/selection_gain.png)']
    main=text_file('RESULTS_full_campaign.md',lines)
    return [main,detail_path,*figure_paths],sources

def verify_links(paths):
    for path in paths:
        if path.suffix!='.md':continue
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if '://' not in target and not (path.parent/target.split('#')[0]).exists():raise ValueError('broken report link '+target)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--criterion-only',action='store_true');ap.add_argument('--probe-manifest',type=Path);args=ap.parse_args()
    outputs,sources=criterion_report()
    if not args.criterion_only:
        if not args.probe_manifest:raise ValueError('full report requires structural manifest')
        extra,inputs=full_report(args.probe_manifest);outputs+=extra;sources+=inputs
    verify_links(outputs)
    write(RESULTS/'campaign_report_receipt.json',{'run_id':RUN_ID,'scope':'criterion_only' if args.criterion_only else 'full_scientific_report','outputs':{str(p.relative_to(E)):sha(p.read_bytes()) for p in outputs},'sources':{str(p.relative_to(E)):sha(p.read_bytes()) for p in sources},'whole_experiment_complete':False,'publication_and_final_verification':'separate required gate'})
    print('Verified report files:',len(outputs))

if __name__=='__main__':main()
