"""Read saved experiments only; verify, aggregate and typeset historical evidence.

No simulator/engine/runner imports; no seed selection or new diffusion draws.
Usage: python src/integrate_historical.py [--project-root PATH]
"""
from pathlib import Path
import argparse, hashlib, json, shutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

R = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--project-root', type=Path, default=R.parents[2])
args = parser.parse_args()
H = args.project_root / 'submission/computing-strengthening-20261015'
E = H.parent / 'computing-external-validation-20261015'
A = R/'analysis'; M = R/'manuscript'; Q = R/'qa'
for p in (A, A/'figures', M, Q): p.mkdir(parents=True, exist_ok=True)
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p, x): p.write_text(json.dumps(x, indent=2, ensure_ascii=False, allow_nan=False)+'\n', encoding='utf-8')
def close(a,b): return bool(np.allclose(np.asarray(a,dtype=float),np.asarray(b,dtype=float),rtol=1e-9,atol=1e-11,equal_nan=True))
cfg=read(H/'snapshot/config.json'); manifest=read(H/'results/manifest.json')
sm=read(H/'snapshot/source_manifest.json')
assert all(sha(H/'snapshot'/n)==v for n,v in sm['files'].items())
assert sha(H/'snapshot/engine.py')==sha(E/'snapshot/legacy_engine.py')
assert sha(H/'snapshot/source_manifest.json')==manifest['source_manifest_sha256']
assert len(cfg['conditions'])==len(manifest['runs'])==520
audit={'status':'PASS','new_experiments_executed':False,'simulation_or_selection_replayed':False,
       'scope':'Stored arrays, metadata and descriptive aggregation only; no new inference or timing.',
       'conditions':520,'result_files_hashed':0,'arms_recomputed':0,
       'snapshot_hashes_match':True,'legacy_engine_identical':True,
       'historical_source_manifest_sha256':sha(H/'snapshot/source_manifest.json')}
rows=[]; armrows=[]; fulls={}; seen=[]; input_hashes={}
keys=['stage','dataset','path','W','k','p','h','coupling']
metrics=['mean_spread','incremental_spread','delta','mc_se','same_order','same_set','jaccard','coverage','candidate_count','relative_incremental_loss']
for run in manifest['runs']:
    key=run['key']; jp=H/'results/conditions'/f'{key}.json'; zp=jp.with_suffix('.npz')
    for p, expected in ((jp,run['json_sha256']),(zp,run['npz_sha256'])):
        actual=sha(p); assert actual==expected, str(p)
        input_hashes[str(p.relative_to(H))]=actual; audit['result_files_hashed']+=1
    x=read(jp); c=x['config']; seen.append(c)
    assert x['source_manifest_sha256']==manifest['source_manifest_sha256']
    n=x['graph']['n']; arms=x['arms']; fs=arms['full']['selected']
    with np.load(zp,allow_pickle=False) as z:
        ev={name:z[name+'_evaluation'].astype(float) for name in arms}
    assert all(v.shape==(10000,) for v in ev.values())
    fv=ev['full']; fullmean=float(fv.mean()); inc=fullmean-c['k']; assert inc>0
    for name, a in arms.items():
        d=ev[name]-fv; selected=a['selected']
        delta=float(d.mean()); se=float(d.std(ddof=1)/np.sqrt(len(d)))
        assert close([ev[name].mean(),delta,se],[a['mean_spread'],a['delta'],a['mc_se']]),(key,name)
        assert len(a['candidate_ids'])==a['candidate_count']
        assert close(a['coverage'],a['candidate_count']/n)
        assert set(selected)<=set(a['candidate_ids'])
        if set(selected)==set(fs): assert np.array_equal(ev[name],fv)
        armrows.append({**c,'method':name,'mean_spread':ev[name].mean(),'delta':delta,'mc_se':se,
                        'same_order':int(selected==fs),'same_set':int(set(selected)==set(fs)),
                        'coverage':a['coverage'],'candidate_count':a['candidate_count']})
        audit['arms_recomputed']+=1
    for method in ['full','weighted_2k','weighted_4k','weighted_8k','degree_4k','pagerank_4k','random_4k']:
        names=[f'random{i}_4k' for i in range(3)] if method=='random_4k' else [method]
        v=np.mean([ev[t] for t in names],axis=0); d=v-fv
        s=[arms[t]['selected'] for t in names]
        rows.append({**c,'method':method,'n':n,'candidate_count':np.mean([arms[t]['candidate_count'] for t in names]),
            'coverage':np.mean([arms[t]['coverage'] for t in names]),'mean_spread':float(v.mean()),
            'incremental_spread':float(v.mean()-c['k']),'full_spread':fullmean,'full_incremental':inc,
            'delta':float(d.mean()),'mc_se':float(d.std(ddof=1)/100),
            'relative_incremental_loss':float(-d.mean()/inc),
            'same_order':np.mean([u==fs for u in s]),'same_set':np.mean([set(u)==set(fs) for u in s]),
            'jaccard':np.mean([len(set(u)&set(fs))/len(set(u)|set(fs)) for u in s])})
    fulls[tuple(c[k] for k in keys)]=(fv,fs,x['evaluation_world_sha256'])
