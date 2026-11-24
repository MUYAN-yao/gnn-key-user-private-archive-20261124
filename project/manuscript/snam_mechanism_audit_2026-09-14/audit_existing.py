"""Audit archived v3 runs; no training, diffusion, or optimization is executed.

Outputs are new manuscript audit derivatives. Existing studies are read-only.
Structural ranks are reconstructed from archived inputs and decision cutoffs.
"""
from collections import Counter
from itertools import product
from pathlib import Path
import hashlib
import json

import networkx as nx
import numpy as np
import pandas as pd
from scipy import stats

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
STUDY = ROOT / "results/large-robust-greedy-higgs-50000-v3-fairness-sensitivity"
DATA = ROOT / "data/processed/higgs-twitter/pilot-50000"
OLD = ROOT / "analysis/v3-fairness-sensitivity-strict-paired-v1/paired_comparisons.json"
BASE = "screened_robust_greedy"
FULL = "full_candidate_robust_greedy"
TOP = "gnn_top_k_protected_lower_bound_audit"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expand(a):
    m = a["methods"]
    return {BASE: m[BASE], FULL: m[FULL], TOP: m[TOP],
            **{f"screened_pool_{k}": v for k, v in m["candidate_pool_sensitivity"].items()},
            **{f"objective_{k}": v for k, v in m["objective_weight_sensitivity"].items()}}


def describe(x):
    return {"n": len(x), "mean": float(np.mean(x)), "sd": float(np.std(x, ddof=1)),
            "min": float(np.min(x)), "max": float(np.max(x)), "median": float(np.median(x))}


manifest = json.loads((STUDY / "manifest.json").read_text(encoding="utf-8"))
assert not manifest["smoke_test"] and manifest["run_parameters"]["full_candidate_limit"] is None
paths = sorted(STUDY.glob("split-*.json"))
assert {p.name for p in paths} == set(manifest["runs"])
assert len(paths) == 30
checks = {}
for path in paths:
    assert digest(path) == manifest["runs"][path.name], path
    checks[str(path.relative_to(ROOT))] = digest(path)
for filename, expected in manifest["inputs"].items():
    path = DATA / filename
    assert digest(path) == expected, path
    checks[str(path.relative_to(ROOT))] = expected
for filename, expected in manifest["source"].items():
    path = ROOT / ("experiments" if filename.startswith("run_") else "backend/app") / filename
    assert digest(path) == expected, path
    checks[str(path.relative_to(ROOT))] = expected
for filename, expected in manifest["protocol"].items():
    assert digest(STUDY / filename) == expected
    checks[str((STUDY / filename).relative_to(ROOT))] = expected
for path in (STUDY / "manifest.json", STUDY / "method_metrics.csv", OLD,
             ROOT / "backend/app/graph.py", ROOT / "backend/app/validation.py"):
    checks[str(path.relative_to(ROOT))] = digest(path)

runs = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in paths}
assert {(a["config"]["train_fraction"], a["config"]["random_seed"]) for a in runs.values()} == {(f,s) for f in (.6,.65,.7) for s in range(42,52)}
rows, summaries, changes = [], [], []
for identifier, a in runs.items():
    c, r, m = a["config"], a["reproducibility"], a["methods"]
    assert (c["seed_count"], c["horizon"], c["simulations"]) == (2,4,20)
    assert r["encoder_history_cutoff"] < r["supervised_cutoff"] < r["calibration_cutoff"] < r["outer_test_start"]
    worlds = []
    for namespace, key in ((101,"selection"),(202,"evaluation")):
        generator = np.random.default_rng(np.random.SeedSequence([c["random_seed"], namespace, 3]))
        values = [int(x) for x in generator.integers(0, 2**63-1, size=20)]
        encoded = json.dumps(values, separators=(",", ":"), sort_keys=True).encode()
        assert hashlib.sha256(encoded).hexdigest() == r[f"{key}_worlds_sha256"]
        worlds.append(set(values))
    assert not worlds[0] & worlds[1]
    assert m[BASE]["selection"] == m[FULL]["selection"]
    assert m[BASE]["reporting_evaluation"] == m[FULL]["reporting_evaluation"]
    for k, arm in m["candidate_pool_sensitivity"].items():
        assert arm["candidate_count"] == int(k)
        assert arm["selection"] == m[BASE]["selection"]
        assert arm["reporting_evaluation"] == m[BASE]["reporting_evaluation"]
    prior2 = m[TOP]["reporting_evaluation"]["top_k"]
    chosen = m[BASE]["selection"]["top_k"]
    for position, node in enumerate(chosen, 1):
        # The archived direct Top-K list reveals ranks 1 and 2 exactly.
        rank = prior2.index(node) + 1 if node in prior2 else None
        rows.append({"run_id": identifier, "fraction": c["train_fraction"], "seed": c["random_seed"],
                     "selection_step": position, "node": node, "prior_rank_exact": rank,
                     "prior_rank_lower": rank if rank is not None else 3,
                     "prior_rank_upper": rank if rank is not None else 60})
    summaries.append({"run_id": identifier, "fraction": c["train_fraction"], "seed": c["random_seed"],
                      "selected_order": chosen, "prior_top2": prior2, "direct_top2_same_set": set(chosen)==set(prior2),
                      "full_n": m[FULL]["candidate_count"], "screen_seconds": m[BASE]["selection_seconds"],
                      "full_seconds": m[FULL]["selection_seconds"],
                      "audit_minus_greedy_J": m[TOP]["reporting_evaluation"]["robust_objective"]-m[BASE]["reporting_evaluation"]["robust_objective"]})
    for key, arm in m["objective_weight_sensitivity"].items():
        if arm["selection"]["top_k"] != chosen:
            changes.append({"run_id": identifier, "arm": key, "base": m[BASE], "changed": arm})

