"""Recompute all statistics directly from immutable per-world NPZ arrays."""
from pathlib import Path
import json,sys,hashlib,platform
import numpy as np
import pandas as pd
from scipy.stats import binomtest,t
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'review-v2/analysis';OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'snapshot'));import engine
cfg=json.loads((ROOT/'config.json').read_text());setup=pd.read_csv(OUT/'supplement_setup_timing.csv').groupby(['dataset','method']).median(numeric_only=True)
rows=[];repeats=[];raw={};direction=[]
def stats(v):
    v=np.asarray(v,dtype=float);se=float(v.std(ddof=1)/np.sqrt(len(v)))
    return dict(delta=float(v.mean()),mc_se=se,mc_lo=float(v.mean()-1.96*se),mc_hi=float(v.mean()+1.96*se))
for js in sorted((ROOT/'results/main/conditions').glob('*.json')):
    r=json.loads(js.read_text());c=r['config'];z=np.load(js.with_suffix('.npz'));full=r['arms']['full'];fv=z['full_evaluation'];common={k:c[k] for k in ['stage','dataset','path','W','coupling']}
    means={};armrows=[]
    for name,a in r['arms'].items():
        val=z[name+'_evaluation'].astype(float);diff=val-fv;s=set(a['selected']);f=set(full['selected'])
        m=stats(diff); first=next((i+1 for i,(u,v) in enumerate(zip(a['selected'],full['selected'])) if u!=v),0)
        setupname='random_mean_4k' if name.startswith('random') else name;su=float(setup.loc[(c['dataset'],setupname),'setup_seconds'])
        deploy=su+r['selection_world_preparation_seconds']+a['selection_seconds'];verified=deploy+r['evaluation_world_preparation_seconds']+a['evaluation_seconds']
        row={**common,'method':name,'n':r['graph']['n'],'candidate_count':a['candidate_count'],'coverage':a['coverage'],'total_spread':float(val.mean()),'incremental_spread':float(val.mean()-c['k']),'full_incremental_spread':float(fv.mean()-c['k']),**m,'loss_percent':float(-100*diff.mean()/(fv.mean()-c['k'])),'same_order':a['selected']==full['selected'],'same_set':s==f,'jaccard':len(s&f)/len(s|f),'first_divergence':first,'selection_seconds':a['selection_seconds'],'evaluation_seconds':a['evaluation_seconds'],'selection_world_seconds':r['selection_world_preparation_seconds'],'evaluation_world_seconds':r['evaluation_world_preparation_seconds'],'frozen_graph_preparation_seconds':r['preparation_seconds'],'supplement_setup_seconds':su,'deployment_seconds':deploy,'verification_seconds':verified,'peak_working_set_bytes':r['peak_working_set_bytes']}
        rows.append(row);armrows.append(row);means[name]=val
    randomrows=[r for r in armrows if r['method'].startswith('random')];av=np.mean([means[f'random{i}_4k'] for i in range(3)],axis=0)
    rr={**common,'method':'random_mean_4k'}
    for col in [k for k in randomrows[0] if k not in common and k!='method']: rr[col]=float(np.mean([r[col] for r in randomrows]))
    rr.update(stats(av-fv));rr['within_path_random_delta_sd']=float(np.std([r['delta'] for r in randomrows],ddof=1));rr['first_divergence']=np.nan
    rows.append(rr)
    raw[(c['dataset'],c['path'],c['W'],c['coupling'])]=(r,{n:v.copy() for n,v in means.items()})
    repeats.extend([{**common,**x} for x in r['timing_repeats']]);z.close()
df=pd.DataFrame(rows)
for _,ix in df.groupby(['dataset','stage','path','W','coupling']).groups.items():
    group=df.loc[ix];f=group[group.method=='full'].iloc[0]
    for scope in ['selection','deployment','verification']:
        df.loc[ix,scope+'_saving_percent']=100*(1-group[scope+'_seconds']/f[scope+'_seconds'])
df.to_csv(OUT/'arm_path.csv',index=False)
summary=[]
num=['total_spread','incremental_spread','delta','loss_percent','mc_se','coverage','same_order','same_set','jaccard','selection_seconds','deployment_seconds','verification_seconds','selection_saving_percent','deployment_saving_percent','verification_saving_percent']
for keys,g in df[~df.method.str.match(r'random\d')].groupby(['dataset','stage','W','coupling','method']):
    row=dict(zip(['dataset','stage','W','coupling','method'],keys));row['paths']=len(g)
    for col in num: row[col+'_mean']=float(g[col].mean());row[col+'_path_sd']=float(g[col].std(ddof=1))
    se=g.delta.std(ddof=1)/np.sqrt(len(g));q=t.ppf(.975,len(g)-1)
    row.update(path_delta_lo=float(g.delta.mean()-q*se),path_delta_hi=float(g.delta.mean()+q*se),delta_min=float(g.delta.min()),delta_max=float(g.delta.max()))
    summary.append(row)