assert sorted(map(lambda c:json.dumps(c,sort_keys=True),seen))==sorted(map(lambda c:json.dumps(c,sort_keys=True),cfg['conditions']))
df=pd.DataFrame(rows); pd.DataFrame(armrows).to_csv(A/'historical_arm_metrics.csv',index=False)
df.to_csv(A/'historical_path_metrics.csv',index=False)
old=pd.read_csv(H/'analysis/path_level_metrics.csv')
join=keys+['method']; old=old.set_index(join).sort_index(); new=df.set_index(join).sort_index()
assert new.index.equals(old.index)
assert close(new[metrics],old[metrics]); audit['path_rows_recomputed_and_matched']=len(new)
gkeys=['stage','dataset','k','p','h','coupling','W','method']
summary=[]
for key,sub in df.groupby(gkeys,sort=True):
    row=dict(zip(gkeys,key)); row['paths']=len(sub)
    for col in metrics:
        row[col+'_mean']=float(sub[col].mean()); row[col+'_sd']=float(sub[col].std(ddof=1))
    row['order_matches']=float(sub.same_order.sum()); row['negative_delta_paths']=int((sub.delta<0).sum()); row['positive_delta_paths']=int((sub.delta>0).sum())
    summary.append(row)
sg=pd.DataFrame(summary); sg.to_csv(A/'historical_group_summary.csv',index=False)
os=pd.read_csv(H/'analysis/group_summary.csv').set_index(gkeys).sort_index(); ns=sg.set_index(gkeys).sort_index()
common=[c for c in ns if c in os and c!='paths']
assert ns.index.equals(os.index) and close(ns[common],os[common]);audit['group_rows_recomputed_and_matched']=len(ns)
audit['group_columns_checked']=common
trans=[]
for key,(v,s,wh) in fulls.items():
    c=dict(zip(keys,key)); ws=sorted(q[3] for q in fulls if all(q[i]==key[i] for i in range(len(keys)) if i!=3))
    pos=ws.index(c['W'])
    if pos==0: continue
    low=ws[pos-1]; lk=list(key);lk[3]=low; lv,ls,lwh=fulls[tuple(lk)]
    assert wh==lwh; d=v-lv; se=float(d.std(ddof=1)/100)
    trans.append({**{k:c[k] for k in keys if k!='W'},'low':low,'high':c['W'],
        'same_set':int(set(s)==set(ls)),'same_order':int(s==ls),
        'jaccard':len(set(s)&set(ls))/len(set(s)|set(ls)),
        'delta_full_high_low':float(d.mean()),'mc_se':se,'mc_lower':float(d.mean()-1.96*se),'mc_upper':float(d.mean()+1.96*se)})
td=pd.DataFrame(trans); td.to_csv(A/'historical_reference_transitions.csv',index=False)
tkeys=[k for k in keys if k!='W']+['low','high']
ot=pd.read_csv(H/'analysis/reference_transitions.csv').set_index(tkeys).sort_index(); nt=td.set_index(tkeys).sort_index()
assert nt.index.equals(ot.index) and close(nt,ot[nt.columns]);audit['reference_transition_rows_checked']=len(td)

