"""Four main figures; descriptive displays from the complete admitted matrix."""
from pathlib import Path
import csv
import json
import hashlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import ListedColormap

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "analysis/sociopatterns-resolution-confirmation-v0_2"
OUT = ROOT / "manuscript/resolution_aware_candidate_truncation_submission_v0_1/figures"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
                     "font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
                     "pdf.fonttype": 42, "svg.fonttype": "none", "legend.frameon": False})
W = [20, 80, 320]
METHODS = ["degree_2k", "degree_4k", "degree_8k"]
COLORS = ["#0072B2", "#D55E00", "#555555"]
MARKERS = ["o", "s", "^"]
records = list(csv.DictReader((SOURCE / "candidate_condition_profile.csv").open(encoding="utf-8")))
traces = json.loads((SOURCE / "full_trajectories.json").read_text())
summary = json.loads((SOURCE / "summary.json").read_text())
assert len(records) == 126 and len(traces) == 14
blocks = sorted({(r["dataset"], int(r["k"]), int(r["world_path"])) for r in records})
lookup = {(r["dataset"], int(r["k"]), int(r["world_path"]), int(r["selection_world_count"]), r["method"]): r for r in records}
assert len(lookup) == 126

def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf", facecolor="white")
    fig.savefig(OUT / f"{name}.svg", facecolor="white")
    fig.savefig(OUT / f"{name}.png", dpi=600, facecolor="white")
    plt.close(fig)

def label(ax, text):
    ax.text(-0.12, 1.04, text, transform=ax.transAxes, weight="bold", fontsize=10)

# Contract: schematic-led figure. Show evaluation dependencies, not a causal
# explanation of observed trace changes. Fixed 174 mm width; editable vectors.
fig, ax = plt.subplots(figsize=(174/25.4, 4.8))
fig.subplots_adjust(left=.02, right=.98, top=.98, bottom=.02)
ax.set(xlim=(0, 10), ylim=(0, 10))
ax.axis("off")
def box(x, y, width, height, text, fill="#F1F4F6"):
    ax.add_patch(FancyBboxPatch((x,y),width,height,boxstyle="round,pad=0.08,rounding_size=0.10",
                              facecolor=fill,edgecolor="#52606A",linewidth=.8))
    ax.text(x+width/2,y+height/2,text,ha="center",va="center",fontsize=8)
def arrow(a,b):
    ax.annotate("",xy=b,xytext=a,arrowprops=dict(arrowstyle="-|>",color="#52606A",lw=1))
box(.2,8.4,9.6,1.0,"Observed contacts → historical aggregation → fixed graph\nSimulated independent cascade: p = 0.01; horizon = 3")
box(.2,6.3,4.0,1.3,"Search-space choice\nFull node set  |  Degree pools: 2k, 4k, 8k", "#E7EFF5")
box(5.0,6.3,4.8,1.3,"Selection-resolution choice\nNested world prefixes: 20 → 80 → 320", "#F8EEE5")
arrow((2.2,8.4),(2.2,7.6)); arrow((7.4,8.4),(7.4,7.6))
box(1.1,4.1,7.8,1.35,"Greedy re-optimization for each pool and budget\nShared selection worlds and deterministic tie-breaking\nRecord ordered seeds, score gaps, ties, and elapsed time")
arrow((2.2,6.3),(3.2,5.45)); arrow((7.4,6.3),(6.8,5.45))
box(.2,1.8,4.3,1.45,"Decision reproduction\nAcross budgets: full-reference stability\nWithin budget: pool–full agreement")
box(5.1,1.8,4.7,1.45,"Independent utility and cost\nEvaluate seeds on 2,000 unused worlds\nCompare spread and measured time", "#EAF2EE")
arrow((3.0,4.1),(2.35,3.25)); arrow((7.0,4.1),(7.45,3.25))
ax.text(5,.85,"Ordered trace agreement ≠ final-set equality ≠ utility equivalence",
        ha="center",fontsize=9,weight="bold")
