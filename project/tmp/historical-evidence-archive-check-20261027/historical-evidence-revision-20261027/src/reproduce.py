"""Verify frozen inputs, replay selected conditions, regenerate analyses in a copy.

No writes to --base. Use a fresh --output for every invocation.
"""
import os
for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMBA_NUM_THREADS'):
    os.environ[name] = '1'
import argparse, hashlib, importlib.metadata, json, platform, shutil, subprocess, sys
from pathlib import Path
import numpy as np
import pandas as pd
import networkx as nx
from PIL import Image

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def dump(p, value): Path(p).write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--base', type=Path, required=True)
ap.add_argument('--output', type=Path, required=True)
ap.add_argument('--replay', choices=['none', 'representative', 'all'], default='representative')
args = ap.parse_args()
B, O = args.base.resolve(), args.output.resolve()
if O == B or B in O.parents and 'results' in O.relative_to(B).parts:
    raise ValueError('Never write into the frozen result tree')
O.mkdir(parents=True, exist_ok=False)
report = {'status':'running', 'replay_scope':args.replay, 'python':sys.version,
          'platform':platform.platform(), 'packages':{}, 'replayed':[], 'regenerated':[]}
for package in ('numpy','pandas','scipy','networkx','matplotlib','numba','llvmlite','psutil','Pillow'):
    report['packages'][package] = importlib.metadata.version(package)
# Copy the engine as well: Numba's cache is written only in this new workspace.
shutil.copytree(B/'snapshot', O/'engine', ignore=shutil.ignore_patterns('__pycache__'))
sys.path.insert(0,str(O/'engine'))
import engine
import run_experiment as runner

