"""Frozen, resumable, serial nine-arm extension runner."""
from __future__ import annotations
import argparse,json,time,hashlib,os,sys,platform
from pathlib import Path
import numpy as np
import engine

REAL=['invs2013','invs2015','kenya2012','sfhh2009']

def matrix():
    rows=[]
    def add(stage,datasets,paths,Ws,k,phs,coupling):
        for dataset in datasets:
            for path in paths:
                for p,h in phs:
                    for W in Ws:
                        rows.append(dict(stage=stage,dataset=dataset,path=path,W=W,k=k,p=p,h=h,coupling=coupling))
    add('resolution',REAL,range(1001,1011),[20,80,320,1280,5120],5,[(.01,3)],'step')
    add('seed_budget',REAL[:3],range(1001,1011),[320,1280],20,[(.01,3)],'step')
    add('parameters',REAL,range(1001,1011),[320],5,[(.005,3),(.05,3),(.01,1),(.01,5)],'step')
    add('coupling',REAL,range(1001,1011),[320,1280],5,[(.01,3)],'edge')
    add('scale',['synthetic_ba2000','synthetic_sbm2000'],range(1001,1006),[80,320],5,[(.01,3)],'step')
    assert len(rows)==520
    return rows

def key(c):
    return f"{c['stage']}-{c['dataset']}-k{c['k']}-p{c['p']}-h{c['h']}-{c['coupling']}-path{c['path']}-w{c['W']}"

def jsonwrite(path,content,exclusive=False):
    path.parent.mkdir(parents=True,exist_ok=True)
    if exclusive:
        with path.open('x',encoding='utf-8') as f:json.dump(content,f,indent=2)
    else:
        tmp=path.with_suffix('.tmp')
        tmp.write_text(json.dumps(content,indent=2),encoding='utf-8');tmp.replace(path)

def verify_source(base):
    manifest=json.loads((base/'source_manifest.json').read_text())
    for name,sha in manifest['files'].items():
        if engine.digest(base/name)!=sha:raise ValueError('changed frozen source: '+name)
    return engine.digest(base/'source_manifest.json')

def seed_integer(text):
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8],'big')

def arms_for(g,c):
    n=len(g['nodes']);k=c['k']
    arms={'full':np.arange(n,dtype=np.int64)};ranktimes={'full':0.}
    for factor in [2,4,8]:
        name=f'weighted_{factor}k';arms[name]=g['rankings']['weighted'][:min(n,factor*k)];ranktimes[name]=g['ranking_seconds']['weighted']
    for name in ['degree','pagerank']:
        arms[name+'_4k']=g['rankings'][name][:min(n,4*k)];ranktimes[name+'_4k']=g['ranking_seconds'][name]
    for repeat in range(3):
        t=time.perf_counter();name=f'random{repeat}_4k'
        rng=np.random.default_rng(seed_integer(f"pool|{c['dataset']}|{c['path']}|{repeat}"))
        arms[name]=rng.permutation(n)[:min(n,4*k)];ranktimes[name]=time.perf_counter()-t
    return arms,ranktimes

