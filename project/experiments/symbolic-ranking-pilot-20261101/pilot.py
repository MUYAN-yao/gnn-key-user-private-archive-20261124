import os,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'vendor'))
os.environ['NUMBA_CACHE_DIR']=str(BASE/'numba_cache')
import json,time,hashlib,platform,importlib.metadata as md
import numpy as np,pandas as pd,networkx as nx
from scipy import sparse
import engine as en
PROJECT=BASE.parent.parent
RAW=PROJECT/'submission/computing-external-validation-20261015/data/raw/snap'
def dump(name,obj): (BASE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)),encoding='utf-8')
def ids(g,path,fam,n): return en.world_ids(g['name'],path,fam,n,'symbolic-ranking-pilot-20261101-v1')
def worlds(g,path,fam,n): return en.make_worlds(ids(g,path,fam,n),g['sources'],g['targets'],.01,3,False)
def ev(g,ww,seeds): return en.evaluate(g['indptr'],g['targets'],ww,np.array(seeds,dtype=np.int64),3)
def select(g,ww,cs): return en.greedy(g['indptr'],g['targets'],ww,np.array(cs,dtype=np.int64),5,3)
def real(name):
 g=en.load_external_graph(RAW,name);g['name']=name; return g
def preflight():
 t=time.perf_counter();en.warmup();rows=[]
 for name in ['college_msg','ca_grqc','wiki_vote']:
  g=real(name);t0=time.perf_counter();ww=worlds(g,4000,'preflight-select',80);prep=time.perf_counter()-t0
  t0=time.perf_counter();s,_=select(g,ww,range(len(g['nodes'])));full=time.perf_counter()-t0
  t0=time.perf_counter();select(g,ww,g['rankings']['pagerank'][:20]);rest=time.perf_counter()-t0
  t0=time.perf_counter();we=worlds(g,4000,'preflight-eval',400);ev(g,we,s);evaluation=time.perf_counter()-t0
  rows.append(dict(graph=name,n=len(g['nodes']),edges=len(g['targets']),prep80=prep,full80=full,restricted80=rest,eval400=evaluation))
  print(rows[-1],flush=True)
 dump('preflight.json',dict(seconds=time.perf_counter()-t,rows=rows,outcome_blind=True))
 dump('environment.json',dict(python=sys.version,executable=sys.executable,platform=platform.platform(),versions={p:md.version(p) for p in ['numpy','scipy','pandas','networkx','scikit-learn','matplotlib','numba','llvmlite']}))
if __name__=='__main__': preflight()

