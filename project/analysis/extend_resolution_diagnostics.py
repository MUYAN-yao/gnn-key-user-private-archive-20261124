"""Post-hoc descriptive diagnostics; reads frozen outputs, never reruns selection."""
from pathlib import Path
import json,csv,math,hashlib
from statistics import mean,stdev
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/"audits/sociopatterns-resolution-confirmation-v0_1/snapshot-r3-confirmation-run-20260920"
PACKAGE=ROOT/"manuscript/resolution_aware_candidate_truncation_submission_v0_1"
OUT=ROOT/"analysis/resolution-diagnostics-posthoc-20260920"
OUT.mkdir(exist_ok=True)
FIG=PACKAGE/"figures"
assert json.loads((RUN/"manifest.json").read_text(encoding="utf-8"))["status"]=="COMPLETE"
assert json.loads((ROOT/"analysis/sociopatterns-resolution-confirmation-v0_1/validation-v0_2.json").read_text(encoding="utf-8"))["status"]=="PASS"
rows=[json.loads(p.read_text(encoding="utf-8")) for p in sorted(RUN.rglob("*.json")) if p.name!="manifest.json"]
assert len(rows)==42
index={(r["dataset"],r["k"],r["world_path"],r["selection_world_count"]):r for r in rows}
blocks=sorted({key[:3] for key in index})
def writecsv(name,data):
    with (OUT/name).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=data[0].keys());w.writeheader();w.writerows(data)
transitions=[]
for block in blocks:
    for low,high in [(20,80),(80,320)]:
        a=index[(*block,low)]["arms"]["full"]["selection"]["top_k"]
        b=index[(*block,high)]["arms"]["full"]["selection"]["top_k"]
        assert len(set(a))==len(a)==block[1]
        aa,bb=set(a),set(b)
        transitions.append(dict(dataset=block[0],k=block[1],path=block[2],low=low,high=high,
            same_order=a==b,same_set=aa==bb,jaccard=len(aa&bb)/len(aa|bb),
            retained_fraction=len(aa&bb)/block[1],
            first_divergence=next((i+1 for i,(x,y) in enumerate(zip(a,b)) if x!=y),None)))
writecsv("full_set_transitions.csv",transitions)
candidate=[]
for r in rows:
    full=r["arms"]["full"]
    for m in ["degree_2k","degree_4k","degree_8k"]:
        arm=r["arms"][m]
        a,b=set(full["selection"]["top_k"]),set(arm["selection"]["top_k"])
        av,bv=arm["evaluation"]["world_spreads"],full["evaluation"]["world_spreads"]
        assert len(av)==len(bv)==2000
        dif=[x-y for x,y in zip(av,bv)]
        delta=mean(dif);se=stdev(dif)/math.sqrt(len(dif))
        assert abs(delta-arm["comparison_to_full"]["mean_spread_delta"])<1e-5
        candidate.append(dict(dataset=r["dataset"],k=r["k"],path=r["world_path"],W=r["selection_world_count"],
            method=m,same_set=a==b,same_order=arm["comparison_to_full"]["same_ordered_top_k"],
            jaccard=len(a&b)/len(a|b),delta=delta,mc_se=se,lower=delta-1.96*se,upper=delta+1.96*se,
            n_worlds=2000,candidate_count=arm["candidate_count"],
            full_pool=arm["candidate_count"]==r["graph"]["historical_nodes"]))
writecsv("paired_evaluation_diagnostics.csv",candidate)
graphs=[]
for d in sorted({r["dataset"] for r in rows}):
    rr=[r for r in rows if r["dataset"]==d]
    g=rr[0]["graph"]
    assert all(r["graph"]==g for r in rr)
    graphs.append(dict(dataset=d,nodes=g["historical_nodes"],directed_edges=g["historical_edges"],
                       k=";".join(map(str,sorted({r["k"] for r in rr}))),conditions=len(rr)))