def run(g,c,source_hash,out):
    start=time.perf_counter();n=len(g['nodes'])
    select_ids=engine.world_ids(c['dataset'],c['path'],'selection',c['W'])
    eval_ids=engine.world_ids(c['dataset'],c['path'],'evaluation',10000)
    assert len(set(select_ids))==len(select_ids) and len(set(eval_ids))==len(eval_ids)
    assert not set(select_ids)&set(eval_ids)
    t=time.perf_counter()
    worlds=engine.make_worlds(select_ids,g['sources'],g['targets'],c['p'],c['h'],c['coupling']=='edge')
    evalworlds=engine.make_worlds(eval_ids,g['sources'],g['targets'],c['p'],c['h'],c['coupling']=='edge')
    world_seconds=time.perf_counter()-t
    candidates,ranking_seconds=arms_for(g,c)
    order=list(candidates);np.random.default_rng(seed_integer('order|'+key(c))).shuffle(order)
    arrays={};arms={}
    for name in order:
        t=time.perf_counter()
        selected,scores=engine.greedy(g['indptr'],g['targets'],worlds,candidates[name],c['k'],c['h'])
        sel_time=time.perf_counter()-t
        t=time.perf_counter();values=engine.evaluate(g['indptr'],g['targets'],evalworlds,selected,c['h']);evtime=time.perf_counter()-t
        arrays[name+'_evaluation']=values;arrays[name+'_round_totals']=scores
        trace=[]
        for r,score in enumerate(scores):
            ordered=np.sort(score[score>=0])[::-1]
            trace.append(dict(winner=g['nodes'][selected[r]],total=int(ordered[0]),ties=int(np.sum(score==ordered[0])),margin=float((ordered[0]-ordered[1])/c['W']) if len(ordered)>1 else None))
        arms[name]=dict(selected=[g['nodes'][i] for i in selected],candidate_ids=[g['nodes'][i] for i in sorted(candidates[name])],candidate_count=len(candidates[name]),coverage=len(candidates[name])/n,full_pool=len(candidates[name])==n,mean_spread=float(values.mean()),incremental_spread=float(values.mean()-c['k']),selection_seconds=sel_time,evaluation_seconds=evtime,ranking_seconds=ranking_seconds[name],trace=trace)
    for name,arm in arms.items():
        d=arrays[name+'_evaluation']-arrays['full_evaluation']
        arm['delta']=float(d.mean());arm['mc_se']=float(d.std(ddof=1)/np.sqrt(len(d)))
        arm['same_order']=arm['selected']==arms['full']['selected'];arm['same_set']=set(arm['selected'])==set(arms['full']['selected'])
        assert not arm['full_pool'] or arm['same_order']
        assert np.all(arrays[name+'_evaluation']>=c['k']) and np.all(arrays[name+'_evaluation']<=n)
    repeated=[]
    if c['stage']=='resolution' and c['path']==1001 and c['W']==320:
        for rep in range(5):
            order2=list(candidates);np.random.default_rng(seed_integer('timing|'+key(c)+f'|{rep}')).shuffle(order2)
            for name in order2:
                t=time.perf_counter();sel,_=engine.greedy(g['indptr'],g['targets'],worlds,candidates[name],c['k'],c['h']);st=time.perf_counter()-t
                t=time.perf_counter();v=engine.evaluate(g['indptr'],g['targets'],evalworlds,sel,c['h']);et=time.perf_counter()-t
                assert [g['nodes'][i] for i in sel]==arms[name]['selected'] and np.array_equal(v,arrays[name+'_evaluation'])
                repeated.append(dict(repeat=rep,method=name,selection_seconds=st,evaluation_seconds=et,order=order2.index(name)))
    directory=out/'conditions';directory.mkdir(exist_ok=True)
    npz=directory/(key(c)+'.npz');jp=directory/(key(c)+'.json')
    if npz.exists() or jp.exists():raise FileExistsError(key(c))
    with npz.open('xb') as f:np.savez_compressed(f,**arrays)
    import psutil
    report=dict(config=c,source_manifest_sha256=source_hash,graph=g['metadata'],selection_world_sha256=hashlib.sha256(select_ids.tobytes()).hexdigest(),evaluation_world_sha256=hashlib.sha256(eval_ids.tobytes()).hexdigest(),evaluation_world_count=10000,preparation_seconds=g['preparation_seconds'],world_preparation_seconds=world_seconds,order=order,arms=arms,timing_repeats=repeated,array_sha256=engine.digest(npz),elapsed_seconds=time.perf_counter()-start,peak_working_set_bytes=getattr(psutil.Process().memory_info(),'peak_wset',None))
    jsonwrite(jp,report,True)
    return dict(key=key(c),json_sha256=engine.digest(jp),npz_sha256=engine.digest(npz),elapsed_seconds=report['elapsed_seconds'])

def main():
    p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    base=Path(__file__).resolve().parent
    source_hash=verify_source(base)
    config=json.loads((base/'config.json').read_text());assert config['conditions']==matrix()
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    manifest_path=out/'manifest.json'
    if manifest_path.exists():
        manifest=json.loads(manifest_path.read_text());assert manifest['source_manifest_sha256']==source_hash
        for r in manifest['runs']:
            assert engine.digest(out/'conditions'/(r['key']+'.json'))==r['json_sha256']
            assert engine.digest(out/'conditions'/(r['key']+'.npz'))==r['npz_sha256']
    else:
        manifest=dict(status='RUNNING',source_manifest_sha256=source_hash,expected_conditions=len(matrix()),started_epoch=time.time(),runs=[],python=sys.version,platform=platform.platform())
    completed={r['key'] for r in manifest['runs']}
    engine.warmup();graphs={}
    try:
        for c in matrix():
            if key(c) in completed:continue
            if c['dataset'] not in graphs:graphs[c['dataset']]=engine.load_graph(args.project,c['dataset'])
            row=run(graphs[c['dataset']],c,source_hash,out)
            manifest['runs'].append(row);manifest['status']='RUNNING';jsonwrite(manifest_path,manifest)
            print(json.dumps(dict(completed=len(manifest['runs']),expected=len(matrix()),**row)),flush=True)
        assert len(manifest['runs'])==len(matrix());verify_source(base)
        manifest['status']='COMPLETE';manifest['completed_epoch']=time.time();jsonwrite(manifest_path,manifest)
    except BaseException as exc:
        manifest['status']='INTERRUPTED';manifest['error']=repr(exc);jsonwrite(manifest_path,manifest);raise

if __name__=='__main__':main()
