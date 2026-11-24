from __future__ import annotations
import argparse, hashlib, json, time
from pathlib import Path
import numpy as np
import psutil
import engine

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def seed_int(text): return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "big")
def key(c): return f"{c['stage']}__{c['dataset']}__p{c['path']}__w{c['W']}__{c['coupling']}"
def write_json(path, obj):
    with Path(path).open("x", encoding="utf-8") as f: json.dump(obj, f, indent=2, sort_keys=True); f.write("\n")

def verify(base):
    manifest=json.loads((base/"snapshot/source_manifest.json").read_text(encoding="utf-8"))
    for rel, expected in manifest["files"].items():
        found=sha(base/rel)
        if found != expected: raise RuntimeError(f"Frozen source mismatch: {rel}")
    return sha(base/"snapshot/source_manifest.json")

def condition_matrix(cfg):
    p=cfg["propagation"]
    for ds in cfg["datasets"]:
        for path in cfg["resolution"]["paths"]:
            for W in cfg["resolution"]["selection_worlds"]:
                yield {"stage":"resolution","dataset":ds,"path":path,"W":W,"k":cfg["seed_budget"],"p":p["probability"],"h":p["horizon"],"coupling":"step"}
        for path in cfg["fixed_edge_control"]["paths"]:
            yield {"stage":"fixed_edge_control","dataset":ds,"path":path,"W":cfg["fixed_edge_control"]["selection_worlds"],"k":cfg["seed_budget"],"p":p["probability"],"h":p["horizon"],"coupling":"edge"}

def arms_for(g, c, cfg):
    n=len(g["nodes"]); k=c["k"]; spec=cfg["candidate_pools"]
    size4=min(n, spec["fixed_multiplier"]*k); sizepct=min(n, int(np.ceil(spec["coverage_fraction"]*n)))
    arms={"full":np.arange(n,dtype=np.int64),"degree_4k":g["rankings"]["degree"][:size4],"pagerank_4k":g["rankings"]["pagerank"][:size4],"degree_5pct":g["rankings"]["degree"][:sizepct],"pagerank_5pct":g["rankings"]["pagerank"][:sizepct]}
    for repeat in range(spec["random_repeats"]):
        rng=np.random.default_rng(seed_int(f"{cfg['namespace']}|pool|{c['dataset']}|{c['path']}|{repeat}"))
        arms[f"random{repeat}_4k"]=rng.permutation(n)[:size4]
    if "history_weighted" in g["rankings"]:
        arms["history_weighted_4k"]=g["rankings"]["history_weighted"][:size4]
        arms["history_weighted_5pct"]=g["rankings"]["history_weighted"][:sizepct]
    for name, values in arms.items():
        if len(np.unique(values)) != len(values): raise RuntimeError(f"duplicate candidates {name}")
    return arms

