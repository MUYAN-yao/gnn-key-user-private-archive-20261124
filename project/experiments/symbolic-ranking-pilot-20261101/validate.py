from pilot import *
def main():
 checks=[]
 # Deliberate tiny graph: 0->1->2; all edges open, horizon3 reaches 3; reversed seed reaches 1.
 ptr=np.array([0,1,2,2],dtype=np.int64);targets=np.array([1,2],dtype=np.int64);ww=np.ones((4,3,2),dtype=np.bool_)
 assert np.all(en.evaluate(ptr,targets,ww,np.array([0],dtype=np.int64),3)==3)
 assert np.all(en.evaluate(ptr,targets,ww,np.array([2],dtype=np.int64),3)==1)
 shut=np.zeros_like(ww);s,tot=en.greedy(ptr,targets,shut,np.array([2,0,1],dtype=np.int64),2,3);assert list(s)==[0,1]
 checks+=['directed cascade hand check','exact tie picks lexicographic index']
 for file in ['engine.py','legacy_engine.py']:
  assert (BASE/file).read_bytes()==(PROJECT/'submission/computing-external-validation-20261015/snapshot'/file).read_bytes()
 checks+=['copied engine byte identity']
 rows=[]
 for name in ['college_msg','ca_grqc','wiki_vote']:
  g=real(name);x,r,res,it,sec=pagerank(g,1e-6);G=nx.DiGraph();G.add_nodes_from(g['nodes']);G.add_edges_from((g['nodes'][u],g['nodes'][v]) for u,v in zip(g['sources'],g['targets']));scores=nx.pagerank(G,alpha=.85,tol=1e-6,weight=None);z=np.array([scores[node] for node in g['nodes']]);assert np.max(np.abs(x-z))<1e-13
  rows.append(dict(graph=name,max_score_difference_networkx=float(np.max(np.abs(x-z))),default_pool20_matches_legacy=set(r[:20])==set(g['rankings']['pagerank'][:20])))
 checks+=['PR score parity against installed NetworkX']
 if (BASE/'execution_status.json').exists():
  runs=pd.read_csv(BASE/'runs.csv');pr=pd.read_csv(BASE/'pagerank.csv');rounds=pd.read_csv(BASE/'rounds.csv');assert len(runs)==219;assert len(pr)==150;assert len(rounds)==1095
  assert not runs[['instability','spread','delta_se']].isna().any().any();assert runs.spread.between(5,7115).all();assert not ((pr.certified)&(pr.replacements>0)).any()
  for name in runs.graph.unique():
   a=np.load(BASE/'raw'/f'{name}_evaluation.npz');assert len(a['world_ids'])==10000
   for k in a.files:
    if k!='world_ids':assert ((a[k]>=5)&(a[k]<=7115)).all()
  checks+=['complete frozen matrix counts','nonmissing bounded utility and stability','no violated numerical sufficient certificates','10000 evaluation worlds in every graph']
 dump('qa.json',dict(status='PASS',checks=checks,networkx_parity=rows))
 print('PASS',checks)
if __name__=='__main__':main()