# Exact agreement with the previously saved metric CSV, not just its aggregate table.
metrics = pd.read_csv(STUDY / "method_metrics.csv")
assert len(metrics) == 480 and not metrics.duplicated(["run_id","method"]).any()
for _, row in metrics.iterrows():
    arm = expand(runs[row.run_id])[row.method]
    e = arm["reporting_evaluation"]
    assert json.loads(row.top_k) == e["top_k"]
    for key in ("mean_spread", "spread_std", "robust_objective", "community_coverage"):
        assert float(row[key]) == e[key]

# Validate archived inferential contrasts without changing the test family.
contrasts = json.loads(OLD.read_text(encoding="utf-8"))
assert Counter(x["family"] for x in contrasts) == {"primary_fairness": 3, "candidate_pool_sensitivity": 9, "objective_weight_sensitivity": 24}
for item in contrasts:
    d = np.array([expand(runs[i])[item["reference"]]["reporting_evaluation"]["robust_objective"] -
                  expand(runs[i])[item["comparator"]]["reporting_evaluation"]["robust_objective"] for i in item["run_ids"]])
    assert np.array_equal(d, item["differences"])
    exact_p = np.mean([abs(np.dot(signs, d)/10) >= abs(d.mean())-1e-12 for signs in product((-1,1), repeat=10)])
    assert exact_p == item["exact_sign_flip_p"] == 1.0
    assert item["holm_p"] == 1.0 if "holm_p" in item else item["holm_adjusted_p"] == 1.0
    assert np.isclose(d.mean(), item["mean_difference"])

# Reconstruct only the lightweight structural graph, not GNN probabilities.
nodes = pd.read_csv(DATA / "nodes.csv", dtype={"node_id": "string"}).node_id.astype(str).tolist()
edges = pd.read_csv(DATA / "edges.csv", dtype={"src":"string","dst":"string"})
edges["timestamp"] = pd.to_datetime(edges.timestamp, utc=True)
edges = edges.sort_values("timestamp").drop_duplicates(["src","dst","timestamp"], keep="first")
structural, graph_stats, pools = [], [], {}
for f in (.6,.65,.7):
    selected_runs = [a for a in runs.values() if a["config"]["train_fraction"] == f]
    cutoff = selected_runs[0]["reproducibility"]["outer_test_start"]
    train = edges[edges.timestamp < pd.Timestamp(cutoff)].copy()
    r = selected_runs[0]["reproducibility"]
    assert len(train) == sum(r["window_rows"][k] for k in ("history","supervised","calibration"))
    assert train.timestamp.max().isoformat() == r["calibration_cutoff"]
    age = (train.timestamp.max() - train.timestamp).dt.total_seconds().clip(lower=0)/86400
    decay = np.exp(-age/max(age.quantile(.75), 1.0))
    graph = nx.DiGraph()
    graph.add_nodes_from(sorted(nodes))
    for (_, row), value in zip(train.iterrows(), decay):
        src, dst = str(row.src), str(row.dst)
        previous = graph.get_edge_data(src,dst,default={}).get("weight",0)
        graph.add_edge(src,dst,weight=float(previous)+float(value))
    scores = {"weighted_out_degree": dict(graph.out_degree(weight="weight")),
              "out_degree": dict(graph.out_degree()), "pagerank": nx.pagerank(graph, weight="weight")}
    ranks = {key: {n: i+1 for i,n in enumerate(sorted(s, key=lambda n: (-s[n],str(n))))} for key,s in scores.items()}
    pools[str(f)] = {key: [n for n in sorted(s,key=lambda n:(-s[n],str(n)))[:120]] for key,s in scores.items()}
    for node in ("88","1988","677"):
        structural.append({"fraction":f, "node":node, **{key+"_rank": rank[node] for key,rank in ranks.items()},
                           "out_degree": graph.out_degree(node), "weighted_out_degree": graph.out_degree(node,weight="weight")})
    graph_stats.append({"fraction":f, "nodes":graph.number_of_nodes(), "edges":graph.number_of_edges(),
                        "outgoing_nodes":sum(graph.out_degree(n)>0 for n in nodes),
                        "isolates":len(list(nx.isolates(graph))), "retained_event_rows":len(train)})