def run_condition(base, out, cfg, g, c, source_hash):
    process=psutil.Process(); started=time.perf_counter(); n=len(g["nodes"])
    selection_ids=engine.world_ids(c["dataset"],c["path"],"selection",c["W"],cfg["namespace"])
    evaluation_ids=engine.world_ids(c["dataset"],c["path"],"evaluation",cfg["evaluation_worlds"],cfg["namespace"])
    if set(selection_ids)&set(evaluation_ids): raise RuntimeError("world-family collision")
    t=time.perf_counter(); worlds=engine.make_worlds(selection_ids,g["sources"],g["targets"],c["p"],c["h"],c["coupling"]=="edge"); sw=time.perf_counter()-t
    t=time.perf_counter(); eworlds=engine.make_worlds(evaluation_ids,g["sources"],g["targets"],c["p"],c["h"],c["coupling"]=="edge"); ew=time.perf_counter()-t
    candidates=arms_for(g,c,cfg); order=sorted(candidates)
    np.random.default_rng(seed_int(f"{cfg['namespace']}|order|{key(c)}")).shuffle(order)
    arrays={}; arms={}
    for name in order:
        t=time.perf_counter(); selected, totals=engine.greedy(g["indptr"],g["targets"],worlds,candidates[name],c["k"],c["h"]); st=time.perf_counter()-t
        t=time.perf_counter(); values=engine.evaluate(g["indptr"],g["targets"],eworlds,selected,c["h"]); et=time.perf_counter()-t
        if np.any(values<c["k"]) or np.any(values>n): raise RuntimeError("spread bound failed")
        arrays[name+"_evaluation"]=values; arrays[name+"_round_totals"]=totals
        arms[name]={"selected":[g["nodes"][i] for i in selected],"candidate_ids":[g["nodes"][i] for i in sorted(candidates[name])],"candidate_count":int(len(candidates[name])),"coverage":float(len(candidates[name])/n),"full_pool":bool(len(candidates[name])==n),"mean_spread":float(values.mean()),"incremental_spread":float(values.mean()-c["k"]),"selection_seconds":st,"evaluation_seconds":et,"ranking_seconds":0.0 if name.startswith("random") or name=="full" else g["ranking_seconds"]["history_weighted" if name.startswith("history_weighted") else name.split("_")[0]],"trace":[{"winner":g["nodes"][selected[r]],"total":int(np.max(totals[r])),"ties":int(np.sum(totals[r]==np.max(totals[r]))),"margin":None if np.sum(totals[r]>=0)<2 else float((np.sort(totals[r][totals[r]>=0])[-1]-np.sort(totals[r][totals[r]>=0])[-2])/c["W"])} for r in range(c["k"])]}
    if not arms["full"]["full_pool"]: raise RuntimeError("full pool lost")
    for name, arm in arms.items():
        diff=arrays[name+"_evaluation"]-arrays["full_evaluation"]
        arm.update({"delta":float(diff.mean()),"mc_se":float(diff.std(ddof=1)/np.sqrt(len(diff))),"same_order":arm["selected"]==arms["full"]["selected"],"same_set":set(arm["selected"])==set(arms["full"]["selected"])})
        if arm["full_pool"] and not arm["same_order"]: raise RuntimeError("complete pool did not reproduce full")
    repeats=[]
    timing=cfg["timing"]
    if c["stage"]=="resolution" and c["path"] in timing["dataset_paths"] and c["W"]==timing["selection_worlds"]:
        for rep in range(timing["repeats"]):
            repeat_order=list(candidates); np.random.default_rng(seed_int(f"{cfg['namespace']}|timing|{key(c)}|{rep}")).shuffle(repeat_order)
            for name in repeat_order:
                t=time.perf_counter(); selected,_=engine.greedy(g["indptr"],g["targets"],worlds,candidates[name],c["k"],c["h"]); st=time.perf_counter()-t
                t=time.perf_counter(); values=engine.evaluate(g["indptr"],g["targets"],eworlds,selected,c["h"]); et=time.perf_counter()-t
                if [g["nodes"][i] for i in selected] != arms[name]["selected"] or not np.array_equal(values,arrays[name+"_evaluation"]): raise RuntimeError("repeat determinism failed")
                repeats.append({"repeat":rep,"method":name,"selection_seconds":st,"evaluation_seconds":et,"order":repeat_order.index(name)})
    folder=out/"conditions"; folder.mkdir(exist_ok=True); stem=key(c); npz=folder/(stem+".npz"); js=folder/(stem+".json")
    if npz.exists() or js.exists(): raise FileExistsError(stem)
    with npz.open("xb") as f: np.savez_compressed(f,**arrays)
    report={"config":c,"source_manifest_sha256":source_hash,"graph":g["metadata"],"selection_world_sha256":hashlib.sha256(selection_ids.tobytes()).hexdigest(),"evaluation_world_sha256":hashlib.sha256(evaluation_ids.tobytes()).hexdigest(),"evaluation_world_count":cfg["evaluation_worlds"],"preparation_seconds":g["preparation_seconds"],"ranking_seconds":g["ranking_seconds"],"selection_world_preparation_seconds":sw,"evaluation_world_preparation_seconds":ew,"order":order,"arms":arms,"timing_repeats":repeats,"array_sha256":sha(npz),"elapsed_seconds":time.perf_counter()-started,"peak_working_set_bytes":int(getattr(process.memory_info(),"peak_wset",process.memory_info().rss))}
    write_json(js,report); return {"key":stem,"json_sha256":sha(js),"npz_sha256":sha(npz),"elapsed_seconds":report["elapsed_seconds"]}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--base",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); args=ap.parse_args(); base=args.base.resolve(); cfg=json.loads((base/"config.json").read_text()); source_hash=verify(base); out=args.output; out.mkdir(parents=True,exist_ok=True)
    if (out/"run_status.json").exists(): raise FileExistsError("run_status.json exists; use an empty output directory")
    t=time.perf_counter(); engine.warmup(); warm=time.perf_counter()-t; graphs={}; completed=[]
    try:
        for c in condition_matrix(cfg):
            if c["dataset"] not in graphs: graphs[c["dataset"]]=engine.load_external_graph(base/"data/raw/snap",c["dataset"])
            completed.append(run_condition(base,out,cfg,graphs[c["dataset"]],c,source_hash))
            (out/"run_status.json").write_text(json.dumps({"status":"running","completed":completed,"jit_warmup_seconds":warm},indent=2)+"\n",encoding="utf-8")
    except Exception as e:
        (out/"run_status.json").write_text(json.dumps({"status":"failed","error":repr(e),"completed":completed,"jit_warmup_seconds":warm},indent=2)+"\n",encoding="utf-8"); raise
    (out/"run_status.json").write_text(json.dumps({"status":"complete","completed":completed,"jit_warmup_seconds":warm},indent=2)+"\n",encoding="utf-8")
if __name__=="__main__": main()