ax.text(5,.35,"Evaluation mechanism and information flow; no causal mechanism is inferred.",ha="center",fontsize=8)
save(fig,"Fig1-evaluation-mechanism")

# Shared builder keeps the simplified main panel and all supplementary paths current.
from build_reference_resolution_figures import build as build_reference_figures
build_reference_figures()

# Contract: all-condition binary heatmap, same row order across all three pools.
fig, axes = plt.subplots(1,3,figsize=(174/25.4,4.25),sharey=True)
fig.subplots_adjust(left=.29,right=.98,bottom=.16,top=.90,wspace=.20)
for ax,method,short in zip(axes,METHODS,["2k","4k","8k"]):
    node_counts={"invs2013":91,"invs2015":212,"kenya2012":75,"sfhh2009":402}
    multiplier=int(method.split('_')[1][:-1])
    matrix=np.array([[2 if multiplier*b[1]>=node_counts[b[0]] else int(lookup[(*b,w,method)]["same_ordered_top_k"]=="True") for w in W] for b in blocks])
    ax.imshow(matrix,aspect="auto",cmap=ListedColormap(["#F0F0F0","#277DA8","#F4D6AF"]),vmin=0,vmax=2)
    for y in range(14):
        for x in range(3):
            ax.text(x,y,["×","=","V"][matrix[y,x]],ha="center",va="center",
                    color="white" if matrix[y,x]==1 else "#555555",fontsize=9)
    ax.set(xticks=range(3),xticklabels=W,xlabel="Selection worlds")
    ax.set_title(f"Degree {short}",fontsize=9,pad=9)
axes[0].set_yticks(range(14),[f"{d} | k={k} | path {p}" for d,k,p in blocks],fontsize=7)
fig.text(.63,.045,"= restricted match    × mismatch    V full-node pool",ha="center",fontsize=8)
save(fig,"Fig3-candidate-agreement")

# Contract: cost versus held-out utility for all 126 pool-condition observations.
# Separate panels by W; every point shown, no inferential intervals or trend fits.
fig, axes = plt.subplots(1,3,figsize=(174/25.4,3.35),sharex=True,sharey=True)
fig.subplots_adjust(left=.12,right=.98,bottom=.25,top=.83,wspace=.16)
for ax,w in zip(axes,W):
    for method,color,marker,short in zip(METHODS,COLORS,MARKERS,["2k","4k","8k"]):
        rs=[r for r in records if r["method"]==method and int(r["selection_world_count"])==w]
        ax.scatter([100*float(r["decision_time_saving_fraction"]) for r in rs],
                   [float(r["mean_spread_delta"]) for r in rs],
                   c=color,marker=marker,s=20,alpha=.75,label=f"Degree {short}",linewidths=.4,edgecolors="white")
    ax.axhline(0,color="#555555",lw=.8,ls="--")
    ax.set_title(f"W = {w}",fontsize=9)
    ax.set_xlabel("Measured time saving (%)")
axes[0].set_ylabel("Held-out mean spread difference\n(pool − full; activated nodes)")
handles,labels=axes[0].get_legend_handles_labels()
fig.legend(handles,labels,loc="upper center",ncol=3,bbox_to_anchor=(.55,.995),fontsize=8)
fig.text(.55,.035,"Each point: one network × seed budget × random path; 14 points per pool per panel",ha="center",fontsize=7)
save(fig,"Fig4-cost-utility")

provenance = {"observations":len(records),"trajectory_blocks":len(blocks),"exclusions":0,
              "source_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [
                  SOURCE/"candidate_condition_profile.csv",SOURCE/"full_trajectories.json",SOURCE/"summary.json"]}}
(OUT/"source_provenance.json").write_text(json.dumps(provenance,indent=2))
print(json.dumps(provenance,indent=2))
