"""Descriptive quantitative grid: pooled ties decrease, final sets still change.

Python backend; 174 mm width; all 14 blocks retained in supplementary facets.
No inferential intervals: rounds and blocks are dependent descriptive units.
Final-set change counts are explicitly post-hoc diagnostics of frozen outputs.
"""
from pathlib import Path
import csv
import json
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manuscript/resolution_aware_candidate_truncation_submission_v0_1/figures'
SOURCE=ROOT/'analysis/sociopatterns-resolution-confirmation-v0_2'

def build():
    traces=json.loads((SOURCE/'full_trajectories.json').read_text(encoding='utf-8'))
    summary=json.loads((SOURCE/'summary.json').read_text(encoding='utf-8'))
    with (ROOT/'analysis/resolution-diagnostics-posthoc-20260920/full_set_transitions.csv').open(encoding='utf-8') as f:
        transitions=list(csv.DictReader(f))
    assert len(traces)==14 and len(transitions)==28
    budgets=[20,80,320]
    rounds=sum(t['k'] for t in traces)
    counts=[sum(t['zero_margin_rounds'][str(w)] for t in traces) for w in budgets]
    assert rounds==160 and counts==[80,46,21]
    assert counts==[summary['full_zero_margin_rounds'][str(w)] for w in budgets]
    changed=[sum(t['same_set']=='False' for t in transitions if int(t['low'])==w) for w in [20,80]]
    assert changed==[14,14]
    plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],
        'font.size':8,'axes.spines.top':False,'axes.spines.right':False,
        'svg.fonttype':'none','pdf.fonttype':42,'legend.frameon':False})
    def save(fig,name):
        for ext in ['pdf','svg','png']:
            target=OUT/f'{name}.{ext}'
            backup=OUT/f'{name}.before-simplification.{ext}'
            if target.exists() and not backup.exists(): shutil.copy2(target,backup)
        fig.savefig(OUT/f'{name}.pdf',facecolor='white')
        fig.savefig(OUT/f'{name}.svg',facecolor='white')
        fig.savefig(OUT/f'{name}.png',dpi=600,facecolor='white')
        plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(6.85,2.9),gridspec_kw={'width_ratios':[1.15,1]})
    fig.subplots_adjust(left=.10,right=.98,bottom=.30,top=.85,wspace=.46)
    rates=[100*n/rounds for n in counts]
    axes[0].bar(range(3),rates,width=.52,color='#2B6F9E')
    for x,(rate,n) in enumerate(zip(rates,counts)):
        axes[0].text(x,rate+3,f'{rate:.1f}%\n({n}/{rounds})',ha='center',va='bottom',fontsize=8)
    axes[0].set(xticks=range(3),xticklabels=budgets,xlabel='Selection worlds',
                ylabel='Rounds with tied best scores (%)',ylim=(0,100),yticks=[0,25,50,75,100])
    axes[0].set_title('a  Pooled tie frequency',loc='left',fontsize=9,fontweight='bold',pad=12)
    axes[1].bar(range(2),changed,width=.45,color='#D17C41')
    for x,n in enumerate(changed): axes[1].text(x,n+.4,f'{n}/14',ha='center',fontsize=8)
    axes[1].set(xticks=range(2),xticklabels=['20 → 80','80 → 320'],xlabel='Selection-world transition',
                ylabel='Changed final seed sets (blocks)',ylim=(0,17),yticks=[0,7,14])
    axes[1].set_title('b  Final-set changes',loc='left',fontsize=9,fontweight='bold',pad=12)
    fig.text(.54,.09,f'{rounds} rounds per budget = 8 traces × 5 rounds + 6 traces × 20 rounds',ha='center',fontsize=7)
    fig.text(.54,.035,'Descriptive counts; final-set changes are post-hoc diagnostics.',ha='center',fontsize=7,color='#555555')
    save(fig,'Fig2-reference-resolution')

    settings=sorted({(t['dataset'],t['k']) for t in traces})
    fig,axes=plt.subplots(2,4,figsize=(6.85,4.5),sharex=True,sharey=True)
    fig.subplots_adjust(left=.08,right=.98,bottom=.13,top=.91,wspace=.26,hspace=.55)
    data=[]
    for ax,(dataset,k) in zip(axes.flat,settings):
        for path,color,marker,style in [(301,'#2B6F9E','o','-'),(302,'#D17C41','s','--')]:
            t=next(t for t in traces if (t['dataset'],t['k'],t['world_path'])==(dataset,k,path))
            values=[100*t['zero_margin_rounds'][str(w)]/k for w in budgets]
            ax.plot(range(3),values,color=color,marker=marker,ls=style,lw=1,ms=4,
                    markerfacecolor='white' if path==302 else color,markeredgewidth=1)
            for w,v in zip(budgets,values):
                data.append(dict(dataset=dataset,k=k,path=path,W=w,tied_rounds=t['zero_margin_rounds'][str(w)],rounds=k,percent=v))
        ax.set_title(f'{dataset} | k = {k}',fontsize=8,pad=8)
        ax.set(xticks=range(3),xticklabels=budgets,ylim=(-4,104),yticks=[0,50,100])
        ax.tick_params(labelsize=7)
    axes.flat[7].axis('off')
    axes.flat[7].legend([Line2D([],[],color='#2B6F9E',marker='o'),
                         Line2D([],[],color='#D17C41',marker='s',ls='--',markerfacecolor='white')],
                        ['Path 301','Path 302'],loc='upper left',fontsize=8)
    axes.flat[7].text(0,.35,'14 trajectories\n7 network-budget settings\n2 paths per setting',transform=axes.flat[7].transAxes,fontsize=7,linespacing=1.8)
    fig.supylabel('Rounds with tied best scores (%)',x=.008,fontsize=8)
    fig.supxlabel('Selection worlds (nested budgets)',y=.025,fontsize=8)
    save(fig,'FigS1-tie-trajectories')
    with (OUT/'FigS1-tie-trajectories-source.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=data[0].keys());writer.writeheader();writer.writerows(data)
    print(f'Validated {len(traces)} trajectories, {len(data)} budget observations, {rounds} rounds per budget; final-set changes {changed}.')

if __name__=='__main__': build()
