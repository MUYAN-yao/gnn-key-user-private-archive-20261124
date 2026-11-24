from pathlib import Path
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1]
B=R.parent
OUT=R/'manuscript'
A=R/'sources/data'
METHODS=('pagerank_4k','pagerank_5pct')
BUDGETS=(80,320,1280)
def plot(summary: pd.DataFrame) -> None:
    labels = {"ca_grqc": "ca-GrQc", "college_msg": "CollegeMsg", "wiki_vote": "wiki-Vote"}
    method_labels = {"pagerank_4k": "PageRank 4k", "pagerank_5pct": "PageRank 5%"}
    colors = {"default": "#c65f20", "strict": "#176b87"}
    styles = {"default": "o--", "strict": "s-"}
    fig, axes = plt.subplots(2, 3, figsize=(7.2, 4.5), sharex=True)
    chart = []
    for row, method in enumerate(METHODS):
        for col, dataset in enumerate(("ca_grqc", "college_msg", "wiki_vote")):
            axis = axes[row, col]
            part = summary[(summary.dataset == dataset) & (summary.method == method)]
            for solver in ("default", "strict"):
                values = part[part.solver == solver].sort_values("W")
                axis.errorbar(values.W, values.loss_percent_mean, yerr=values.loss_percent_path_sd, fmt=styles[solver], color=colors[solver], capsize=2.5, linewidth=1.2, markersize=4, label=solver.title())
                chart.extend(values.assign(panel=f"{method_labels[method]} | {labels[dataset]}").to_dict("records"))
            axis.axhline(0, color="#555555", linewidth=.7)
            axis.set_xscale("symlog", linthresh=80, base=2)
            axis.set_xticks(list(BUDGETS), [str(x) for x in BUDGETS])
            axis.grid(axis="y", color="#dddddd", linewidth=.55)
            if row == 0:
                axis.set_title(labels[dataset], fontsize=9)
            if col == 0:
                axis.set_ylabel(f"{method_labels[method]}\nIncremental loss (%)", fontsize=8)
            if row == 1:
                axis.set_xlabel("Selection worlds W", fontsize=8)
            axis.tick_params(labelsize=7)
    axes[0, 0].legend(loc="best", frameon=False, fontsize=7)
    fig.tight_layout()
    figs = OUT
    figs.mkdir(exist_ok=True)
    for ext in ("pdf", "svg", "png"):
        fig.savefig(figs / f"Fig4.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)


plot(pd.read_csv(A/'summary_by_budget_precision.csv'))
mpl.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],'font.size':8,'axes.labelsize':8,'axes.titlesize':9,'xtick.labelsize':8,'ytick.labelsize':8,'legend.fontsize':8,'legend.frameon':False,'svg.fonttype':'none','svg.hashsalt':'computing-review-v2','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.7})
dslist=['ca_grqc','college_msg','wiki_vote'];names={'ca_grqc':'ca-GrQc','college_msg':'CollegeMsg','wiki_vote':'wiki-Vote'}
methods=['degree_4k','pagerank_4k','pagerank_5pct','random_mean_4k'];labels=['Degree 4k','PageRank 4k','PageRank 5%','Random 4k mean'];colors=['#287271','#9c3d10','#435a9d','#666666'];markers=['o','s','^','D']
tr=pd.read_csv(A/'full_reference_transitions.csv');sub=tr[tr.low.isin([80,320])&~((tr.low==80)&(tr.high==1280))]
fig,axes=plt.subplots(2,1,figsize=(119/25.4,123/25.4),layout='constrained')
for j,(ax,low) in enumerate(zip(axes,[80,320])):
    for d,ds in enumerate(dslist):
        g=sub[(sub.dataset==ds)&(sub.low==low)].sort_values('path');x=np.arange(5)+d*6
        ax.errorbar(x,g.delta,yerr=1.96*g.mc_se,fmt='none',ecolor=colors[d],capsize=2,lw=.8)
        for xx,(_,r) in zip(x,g.iterrows()): ax.scatter(xx,r.delta,marker='o' if r.changed else 's',s=22,facecolor=colors[d] if r.changed else 'white',edgecolor=colors[d],zorder=3)
    ax.axhline(0,color='.6',lw=.7);ax.set_xticks([2,8,14],[names[d] for d in dslist]);ax.set_ylabel('Full-reference spread change (nodes)');ax.set_title(f'{chr(97+j)}  W: {low} to {320 if low==80 else 1280}',loc='left');ax.set_xlim(-1,17)
axes[-1].set_xlabel('Five replicates per graph (1101–1105)')
for ext in ('pdf','svg','png'): fig.savefig(OUT/('Fig2.'+ext),dpi=300)
plt.close(fig)
