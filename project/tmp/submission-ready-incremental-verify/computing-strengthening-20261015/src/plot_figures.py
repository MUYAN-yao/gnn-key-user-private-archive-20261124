"""Computing figure contract: real observed outputs, 119-mm quantitative grids.

Fig1 membership vs utility; Fig2 all primary candidate effects; Fig3 cost and
tolerance; Fig4 predefined sensitivity; Fig5 repeated timing. All omissions from
panels are design-based and all observations remain in the source tables.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],
 'font.size':8,'axes.labelsize':8,'xtick.labelsize':8,'ytick.labelsize':8,
 'legend.fontsize':8,'axes.spines.top':False,'axes.spines.right':False,
 'axes.linewidth':.7,'pdf.fonttype':42,'svg.fonttype':'none','legend.frameon':False})
REAL=['invs2013','invs2015','kenya2012','sfhh2009']
COLORS=['#2979A8','#D17A32','#61936C','#8A6CA8']
MARKERS=['o','s','^','D']
METHODS=['weighted_2k','weighted_4k','weighted_8k','degree_4k','pagerank_4k','random_4k']
LABELS=['Weighted 2k','Weighted 4k','Weighted 8k','Degree 4k','PageRank 4k','Random 4k']

def save(fig,out,name):
    # Constrained layout keeps labels inside an exact 119-mm canvas.
    fig.savefig(out/(name+'.pdf'))
    fig.savefig(out/(name+'.svg'))
    fig.savefig(out/(name+'.png'),dpi=300)
    plt.close(fig)

def main(base):
    base=Path(base);src=base/'analysis';out=src/'figures';out.mkdir(exist_ok=True)
    assert (src/'validation.json').exists()
    g=pd.read_csv(src/'group_summary.csv');d=pd.read_csv(src/'path_level_metrics.csv')
    tr=pd.read_csv(src/'reference_transitions.csv');tol=pd.read_csv(src/'tolerance_sensitivity.csv')
    # a shared legend outside two full-width axes preserves readable text at 119mm.
    fig,ax=plt.subplots(2,1,figsize=(119/25.4,5.6),layout='constrained')
    for dataset,col,mark in zip(REAL,COLORS,MARKERS):
        b=tr[(tr.stage=='resolution')&(tr.dataset==dataset)]
        for path,v in b.groupby('path'):
            ax[0].plot(v.high,v.jaccard,color=col,alpha=.16,lw=.55)
        means=b.groupby('high').jaccard.mean();ax[0].plot(means.index,means.values,color=col,marker=mark,label=dataset,lw=1.3)
        b=g[(g.stage=='resolution')&(g.dataset==dataset)&(g.method=='full')].sort_values('W')
        ax[1].errorbar(b.W,b.incremental_spread_mean,yerr=[b.incremental_spread_mean-b.incremental_spread_lo,b.incremental_spread_hi-b.incremental_spread_mean],color=col,marker=mark,lw=1,capsize=2)
    ax[0].set(ylabel='Adjacent-budget Jaccard overlap',ylim=(-.03,1.03),title='a  Reference membership')
    ax[1].set(ylabel='Full greedy: incremental spread',title='b  Independent utility')
    for a in ax:
        assert (g.W>0).all()
        a.set_xscale('log',base=4);a.set_xticks([20,80,320,1280,5120],['20','80','320','1280','5120']);a.set_xlabel('Selection worlds W');a.grid(axis='y',alpha=.15)
    ax[0].legend(ncol=2,loc='lower right')
    save(fig,out,'Fig1')
    fig,axes=plt.subplots(4,1,figsize=(119/25.4,6.2),layout='constrained')
    for a,dataset,col in zip(axes,REAL,COLORS):
        b=g[(g.stage=='resolution')&(g.W==5120)&(g.dataset==dataset)].set_index('method').loc[METHODS]
        y=np.arange(6)
        a.errorbar(b.delta_mean,y,xerr=[b.delta_mean-b.delta_lo,b.delta_hi-b.delta_mean],fmt='o',color=col,capsize=2,ms=3)
        a.axvline(0,color='.55',ls='--',lw=.7);a.set_yticks(y,LABELS);a.invert_yaxis();a.set_title(dataset,loc='left');a.grid(axis='x',alpha=.12)
    axes[-1].set_xlabel('Candidate minus full spread (activated nodes)')
    save(fig,out,'Fig2')
    fig,ax=plt.subplots(2,1,figsize=(119/25.4,5.8),layout='constrained')
    primary=d[(d.stage=='resolution')&(d.W==5120)&(d.method=='weighted_4k')]
    for dataset,col,marker in zip(REAL,COLORS,MARKERS):
        b=primary[primary.dataset==dataset]
        ax[0].scatter(100*b.selection_saving,100*b.relative_incremental_loss,color=col,marker=marker,s=22,label=dataset,alpha=.8)
        t=tol[(tol.dataset==dataset)&(tol.method=='weighted_4k')]
        ax[1].plot(100*t.tolerance,t.point_fraction,color=col,marker=marker,ms=4)
    ax[0].axhline(0,color='.55',ls='--',lw=.7)
    ax[0].set(xlabel='Selection time saved (%)',ylabel='Incremental spread loss (%)',title='a  Weighted 4k: all ten paths per network')
    ax[0].legend(ncol=2)
    ax[1].set(xlabel='Illustrative tolerated incremental loss (%)',ylabel='Fraction of paths meeting tolerance',ylim=(-.03,1.03),title='b  Descriptive tolerance sensitivity')
    save(fig,out,'Fig3')
    fig,ax=plt.subplots(3,1,figsize=(119/25.4,6.1),layout='constrained')
    settings=[(.005,3),(.01,1),(.01,3),(.01,5),(.05,3)]
    for i,(dataset,col,mark) in enumerate(zip(REAL,COLORS,MARKERS)):
        vals=[]
        for p,h in settings:
            b=g[(g.dataset==dataset)&(g.W==320)&(g.k==5)&(g.p==p)&(g.h==h)&(g.coupling=='step')&(g.method=='weighted_4k')]
            assert len(b)==1;vals.append(float(b.relative_incremental_loss_mean.iloc[0])*100)
        ax[0].plot(np.arange(5),vals,marker=mark,color=col,label=dataset)
        b=g[(g.dataset==dataset)&(g.k==5)&(g.W==1280)&(g.method=='weighted_4k')&(g.p==.01)&(g.h==3)]
        b=b.set_index('coupling').loc[['step','edge']]
        ax[1].plot([0,1],100*b.relative_incremental_loss_mean,marker=mark,color=col)
    ax[0].set_xticks(range(5),['.005 / 3','.01 / 1','.01 / 3','.01 / 5','.05 / 3'],rotation=25)
    ax[0].set(ylabel='Incremental loss (%)',xlabel='Transmission p / horizon h',title='a  Weighted 4k, W = 320')
    handles,labels=ax[0].get_legend_handles_labels()
    fig.legend(handles,labels,ncol=2,loc='outside upper center',markerscale=.8)
    ax[1].set_xticks([0,1],['Step coupling','Fixed-edge coupling'])
    ax[1].set(ylabel='Incremental loss (%)',title='b  Weighted 4k, W = 1280')
    for i,(dataset,col,mark) in enumerate(zip(['synthetic_ba2000','synthetic_sbm2000'],COLORS,MARKERS)):
        b=g[(g.dataset==dataset)&(g.W==320)].set_index('method').loc[METHODS]
        ax[2].plot(np.arange(6),100*b.relative_incremental_loss_mean,color=col,marker=mark,label=dataset.replace('synthetic_',''))
    ax[2].set_xticks(range(6),['W2k','W4k','W8k','D4k','PR4k','R4k'])
    ax[2].set(ylabel='Incremental loss (%)',title='c  Two synthetic 2,000-node instances, W = 320');ax[2].legend()
    for a in ax:a.axhline(0,color='.6',lw=.6,ls='--')
    save(fig,out,'Fig4')
    t=pd.read_csv(src/'timing_repeats.csv')
    fig,axes=plt.subplots(4,1,figsize=(119/25.4,5.8),layout='constrained')
    methods=['full','weighted_2k','weighted_4k','weighted_8k','degree_4k','pagerank_4k','random0_4k','random1_4k','random2_4k']
    for a,dataset in zip(axes,REAL):
        b=t[t.dataset==dataset];x=np.arange(len(methods))
        s=b.groupby('method').selection_seconds.median().reindex(methods)
        e=b.groupby('method').evaluation_seconds.median().reindex(methods)
        a.bar(x,s,color='#2979A8',label='Selection');a.bar(x,e,bottom=s,color='#9DB7C9',label='Evaluation')
        for j,m in enumerate(methods):
            v=b[b.method==m];a.scatter(np.full(len(v),j),v.selection_seconds+v.evaluation_seconds,color='.2',s=7,zorder=3)
        a.set_title(dataset,loc='left');a.set_ylabel('Seconds');a.set_xticks(x,['Full','W2','W4','W8','D4','PR4','R0','R1','R2'],rotation=35)
    axes[0].legend(ncol=2);axes[-1].set_xlabel('Candidate arm (k = 5, W = 320)')
    save(fig,out,'Fig5')
    print('Created 5 figures, each PDF/SVG/PNG')

if __name__=='__main__':main(sys.argv[1])
