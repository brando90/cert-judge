#!/usr/bin/env python3
"""Reproduce manuscript plots and sensitivity summaries from committed scores only.

No model clients, network operations, credential access, or archived writes.
Run from any directory: python3 experiments/34_iclr_mega_rewrite_astra/analysis/rebuild_paper_evidence.py
"""
from pathlib import Path
import csv
import hashlib
import json
import subprocess
from collections import defaultdict
import numpy as np
from scipy.stats import spearmanr, pearsonr, kendalltau
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / 'results'
FIG = ROOT / 'paper_latex/ICLR_2027_submission/figures'
B = 'experiments/archive/04_veribench_validation/'
INPUTS = {}
INPUT_REVISION = subprocess.check_output(['git', 'rev-parse', '8d2e005'], cwd=ROOT).decode().strip()


def read(relative):
    path = ROOT / relative
    data = path.read_bytes()
    frozen = subprocess.check_output(['git', 'show', INPUT_REVISION + ':' + relative], cwd=ROOT)
    if data != frozen:
        raise ValueError('Input differs from committed artifact: ' + relative)
    INPUTS[relative] = {'sha256': hashlib.sha256(data).hexdigest(),
                        'git_blob': subprocess.check_output(['git', 'rev-parse', INPUT_REVISION + ':' + relative], cwd=ROOT).decode().strip()}
    return data.decode()


def load_json(relative):
    return json.loads(read(relative))


def load_csv(relative):
    return list(csv.DictReader(read(relative).splitlines()))