mainmethods=['degree_4k','pagerank_4k','weighted_4k']; graphs=['invs2013','invs2015','kenya2012','sfhh2009']
param=sg[(sg.stage=='parameters')|((sg.stage=='resolution')&(sg.W==320))].copy()
param=param[param.method.isin(mainmethods)]; param.to_csv(A/'parameter_sensitivity_display.csv',index=False)
controls=sg[(sg.stage=='coupling')|((sg.stage=='resolution')&sg.W.isin([320,1280]))].copy()
controls[controls.method.isin(mainmethods)].to_csv(A/'coupling_display.csv',index=False)
secondary=sg[sg.stage.isin(['seed_budget','scale']) & sg.method.isin(mainmethods)].copy()
secondary.to_csv(A/'secondary_display.csv',index=False)
assert len(param)==60 and len(secondary)==30
metadata=read(H/'analysis/network_metadata.json')
cover=pd.DataFrame(cfg['conditions']).groupby(['stage','dataset','k','p','h','coupling'],sort=True).agg(
    conditions=('W','size'),paths=('path','nunique'),budgets=('W',lambda s:','.join(map(str,sorted(set(s)))))).reset_index()
cover['nodes']=cover.dataset.map(lambda d:metadata[d]['n']);cover['evaluation_worlds']=10000
cover['arms']=cover.conditions*9;cover.to_csv(A/'historical_experiment_coverage.csv',index=False)
legacy=H/'legacy_project/audits/sociopatterns-resolution-confirmation-v0_1/snapshot-r3-confirmation-run-20260920'
legacy_records=[read(p) for p in legacy.glob('*/*/*.json')]
assert len(legacy_records)==42 and sum(len(x['arms']) for x in legacy_records)==168
assert {x['evaluation_world_count'] for x in legacy_records}=={2000}
assert {x['world_path'] for x in legacy_records}=={301,302}
assert {x['selection_world_count'] for x in legacy_records}=={20,80,320}
assert all(x['config']=={'p':.01,'horizon':3} for x in legacy_records)
audit['initial_study_metadata_records_read']=42
audit['initial_study_arrays_recomputed']=False
facts={}
for label,stage,low,high in [('step','resolution',1280,5120),('edge','coupling',320,1280)]:
    t=td[(td.stage==stage)&(td.low==low)&(td.high==high)]
    facts[label]={'pairs':len(t),'changed_sets':int((t.same_set==0).sum()),'mean_delta':float(t.delta_full_high_low.mean()),
         'path_pair_sd':float(t.delta_full_high_low.std(ddof=1)),'min_delta':float(t.delta_full_high_low.min()),'max_delta':float(t.delta_full_high_low.max())}
pp=df[df.stage=='parameters'];facts['parameters']={m:{'conditions':len(pp[pp.method==m]),'order_matches':int(pp[pp.method==m].same_order.sum()),
    'negative_delta':int((pp[pp.method==m].delta<0).sum()),'positive_delta':int((pp[pp.method==m].delta>0).sum())} for m in mainmethods}
dump(A/'historical_key_facts.json',facts)
ts=[]
for key,t in td[((td.stage=='coupling')& (td.low==320)) | ((td.stage=='resolution')&(td.low==1280))].groupby(['coupling','dataset','low','high']):
    ts.append(dict(zip(['coupling','dataset','low','high'],key))|{'paths':len(t),'changed_sets':int((t.same_set==0).sum()),
        'mean_delta':t.delta_full_high_low.mean(),'sd_delta':t.delta_full_high_low.std(ddof=1),
        'min_delta':t.delta_full_high_low.min(),'max_delta':t.delta_full_high_low.max(),
        'positive_conditional_intervals':int((t.mc_lower>0).sum()),'intervals_crossing_zero':int(((t.mc_lower<=0)&(t.mc_upper>=0)).sum())})
ts=pd.DataFrame(ts);ts.to_csv(A/'historical_transition_summary.csv',index=False)

