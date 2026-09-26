#!/usr/bin/env python3
"""Relabel the frozen 13-point comparison; never recompute its estimates."""
from pathlib import Path
import hashlib
import json
import os

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'py_src/cert_judge').is_dir() and (p / 'pyproject.toml').is_file())
HERE = Path(__file__).resolve().parents[1]
# Keep Matplotlib's temporary cache inside the owned checkout.
os.environ.setdefault('MPLCONFIGDIR', str(HERE / 'tmp/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SOURCE = ROOT / 'experiments/archive/04_veribench_validation/results_exp22_expanded_judges_stable/exp25_geom_avg/summary.json'
OUTPUT = ROOT / 'paper_latex/ICLR_2027_submission/figures/expanded_panel_v2_vs_geometric.pdf'
LABELS = {
    'gpt-5.3-codex|P1_BASELINE': 'Codex baseline',
    'gpt-5.3-codex|P2_FORMAL': 'Codex formal',
    'gpt-5.3-codex|P3_CONCISE': 'Codex concise',
    'gpt-5.3-codex|P4_CHECKLIST': 'Codex checklist',
    'gpt-5.3-codex|P7_STRICT_A': 'Codex strict A',
    'gpt-5.3-codex|P8_STRICT_B': 'Codex strict B',
    'gpt-5.3-codex|P11_JSON_FIRST': 'Codex structured output',
    'gpt-4o-mini|P1_BASELINE': 'GPT-4o-mini baseline',
    'gpt-4o-mini|P4_CHECKLIST': 'GPT-4o-mini checklist',
    'gpt-4o-mini|P8_STRICT_B': 'GPT-4o-mini strict',
    'gpt-5.3-codex|BAD_STRINGY': 'Codex lexical control',
    'editdist_e1': 'Edit distance',
    'random_r1': 'Random control',
}


def main():
    raw=SOURCE.read_bytes(); saved=json.loads(raw)
    rows=saved['rows']
    assert len(rows)==13 and {r['judge_id'] for r in rows}==set(LABELS)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,
                         'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(6.7,5.4),sharey=True)
    fig.subplots_adjust(left=.105,right=.98,bottom=.42,top=.84,wspace=.19)
    letters='ABCDEFGHIJKLM'
    # Small manual offsets separate neighboring labels; data coordinates stay exact.
    offsets_left={0:(-9,-3),1:(-14,4),2:(-14,-4),3:(6,0),6:(6,2),10:(-4,6)}
    offsets_right={0:(-14,-1),1:(6,-2),2:(-14,-6),3:(-14,1),6:(-10,6),10:(-16,0)}
    data=[]
    for ax,key,rkey,ckey,title,offsets in [
      (axes[0],'baseline_v2','rho_baseline','baseline_ci','Arithmetic $v2$',offsets_left),
      (axes[1],'geo_trust_index','rho_geometric','geometric_ci',r'Geometric $\mathrm{mono}^{0.4}\mathrm{stab}^{0.6}$',offsets_right)]:
        for i,r in enumerate(rows):
            jid=r['judge_id']
            color,marker=('#1965a0','o') if jid.startswith('gpt-5.3') and 'BAD_STRINGY' not in jid else (('#45852f','s') if jid.startswith('gpt-4o') else ('#b05220','D'))
            artist=ax.scatter([r[key]],[r['human_spearman']],s=25,c=color,marker=marker,zorder=3)
            # Check actual artist coordinates rather than only the input arrays.
            x,y=map(float,artist.get_offsets()[0])
            assert (x,y)==(r[key],r['human_spearman'])
            ax.annotate(letters[i],(x,y),xytext=offsets.get(i,(5,4)),textcoords='offset points',
                        fontsize=8.5,color=color,fontweight='bold')
            data.append({'panel':key,'letter':letters[i],'label':LABELS[jid],'judge_id':jid,'x':x,'y':y})
        lo,hi=saved[ckey]
        ax.set_title(title+'\n'+rf'$\rho={saved[rkey]:.3f}$  [{lo:.2f}, {hi:.2f}]',fontsize=9.5,pad=12)
        ax.set_xlabel('Index value')
        ax.set_ylim(-.085,.56)
        ax.set_yticks([0,.1,.2,.3,.4,.5])
        ax.grid(alpha=.17,zorder=0)
        ax.axhline(0,color='#999999',lw=.6,zorder=1)
    axes[0].set_xlim(.42,.94); axes[1].set_xlim(.72,1.005)
    axes[0].set_xticks([.5,.6,.7,.8,.9]);axes[1].set_xticks([.75,.85,.95])
    axes[0].set_ylabel('Human agreement (Spearman correlation)')
    fig.suptitle('Expanded validation panel: 13 configurations',fontsize=11,y=.985)
    for i,r in enumerate(rows):
        col,row=(0,i) if i<7 else (1,i-7)
        fig.text(.09+col*.48,.29-row*.037,letters[i]+'  '+LABELS[r['judge_id']],fontsize=8.5,va='center')
    fig.text(.5,.012,'Titles retain the archived correlations and 95% bootstrap intervals.',ha='center',fontsize=8)
    # No current time in metadata: identical inputs/script/runtime yield identical PDF.
    fig.savefig(OUTPUT,metadata={'Creator':'Experiment 37 deterministic relabeling','CreationDate':None,'ModDate':None})
    plt.close(fig)
    receipt={'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(raw).hexdigest(),
      'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'matplotlib_version':matplotlib.__version__,
      'output':str(OUTPUT.relative_to(ROOT)),'output_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
      'estimates_recomputed':False,'points_per_panel':13,'rendered_points':data,
      'archived_estimates':{k:saved[k] for k in ['rho_baseline','rho_geometric','baseline_ci','geometric_ci']},
      'display_precision':{'correlation_decimals':3,'interval_decimals':2},
      'source_rows':rows,'coordinates_checked_against_artists':True}
    (HERE/'results/figure_provenance.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Preserved 13 points per panel and all four exact interval endpoints:',receipt['output'])


if __name__=='__main__':
    main()
