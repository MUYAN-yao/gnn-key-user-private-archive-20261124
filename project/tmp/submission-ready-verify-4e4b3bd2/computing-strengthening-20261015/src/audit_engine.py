"""Meaningful semantic/provenance tests, plus outcome-blind timing preflight."""
import sys,json,time,itertools,platform,os,hashlib
from pathlib import Path
import numpy as np
import engine

def main():
    project=Path(sys.argv[1]).resolve()
    out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
    snapshot=project/'reproducibility/v10-source-snapshots/sociopatterns-resolution-confirmation-v0_1-20260920-r3'
    sys.path.insert(0,str(snapshot))
    from experiments.v7_exact_search import deterministic_uniform,simulate_ic_common_world,full_greedy
    from experiments.v10_source_snapshot import verify
    from experiments.v10_sociopatterns_resolution_confirmation import world_ids as old_ids
    tests=[]
    t=time.perf_counter();engine.warmup();jit=time.perf_counter()-t
    verify(snapshot);tests.append('archived snapshot hashes verified')
    for w in [0,1,301,2**63-1]:
        for s in [0,1,3]:
            for u in [0,5,401]:
                for v in [0,9,211]:
                    assert engine.uniform(np.uint64(w),s,u,v)==deterministic_uniform(w,s,u,v)
    tests.append('108 edge-time uniforms bit-identical to archived Python')
    graph={'a':('b',),'b':('c',),'c':()};nodes=sorted(graph);codes={n:i for i,n in enumerate(nodes)}
    ip,tg,src=engine.csr(nodes,graph)
    ids=np.arange(100,dtype=np.uint64)
    for h in [0,1,2,3]:
        for p in [0.,.3,1.]:
            worlds=engine.make_worlds(ids,src,tg,p,h,False)
            probabilities={(a,b):p for a in graph for b in graph[a]}
            for length in range(4):
                for seeds in itertools.combinations(nodes,length):
                    a=engine.evaluate(ip,tg,worlds,np.asarray([codes[s] for s in seeds],dtype=np.int64),h)
                    b=[simulate_ic_common_world(graph,seeds,probabilities,h,int(w),codes) for w in ids]
                    assert list(a)==b
    tests.append('9600 chain outcomes match Python; empty seeds, p=0/1, horizons 0..3')
    # Exhibit why a time-coupled finite objective is not automatically monotone.
    counterexample=None
    for w in range(10000):
        a=simulate_ic_common_world(graph,['a'],{('a','b'):.5,('b','c'):.5},2,w,codes)
        b=simulate_ic_common_world(graph,['a','b'],{('a','b'):.5,('b','c'):.5},2,w,codes)
        if a>b:
            counterexample={'world':w,'A':['a'],'B':['a','b'],'f_A':a,'f_B':b,'p':.5,'h':2};break
    assert counterexample
    tests.append('finite step-coupled objective has an explicit monotonicity counterexample')
    # Edge-coupled worlds agree with an independent shortest-path reachability oracle.
    import networkx as nx
    rng=np.random.default_rng(7)
    for rep in range(15):
        dg=nx.gnp_random_graph(7,.3,seed=rep,directed=True)
        graph2={str(n):tuple(str(v) for v in dg[n]) for n in dg};ns=sorted(graph2)
        ip2,tg2,src2=engine.csr(ns,graph2)
        world=engine.make_worlds(np.arange(12,dtype=np.uint64),src2,tg2,.4,3,True)
        stepworld=engine.make_worlds(np.arange(12,dtype=np.uint64),src2,tg2,.4,3,False)
        probs={(a,b):.4 for a in graph2 for b in graph2[a]};cd={n:i for i,n in enumerate(ns)}
        for w in range(12):
            live=nx.DiGraph();live.add_nodes_from(range(7));live.add_edges_from((int(src2[e]),int(tg2[e])) for e in range(len(tg2)) if world[w,0,e])
            for seeds in [[],[0],[0,2],[0,2,5]]:
                reached=set()
                for seed in seeds:reached.update(nx.single_source_shortest_path_length(live,seed,cutoff=3))
                assert engine.spread_one(ip2,tg2,world[w],np.asarray(seeds,dtype=np.int64),3)==len(reached)
                assert engine.spread_one(ip2,tg2,stepworld[w],np.asarray(seeds,dtype=np.int64),3)==simulate_ic_common_world(graph2,[ns[s] for s in seeds],probs,3,w,cd)
        candidates=np.asarray([0,2,4,6],dtype=np.int64)
        selected,_=engine.greedy(ip2,tg2,stepworld,candidates,3,3)
        ref=full_greedy(graph2,probs,{n:'0' for n in ns},tuple(range(12)),horizon=3,seed_count=3,risk_lambda=0,community_weight=0,candidate_universe=[ns[i] for i in candidates])
        assert [ns[i] for i in selected]==ref['selected']
    tests.append('720 live-edge reachability checks, 720 cyclic step-oracle checks and 15 restricted greedy checks passed')
    root=project/'audits/sociopatterns-resolution-confirmation-v0_1/snapshot-r3-confirmation-run-20260920'
    ledger=json.loads((project/'analysis/sociopatterns-resolution-confirmation-v0_1-validation.json').read_text())
    for row in ledger['condition_file_hashes']:
        assert engine.digest(root/row['path'])==row['sha256']
    tests.append('all 42 archived output hashes match historical validation ledger')
    recreated=[]
    for name in ['kenya2012','invs2013','invs2015','sfhh2009']:
        g=engine.load_graph(project,name)
        for W in [20,80]:
            record=json.loads((root/name/'k5'/f'path-301-w{W}.json').read_text())
            assert g['metadata']['input_sha256']==record['input_sha256']
            ids=np.asarray(old_ids(name,301,'selection',W),dtype=np.uint64)
            worlds=engine.make_worlds(ids,g['sources'],g['targets'],.01,3,False)
            ev=engine.make_worlds(np.asarray(old_ids(name,301,'evaluation',2000),dtype=np.uint64),g['sources'],g['targets'],.01,3,False)
            for method,arm in record['arms'].items():
                cand=np.arange(len(g['nodes'])) if method=='full' else g['rankings']['weighted'][:int(method.split('_')[1][:-1])*5]
                sel,scores=engine.greedy(g['indptr'],g['targets'],worlds,cand,5,3)
                assert [g['nodes'][i] for i in sel]==arm['selection']['top_k']
                vals=engine.evaluate(g['indptr'],g['targets'],ev,sel,3)
                assert vals.tolist()==arm['evaluation']['world_spreads']
                recreated.append([name,W,method])
    tests.append('32 archived arm traces and all 64000 evaluation outcomes exactly reproduced')
    timing=[]
    for name,k,W,p,h in [('sfhh2009',5,1280,.01,3),('invs2015',20,320,.01,3),('synthetic_ba2000',5,80,.01,3),('synthetic_sbm2000',5,80,.01,3),('sfhh2009',5,320,.05,5)]:
        g=engine.load_graph(project,name);ids=engine.world_ids(name,9001,'preflight',W)
        start=time.perf_counter();worlds=engine.make_worlds(ids,g['sources'],g['targets'],p,h,False);prep=time.perf_counter()-start
        start=time.perf_counter();engine.greedy(g['indptr'],g['targets'],worlds,np.arange(len(g['nodes'])),k,h);elapsed=time.perf_counter()-start
        timing.append(dict(dataset=name,k=k,W=W,p=p,h=h,n=len(g['nodes']),m=len(g['targets']),world_seconds=prep,selection_seconds=elapsed,outcome_recorded=False))
        print(json.dumps(timing[-1]),flush=True)
    import psutil,numba,llvmlite,pandas,scipy
    report=dict(status='PASS',tests=tests,counterexample=counterexample,recreated_arms=recreated,preflight=timing,jit_seconds=jit,environment=dict(python=sys.version,platform=platform.platform(),cpu=platform.processor(),logical_cpus=os.cpu_count(),physical_cpus=psutil.cpu_count(logical=False),ram_bytes=psutil.virtual_memory().total,numpy=np.__version__,numba=numba.__version__,llvmlite=llvmlite.__version__,pandas=pandas.__version__,scipy=scipy.__version__,threads=1),engine_sha256=engine.digest(Path(__file__).with_name('engine.py')))
    target=out/'audit-and-preflight.json'
    with target.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
    print('PASS',len(tests),flush=True)

if __name__=='__main__':main()