frame = pd.DataFrame(summaries)
group_summary = []
for f, group in frame.groupby("fraction"):
    group_summary.append({"fraction":f, "n":len(group), "selected_sets":dict(Counter(",".join(v) for v in group.selected_order)),
                          "same_as_prior_top2":int(group.direct_top2_same_set.sum()),
                          "screen_seconds":describe(group.screen_seconds), "full_seconds":describe(group.full_seconds),
                          "ratio_of_mean_times":float(group.full_seconds.mean()/group.screen_seconds.mean()),
                          "audit_minus_greedy_J":describe(group.audit_minus_greedy_J)})
change = changes[0]
assert len(changes)==3 and len({x["run_id"] for x in changes})==1
a,b = change["base"]["selection"],change["changed"]["selection"]
delta_mu = a["mean_spread"]-b["mean_spread"]
delta_sd = a["spread_std"]-b["spread_std"]
threshold = delta_mu/delta_sd
assert a["community_coverage"] == b["community_coverage"] == 2
community_invariant = 0
for run in runs.values():
    arms = run["methods"]["objective_weight_sensitivity"]
    for risk in (0,.35,.7):
        selections = [arms[f"risk-{risk:.2f}_community-{eta:.2f}"]["selection"]["top_k"] for eta in (0,.25,.5)]
        community_invariant += int(all(x==selections[0] for x in selections))

pd.DataFrame(rows).to_csv(OUT/"selected_node_rank_bounds.csv", index=False, encoding="utf-8-sig")
pd.DataFrame(structural).to_csv(OUT/"structural_node_ranks.csv", index=False, encoding="utf-8-sig")
frame.to_csv(OUT/"run_audit.csv", index=False, encoding="utf-8-sig")
result = {"integrity": {"run_hashes":30,"input_hashes":3,"recorded_source_hashes":4,"csv_rows":480,"contrasts_checked":36,
                         "source_limit":"graph.py and validation.py were not listed in the original v3 source manifest; current versions recorded below"},
          "groups":group_summary,"graph_stats":graph_stats,"structural_ranks":structural,
          "prior_rank_known":sum(r["prior_rank_exact"] is not None for r in rows),
          "prior_rank_bounded":sum(r["prior_rank_exact"] is None for r in rows),
          "community_invariant_blocks":community_invariant,
          "risk_switch":{"run_id":change["run_id"],"changed_arms":3,"base":a,"alternative":b,
                         "delta_mean":delta_mu,"delta_sd":delta_sd,"pairwise_crossing_lambda":threshold,
                         "base_minus_alternative_at_lambda_035":delta_mu-.35*delta_sd,
                         "base_minus_alternative_at_lambda_070":delta_mu-.7*delta_sd,
                         "reporting_difference":change["base"]["reporting_evaluation"]["robust_objective"]-change["changed"]["reporting_evaluation"]["robust_objective"]},
          "missing_evidence":["full prior vectors and candidate lists","per-round runner-up scores and tie counts","saved edge probabilities/model checkpoints","separate training and preprocessing timers"],
          "hashes":checks}
(OUT/"audit_summary.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"structural_top120.json").write_text(json.dumps(pools,ensure_ascii=False,indent=2),encoding="utf-8")
assert all(digest(ROOT/path)==expected for path,expected in checks.items())
print(json.dumps({k:v for k,v in result.items() if k!="hashes"}, ensure_ascii=False,indent=2))