writecsv("graph_instances.csv",graphs)
stats={"analysis_type":"post-hoc; frozen selection outputs; no new training",
       "transitions":{f"{l}-{h}":{"unchanged_sets":sum(t["same_set"] for t in transitions if t["low"]==l),
                    "min_jaccard":min(t["jaccard"] for t in transitions if t["low"]==l),
                    "max_jaccard":max(t["jaccard"] for t in transitions if t["low"]==l),
                    "mean_jaccard":mean(t["jaccard"] for t in transitions if t["low"]==l)}
                    for l,h in [(20,80),(80,320)]},
       "candidate_set_matches":{m:sum(c["same_set"] for c in candidate if c["method"]==m) for m in ["degree_2k","degree_4k","degree_8k"]},
       "pool_saturation":{m:{"full_pool":sum(c["full_pool"] for c in candidate if c["method"]==m),
                            "restricted":sum(not c["full_pool"] for c in candidate if c["method"]==m),
                            "restricted_matches":sum(c["same_order"] and not c["full_pool"] for c in candidate if c["method"]==m)}
                          for m in ["degree_2k","degree_4k","degree_8k"]},
       "graphs":graphs}
(OUT/"summary.json").write_text(json.dumps(stats,indent=2))
plt.rcParams.update({"font.family":"sans-serif","font.sans-serif":["Arial","DejaVu Sans"],
                     "font.size":8,"svg.fonttype":"none","pdf.fonttype":42,
                     "axes.spines.top":False,"axes.spines.right":False})
def save(fig,name):
    fig.savefig(FIG/(name+".pdf"));fig.savefig(FIG/(name+".svg"))
    fig.savefig(FIG/(name+".png"),dpi=600);plt.close(fig)
labels=[f"{d} | k={k} | {p}" for d,k,p in blocks]
fig,axes=plt.subplots(1,2,figsize=(6.85,4.8),sharey=True,gridspec_kw={"width_ratios":[1.4,1]})
fig.subplots_adjust(left=.30,right=.98,bottom=.12,top=.88,wspace=.27)
for y,b in enumerate(blocks):
    a,c=[t for t in transitions if (t["dataset"],t["k"],t["path"])==b]
    axes[0].plot([a["jaccard"],c["jaccard"]],[y,y],color="#BAC2C8",lw=1)
    axes[0].scatter(a["jaccard"],y,c="#0072B2",s=25,marker="o")
    axes[0].scatter(c["jaccard"],y,c="#D55E00",s=25,marker="s")
    axes[1].scatter(a["first_divergence"]/b[1],y,c="#0072B2",s=25,marker="o")
    axes[1].scatter(c["first_divergence"]/b[1],y,c="#D55E00",s=25,marker="s")
axes[0].set_yticks(range(14),labels,fontsize=7)
axes[0].invert_yaxis()
axes[0].set(xlim=(-.03,1.03),xlabel="Final-set Jaccard overlap")
axes[1].set(xlim=(0,1.06),xlabel="First divergence / seed budget")
axes[0].set_title("a  Final-set stability",loc="left",fontsize=9)
axes[1].set_title("b  Trace divergence",loc="left",fontsize=9)
from matplotlib.lines import Line2D
fig.legend([Line2D([],[],marker='o',color="#0072B2",ls=""),Line2D([],[],marker='s',color="#D55E00",ls="")],
           ["20 → 80 worlds","80 → 320 worlds"],loc="upper center",ncol=2,bbox_to_anchor=(.63,.99),frameon=False)
save(fig,"Fig5-set-stability")

fig,axes=plt.subplots(1,3,figsize=(6.85,4.8),sharey=True,sharex=True)
fig.subplots_adjust(left=.30,right=.98,bottom=.13,top=.89,wspace=.15)
for ax,m,color in zip(axes,["degree_2k","degree_4k","degree_8k"],["#0072B2","#D55E00","#555555"]):
    for y,b in enumerate(blocks):
        c=next(c for c in candidate if (c["dataset"],c["k"],c["path"])==b and c["W"]==320 and c["method"]==m)
        ax.plot([c["lower"],c["upper"]],[y,y],color=color,lw=.9)
        ax.scatter(c["delta"],y,color=color,s=15)
    ax.axvline(0,color="#AAAAAA",ls="--",lw=.8)
    ax.set_title(m.replace("degree_","Degree "),fontsize=9)
    ax.set_xlabel("Spread difference")
axes[0].set_yticks(range(14),labels,fontsize=7)
axes[0].invert_yaxis()
fig.text(.63,.03,"W = 320; paired Monte Carlo point estimates and 95% intervals",ha="center",fontsize=7)
save(fig,"Fig6-evaluation-uncertainty")
print(json.dumps(stats,indent=2))
