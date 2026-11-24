"""Post-hoc setup-only repeated timings; no seed or utility selection."""
from pathlib import Path
import sys,json,time,platform
import numpy as np
import networkx as nx
import pandas as pd
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'snapshot'))
import engine,run_experiment as runner
OUT=ROOT/'review-v2/analysis';OUT.mkdir(parents=True,exist_ok=True)
cfg=json.loads((ROOT/'config.json').read_text());rows=[]
for ds in cfg['datasets']:
    raw=ROOT/'data/raw/snap'/engine.RAW_FILENAMES[ds]
    for rep in range(5):
        t=time.perf_counter()
        parsed=engine._read_college(raw) if ds=='college_msg' else engine._read_static(raw,ds=='ca_grqc','timing')
        nodes=parsed['nodes'];ad=parsed['adjacency']; ip,tt,ss=engine.csr(nodes,ad)
        load=time.perf_counter()-t
        rankings={};dur={}
        for family in ['degree','pagerank']+(['history_weighted'] if ds=='college_msg' else []):
            t=time.perf_counter()
            scores={n:len(ad[n]) for n in nodes} if family=='degree' else nx.pagerank(nx.DiGraph(ad),weight=None) if family=='pagerank' else parsed['weighted_scores']
            rankings[family]=np.asarray(sorted(range(len(nodes)),key=lambda i:(-float(scores.get(nodes[i],0)),nodes[i])),dtype=np.int64)
            dur[family]=time.perf_counter()-t
        for name in ['full','degree_4k','degree_5pct','pagerank_4k','pagerank_5pct','random_mean_4k']+(['history_weighted_4k','history_weighted_5pct'] if ds=='college_msg' else []):
            t=time.perf_counter();rank=0.
            if name=='full': pool=np.arange(len(nodes),dtype=np.int64)
            elif name.startswith('random'):
                # A single random-pool deployment; three experimental repeats are not three deployment executions.
                rng=np.random.default_rng(runner.seed_int(f"{cfg['namespace']}|pool|{ds}|1101|{rep%3}"));pool=rng.permutation(len(nodes))[:20]
            else:
                family='history_weighted' if name.startswith('history') else name.split('_')[0]
                rank=dur[family];pool=rankings[family][:(int(np.ceil(.05*len(nodes))) if name.endswith('5pct') else 20)]
            # Frozen greedy already sorts candidates inside selection_seconds.
            # Charge pool creation here, but do not charge that sort twice.
            pool_s=time.perf_counter()-t
            rows.append(dict(dataset=ds,repeat=rep,method=name,parse_csr_seconds=load,ranking_seconds=rank,pool_seconds=pool_s,setup_seconds=load+rank+pool_s))
pd.DataFrame(rows).to_csv(OUT/'supplement_setup_timing.csv',index=False)
(OUT/'supplement_setup_timing.json').write_text(json.dumps({'status':'complete','posthoc':True,'repetitions':5,'python':sys.version,'platform':platform.platform(),'scope':'Warm process; OS cache uncontrolled, raw gzip parse and CSR plus one method rank and pool construction; lexical candidate sort remains in frozen selection timer. Excludes imports/JIT, diagnostics, downloads, result writing. Setup measurement is assembled with frozen selection timings, not a single end-to-end benchmark.'},indent=2),encoding='utf-8')
print('setup timing complete',len(rows))