# Typesetting: normal-size longtables; no scaling or compressed font.
def longtable(name,caption,label,header,body,colspec):
    text='\\begin{longtable}{'+colspec+'}\n\\caption{'+caption+'}\\label{'+label+'}\\\\\n\\toprule\n'+header+' \\\\\n\\midrule\n\\endfirsthead\n\\multicolumn{'+str(len(colspec))+'}{l}{\\tablename~\\thetable{} (continued)}\\\\\n\\toprule\n'+header+' \\\\\n\\midrule\n\\endhead\n\\bottomrule\n\\endfoot\n'+'\n'.join(body)+'\n\\end{longtable}\n'
    (M/name).write_text(text,encoding='utf-8')
names={'degree_4k':'D','pagerank_4k':'P','weighted_4k':'W'}
def table_rows(data,kind):
    out=[]
    for dataset in graphs+['synthetic_ba2000','synthetic_sbm2000']:
        sub=data[data.dataset==dataset]
        if sub.empty:continue
        if kind=='secondary' and dataset=='synthetic_ba2000': out.append(r'\pagebreak[4]')
        title=dataset.replace('_','\\_')
        out.append(r'\multicolumn{7}{l}{\textit{'+title+r'}}\\*')
        block_start=len(out)
        for _,r in sub.sort_values(['p','h','W','coupling','method']).iterrows():
            setting=(f'{r.p:g}, {r.h}' if kind=='param' else (f'{r.coupling}, {r.W}' if kind=='coupling' else str(r.W)))
            out.append(f'{setting} & {names[r.method]} & {r.delta_mean:+.4f} & {r.delta_sd:.4f} & {100*r.relative_incremental_loss_mean:+.2f} & {int(r.order_matches)}/{r.paths} & {100*r.coverage_mean:.2f}' +r'\\')
        for idx in range(block_start,len(out)-1): out[idx]+='*'
    return out
commoncaption='D, P and W denote Degree-4k, PageRank-4k and Weighted-4k. $\\Delta$ is restricted minus full spread (nodes); SD is across paths; loss is the mean pathwise incremental loss (\\%), negative when restriction gains. Match counts refer to the entire ordered sequence. Coverage is the fraction of eligible vertices (\\%).'
head=r'$(p,h)$ & Rank & $\overline\Delta$ & SD & Loss & Match & Cov.'
longtable('history_parameter_table.tex','Historical propagation-parameter sensitivity at $k=5$, $W=320$, step coupling. '+commoncaption+' The default $(.01,3)$ rows reuse the budget scan; they are not additional conditions.','tab:hist-parameters',head,table_rows(param,'param'),'llrrrrr')
longtable('history_coupling_table.tex','Historical coupling controls at $k=5$, $p=.01$, $h=3$. Each row uses its own coupling-specific full reference. '+commoncaption,'tab:hist-coupling',r'Coupling, $W$ & Rank & $\overline\Delta$ & SD & Loss & Match & Cov.',table_rows(controls[controls.method.isin(mainmethods)],'coupling'),'llrrrrr')
longtable('history_secondary_table.tex','Secondary historical controls: $k=20$ for the three contact graphs and $k=5$ for the two fixed synthetic instances; $p=.01$, $h=3$, step coupling. '+commoncaption+' Synthetic W denotes topology-derived weights, not observed event frequency.','tab:hist-secondary',r'$W$ & Rank & $\overline\Delta$ & SD & Loss & Match & Cov.',table_rows(secondary,'secondary'),'llrrrrr')
tr=[]
for coupling in ['step','edge']:
    tr.append(r'\multicolumn{6}{l}{\textit{'+('Step: $1280\\to5120$' if coupling=='step' else 'Fixed edge: $320\\to1280$')+r'}}\\')
    for _,r in ts[ts.coupling==coupling].iterrows():
        tr.append(f'{r.dataset} & {r.changed_sets}/10 & {r.mean_delta:+.5f} & {r.sd_delta:.5f} & {r.min_delta:+.4f} & {r.max_delta:+.4f}'+r'\\')
