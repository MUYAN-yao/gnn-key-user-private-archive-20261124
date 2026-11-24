"""Independent output validation and protocol-specified conditional analysis.

No inference about a population of independently sampled networks is performed.
"""
import sys,json,hashlib,itertools,math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import binomtest

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def boot(values,rng):
    x=np.asarray(values,dtype=float);n=len(x)
    means=x[rng.integers(0,n,(10000,n))].mean(axis=1)
    return np.quantile(means,[.025,.975]).tolist()

def main(base):
    base=Path(base);root=base/'results';out=base/'analysis';out.mkdir(exist_ok=True)
    manifest=json.loads((root/'manifest.json').read_text());assert manifest['status']=='COMPLETE'
    snapshot=base/'snapshot';src=json.loads((snapshot/'source_manifest.json').read_text())
    for name,h in src['files'].items():assert sha(snapshot/name)==h
    assert sha(base/'audit/audit-and-preflight.json')==src['audit_sha256']
    source_hash=sha(snapshot/'source_manifest.json');assert manifest['source_manifest_sha256']==source_hash
    configs=json.loads((snapshot/'config.json').read_text())['conditions']
    def key(c):return f"{c['stage']}-{c['dataset']}-k{c['k']}-p{c['p']}-h{c['h']}-{c['coupling']}-path{c['path']}-w{c['W']}"
    expected={key(c):c for c in configs};assert len(expected)==len(manifest['runs'])==520
    assert {r['key'] for r in manifest['runs']}==set(expected)
    # Independently reconstruct world identifiers from the published specification.
    worlds={};all_ids=set()
    for dataset in sorted({c['dataset'] for c in configs}):
        for path in range(1001,1011):
            for family,count in [('selection',5120),('evaluation',10000)]:
                ids=np.asarray([int.from_bytes(hashlib.sha256(f'computing-extension-20261015-v1|{dataset}|{path}|{family}|{i}'.encode()).digest()[:8],'big')&((1<<63)-1) for i in range(count)],dtype=np.uint64)
                ids_set=set(map(int,ids));assert len(ids_set)==count and not all_ids.intersection(ids_set)
                all_ids.update(ids_set);worlds[dataset,path,family]=ids
    assert len(all_ids)==907200
    records={};raw=[];grouped=[];timing=[];evals={};network_meta={};rounds=[]
    for entry in manifest['runs']:
        name=entry['key'];jp=root/'conditions'/(name+'.json');npz=root/'conditions'/(name+'.npz')
        assert sha(jp)==entry['json_sha256'] and sha(npz)==entry['npz_sha256']
        r=json.loads(jp.read_text());c=r['config'];assert c==expected[name]
        assert r['source_manifest_sha256']==source_hash and r['array_sha256']==sha(npz)
        assert r['selection_world_sha256']==hashlib.sha256(worlds[c['dataset'],c['path'],'selection'][:c['W']].tobytes()).hexdigest()
        assert r['evaluation_world_sha256']==hashlib.sha256(worlds[c['dataset'],c['path'],'evaluation'].tobytes()).hexdigest()
        assert r['evaluation_world_count']==10000
        if c['dataset'] in network_meta:assert network_meta[c['dataset']]==r['graph']
        n=r['graph']['n'];k=c['k'];W=c['W'];arrays=np.load(npz)
        assert set(r['arms'])=={'full','weighted_2k','weighted_4k','weighted_8k','degree_4k','pagerank_4k','random0_4k','random1_4k','random2_4k'}
        full=arrays['full_evaluation'];assert len(full)==10000
        for method,a in r['arms'].items():
            v=arrays[method+'_evaluation'];score=arrays[method+'_round_totals'];candidate=a['candidate_ids']
            assert len(v)==10000 and score.shape==(k,a['candidate_count'])
            assert candidate==sorted(candidate) and len(set(candidate))==len(candidate)
            assert len(set(a['selected']))==k and set(a['selected'])<=set(candidate)
            assert np.all((v>=k)&(v<=n))
            selected=[];previous_total=0
            for rd,scores in enumerate(score):
                used={candidate.index(s) for s in selected}
                assert {int(i) for i in np.where(scores==-1)[0]}==used
                idx=int(np.argmax(scores));winner=candidate[idx];assert winner==a['selected'][rd]
                assert a['trace'][rd]['ties']==int(np.sum(scores==scores[idx]))
                valid=np.sort(scores[scores>=0])[::-1]
                margin=float((valid[0]-valid[1])/W) if len(valid)>1 else np.nan
                assert np.isnan(margin) or abs(margin-a['trace'][rd]['margin'])<1e-12
                rounds.append({**c,'method':method,'round':rd+1,'winner':winner,'total_spread':float(scores[idx]/W),'marginal_gain':float((scores[idx]-previous_total)/W),'winner_runnerup_margin':margin,'ties':a['trace'][rd]['ties']})
                previous_total=int(scores[idx])
                selected.append(winner)
            d=v-full
            assert abs(d.mean()-a['delta'])<1e-12 and abs(v.mean()-a['mean_spread'])<1e-12
            assert abs(d.std(ddof=1)/100-a['mc_se'])<1e-12
            assert a['same_order']==(a['selected']==r['arms']['full']['selected'])
            assert a['same_set']==(set(a['selected'])==set(r['arms']['full']['selected']))
            assert a['full_pool']==(len(candidate)==n)
            if a['full_pool']:assert a['same_order'] and np.array_equal(v,full)
            if a['same_set']:assert np.array_equal(v,full)
            inc=float(full.mean()-k)
            row={**c,'method':method,'n':n,'candidate_count':a['candidate_count'],'coverage':a['coverage'],'full_pool':a['full_pool'],'mean_spread':a['mean_spread'],'incremental_spread':a['incremental_spread'],'full_spread':float(full.mean()),'full_incremental':inc,'delta':a['delta'],'mc_se':a['mc_se'],'mc_lower':a['delta']-1.96*a['mc_se'],'mc_upper':a['delta']+1.96*a['mc_se'],'same_order':a['same_order'],'same_set':a['same_set'],'selection_seconds':a['selection_seconds'],'evaluation_seconds':a['evaluation_seconds'],'ranking_seconds':a['ranking_seconds'],'world_preparation_seconds':r['world_preparation_seconds'],'graph_preparation_seconds':r['preparation_seconds'],'selection_saving':1-a['selection_seconds']/r['arms']['full']['selection_seconds'],'relative_incremental_loss':-a['delta']/inc if inc>0 else np.nan,'descriptive_loss_upper_fraction':(-a['delta']+1.96*a['mc_se'])/inc if inc>0 else np.nan,'ties':sum(t['ties']>1 for t in a['trace'])}
            a_cost=r['preparation_seconds']+r['world_preparation_seconds']+a['ranking_seconds']+a['selection_seconds']+a['evaluation_seconds']
            f=r['arms']['full'];f_cost=r['preparation_seconds']+r['world_preparation_seconds']+f['selection_seconds']+f['evaluation_seconds']
            row['end_to_end_seconds']=a_cost;row['end_to_end_saving']=1-a_cost/f_cost
            A=set(a['selected']);B=set(f['selected'])
            row.update(jaccard=len(A&B)/len(A|B),first_divergence=next((i+1 for i,(u,v) in enumerate(zip(a['selected'],f['selected'])) if u!=v),np.nan),relative_total_loss=-a['delta']/full.mean(),selection_speedup=f['selection_seconds']/a['selection_seconds'],end_to_end_speedup=f_cost/a_cost)
            raw.append(row)
            if not method.startswith('random'):grouped.append(row.copy())
        # Paired evaluation across random candidate repetitions preserves shared worlds.
        rand=np.mean([arrays[f'random{i}_4k_evaluation'] for i in range(3)],axis=0)
        rr=[x for x in raw[-9:] if x['method'].startswith('random')]
        row=rr[0].copy();row['method']='random_4k'
        for field in ['mean_spread','incremental_spread','same_order','same_set','selection_seconds','evaluation_seconds','ranking_seconds','selection_saving','end_to_end_seconds','end_to_end_saving','ties','jaccard','first_divergence','relative_total_loss','selection_speedup','end_to_end_speedup']:
            row[field]=float(np.mean([v[field] for v in rr]))
        d=rand-full;row.update(delta=float(d.mean()),mc_se=float(d.std(ddof=1)/100))
        row.update(mc_lower=row['delta']-1.96*row['mc_se'],mc_upper=row['delta']+1.96*row['mc_se'])
        row['relative_incremental_loss']=-row['delta']/row['full_incremental'] if row['full_incremental']>0 else np.nan
        row['descriptive_loss_upper_fraction']=(-row['delta']+1.96*row['mc_se'])/row['full_incremental'] if row['full_incremental']>0 else np.nan
        grouped.append(row)
        for t in r['timing_repeats']:timing.append({**c,**t})
        records[name]=r;evals[name]=full
        network_meta[c['dataset']]=r['graph']
    pd.DataFrame(raw).to_csv(out/'all_arm_metrics.csv',index=False)
    pd.DataFrame(rounds).to_csv(out/'round_diagnostics.csv',index=False)
    df=pd.DataFrame(grouped)
    # Binary indicators for deterministic arms, within-path fractions for random pools.
    # Normalize before CSV export to avoid a mixed True/False/0.0/1.0 string column.
    df[['same_order','same_set']]=df[['same_order','same_set']].astype(float)
    df.to_csv(out/'path_level_metrics.csv',index=False)
    pd.DataFrame(timing).to_csv(out/'timing_repeats.csv',index=False)
    (out/'network_metadata.json').write_text(json.dumps(network_meta,indent=2))
    groups=['stage','dataset','k','p','h','coupling','W','method'];rng=np.random.default_rng(20261015)
    summaries=[]
    for group,block in df.groupby(groups,sort=True):
        row=dict(zip(groups,group));row['paths']=len(block)
        for field in ['delta','mean_spread','incremental_spread','relative_incremental_loss','relative_total_loss','selection_saving','end_to_end_saving','selection_seconds','end_to_end_seconds','selection_speedup','end_to_end_speedup','same_set','same_order','jaccard','coverage']:
            values=block[field].astype(float).to_numpy()
            row[field+'_mean']=float(np.mean(values));row[field+'_sd']=float(np.std(values,ddof=1))
            if field in ['delta','incremental_spread']:
                ci=boot(values,rng);row[field+'_lo'],row[field+'_hi']=ci
        summaries.append(row)
    summary=pd.DataFrame(summaries);summary.to_csv(out/'group_summary.csv',index=False)
    primary=df[(df.stage=='resolution')&(df.W==5120)&(df.method!='full')]
    tests=[]
    for (dataset,method),b in primary.groupby(['dataset','method'],sort=True):
        x=b.delta.to_numpy();nz=x[np.abs(x)>1e-12];pos=int(np.sum(nz>0));neg=int(np.sum(nz<0))
        tests.append(dict(dataset=dataset,method=method,n_paths=len(x),n_zero=len(x)-len(nz),positive=pos,negative=neg,mean_delta=float(x.mean()),sd_delta=float(x.std(ddof=1)),p_two_sided=binomtest(pos,len(nz),.5).pvalue if len(nz) else 1.))
    assert len(tests)==24
    last=0.
    for rank,i in enumerate(np.argsort([t['p_two_sided'] for t in tests])):
        last=max(last,min(1.,tests[i]['p_two_sided']*(24-rank)));tests[i]['p_holm']=last
    pd.DataFrame(tests).to_csv(out/'primary_sign_tests_holm.csv',index=False)
    transitions=[]
    blockkeys=['stage','dataset','path','k','p','h','coupling']
    # All prospectively varied W groups; no cross-parameter pseudo-transition.
    for vals,block in df[df.method=='full'].groupby(blockkeys,sort=True):
        records_sorted=block.sort_values('W').to_dict('records')
        for a,b in zip(records_sorted,records_sorted[1:]):
            ka=key(a);kb=key(b);ra=records[ka]['arms']['full'];rb=records[kb]['arms']['full']
            A=set(ra['selected']);B=set(rb['selected']);d=evals[kb]-evals[ka]
            transitions.append({**dict(zip(blockkeys,vals)),'low':a['W'],'high':b['W'],'same_set':A==B,'same_order':ra['selected']==rb['selected'],'jaccard':len(A&B)/len(A|B),'first_divergence':next((i+1 for i,(u,v) in enumerate(zip(ra['selected'],rb['selected'])) if u!=v),None),'delta_full_high_low':float(d.mean()),'mc_se':float(d.std(ddof=1)/100),'mc_lower':float(d.mean()-1.96*d.std(ddof=1)/100),'mc_upper':float(d.mean()+1.96*d.std(ddof=1)/100)})
    tr=pd.DataFrame(transitions);tr.to_csv(out/'reference_transitions.csv',index=False)
    tolerance=[]
    for (dataset,method),b in primary.groupby(['dataset','method']):
        for margin in [0,.01,.025,.05,.1,.2]:
            tolerance.append(dict(dataset=dataset,method=method,tolerance=margin,paths=len(b),point_fraction=float(np.mean(b.relative_incremental_loss<=margin)),conditional_bound_fraction=float(np.mean(b.descriptive_loss_upper_fraction<=margin)),interpretation='descriptive; not a noninferiority test'))
    pd.DataFrame(tolerance).to_csv(out/'tolerance_sensitivity.csv',index=False)
    status=dict(status='PASS',conditions=len(records),arm_executions=len(raw),evaluation_values=10000*len(raw),source_manifest_sha256=source_hash,primary_test_count=len(tests),transitions=len(tr),timing_observations=len(timing),unique_used_or_reserved_world_ids=len(all_ids),checks=['complete frozen matrix','source, pre-freeze audit and result SHA256','independently reconstructed world IDs, nested prefixes and disjoint families/paths','consistent input and graph hashes','per-round greedy argmax, margin and tie policy','per-world range/paired statistics','full-pool consistency','same-set evaluation identity'],scope='structural/numeric audit; independent semantic oracle checks in audit-and-preflight.json')
    (out/'validation.json').write_text(json.dumps(status,indent=2))
    brief={'validation':status,'runtime_minutes':(manifest['completed_epoch']-manifest['started_epoch'])/60,'main_reference_transitions':tr[tr.stage=='resolution'].groupby(['low','high']).agg(changed=('same_set',lambda s:int((~s).sum())),n=('same_set','size'),mean_jaccard=('jaccard','mean'),mean_delta=('delta_full_high_low','mean')).reset_index().to_dict('records'),'primary':summary[(summary.stage=='resolution')&(summary.W==5120)].to_dict('records'),'holm_significant':sum(t['p_holm']<.05 for t in tests),'max_peak_mb':max(r['peak_working_set_bytes'] or 0 for r in records.values())/2**20}
    brief['holm_significant']=int(brief['holm_significant'])
    (out/'summary.json').write_text(json.dumps(brief,indent=2))
    print(json.dumps(status));print('Runtime minutes',brief['runtime_minutes']);print('Reference',brief['main_reference_transitions'])

if __name__=='__main__':main(sys.argv[1])
