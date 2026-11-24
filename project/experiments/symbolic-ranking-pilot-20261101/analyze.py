from pilot import *
from sklearn.linear_model import Ridge
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

def main():
 assert json.loads((BASE/'execution_status.json').read_text())['status']=='COMPLETE'
 t=time.perf_counter();data=pd.read_csv(BASE/'runs.csv');df=data[data.arm=='restricted'].copy().reset_index(drop=True);y=df.instability.to_numpy();X=df[['x','o','c']].to_numpy();tr=df.split.eq('train').to_numpy();va=df.split.eq('validation').to_numpy();te=df.split.eq('test').to_numpy()
 def gmse(pred,mask):return float(pd.DataFrame(dict(graph=df.graph[mask],e=(y[mask]-pred[mask])**2)).groupby('graph').e.mean().mean())
 def exprs():
  # deterministic complete leaves and binary expressions, then ordered bounded extensions
  leaves=[('x',1,X[:,0]),('o',1,X[:,1]),('c',1,X[:,2])];out=list(leaves)
  def combine(a,b,op):
   if op=='+':z=a[2]+b[2]
   elif op=='-':z=a[2]-b[2]
   elif op=='*':z=a[2]*b[2]
   else:z=a[2]/(1+np.abs(b[2]))
   return (f'({a[0]}{op}{b[0]})',a[1]+b[1]+1,z)
  level3=[combine(a,b,op) for op in ['+','-','*','/'] for a in leaves for b in leaves];out+=level3
  out += [combine(a,b,op) for op in ['+','-','*','/'] for a in leaves for b in level3]
  out += [combine(a,b,op) for op in ['+','-','*','/'] for a in level3 for b in leaves]
  out += [combine(a,b,op) for op in ['+','-','*','/'] for a in level3 for b in level3]
  return out[:1200]
 ex=exprs();search=[]
 def fitone(z,idx):
  z=np.asarray(z).reshape(len(df),-1);m=Ridge(alpha=1).fit(z[idx],y[idx]);return np.clip(m.predict(z),0,1),m
 def searchsr(idx):
  st=time.perf_counter();best=None
  for name,length,z in ex:
   pred,m=fitone(z,idx);v=gmse(pred,va);key=v+.002*length
   if best is None or key<best['criterion']:best=dict(expression=name,nodes=length,validation_mse=v,criterion=key,intercept=float(m.intercept_),coefficient=list(map(float,m.coef_)),pred=pred)
   if time.perf_counter()-st>60:raise RuntimeError('SR search time exceeded; do not silently truncate')
  best['search_seconds']=time.perf_counter()-st;return best
 pred={};models={};pred['constant']=np.full(len(df),y[tr].mean())
 for name,z in [('ratio_linear',X[:,0]),('linear_structure',X)]:
  pred[name],m=fitone(z,tr);models[name]=dict(intercept=float(m.intercept_),coefficients=list(map(float,m.coef_)))
 best=searchsr(tr);pred['symbolic']=best.pop('pred');models['symbolic']=best
 # Freeze selected model and baseline BEFORE metrics on test labels.
 simple=min(['constant','ratio_linear','linear_structure'],key=lambda n:gmse(pred[n],va));models['selected_simple_on_validation']=simple
 dump('selected_models.json',models)
 stability=[]
 graphlist=sorted(df.loc[tr,'graph'].unique())
 for seed in [7101,7102,7103]:
  rng=np.random.default_rng(seed);sample=rng.choice(graphlist,len(graphlist),replace=True);idx=np.concatenate([np.flatnonzero(tr & df.graph.eq(g).to_numpy()) for g in sample]);b=searchsr(idx);p=b.pop('pred');b.update(seed=seed,sampled_graphs=list(sample),test_mse=gmse(p,te),beats_simple=gmse(p,te)<gmse(pred[simple],te));stability.append(b)
 dump('formula_stability.json',stability)
 rows=[]
 for name,p in pred.items():
  df['pred_'+name]=p
  for group in ['train','validation','test']:
   mask=df.split.eq(group).to_numpy()
   for g in df.loc[mask,'graph'].unique():
    ix=df.graph.eq(g).to_numpy();rows.append(dict(model=name,split=group,graph=g,n=int(ix.sum()),mse=float(np.mean((p[ix]-y[ix])**2)),mae=float(np.mean(np.abs(p[ix]-y[ix])))))
 metrics=pd.DataFrame(rows);metrics.to_csv(BASE/'model_metrics_by_graph.csv',index=False);df.to_csv(BASE/'predictions.csv',index=False)
 summary=metrics.groupby(['split','model'])[['mse','mae']].agg(['mean','std']);summary.to_csv(BASE/'model_metrics_summary.csv')
 test=metrics[metrics.split=='test'].pivot(index='graph',columns='model',values='mse');improvement=(test[simple].mean()-test.symbolic.mean())/test[simple].mean();pergraph=(test[simple]-test.symbolic)
 # Conditional graph-resampling interval, not representative network-population CI.
 rng=np.random.default_rng(7201);boot=np.array([rng.choice(pergraph.to_numpy(),len(pergraph),replace=True).mean() for _ in range(2000)])
 dump('model_decision.json',dict(primary='graph-equal MSE of final seed-set 1-Jaccard vs independent finite W1280 reference',simple_selected=simple,relative_mse_improvement=float(improvement),graphs_improved=int((pergraph>0).sum()),test_graphs=len(test),resample_positive=sum(b['beats_simple'] for b in stability),formula_structures=[b['expression'] for b in stability],paired_mse_reduction=float(pergraph.mean()),conditional_graph_bootstrap95=list(np.quantile(boot,[.025,.975])),search_expressions=len(ex),analysis_seconds=time.perf_counter()-t))
 # Paired utility differences reuse the disjoint evaluation arrays, never selection margins.
 transitions=[];prutility=[]
 for graph,gdf in data.groupby('graph',sort=False):
  arrays=np.load(BASE/'raw'/f'{graph}_evaluation.npz');index=json.loads((BASE/'raw'/f'{graph}_evaluation_index.json').read_text());lookup={tuple(v):arrays[k].astype(float) for k,v in index.items()}
  def values(row):return lookup[tuple(sorted(json.loads(row.seeds)))]
  def diff(a,b):
   d=values(b)-values(a);mean=float(d.mean());se=float(d.std(ddof=1)/np.sqrt(len(d)));return dict(delta=mean,se=se,low=mean-1.96*se,high=mean+1.96*se,distinguishable=abs(mean)>1.96*se)
  for (arm,path),gg in gdf[gdf.arm.isin(['restricted','full'])].groupby(['arm','path']):
   gg=gg.sort_values('W');rr=list(gg.itertuples(index=False))
   for a,b in zip(rr[:-1],rr[1:]):transitions.append(dict(graph=graph,arm=arm,path=path,W_from=a.W,W_to=b.W,set_jaccard=jacc(json.loads(a.seeds),json.loads(b.seeds)),order_equal=a.seeds==b.seeds,spread_from=a.spread,spread_to=b.spread,**diff(a,b)))
  aa=gdf[gdf.arm=='pr_default'];bb=gdf[gdf.arm=='pr_reference']
  if len(aa):
   a=next(aa.itertuples(index=False));b=next(bb.itertuples(index=False));prutility.append(dict(graph=graph,set_jaccard=jacc(json.loads(a.seeds),json.loads(b.seeds)),spread_default=a.spread,spread_reference=b.spread,**diff(a,b)))
 pd.DataFrame(transitions).to_csv(BASE/'budget_transitions.csv',index=False);pd.DataFrame(prutility).to_csv(BASE/'pagerank_utility.csv',index=False)
 pr=pd.read_csv(BASE/'pagerank.csv');cert=pr.certified
 dump('diagnostic_summary.json',dict(pr_conditions=len(pr),pr_changed=int((pr.replacements>0).sum()),certified=int(cert.sum()),certified_violations=int((cert&(pr.replacements>0)).sum()),uncertified_stable=int((~cert&(pr.replacements==0)).sum()),restricted_conditions=len(df),rounds=len(pd.read_csv(BASE/'rounds.csv'))))
 figdir=BASE/'figures';figdir.mkdir(exist_ok=True);plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
 fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
 for name,gg in pr.groupby('graph'):
  axes[0].scatter(np.log10(np.maximum(gg.ratio,1e-15)),gg.replacements,s=18,alpha=.65)
 axes[0].axvline(0,c='black',ls='--');axes[0].set(xlabel='log10(2 residual / (0.15 gap))',ylabel='Candidate replacements',title='A: sufficient bound is conservative')
 rd=pd.read_csv(BASE/'rounds.csv');rd=rd[rd.arm=='restricted'];stats=rd.groupby('W').ties.apply(lambda s:(s>1).mean());axes[1].plot(stats.index,stats.values,'o-');axes[1].set(xscale='log',xlabel='Selection worlds W',ylabel='Fraction of tied rounds',title='B: finite-world ties')
 fig.savefig(figdir/'diagnostics.png',dpi=180);fig.savefig(figdir/'diagnostics.pdf');plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained');test.plot.bar(ax=axes[0]);axes[0].set(ylabel='Held-out graph MSE',title='Prediction of seed-set instability');axes[0].legend(fontsize=7);axes[0].tick_params(axis='x',rotation=45)
 trans=pd.DataFrame(transitions);realtrans=trans[trans.graph.isin(['college_msg','ca_grqc','wiki_vote'])]
 forest=realtrans[realtrans.path==4101].copy().reset_index(drop=True)
 for arm,gg in forest.groupby('arm'):
  axes[1].errorbar(gg.delta,gg.index,xerr=1.96*gg.se,fmt='o',label=arm,alpha=.8)
 labels=[f'{r.graph} {r.arm} {r.W_from}->{r.W_to}' for r in forest.itertuples()]
 axes[1].set_yticks(range(len(forest)),labels,fontsize=6)
 axes[1].axvline(0,c='black',lw=.8);axes[1].set(xlabel='Spread change with conditional 95% CI',title='Each arm, path 4101');axes[1].legend(fontsize=7)
 fig.savefig(figdir/'models_utility.png',dpi=180);fig.savefig(figdir/'models_utility.pdf');plt.close(fig)
 print(summary.to_string());print(json.dumps(json.loads((BASE/'model_decision.json').read_text()),indent=2))
if __name__=='__main__':main()