def dump_csv(path, rows):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    names = {'codex': 'GPT-5.3-Codex', 'opus': 'Claude Opus 4.7', 'qwen': 'Qwen3-Coder'}
    sources = {'codex': B + 'results_exp16_final_robust_r9_median/',
               'opus': B + 'results_exp16_opus47_r3_median/',
               'qwen': 'experiments/archive/13_qwen_replication_exp16_exp19/results/exp16_qwen_r3_median/'}
    gm_sources = {'codex': B+'results_exp22_geometric_trust_index/median_mono_stab_40_60/summary.json',
                  'opus': B+'results_exp22_geometric_trust_index/opus47_r3_median_mono_stab_40_60_avg/summary.json',
                  'qwen': 'experiments/archive/13_qwen_replication_exp16_exp19/results/exp25_geometric_qwen_r3_median_mono_stab_40_60_avg/summary.json'}
    summaries, vectors, metrics, sensitivity = {}, {}, {}, []
    grid = [(a/10,b/10,(10-a-b)/10) for a in range(2,6) for b in range(2,6) if 2 <= 10-a-b <= 5]
    for family in names:
        base = load_json(sources[family]+'summary.json')
        summaries[family] = base
        metrics[family] = {'v1_avg': base['trend_by_set']['avg']['trend_v1']['spearman_r'],
                           'v2_avg': base['trend_by_set']['avg']['trend_v2']['spearman_r']}
        gm = load_json(gm_sources[family])
        metrics[family]['gm_tuned_avg'] = gm.get('trend', {}).get('spearman_r', gm.get('rho_geometric'))
        for view in ['pass1','pass2','avg']:
            suffix = '_newindex' if family == 'opus' or (family == 'codex' and view != 'pass1') else ''
            folder = B + f'results_exp28_varaware_{family}_{view}{suffix}/'
            rows = load_csv(folder+'judge_trust_vector.csv')
            frozen_summary = load_json(folder+'summary.json')
            x = np.array([float(r['TI_variance_aware']) for r in rows])
            y = np.array([float(r['human_spearman']) for r in rows])
            components = np.array([[float(r[k]) for k in ['C_f_mean','VarCorr_stability_1_minus','VarScore_stability_1_minus']] for r in rows])
            check = np.exp(np.log(np.clip(components,1e-6,1)).mean(axis=1))
            assert np.allclose(check, x, rtol=1e-12, atol=1e-12)
            rho = float(spearmanr(x,y).statistic)
            assert abs(rho - frozen_summary['correlations']['rho_TI_vs_human']) < 1e-12
            metrics[family][view] = {'spearman': rho, 'pearson': float(pearsonr(x,y).statistic),
                                     'kendall': float(kendalltau(x,y).statistic), 'n': len(rows)}
            if view == 'avg': vectors[family] = rows
            for weights in grid:
                score = np.exp(np.log(np.clip(components,1e-6,1)) @ np.array(weights))
                sensitivity.append({'family':family,'label_view':view,'w_corr':weights[0],
                                    'w_varcorr':weights[1],'w_varscore':weights[2],
                                    'spearman':float(spearmanr(score,y).statistic)})
    ci = load_json('experiments/archive/21_tmlr_submission/ci_provenance/headline_cis.json')
    sensitivity_summary = []
    for family in names:
        for view in ['pass1','pass2','avg']:
            vals = [r['spearman'] for r in sensitivity if r['family']==family and r['label_view']==view]
            sensitivity_summary.append({'family':family,'label_view':view,'n_weights':len(vals),
                                        'min_spearman':min(vals),'max_spearman':max(vals)})
    dump_csv(OUT/'weight_sensitivity.csv',sensitivity)
    dump_csv(OUT/'weight_sensitivity_summary.csv',sensitivity_summary)

    # All scatter coordinates use the same equal-weight index as the headline.
    colors = ['#2675A5','#268254','#CE7D25','#C43C39','#9169AC','#876B53','#666666','#A09B27']
    labels = ['Baseline','Checklist','Strict','Lexical','4o-mini strict','4o-mini checklist','Edit distance','Random']
    keys = ['P1_BASELINE','P4_CHECKLIST','P8_STRICT_B','BAD_STRINGY','gpt-4o-mini|P8_STRICT_B','gpt-4o-mini|P4_CHECKLIST','editdist_e1','random_r1']
    fig, axes = plt.subplots(1,3,figsize=(7.1,2.65),sharey=True)
    coordinate_rows=[]
    for ax,(family,rows) in zip(axes, vectors.items()):
        for idx,key in enumerate(keys):
            match = next(r for r in rows if r['judge_id']==key or ('|' not in key and r['judge_id'].endswith('|'+key) and not r['judge_id'].startswith('gpt-4o-mini')))
            x,y=float(match['TI_variance_aware']),float(match['human_spearman'])
            ax.scatter(x,y,s=31,c=colors[idx],marker='x' if idx>=4 else 'o',label=labels[idx],zorder=3)
            coordinate_rows.append({'family':family,'judge_id':match['judge_id'],'index':x,'human_spearman':y})
        ax.set(xlim=(-.04,1.04),ylim=(-.07,.53),xlabel=r'$\mathrm{TI}_{\mathrm{var}}$')
        ax.set_title(names[family]+'\n'+r'$\rho='+f"{metrics[family]['avg']['spearman']:.3f}"+'$',fontsize=10)
        ax.grid(alpha=.18); ax.tick_params(labelsize=8)
    axes[0].set_ylabel('Agreement with human ratings\n(Spearman, averaged labels)',fontsize=9)
    handles,legendlabels=axes[0].get_legend_handles_labels()
    fig.legend(handles,legendlabels,loc='lower center',ncol=4,frameon=False,fontsize=8,columnspacing=1.1)
    fig.subplots_adjust(bottom=.31,left=.095,right=.985,top=.80,wspace=.13)
    fig.savefig(FIG/'judge_agreement_fixed_index.pdf',metadata={'CreationDate':None,'ModDate':None})
    fig.savefig(OUT/'judge_agreement_fixed_index.png',dpi=200)
    plt.close(fig)
    dump_csv(OUT/'scatter_coordinates.csv',coordinate_rows)

    # Replot the unmodified 24-problem Codex detail rows; no hybrid 184-file study.
    rows=load_csv(sources['codex']+'detail_rows.csv')
    grouped=defaultdict(list)
    rewrite_stats=[]
    bug_curve_stats=[]
    for r in rows:
        if r['row_type'] in ['property_identity','property_bug']:
            kind=r['item_key'].split('::')[-1]
            rep=np.array(json.loads(r['repeat_scores']))
            grouped[(r['judge_id'],r['row_type'],kind)].append((float(np.median(rep)),float(np.std(rep))))
    fig,axes=plt.subplots(1,2,figsize=(7.1,2.7))
    for idx,prompt in enumerate(['P1_BASELINE','P4_CHECKLIST','P8_STRICT_B']):
        jid='gpt-5.3-codex|'+prompt
        means=[]
        for level in range(5):
            vals=np.array([x[0] for x in grouped[jid,'property_bug','L'+str(level)]])
            means.append(float(vals.mean()))
            bug_curve_stats.append({"judge_id":jid,"level":level,"n_pairs":len(vals),"mean_median_score":means[-1]})
        axes[0].plot(range(5),means,marker='o',ms=4,lw=1.4,color=colors[idx],label=labels[idx])
        for variant in ['RENAME','REORDER','STYLE','ALPHA']:
            vals=grouped[jid,'property_identity',variant]
            rewrite_stats.append({'judge_id':jid,'rewrite':variant,'n_pairs':len(vals),
                                  'mean_median_score':float(np.mean([x[0] for x in vals])),
                                  'mean_within_pair_std':float(np.mean([x[1] for x in vals]))})
    for idx,variant in enumerate(['RENAME','REORDER','STYLE','ALPHA']):
        vals=[r['mean_median_score'] for r in rewrite_stats if r['rewrite']==variant]
        axes[1].scatter([idx-.12,idx,idx+.12],vals,c=colors[:3],s=31,zorder=3)
    axes[0].set(xlabel='Cumulative bug level',ylabel='Mean judge score',xticks=range(5),ylim=(-.04,1.06))
    axes[0].set_title('Bug ladder',fontsize=10)
    axes[1].set(xticks=range(4),xticklabels=['Rename','Reorder','Style','Alpha'],ylim=(-.04,1.06),ylabel='Mean judge score')
    axes[1].set_title('Unvalidated rewrite probes',fontsize=10)
    for ax in axes:ax.grid(alpha=.18);ax.tick_params(labelsize=8)
    fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=3,frameon=False,fontsize=9)
    fig.tight_layout(rect=[0,.10,1,1]);fig.savefig(FIG/'codex_property_checks.pdf',metadata={'CreationDate':None,'ModDate':None})
    fig.savefig(OUT/'codex_property_checks.png',dpi=200);plt.close(fig)
    dump_csv(OUT/'clean_rewrite_statistics.csv',rewrite_stats)
    dump_csv(OUT/'bug_curve_statistics.csv',bug_curve_stats)

    payload={'input_revision':INPUT_REVISION,
             'inputs':INPUTS,'family_metrics':metrics,'headline_cis':ci,
             'weight_grid':{'step':.1,'minimum':.2,'maximum':.5,'n_triples':len(grid),'includes_equal_weights':False,
                            'note':'Local descriptive sensitivity; normalization held at committed family-panel values; no labels used to choose a replacement.'},
             'sensitivity_summary':sensitivity_summary,
             'limits':['Shared controls and family-specific normalization preclude interpreting a pooled leave-one-family-out correlation as independent transfer evidence.',
                       'No missing-specification rows exist in the eight-configuration panel; P3 association is unavailable.']}
    (OUT/'summary.json').write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({'family_metrics':metrics,'weight_sensitivity':sensitivity_summary},indent=2))

if __name__=='__main__':main()
