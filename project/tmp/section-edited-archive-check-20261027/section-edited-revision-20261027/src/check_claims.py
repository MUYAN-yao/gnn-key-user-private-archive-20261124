"""Read-only numerical and editorial audit for the narrative revision."""
from pathlib import Path
import hashlib, json, re
import numpy as np
import pandas as pd

R=Path(__file__).resolve().parents[1]; B=R.parent
OLD=B/'reproducible-revision-20261026'; M=R/'manuscript'; Q=R/'qa'
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
report={'date':'2026-10-27','scope':'Read-only raw-result/statistical cross-check and editorial consistency; no new experimental executions'}
source=(M/'manuscript.tex').read_text(encoding='utf-8')
old=(OLD/'manuscript/manuscript.tex').read_text(encoding='utf-8')
report['methods_and_setup_unchanged']=source.split('\\section{Methods}',1)[1].split('\\section{Results}',1)[0]==old.split('\\section{Methods}',1)[1].split('\\section{Results}',1)[0]
report['declarations_unchanged']=source.split('\\section*{Statements and Declarations}',1)[1]==old.split('\\section*{Statements and Declarations}',1)[1]
report['replay_script_unchanged']=sha(R/'src/reproduce.py')==sha(OLD/'src/reproduce.py')
report['asset_hashes']={p.name:sha(p) for p in M.iterdir() if p.is_file() and (p.name.startswith('Fig') or p.suffix in ('.cls','.clo') or p.name in ('numbers.tex','primary_table.tex','cost_table.tex','transition_table.tex','supp_tables.tex','precision_budget_table.tex','references.tex'))}
assert all(sha(OLD/'manuscript'/n)==h for n,h in report['asset_hashes'].items())
assert report['methods_and_setup_unchanged'] and report['declarations_unchanged'] and report['replay_script_unchanged']
title=re.search(r'\\title\{([^}]+)\}',source).group(1)
assert title in (M/'Online_Resource_1.tex').read_text(encoding='utf-8')
for file in ('summary_for_editor.txt','cover_letter_draft.txt','novelty_and_scope_statement.txt'):
    assert title in (R/file).read_text(encoding='utf-8')
contrib=source.split('\\begin{enumerate}',1)[1].split('\\end{enumerate}',1)[0]
assert len(re.findall(r'\\item\[\([123]\)\]',contrib))==3
report['title']=title; report['numbered_contributions']=3
keywords=re.search(r'\\keywords\{(.*?)\}',source,re.S).group(1).split('\\and')
assert 4<=len(keywords)<=6
report['keywords']=len(keywords)
rows=[]; raw={}; inputs={}
main=B/'results/main'; status=read(main/'run_status.json'); assert status['status']=='complete'
assert len(status['completed'])==54
for entry in status['completed']:
    js=main/'conditions'/(entry['key']+'.json'); npz=js.with_suffix('.npz')
    assert sha(js)==entry['json_sha256'] and sha(npz)==entry['npz_sha256']
    r=read(js); c=r['config']; inputs[str(js.relative_to(B))]=sha(js)
    with np.load(npz) as z:
        fv=z['full_evaluation']; raw[(c['dataset'],c['path'],c['W'],c['coupling'])]=(r,fv.copy())
        for name,a in r['arms'].items():
            diff=z[name+'_evaluation']-fv
            assert np.isclose(diff.mean(),a['delta'],atol=1e-12,rtol=0)
            assert np.isclose(diff.std(ddof=1)/100,a['mc_se'],atol=1e-12,rtol=0)
            rows.append(dict(dataset=c['dataset'],path=c['path'],W=c['W'],coupling=c['coupling'],method=name,
                             delta=float(diff.mean()),loss=float(-100*diff.mean()/(fv.mean()-5)),
                             same_order=a['selected']==r['arms']['full']['selected']))
df=pd.DataFrame(rows); report['main_conditions']=54; report['main_arms']=len(rows); assert len(rows)==468
primary=df[(df.W==1280)&(df.coupling=='step')]
degree=primary[primary.method=='degree_4k']; assert len(degree)==15 and degree.same_order.all()
report['degree_trajectory_matches']=int(degree.same_order.sum())
precision=[]; pool_exchanges={}
for folder,count in ((B/'review-v2/supplement-pr-precision',15),(B/'review-v3-budget-precision/supplement-pr-budget-precision',30)):
    state=read(folder/'run_status.json'); assert state['status']=='complete' and len(state['completed'])==count
    for entry in state['completed']:
        js=folder/'conditions'/(entry['key']+'.json'); npz=js.with_suffix('.npz')
        assert sha(js)==entry['json_sha256'] and sha(npz)==entry['npz_sha256']
        r=read(js); inputs[str(js.relative_to(B))]=sha(js)
        fv=raw[(r['dataset'],r['path'],r['W'],'step')][1]
        with np.load(npz) as z:
            for name,a in r['arms'].items():
                diff=z[name+'_evaluation']-fv
                assert np.isclose(diff.mean(),a['delta_vs_full'],atol=1e-12,rtol=0)
                if r['path']==1101 and r['W']==1280 and name=='pagerank_4k':
                    default=raw[(r['dataset'],r['path'],r['W'],'step')][0]['arms'][name]['candidate_ids']
                    pool_exchanges[r['dataset']]=len(set(default)-set(a['candidate_ids']))
                precision.append(dict(dataset=r['dataset'],W=r['W'],path=r['path'],method=name,
                                      delta=float(diff.mean()),loss=float(-100*diff.mean()/(fv.mean()-5))))