try:
    manifest = runner.verify(B)
    cfg = read(B/'config.json')
    expected = {runner.key(c):c for c in runner.condition_matrix(cfg)}
    status = read(B/'results/main/run_status.json')
    assert status['status']=='complete'
    assert {c['key'] for c in status['completed']} == set(expected)
    assert len(status['completed']) == len(expected) == 54
    conditions = B/'results/main/conditions'
    assert {p.stem for p in conditions.glob('*.json')} == set(expected)
    assert {p.stem for p in conditions.glob('*.npz')} == set(expected)
    graphs = {}
    for ds, m in read(B/'data/source_manifest.json')['datasets'].items():
        assert sha(B/'data/raw/snap'/m['source_filename']) == m['source_sha256']
        graphs[ds] = engine.load_external_graph(B/'data/raw/snap',ds)
        assert graphs[ds]['metadata']['graph_sha256'] == m['graph_sha256']
    arm_count = 0
    for entry in status['completed']:
        key = entry['key']; js = conditions/(key+'.json'); npz = js.with_suffix('.npz')
        assert sha(js)==entry['json_sha256'] and sha(npz)==entry['npz_sha256']
        r=read(js); c=r['config']; g=graphs[c['dataset']]
        assert c == expected[key] and r['array_sha256']==sha(npz)
        assert r['source_manifest_sha256']==manifest
        assert r['graph']['graph_sha256']==g['metadata']['graph_sha256']
        ids=engine.world_ids(c['dataset'],c['path'],'selection',c['W'],cfg['namespace'])
        ev=engine.world_ids(c['dataset'],c['path'],'evaluation',10000,cfg['namespace'])
        longer=engine.world_ids(c['dataset'],c['path'],'selection',1280,cfg['namespace'])
        assert np.array_equal(ids,longer[:c['W']]) and not set(ids)&set(ev)
        assert hashlib.sha256(ids.tobytes()).hexdigest()==r['selection_world_sha256']
        assert hashlib.sha256(ev.tobytes()).hexdigest()==r['evaluation_world_sha256']
        candidates=runner.arms_for(g,c,cfg)
        assert set(candidates)==set(r['arms'])
        with np.load(npz) as z:
            fv=z['full_evaluation']
            assert fv.shape==(10000,)
            for name,a in r['arms'].items():
                arm_count+=1
                pool=[g['nodes'][i] for i in sorted(candidates[name])]
                assert pool==a['candidate_ids']
                assert a['candidate_count']==len(pool)
                totals=z[name+'_round_totals']
                assert totals.shape==(5,len(pool))
                assert [pool[int(np.argmax(row))] for row in totals]==a['selected']
                val=z[name+'_evaluation']; diff=val-fv
                assert val.shape==(10000,) and np.issubdtype(val.dtype,np.integer)
                assert np.all((val>=5)&(val<=len(g['nodes'])))
                for field,value in [('mean_spread',val.mean()),('incremental_spread',val.mean()-5),
                                    ('delta',diff.mean()),('mc_se',diff.std(ddof=1)/100)]:
                    assert np.isclose(a[field],value,rtol=0,atol=1e-12),(key,name,field)
                if set(a['selected'])==set(r['arms']['full']['selected']):
                    assert np.array_equal(val,fv)
    report.update(conditions_checked=54, arms_checked=arm_count, source_manifest_sha256=manifest,
                  graph_hashes={d:g['metadata']['graph_sha256'] for d,g in graphs.items()})
    assert arm_count==468
    dump(O/'verification.json',report)
    print('PASS: source/data hashes, 54 conditions, 468 arms, worlds, candidates, totals and statistics',flush=True)

    # Predetermined coverage: all three networks at W80/step; all three W320/edge.
    selected = [c for c in expected.values() if args.replay=='all' or
                args.replay=='representative' and c['path']==1101 and
                (c['W']==80 or c['coupling']=='edge')]
    if selected:
        engine.warmup(); replay=O/'replay'; replay.mkdir()
        for c in selected:
            key=runner.key(c)
            runner.run_condition(B,replay,cfg,graphs[c['dataset']],c,manifest)
            with np.load(replay/'conditions'/(key+'.npz')) as a, np.load(conditions/(key+'.npz')) as b:
                assert set(a.files)==set(b.files)
                assert all(np.array_equal(a[n],b[n]) for n in a.files),key
            old=read(conditions/(key+'.json')); new=read(replay/'conditions'/(key+'.json'))
            assert all(old['arms'][n]['selected']==new['arms'][n]['selected'] for n in old['arms'])
            report['replayed'].append({'condition':key,'arrays_exact':True,'arms':len(old['arms'])})
            dump(O/'verification.json',report)
            print('REPLAY PASS: '+key,flush=True)

    # Check all post-hoc arrays; representative replays cover both precision protocols.
    report['strict_replayed']=[]
    strict_count=0
    for folder in (B/'review-v2/supplement-pr-precision',
                   B/'review-v3-budget-precision/supplement-pr-budget-precision'):
        st=read(folder/'run_status.json')
        assert st['status']=='complete'
        for entry in st['completed']:
            js=folder/'conditions'/(entry['key']+'.json'); npz=js.with_suffix('.npz')
            assert sha(js)==entry['json_sha256'] and sha(npz)==entry['npz_sha256']
            r=read(js); ds=r['dataset']; path=r['path']; W=r['W']; g=graphs[ds]
            with np.load(npz) as z, np.load(conditions/f'resolution__{ds}__p{path}__w{W}__step.npz') as fz:
                for name,a in r['arms'].items():
                    strict_count+=1; values=z[name+'_evaluation']; difference=values-fz['full_evaluation']
                    assert np.isclose(a['delta_vs_full'],difference.mean(),rtol=0,atol=1e-12)
                    assert np.isclose(a['mc_se_vs_full'],difference.std(ddof=1)/100,rtol=0,atol=1e-12)
                if not (args.replay=='all' or args.replay=='representative' and path==1101 and W in (80,1280)):
                    continue
                graph=nx.DiGraph(); nodes=g['nodes']; graph.add_nodes_from(nodes)
                graph.add_edges_from((nodes[int(s)],nodes[int(t)]) for s,t in zip(g['sources'],g['targets']))
                ranks=[]
                for tolerance in (1e-12,1e-14):
                    scores=nx.pagerank(graph,alpha=.85,tol=tolerance,max_iter=1000,weight=None)
                    ranks.append(np.asarray(sorted(range(len(nodes)),key=lambda i:(-scores[nodes[i]],nodes[i])),dtype=np.int64))
                ids=engine.world_ids(ds,path,'selection',W,cfg['namespace'])
                eid=engine.world_ids(ds,path,'evaluation',10000,cfg['namespace'])
                worlds=engine.make_worlds(ids,g['sources'],g['targets'],.01,3,False)
                generated={}
                for name,a in r['arms'].items():
                    size=len(a['candidate_ids']); pool=ranks[0][:size]
                    assert set(pool)==set(ranks[1][:size])
                    assert [nodes[i] for i in sorted(pool)]==a['candidate_ids']
                    seeds,totals=engine.greedy(g['indptr'],g['targets'],worlds,pool,5,3)
                    assert [nodes[i] for i in seeds]==a['selected']
                    assert np.array_equal(totals,z[name+'_round_totals'])
                    values=[]
                    for offset in range(0,10000,256):
                        ew=engine.make_worlds(eid[offset:offset+256],g['sources'],g['targets'],.01,3,False)
                        values.append(engine.evaluate(g['indptr'],g['targets'],ew,seeds,3))
                    values=np.concatenate(values)
                    assert np.array_equal(values,z[name+'_evaluation'])
                    generated[name+'_evaluation']=values; generated[name+'_round_totals']=totals
                strict_dir=O/'strict-replay'; strict_dir.mkdir(exist_ok=True)
                np.savez_compressed(strict_dir/(entry['key']+'.npz'),**generated)
                report['strict_replayed'].append({'condition':entry['key'],'arms':2,'arrays_exact':True})
                dump(O/'verification.json',report)
                print('STRICT REPLAY PASS: '+entry['key'],flush=True)
    assert strict_count==90
    report['strict_arms_checked']=strict_count

    # Preserve legacy path assumptions in a disposable tree, never run old generators in situ.
    T=O/'workspace'; T.mkdir()
    for name in ('snapshot','results/main','data'):
        shutil.copytree(B/name,T/name,ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy2(B/'config.json',T/'config.json')
    for name in ('review-v2','review-v3-budget-precision'):
        (T/name/'src').mkdir(parents=True)
        (T/name/'analysis').mkdir()
    for script in ('analyze.py','make_figures.py'):
        shutil.copy2(B/'review-v2/src'/script,T/'review-v2/src'/script)
    shutil.copy2(B/'review-v2/analysis/supplement_setup_timing.csv',T/'review-v2/analysis/supplement_setup_timing.csv')
    shutil.copytree(B/'review-v2/supplement-pr-precision',T/'review-v2/supplement-pr-precision')
    shutil.copytree(B/'review-v3-budget-precision/supplement-pr-budget-precision',T/'review-v3-budget-precision/supplement-pr-budget-precision')
    shutil.copy2(B/'review-v3-budget-precision/src/analyze_precision_budget.py',T/'review-v3-budget-precision/src/analyze_precision_budget.py')
    for script in ('review-v2/src/analyze.py','review-v2/src/make_figures.py',
                   'review-v3-budget-precision/src/analyze_precision_budget.py'):
        with (O/(Path(script).stem+'.log')).open('w',encoding='utf-8') as log:
            subprocess.run([sys.executable,str(T/script)],check=True,stdout=log,stderr=subprocess.STDOUT)
    for root in ('review-v2/analysis','review-v3-budget-precision/analysis/precision_budget'):
        for p in sorted((T/root).rglob('*')):
            if p.suffix not in ('.csv','.png'): continue
            ref=B/p.relative_to(T)
            assert ref.exists(),str(ref)
            if p.suffix=='.csv':
                pd.testing.assert_frame_equal(pd.read_csv(p),pd.read_csv(ref),check_exact=False,rtol=1e-12,atol=1e-12)
                criterion='numeric/text table equality; numerical tolerance 1e-12'
            else:
                assert np.array_equal(np.asarray(Image.open(p)),np.asarray(Image.open(ref))),str(p)
                criterion='exact decoded pixels'
            report['regenerated'].append({'file':str(p.relative_to(T)),'criterion':criterion,'sha256':sha(p)})
    report['status']='PASS'
    print('PASS: '+str(len(report['regenerated']))+' regenerated CSV/PNG artifacts',flush=True)
except Exception as exc:
    report['status']='FAIL'; report['error']=repr(exc)
    raise
finally:
    dump(O/'verification.json',report)
