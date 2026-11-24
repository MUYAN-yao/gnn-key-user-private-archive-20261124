"""All figures derive from audit-generated CSVs; no invented observations."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'analysis';O=A/'figures';O.mkdir(exist_ok=True)
mpl.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],'font.size':8,'axes.labelsize':8,'axes.titlesize':9,'xtick.labelsize':8,'ytick.labelsize':8,'legend.fontsize':8,'legend.frameon':False,'svg.fonttype':'none','svg.hashsalt':'computing-review-v2','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.7})
df=pd.read_csv(A/'arm_path.csv');dslist=['ca_grqc','college_msg','wiki_vote'];names={'ca_grqc':'ca-GrQc','college_msg':'CollegeMsg','wiki_vote':'wiki-Vote'}
methods=['degree_4k','pagerank_4k','pagerank_5pct','random_mean_4k'];labels=['Degree 4k','PageRank 4k','PageRank 5%','Random 4k mean'];colors=['#287271','#9c3d10','#435a9d','#666666'];markers=['o','s','^','D']
def save(fig,name,data):
    fig.savefig(O/(name+'.pdf'));fig.savefig(O/(name+'.svg'));fig.savefig(O/(name+'.png'),dpi=300)
    data.to_csv(O/(name+'_source.csv'),index=False);plt.close(fig)
fig,axes=plt.subplots(3,1,figsize=(119/25.4,166/25.4),layout='constrained')
sub=df[(df.stage=='resolution')&df.method.isin(methods)]
for j,(ax,ds) in enumerate(zip(axes,dslist)):
    for method,label,color,marker in zip(methods,labels,colors,markers):
        g=sub[(sub.dataset==ds)&(sub.method==method)];mean=g.groupby('W').loss_percent.mean();sd=g.groupby('W').loss_percent.std()
        assert (mean.index>0).all() and (mean-sd).min()>-15 and (mean+sd).max()<104
        ax.errorbar(mean.index,mean.values,yerr=sd.values,color=color,marker=marker,label=label,linewidth=1,markersize=3,capsize=2)
    ax.set_xscale('log',base=4);ax.set_xticks([80,320,1280],['80','320','1280']);ax.set_ylim(-15,104);ax.axhline(0,color='.75',lw=.6);ax.set_ylabel('Incremental loss (%)');ax.set_title(f'{chr(97+j)}  {names[ds]}',loc='left');ax.grid(axis='y',alpha=.15)
axes[-1].set_xlabel('Selection worlds W');axes[0].legend(ncol=2,loc='upper center',bbox_to_anchor=(.5,1.56),columnspacing=1)
save(fig,'Fig1',sub)
tr=pd.read_csv(A/'full_reference_transitions.csv');sub=tr[tr.low.isin([80,320])&~((tr.low==80)&(tr.high==1280))]
fig,axes=plt.subplots(2,1,figsize=(119/25.4,123/25.4),layout='constrained')
for j,(ax,low) in enumerate(zip(axes,[80,320])):
    for d,ds in enumerate(dslist):
        g=sub[(sub.dataset==ds)&(sub.low==low)].sort_values('path');x=np.arange(5)+d*6
        ax.errorbar(x,g.delta,yerr=1.96*g.mc_se,fmt='none',ecolor=colors[d],capsize=2,lw=.8)
        for xx,(_,r) in zip(x,g.iterrows()): ax.scatter(xx,r.delta,marker='o' if r.changed else 's',s=22,facecolor=colors[d] if r.changed else 'white',edgecolor=colors[d],zorder=3)
    ax.axhline(0,color='.6',lw=.7);ax.set_xticks([2,8,14],[names[d] for d in dslist]);ax.set_ylabel('Full-reference spread change');ax.set_title(f'{chr(97+j)}  W: {low} to {320 if low==80 else 1280}',loc='left');ax.set_xlim(-1,17)
axes[-1].set_xlabel('Five selection paths per graph (1101–1105)')
save(fig,'Fig2',sub)
tol=pd.read_csv(A/'tolerance_cost_curves.csv');sub=tol[(tol.W==1280)&(tol.scope=='verification')&tol.method.isin(methods)]
fig,axes=plt.subplots(3,1,figsize=(119/25.4,155/25.4),layout='constrained')
for j,(ax,ds) in enumerate(zip(axes,dslist)):
    g=sub[sub.dataset==ds];table=g.pivot(index='method',columns='tolerance_percent',values='passing_paths').reindex(methods);im=ax.imshow(table.to_numpy(),vmin=0,vmax=5,cmap='Blues',aspect='auto')
    saving=g.groupby('method').mean_saving_percent.first();ax.set_yticks(range(4),[f'{label}\n({saving[m]:.1f}% saved)' for m,label in zip(methods,labels)]);ax.set_xticks(range(6),['0','1','2.5','5','10','20']);ax.set_title(f'{chr(97+j)}  {names[ds]}',loc='left')
    for r in range(4):
        for c in range(6):
            val=int(table.iloc[r,c]);ax.text(c,r,f'{val}/5',ha='center',va='center',color='white' if val>2 else 'black')
axes[-1].set_xlabel('Descriptive incremental-loss tolerance (%)')
save(fig,'Fig3',sub)
fig,axes=plt.subplots(3,1,figsize=(119/25.4,145/25.4),layout='constrained');sub=df[(df.W==320)&(df.path<=1103)&df.method.isin(methods)]
for j,(ax,ds) in enumerate(zip(axes,dslist)):
    for i,method in enumerate(methods):
        for coupling,off,marker in [('step',-.12,'o'),('edge',.12,'s')]:
            g=sub[(sub.dataset==ds)&(sub.method==method)&(sub.coupling==coupling)];ax.scatter(np.full(len(g),i+off),g.loss_percent,marker=marker,color=colors[i],s=18,label=coupling if i==0 else None)
    ax.axhline(0,color='.7',lw=.7);ax.set_xticks(range(4),['Degree\n4k','PageRank\n4k','PageRank\n5%','Random\n4k mean']);ax.set_ylabel('Incremental loss (%)');ax.set_title(f'{chr(97+j)}  {names[ds]}',loc='left');ax.set_ylim(-8,104)
axes[0].legend(loc='upper center',ncol=2,bbox_to_anchor=(.5,1.55))
save(fig,'FigS1',sub)
print('4 figures, vector PDF/SVG + PNG + source CSV')
