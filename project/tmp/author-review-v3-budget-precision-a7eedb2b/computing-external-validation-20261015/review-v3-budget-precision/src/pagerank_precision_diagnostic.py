"""Post-hoc numerical-ranking diagnostic; no new diffusion outcomes or tuning."""
from pathlib import Path
import sys,json
import numpy as np
import pandas as pd
import networkx as nx
R=Path(__file__).resolve().parents[1];B=R.parent;sys.path.insert(0,str(B/'snapshot'));import engine
rows=[]
for ds in ['college_msg','ca_grqc','wiki_vote']:
    g=engine.load_external_graph(B/'data/raw/snap',ds);nodes=g['nodes'];graph=nx.DiGraph();graph.add_nodes_from(nodes)
    graph.add_edges_from((nodes[int(u)],nodes[int(v)]) for u,v in zip(g['sources'],g['targets']))
    strict=nx.pagerank(graph,alpha=.85,tol=1e-12,max_iter=1000,weight=None)
    order=sorted(range(len(nodes)),key=lambda i:(-strict[nodes[i]],nodes[i]))
    tighter=nx.pagerank(graph,alpha=.85,tol=1e-14,max_iter=2000,weight=None)
    order2=sorted(range(len(nodes)),key=lambda i:(-tighter[nodes[i]],nodes[i]))
    for count in [20,int(np.ceil(.05*len(nodes)))]:
        a=set(map(int,g['rankings']['pagerank'][:count]));b=set(order[:count]);c=set(order2[:count])
        rows.append({'dataset':ds,'candidate_count':count,'default_vs_strict_overlap':len(a&b),'default_vs_strict_jaccard':len(a&b)/len(a|b),'strict_vs_tighter_same_pool':b==c,'strict_added_ids':';'.join(nodes[i] for i in sorted(b-a)),'strict_removed_ids':';'.join(nodes[i] for i in sorted(a-b))})
df=pd.DataFrame(rows);df.to_csv(R/'audit/pagerank_precision_diagnostic.csv',index=False);print(df.to_string(index=False))