longtable('history_transition_table.tex','Full-reference budget transitions, independently evaluated on the same saved world family within each graph/path/coupling. Differences are high minus low budget; all spread values are nodes. SD describes ten computational paths within one graph.','tab:hist-transitions',r'Graph & Changed & Mean & SD & Min & Max',tr,'lrrrrr')
# This eight-row comparison fits on one page and should not be split.
tp=M/'history_transition_table.tex'
tp.write_text('\\begin{table}[htbp]\n\\caption{Full-reference budget transitions within each graph, path and coupling. Changes count final sets; spread differences are high minus low budget (nodes), with SD across ten paths.}\\label{tab:hist-transitions}\n\\centering\\begin{tabular}{lrrrrr}\n\\toprule\n'+r'Graph & Changed & Mean & SD & Min & Max\\'+'\n\\midrule\n'+'\n'.join(tr)+'\n\\bottomrule\n\\end{tabular}\n\\end{table}\n',encoding='utf-8')
coverage_tex=r'''\begin{longtable}{p{.23\linewidth}p{.51\linewidth}p{.14\linewidth}}
\caption{Evidence layers and experiment coverage. A condition fixes graph, path, $k,p,h,W$ and coupling; an arm changes eligibility. Paths are computational replicates. Counts are not independent network sample sizes.}\label{tab:hist-coverage}\\
\toprule Batch / graphs & Selection design and evaluation & Conditions / arms\\\midrule\endfirsthead
\multicolumn{3}{l}{\tablename~\thetable{} (continued)}\\\toprule
Batch / graphs & Selection design and evaluation & Conditions / arms\\\midrule\endhead\bottomrule\endfoot
Initial study / C4, C3 & C4: $k=5$; C3: $k=20$. $p=.01$, $h=3$, $W=20,80,320$, step; two paths (301--302); $M=2000$. Initial weighted-pool/reference comparisons. & 42 / 168\\
Historical budget / C4 & $k=5$, $p=.01$, $h=3$, $W=20,80,320,1280,5120$, step; ten paths (1001--1010); $M=10{,}000$. Reference-budget sensitivity. & 200 / 1800\\
Historical parameters / C4 & $k=5$, $W=320$, step; $(p,h)=(.005,3),(.05,3),(.01,1),(.01,5)$; ten paths; $M=10{,}000$. Local parameter changes. Default $(.01,3)$ reuses 40 budget conditions. & 160 / 1440\\
Historical coupling / C4 & $k=5$, $p=.01$, $h=3$, $W=320,1280$, fixed edge; ten paths; $M=10{,}000$. Coupling-specific comparisons and budget transitions. & 80 / 720\\
Historical larger seeds / C3 & $k=20$, $p=.01$, $h=3$, $W=320,1280$, step; ten paths; $M=10{,}000$. Seed-budget and coverage control. & 60 / 540\\
Historical synthetic / S2 & $k=5$, $p=.01$, $h=3$, $W=80,320$, step; five paths (1001--1005) per fixed instance; $M=10{,}000$. Topology controls. & 20 / 180\\
External primary / E3 & $k=5$, $p=.01$, $h=3$, $W=80,320,1280$, step; five paths (1101--1105); $M=10{,}000$. External transfer, budget and pool coverage. & 45 / 390\\
External coupling / E3 & $k=5$, $p=.01$, $h=3$, $W=320$, fixed edge; three paths (1101--1103); $M=10{,}000$. Coupling control. & 9 / 78\\
Post-hoc precision / E3 & Strict PageRank-4k/5\%, $W=80,320,1280$, step; other settings, five paths and $M=10{,}000$ reused from primary study. Existing full references reused. Numerical sensitivity, not new independent replication. & 45 / 90\\
\end{longtable}
\noindent C4: invs2013 ($n=91$), invs2015 (212), kenya2012 (75), sfhh2009 (402).
C3 excludes sfhh2009. S2: one BA and one SBM instance, each $n=2000$.
E3: CollegeMsg (1438), ca-GrQc (5241), wiki-Vote (7115).
Historical extension totals are $200+160+80+60+20=520$ conditions and 4680 arms.
Its nine arms are full selection, Weighted-2k/4k/8k, Degree-4k, PageRank-4k and three random-4k pools.
The external matrix totals 54 conditions and 468 arms. Resource-only preflight is outside all outcome totals.
'''
(M/'history_coverage_table.tex').write_text(coverage_tex,encoding='utf-8')