summ=pd.DataFrame(summary);summ.to_csv(OUT/'summary_by_method.csv',index=False)
primary=[]
for ds in cfg['datasets']:
    tmp=[]
    for method in cfg['analysis']['primary_methods']:
        g=df[(df.dataset==ds)&(df.stage=='resolution')&(df.W==1280)&(df.method==method)];v=g.delta.to_numpy();nonzero=v[v!=0];pval=binomtest(int((nonzero>0).sum()),len(nonzero),.5).pvalue if len(nonzero) else 1.
        tmp.append(dict(dataset=ds,method=method,paths=len(v),nonzero_paths=len(nonzero),zero_paths=int((v==0).sum()),positive_paths=int((v>0).sum()),negative_paths=int((v<0).sum()),mean_delta=float(v.mean()),mean_loss_percent=float(g.loss_percent.mean()),p_raw=float(pval)))
    order=sorted(range(3),key=lambda i:tmp[i]['p_raw']);prev=0
    for j,i in enumerate(order):prev=max(prev,min(1,(3-j)*tmp[i]['p_raw']));tmp[i]['p_holm']=prev
    primary+=tmp
pd.DataFrame(primary).to_csv(OUT/'primary_tests.csv',index=False)
trans=[]
for ds in cfg['datasets']:
    for path in cfg['resolution']['paths']:
        for low,high in [(80,320),(320,1280),(80,1280)]:
            a,az=raw[(ds,path,low,'step')];b,bz=raw[(ds,path,high,'step')];sa=set(a['arms']['full']['selected']);sb=set(b['arms']['full']['selected']);m=stats(bz['full']-az['full'])
            trans.append(dict(dataset=ds,path=path,low=low,high=high,changed=sa!=sb,same_order=a['arms']['full']['selected']==b['arms']['full']['selected'],jaccard=len(sa&sb)/len(sa|sb),**m,relative_incremental_change_percent=100*m['delta']/(az['full'].mean()-cfg['seed_budget'])))
tr=pd.DataFrame(trans);tr.to_csv(OUT/'full_reference_transitions.csv',index=False)
tr.groupby(['dataset','low','high']).agg(paths=('path','size'),changed=('changed','sum'),mean_delta=('delta','mean'),delta_sd=('delta','std'),min_delta=('delta','min'),max_delta=('delta','max'),mean_jaccard=('jaccard','mean')).reset_index().to_csv(OUT/'transition_summary.csv',index=False)
couple=[]
for ds in cfg['datasets']:
    for path in cfg['fixed_edge_control']['paths']:
        a,az=raw[(ds,path,320,'step')];b,bz=raw[(ds,path,320,'edge')]
        for method in az:
            couple.append(dict(dataset=ds,path=path,method=method,**stats(bz[method]-az[method]),same_order=a['arms'][method]['selected']==b['arms'][method]['selected'],same_set=set(a['arms'][method]['selected'])==set(b['arms'][method]['selected'])))
pd.DataFrame(couple).to_csv(OUT/'coupling_transitions.csv',index=False)
rep=pd.DataFrame(repeats);rep.to_csv(OUT/'timing_repeats.csv',index=False)
rep.groupby(['dataset','method']).agg(repeats=('repeat','size'),selection_median=('selection_seconds','median'),selection_min=('selection_seconds','min'),selection_max=('selection_seconds','max'),evaluation_median=('evaluation_seconds','median')).reset_index().to_csv(OUT/'timing_summary.csv',index=False)
tol=[]
for (ds,W,meth),g in df[(df.stage=='resolution')&(~df.method.str.match(r'random\d'))].groupby(['dataset','W','method']):
    for threshold in cfg['analysis']['descriptive_loss_tolerances_percent']:
        passing=g.loss_percent<=threshold
        for scope in ['selection','deployment','verification']:
            tol.append(dict(dataset=ds,W=W,method=meth,tolerance_percent=threshold,scope=scope,paths=len(g),passing_paths=int(passing.sum()),fraction=float(passing.mean()),mean_saving_percent=float(g[scope+'_saving_percent'].mean()),passing_mean_saving_percent=float(g.loc[passing,scope+'_saving_percent'].mean()) if passing.any() else np.nan))
pd.DataFrame(tol).to_csv(OUT/'tolerance_cost_curves.csv',index=False)
for ds in cfg['datasets']:
    g=engine.load_external_graph(ROOT/'data/raw/snap',ds);outdegree=np.diff(g['indptr']);indegree=np.bincount(g['targets'],minlength=len(g['nodes']));ix={n:i for i,n in enumerate(g['nodes'])}
    rr=raw[(ds,1101,1280,'step')][0]
    for name,a in rr['arms'].items():
        if name.startswith('random') or name=='full': continue
        pool=np.array([ix[n] for n in a['candidate_ids']]);s=set(a['candidate_ids']);over=[len(s&set(raw[(ds,path,1280,'step')][0]['arms']['full']['selected'])) for path in cfg['resolution']['paths']]
        direction.append(dict(dataset=ds,method=name,candidate_count=len(pool),mean_outdegree=float(outdegree[pool].mean()),mean_indegree=float(indegree[pool].mean()),min_outdegree=int(outdegree[pool].min()),max_outdegree=int(outdegree[pool].max()),full_seed_coverage_mean=float(np.mean(over)/5),full_seed_overlap_counts=';'.join(map(str,over))))
pd.DataFrame(direction).to_csv(OUT/'direction_diagnostics.csv',index=False)
result={'conditions':len(raw),'arms':int((~df.method.eq('random_mean_4k')).sum()),'analysis_rows_including_random_mean':len(df),'primary_tests':primary,'maximum_selection_worlds':1280,'significant_primary_holm_005':int(sum(x['p_holm']<.05 for x in primary)),'runtime_minutes':sum(json.loads(j.read_text())['elapsed_seconds'] for j in (ROOT/'results/main/conditions').glob('*.json'))/60,'peak_GiB':float(df.peak_working_set_bytes.max()/2**30),'python':sys.version,'platform':platform.platform()}
(OUT/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
