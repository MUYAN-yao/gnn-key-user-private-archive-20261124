"""Small post-hoc diagnostic, preserving original reference/worlds/data."""
from pathlib import Path
import sys,json,hashlib,time
import numpy as np
import networkx as nx
import pandas as pd
R=Path(__file__).resolve().parents[1];B=R.parent;D=R/'supplement-pr-precision';sys.path.insert(0,str(B/'snapshot'))
import engine,run_experiment as runner
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):
    with p.open('x',encoding='utf-8') as f:json.dump(o,f,indent=2)
freeze=D/'source_manifest.json'
expected={'protocol.md':sha(D/'protocol.md'),'src/run_precision_control.py':sha(Path(__file__)),'audit/pagerank_precision_diagnostic.csv':sha(R/'audit/pagerank_precision_diagnostic.csv'),'external_snapshot_manifest':sha(B/'snapshot/source_manifest.json')}
if not freeze.exists():write(freeze,expected)
assert json.loads(freeze.read_text())==expected
assert json.loads((R/'audit/full_validation.json').read_text())['status']=='PASS'
runner.verify(B);cfg=json.loads((B/'config.json').read_text());engine.warmup();rows=[];completed=[];folder=D/'conditions';folder.mkdir(exist_ok=True)
for ds in cfg['datasets']:
    g=engine.load_external_graph(B/'data/raw/snap',ds);nodes=g['nodes'];ix={n:i for i,n in enumerate(nodes)};graph=nx.DiGraph();graph.add_nodes_from(nodes);graph.add_edges_from((nodes[int(u)],nodes[int(v)]) for u,v in zip(g['sources'],g['targets']))
    assert g['metadata']==json.loads((B/'data/source_manifest.json').read_text())['datasets'][ds]
    scores=nx.pagerank(graph,alpha=.85,tol=1e-12,max_iter=1000,weight=None);ranking=np.array(sorted(range(len(nodes)),key=lambda i:(-scores[nodes[i]],nodes[i])),dtype=np.int64)
    for path in cfg['resolution']['paths']:
        stem=f'{ds}__p{path}__w1280';js=folder/(stem+'.json');npz=folder/(stem+'.npz')
        assert not js.exists() and not npz.exists(),'use a new version, not overwrite'
        oldfile=B/'results/main/conditions'/f'resolution__{ds}__p{path}__w1280__step.json';old=json.loads(oldfile.read_text());arrays={};arms={};started=time.perf_counter()
        with np.load(oldfile.with_suffix('.npz')) as oz:
            sid=engine.world_ids(ds,path,'selection',1280,cfg['namespace']);eid=engine.world_ids(ds,path,'evaluation',10000,cfg['namespace']);worlds=engine.make_worlds(sid,g['sources'],g['targets'],.01,3,False)
            for meth,count in [('pagerank_4k',20),('pagerank_5pct',int(np.ceil(.05*len(nodes))))]:
                pool=ranking[:count];seeds,totals=engine.greedy(g['indptr'],g['targets'],worlds,pool,5,3);values=[]
                for offset in range(0,len(eid),256):
                    ew=engine.make_worlds(eid[offset:offset+256],g['sources'],g['targets'],.01,3,False);values.append(engine.evaluate(g['indptr'],g['targets'],ew,seeds,3))
                vals=np.concatenate(values);diff=vals-oz['full_evaluation'];change=vals-oz[meth+'_evaluation'];selected=[nodes[i] for i in seeds]
                if set(selected)==set(old['arms'][meth]['selected']):assert np.array_equal(vals,oz[meth+'_evaluation'])
                if set(selected)==set(old['arms']['full']['selected']):assert np.array_equal(vals,oz['full_evaluation'])
                arrays[meth+'_evaluation']=vals;arrays[meth+'_round_totals']=totals
                row={'dataset':ds,'path':path,'method':meth,'candidate_count':count,'mean_spread':float(vals.mean()),'delta_vs_full':float(diff.mean()),'mc_se_vs_full':float(diff.std(ddof=1)/100),'loss_percent':float(-100*diff.mean()/(oz['full_evaluation'].mean()-5)),'delta_vs_default':float(change.mean()),'same_order_as_default':selected==old['arms'][meth]['selected'],'same_set_as_default':set(selected)==set(old['arms'][meth]['selected']),'same_order_as_full':selected==old['arms']['full']['selected']}
                rows.append(row);arms[meth]={**row,'selected':selected,'candidate_ids':[nodes[i] for i in sorted(pool)]}
        with npz.open('xb') as f:np.savez_compressed(f,**arrays)
        write(js,{'scope':'posthoc numerical sensitivity, original paths; not new independent sample','dataset':ds,'path':path,'W':1280,'coupling':'step','graph_sha256':g['metadata']['graph_sha256'],'source_manifest_sha256':sha(freeze),'frozen_reference_json_sha256':sha(oldfile),'array_sha256':sha(npz),'arms':arms,'elapsed_seconds':time.perf_counter()-started})
        completed.append({'key':stem,'json_sha256':sha(js),'npz_sha256':sha(npz)});(D/'run_status.json').write_text(json.dumps({'status':'running','completed':completed},indent=2),encoding='utf-8');print('precision',len(completed),'/15',stem,flush=True)
pd.DataFrame(rows).to_csv(D/'arm_path.csv',index=False)
pd.DataFrame(rows).groupby(['dataset','method']).agg(paths=('path','size'),delta_vs_full=('delta_vs_full','mean'),mean_loss_percent=('loss_percent','mean'),delta_vs_default=('delta_vs_default','mean'),same_order_as_default=('same_order_as_default','sum'),same_set_as_default=('same_set_as_default','sum')).reset_index().to_csv(D/'summary.csv',index=False)
(D/'run_status.json').write_text(json.dumps({'status':'complete','conditions':15,'arms':30,'completed':completed},indent=2),encoding='utf-8');print((D/'summary.csv').read_text())