plt.rcParams.update({'font.family':'Arial','font.size':9,'axes.labelsize':9,'axes.titlesize':9,
    'xtick.labelsize':8,'ytick.labelsize':8,'legend.fontsize':9,'axes.spines.top':False,'axes.spines.right':False,
    'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','savefig.dpi':300})
colors=['#24689A','#C06225','#76549C']; markers=['o','s','^'];labels=['Degree-4k','PageRank-4k','Weighted-4k']
settings=[(.005,3),(.01,3),(.05,3),(.01,1),(.01,5)]
fig,axes=plt.subplots(4,1,figsize=(119/25.4,165/25.4),sharex=True)
for i,(ax,g) in enumerate(zip(axes,graphs)):
    for j,m in enumerate(mainmethods):
        s=param[(param.dataset==g)&(param.method==m)]
        ordered=[s[(s.p==p)&(s.h==h)].iloc[0] for p,h in settings]
        ax.errorbar(np.arange(5)+(j-1)*.18,[r.delta_mean for r in ordered],yerr=[r.delta_sd for r in ordered],fmt=markers[j],
                    color=colors[j],ms=4,capsize=2,elinewidth=.8,linestyle='none')
    ax.axhline(0,color='.55',lw=.7,zorder=0);ax.set_title(f'({chr(97+i)}) {g}',loc='left',pad=3)
    ax.set_ylabel(r'$\Delta$ (nodes)');ax.set_xlim(-.5,4.5);ax.grid(axis='y',alpha=.15)
axes[-1].set_xticks(range(5),['.005, 3','.01, 3','.05, 3','.01, 1','.01, 5']);axes[-1].set_xlabel(r'Discrete settings: $(p,h)$')
fig.legend([Line2D([],[],color=c,marker=m,linestyle='none',markersize=4) for c,m in zip(colors,markers)],labels,loc='upper center',ncol=3,frameon=False,columnspacing=.8,handletextpad=.4)
fig.subplots_adjust(top=.935,bottom=.09,left=.18,right=.98,hspace=.44)
def savefig(fig,name):
    fig.savefig(A/'figures'/f'{name}.pdf',metadata={'Creator':'Saved-result descriptive analysis'})
    fig.savefig(A/'figures'/f'{name}.svg')
    fig.savefig(A/'figures'/f'{name}.png',dpi=300)
    shutil.copy2(A/'figures'/f'{name}.pdf',M/f'{name}.pdf');plt.close(fig)
savefig(fig,'HistoryParameters')
edge=td[td.stage=='coupling'].sort_values(['dataset','path']);edge.to_csv(A/'figures/HistoryEdgeTransitions_source.csv',index=False)
param.to_csv(A/'figures/HistoryParameters_source.csv',index=False)
fig,axes=plt.subplots(4,1,figsize=(119/25.4,175/25.4),sharex=True)
for i,(ax,g) in enumerate(zip(axes,graphs)):
    t=edge[edge.dataset==g].sort_values('path')
    for changed,marker,fill in [(False,'o','white'),(True,'o',colors[0])]:
        sub=t[(t.same_set==0)==changed]
        ax.errorbar(sub.path-1000,sub.delta_full_high_low,yerr=1.96*sub.mc_se,fmt=marker,mfc=fill,mec=colors[0],color=colors[0],ms=4,capsize=2,elinewidth=.8,linestyle='none')
    ax.axhline(0,color='.55',lw=.7);ax.set_ylabel(r'$\Delta_F$ (nodes)');ax.set_title(f'({chr(97+i)}) {g}',loc='left',pad=3);ax.grid(axis='y',alpha=.15)
axes[-1].set_xticks(range(1,11));axes[-1].set_xlabel('Path (1001–1010)')
fig.legend([Line2D([],[],marker='o',mfc=c,mec=colors[0],linestyle='none',markersize=4) for c in [colors[0],'white']],['Set changed','Same set'],loc='upper center',ncol=2,frameon=False)
fig.subplots_adjust(top=.93,bottom=.09,left=.18,right=.98,hspace=.44)
savefig(fig,'HistoryEdgeTransitions')
dump(Q/'historical_input_hashes.json',input_hashes)
dump(Q/'historical_integration_validation.json',audit)
print(json.dumps({'audit':audit,'key_facts':facts},indent=2))