strict=pd.DataFrame(precision); assert len(strict)==90
assert pool_exchanges=={'college_msg':0,'ca_grqc':2,'wiki_vote':1}
report['default_strict_4k_pool_exchanges']=pool_exchanges
summary=pd.read_csv(B/'review-v3-budget-precision/analysis/precision_budget/summary_by_budget_precision.csv')
for solver,frame in [('strict',strict),('default',df[df.coupling=='step'])]:
    for (ds,W,m),g in frame[frame.method.isin(['pagerank_4k','pagerank_5pct'])].groupby(['dataset','W','method']):
        target=summary[(summary.dataset==ds)&(summary.W==W)&(summary.method==m)&(summary.solver==solver)].iloc[0]
        assert np.isclose(g.delta.mean(),target.delta_nodes_mean,atol=1e-12,rtol=0)
        assert np.isclose(g.loss.mean(),target.loss_percent_mean,atol=1e-12,rtol=0)
report['precision_summary_from_raw_arrays']='PASS'
report['precision_arms']=90
report['pagerank_4k_losses']=summary[summary.method=='pagerank_4k'][['dataset','W','solver','delta_nodes_mean','loss_percent_mean']].to_dict('records')
for solver,want in [('default',[-5.61,2.53,5.07]),('strict',[-11.25,-2.96,-.54])]:
    v=summary[(summary.dataset=='ca_grqc')&(summary.method=='pagerank_4k')&(summary.solver==solver)].sort_values('W')
    assert [round(float(x),2) for x in v.loss_percent_mean]==want
transitions=[]
for ds in ('ca_grqc','college_msg','wiki_vote'):
    for path in range(1101,1106):
        a,av=raw[(ds,path,320,'step')];b,bv=raw[(ds,path,1280,'step')]
        diff=bv-av; se=diff.std(ddof=1)/100
        transitions.append(dict(dataset=ds,path=path,changed=set(a['arms']['full']['selected'])!=set(b['arms']['full']['selected']),delta=float(diff.mean()),lo=float(diff.mean()-1.96*se),hi=float(diff.mean()+1.96*se)))
tr=pd.DataFrame(transitions)
assert int(tr.changed.sum())==6 and int((tr.lo>0).sum())==4
assert np.isclose(tr[tr.dataset=='ca_grqc'].delta.mean(),.12720)
assert np.isclose(tr[tr.dataset=='college_msg'].delta.mean(),.05336)
report['reference_transitions']=transitions
hist=read(B.parent/'computing-strengthening-20261015/analysis/summary.json')
h=next(x for x in hist['main_reference_transitions'] if x['low']==1280 and x['high']==5120)
assert h['changed']==16 and round(h['mean_delta'],5)==.01111
report['historical_transition']=h
cost=pd.read_csv(B/'review-v2/analysis/arm_path.csv')
cost=cost[(cost.W==1280)&(cost.coupling=='step')&(cost.method=='degree_4k')]
save=cost.groupby('dataset')[['selection_saving_percent','verification_saving_percent']].mean()
assert round(save.selection_saving_percent.min(),2)==98.40 and round(save.selection_saving_percent.max(),2)==99.67
assert round(save.verification_saving_percent.min(),2)==86.59 and round(save.verification_saving_percent.max(),2)==96.26
report['cost_savings']=save.to_dict('index')
inherited=read(R/'evidence/reproduction-20261026.json'); assert inherited['status']=='PASS'
assert sha(R/'evidence/reproduction-20261026.json')==sha(OLD/'qa/reproduction-final/verification.json')
report['inherited_reproduction']={'source':str(OLD/'qa/reproduction-final/verification.json'),'sha256':sha(R/'evidence/reproduction-20261026.json'),'rerun_this_turn':False}
report['input_json_hashes']=inputs
report['status']='PASS'
(Q/'claim_checks.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k in ('status','main_conditions','main_arms','precision_arms','degree_trajectory_matches','precision_summary_from_raw_arrays','numbered_contributions','methods_and_setup_unchanged','declarations_unchanged')},indent=2))