# Full experiment functions. Run with run.py after the saved preflight.
def synthetic(family,i):
 n=[160,240,320][i];seed=6100+i
 if family=='ER': h=nx.gnp_random_graph(n,8/(n-1),seed=seed)
 elif family=='BA': h=nx.barabasi_albert_graph(n,4,seed=seed)
 elif family=='SBM': h=nx.stochastic_block_model([n//2,n//2],[[.06,.006],[.006,.06]],seed=seed)
 else: h=nx.watts_strogatz_graph(n,8,.12,seed=seed)
 nodes=sorted(map(str,h.nodes()));adj={u:sorted(map(str,h.neighbors(int(u)))) for u in nodes}
 ptr,targets,sources=en.csr(nodes,adj)
 return dict(name=f'{family}_{i}',nodes=nodes,indptr=ptr,targets=targets,sources=sources,metadata=dict(family=family,generator_seed=seed,n=n,m=len(targets),graph_sha256=hashlib.sha256(ptr.tobytes()+targets.tobytes()).hexdigest()))
def split(name):
 if name in ['ca_grqc','wiki_vote'] or name.startswith(('SBM','WS')):return 'test'
 if name in ['ER_2','BA_2']:return 'validation'
 return 'train'
def pagerank(g,tol):
 t=time.perf_counter();n=len(g['nodes']);degree=np.diff(g['indptr']);P=sparse.csr_matrix((np.repeat(1/np.maximum(degree,1),degree),g['targets'],g['indptr']),shape=(n,n))
 x=np.full(n,1/n)
 def step(x):return .85*(x@P + x[degree==0].sum()/n)+.15/n
 for it in range(1,10001):
  z=step(x);diff=np.abs(z-x).sum();x=z
  if diff<n*tol:break
 else:raise RuntimeError('PR not converged')
 residual=float(np.abs(step(x)-x).sum());order=np.lexsort((np.arange(n),-x))
 return x,order,residual,it,time.perf_counter()-t

def jacc(a,b):return len(set(a)&set(b))/len(set(a)|set(b))
def experiment():
 start=time.perf_counter(); cfg=json.loads((BASE/'config.json').read_text(encoding='utf-8-sig')); prrows=[];runs=[];rounds=[];metas=[];features=[];timings=[]
 manifest={}
 for p in [*RAW.glob('*.gz'), PROJECT/'submission/computing-external-validation-20261015/snapshot/engine.py',PROJECT/'submission/computing-external-validation-20261015/snapshot/legacy_engine.py',PROJECT/'docs/research/symbolic-ranking-20261031/research-question-card.md']:
  manifest[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 dump('readonly-input-manifest.json',manifest)
 graphnames=['college_msg','ca_grqc','wiki_vote']+[f'{f}_{i}' for f in ['ER','BA','SBM','WS'] for i in range(3)]
 for name in graphnames:
  if time.perf_counter()-start>3000:raise RuntimeError('50 minute early stop')
  gt=time.perf_counter();g=real(name) if '_' in name and name in ['college_msg','ca_grqc','wiki_vote'] else synthetic(*[name.split('_')[0],int(name.split('_')[1])]);n=len(g['nodes']); isreal=name in ['college_msg','ca_grqc','wiki_vote']
  if isreal:
   frozen=json.loads((PROJECT/'submission/computing-external-validation-20261015/data/source_manifest.json').read_text(encoding='utf-8'))['datasets'][name]
   for key in ['source_sha256','graph_sha256','n','m']:assert g['metadata'][key]==frozen[key],(name,key)
  (BASE/'raw').mkdir(exist_ok=True);np.savez_compressed(BASE/'raw'/f'{name}_graph.npz',indptr=g['indptr'],targets=g['targets'],sources=g['sources'],nodes=g['nodes'])
  xr,rankr,rr,ir,tr=pagerank(g,1e-14);xf,rankf,rf,iff,tf=pagerank(g,1e-15);cs=rankr[:20]
  refcheck=dict(residual14=rr,residual15=rf,maxdiff14_15=float(np.max(np.abs(xr-xf))),pool20_stable=set(cs)==set(rankf[:20]),pool5pct_stable=set(rankr[:int(np.ceil(.05*n))])==set(rankf[:int(np.ceil(.05*n))]))
  assert refcheck['pool20_stable'],'reference candidate pool unstable'
  degree=np.diff(g['indptr']);cv=float(degree.std()/max(degree.mean(),1e-10));g['metadata'].update(name=name,split=split(name),degree_cv=cv,reference_check=refcheck);metas.append(g['metadata'])
  prcache={}
  for tol in cfg['tols']:
   x,rank,res,it,secs=pagerank(g,tol);prcache[tol]=rank
   for m in sorted(set([20,int(np.ceil(.05*n))])):
    gap=float(x[rank[m-1]]-x[rank[m]]);eps=res/.15;near=int(np.sum(np.abs(x-x[rank[m-1]])<=2*eps));a=set(rank[:m]);b=set(rankr[:m])
    prrows.append(dict(graph=name,split=split(name),tol=tol,m=m,residual=res,iterations=it,seconds=secs,gap=gap,epsilon=eps,ratio=2*eps/max(gap,1e-300),certified=gap>2*eps,near=near,replacements=len(a-b),jaccard=jacc(a,b),actual_max_error=float(np.max(np.abs(x-xf)))))
  # Independent pilot. Candidate pair selected on pilot, never called an unbiased population gap.
  pt=time.perf_counter();wp=worlds(g,4099,'pilot',160);pv=np.array([ev(g,wp,[c]) for c in cs]);po=np.lexsort((cs,-pv.mean(axis=1)));u,v=cs[po[:2]];d=pv[po[0]]-pv[po[1]];gap=abs(float(d.mean()));sd=float(d.std(ddof=1));nu=set(g['targets'][g['indptr'][u]:g['indptr'][u+1]]);nv=set(g['targets'][g['indptr'][v]:g['indptr'][v+1]]);overlap=len(nu&nv)/max(len(nu|nv),1);pilotsec=time.perf_counter()-pt
  np.savez_compressed(BASE/'raw'/f'{name}_pilot.npz',candidate_ids=cs,values=pv,world_ids=ids(g,4099,'pilot',160))
  features.append(dict(graph=name,gap=gap,paired_sd=sd,overlap=overlap,cv=cv,pilot_seconds=pilotsec,feature_scope='independent pilot; top-two selected on pilot'))
  del wp
  local=[]
  def addrun(arm,path,W,ww,candidates,family):
   t0=time.perf_counter();seeds,totals=select(g,ww,candidates);secs=time.perf_counter()-t0;candidates=np.sort(candidates)
   rec=dict(graph=name,split=split(name),arm=arm,path=path,W=W,seeds=list(map(int,seeds)),seconds=secs,x=float(np.log1p(sd/(np.sqrt(W)*max(gap,1/160)))),o=overlap,c=cv/(1+cv));local.append(rec)
   stage=[]
   for r in range(5):
    valid=np.flatnonzero(totals[r]>=0);order=valid[np.lexsort((candidates[valid],-totals[r,valid]))];a,b=order[:2];sa=list(seeds[:r])+[candidates[a]];sb=list(seeds[:r])+[candidates[b]];da=ev(g,ww,sa)-ev(g,ww,sb)
    stage.append(dict(round=r+1,winner=int(candidates[a]),runner=int(candidates[b]),margin=float(da.mean()),paired_sd=float(da.std(ddof=1)),paired_se=float(da.std(ddof=1)/np.sqrt(W)),ties=int(np.sum(totals[r]==totals[r,a]))))
   for st in stage: rounds.append({k:rec[k] for k in ['graph','arm','path','W']}|st)
   np.savez_compressed(BASE/'raw'/f'{name}_{arm}_{path}_{W}.npz',seeds=seeds,totals=totals,candidates=candidates,world_ids=ids(g,path,family,W))
   return rec
  wr=worlds(g,4999,'reference',1280);reference=addrun('reference',4999,1280,wr,cs,'reference');del wr
  for path in cfg['paths']:
   ww=worlds(g,path,'selection',max(cfg['W']))
   for W in cfg['W']:
    addrun('restricted',path,W,ww[:W],cs,'selection')
    if isreal and path in cfg['full_paths']:addrun('full',path,W,ww[:W],np.arange(n),'selection')
   if isreal and path==4101:
    for tol,label in [(1e-6,'pr_default'),(1e-14,'pr_reference')]:
     addrun(label,path,320,ww[:320],prcache[tol][:20] if tol!=1e-14 else cs,'selection')
   del ww
  # Shared independent evaluation IDs, disjoint from all selection/pilot/reference IDs.
  evaluation_ids=ids(g,4001,'eval',cfg['evaluation_worlds'])
  for fam,path in [('reference',4999),('pilot',4099)]+[('selection',p) for p in cfg['paths']]:assert not set(map(int,evaluation_ids))&set(map(int,ids(g,path,fam,1280)))
  uniques={tuple(sorted(r['seeds'])) for r in local};values={s:[] for s in uniques};et=time.perf_counter()
  for lo in range(0,cfg['evaluation_worlds'],400):
   we=en.make_worlds(evaluation_ids[lo:lo+400],g['sources'],g['targets'],.01,3,False)
   for s in uniques:values[s].append(ev(g,we,s))
  values={s:np.concatenate(v) for s,v in values.items()};ref=values[tuple(sorted(reference['seeds']))]
  for r in local:
   vv=values[tuple(sorted(r['seeds']))];delta=vv-ref;se=float(delta.std(ddof=1)/np.sqrt(len(delta)));r.update(instability=1-jacc(r['seeds'],reference['seeds']),same_order=r['seeds']==reference['seeds'],spread=float(vv.mean()),spread_se=float(vv.std(ddof=1)/np.sqrt(len(vv))),delta_reference=float(delta.mean()),delta_se=se,ci_low=float(delta.mean()-1.96*se),ci_high=float(delta.mean()+1.96*se));runs.append(r)
  arrays={f'set_{i}':values[s] for i,s in enumerate(sorted(uniques))};arrays['world_ids']=evaluation_ids
  np.savez_compressed(BASE/'raw'/f'{name}_evaluation.npz',**arrays);dump(f'raw/{name}_evaluation_index.json',{f'set_{i}':s for i,s in enumerate(sorted(uniques))})
  timings.append(dict(graph=name,seconds=time.perf_counter()-gt,pilot_seconds=pilotsec,evaluation_seconds=time.perf_counter()-et,distinct_evaluated_sets=len(uniques)))
  for fn,data in [('pagerank.csv',prrows),('runs.csv',runs),('rounds.csv',rounds),('features.csv',features),('timings.csv',timings)]:pd.DataFrame(data).to_csv(BASE/fn,index=False,encoding='utf-8-sig')
  dump('graphs.json',metas);print('COMPLETE',name,'seconds',round(time.perf_counter()-gt,2),flush=True)
 for p,sha in manifest.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha
 dump('execution_status.json',dict(status='COMPLETE',graphs=len(metas),seconds=time.perf_counter()-start,readonly_hashes_unchanged=True))
