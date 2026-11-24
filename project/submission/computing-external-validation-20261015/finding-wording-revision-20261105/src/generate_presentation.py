"""Read saved arrays only; no selection, diffusion, or experiment imports."""
from pathlib import Path
import csv, json, hashlib
import numpy as np

R=Path(__file__).resolve().parents[1]; P=R.parent
A=R/'analysis/presentation'; A.mkdir(exist_ok=True)
sources={}
def read(p):
    sources[str(p.relative_to(P))]=hashlib.sha256(p.read_bytes()).hexdigest()
    return json.loads(p.read_text(encoding='utf-8'))
def arrays(p):
    sources[str(p.relative_to(P))]=hashlib.sha256(p.read_bytes()).hexdigest()
    return np.load(p)
def csvout(name,rows):
    with (A/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
names={'ca_grqc':'ca-GrQc','college_msg':'CollegeMsg','wiki_vote':'wiki-Vote'}
methods={'full':'Full','degree_4k':'Degree-4k','pagerank_4k':'PR-4k','pagerank_5pct':r'PR-5\%'}
rows=[]; case=[]; details=[]
for g in names:
    for path in range(1101,1106):
        f=P/f'results/main/conditions/resolution__{g}__p{path}__w1280__step.json'
        d=read(f);z=arrays(f.with_suffix('.npz'));full=z['full_evaluation']
        assert len(full)==10000
        for m,a in d['arms'].items():
            x=z[m+'_evaluation']; diff=x-full
            assert abs(float(x.mean())-a['mean_spread'])<1e-10
            assert abs(float(diff.mean())-a['delta'])<1e-10
            row=dict(dataset=g,path=path,method=m,candidates=a['candidate_count'],coverage=a['coverage'],total=float(x.mean()),incremental=float(x.mean()-5),delta=float(diff.mean()),mc_se=float(diff.std(ddof=1)/np.sqrt(len(diff))),same_order=a['selected']==d['arms']['full']['selected'],selected=';'.join(a['selected']),selection_seconds=a['selection_seconds'])
            rows.append(row)
            if g=='wiki_vote' and path==1101 and m in methods: case.append(row)
            details.append(dict(dataset=g,path=path,W=1280,method=m,candidate_ids=';'.join(a['candidate_ids']),selected=row['selected'],trace=json.dumps(a.get('trace',[]))))
csvout('all_primary_arms_paths.csv',rows);csvout('candidate_seed_trace_index.csv',details)
csvout('wiki_case.csv',case)
summary=[]
for g in names:
    for m in methods:
        rs=[x for x in rows if x['dataset']==g and x['method']==m]
        summary.append(dict(dataset=g,method=m,n_paths=5,candidates=rs[0]['candidates'],total=np.mean([x['total'] for x in rs]),incremental=np.mean([x['incremental'] for x in rs]),delta=np.mean([x['delta'] for x in rs]),delta_path_sd=np.std([x['delta'] for x in rs],ddof=1),same_order=sum(x['same_order'] for x in rs)))
csvout('primary_summary.csv',summary)
for zh,folder in [(False,R/'manuscript'),(True,R/'chinese/manuscript')]:
    caption=('各外部网络在 $W=1280$ 下的实际输出（五条路径均值）。PR 使用默认容差。增量传播量扣除 $k=5$ 个种子；差值为受限方法减全候选参照，单位均为节点。一致性为相同选择顺序的路径数。' if zh else 'Outputs on each external network at $W=1280$ (means over five paths). PR uses default tolerance. Incremental spread subtracts $k=5$ seeds; the gap is restricted minus full spread, in nodes. Agreement counts identical ordered trajectories.')
    header=('网络 / 方法 & 候选数 & 增量传播量 & 差值 & 一致性' if zh else r'Graph / method & Candidates & Incremental & Gap & Agreement')
    lines=[r'\begin{table}[htbp]',r'\caption{'+caption+r'}\label{tab:primary}',r'\centering\begin{tabular}{lrrrr}\toprule',header+r' \\ \midrule']
    for g in names:
        lines.append(r'\multicolumn{5}{l}{\textit{'+names[g]+r'}} \\')
        for x in [x for x in summary if x['dataset']==g]:
            gap='---' if x['method']=='full' else f"{x['delta']:+.5f}"
            agree='---' if x['method']=='full' else f"{x['same_order']}/5"
            lines.append(f"{methods[x['method']]} & {x['candidates']} & {x['incremental']:.3f} & {gap} & {agree}"+r' \\')
        lines.append(r'\addlinespace')
    lines.extend([r'\bottomrule\end{tabular}',r'\end{table}'])
    (folder/'primary_table.tex').write_text('\n'.join(lines),encoding='utf-8')
    caption=('wiki-Vote 的输入与输出案例：路径1101，$k=5$、$p=.01$、$h=3$、$W=1280$、$M=10,000$，按步耦合。输入图含7,115个节点和103,689条弧。PR采用默认容差；箭头表示选择顺序。传播量是独立模拟均值，包含种子。' if zh else 'Input--output example on wiki-Vote, path 1101: $k=5$, $p=.01$, $h=3$, $W=1280$, $M=10,000$, step coupling. The input graph has 7,115 vertices and 103,689 arcs. PR uses default tolerance. Arrows indicate selection order; total spread is independently estimated and includes seeds.')
    lines=[r'\begin{table}[htbp]',r'\caption{'+caption+r'}\label{tab:case}',r'\begin{tabularx}{\linewidth}{lXr}\toprule',('方法 & 输出的种子顺序 & 总传播量' if zh else 'Method & Selected seed sequence & Total spread')+r' \\ \midrule']
    for m in methods:
        x=next(x for x in case if x['method']==m)
        seq=r'$'+r'\to '.join(x['selected'].split(';'))+'$'
        lines.append(f'{methods[m]} & {seq} & {x["total"]:.4f}'+r' \\')
    lines.extend([r'\bottomrule\end{tabularx}',r'\end{table}'])
    (folder/'input_output_case.tex').write_text('\n'.join(lines),encoding='utf-8')

# Recompute precision effects from original default and strict arrays, all three graphs,
# all budgets and five paths; W1280 is inherited from the earlier precision study.
prec=[]
for g in names:
 for w in [80,320,1280]:
  for path in range(1101,1106):
   f=P/f'results/main/conditions/resolution__{g}__p{path}__w{w}__step.json'
   d=read(f);dz=arrays(f.with_suffix('.npz'));full=dz['full_evaluation']
   base='review-v2/supplement-pr-precision' if w==1280 else 'review-v3-budget-precision/supplement-pr-budget-precision'
   s=P/f'{base}/conditions/{g}__p{path}__w{w}.json';sd=read(s);sz=arrays(s.with_suffix('.npz'))
   assert sd['frozen_reference_json_sha256']==hashlib.sha256(f.read_bytes()).hexdigest()
   for m in ['pagerank_4k','pagerank_5pct']:
    da=d['arms'][m];sa=sd['arms'][m]
    for solver,a,z in [('default',da,dz),('strict',sa,sz)]:
     x=z[m+'_evaluation']; diff=x-full
     assert abs(float(x.mean())-a['mean_spread'])<1e-10
     prec.append(dict(dataset=g,W=w,path=path,method=m,solver=solver,total=float(x.mean()),delta=float(diff.mean()),loss_percent=float(-100*diff.mean()/(full.mean()-5)),mc_se=float(diff.std(ddof=1)/100),selected=';'.join(a['selected']),candidate_ids=';'.join(a['candidate_ids']),set_changed_by_tolerance=set(da['selected'])!=set(sa['selected']),added=';'.join(sorted(set(sa['candidate_ids'])-set(da['candidate_ids']))),removed=';'.join(sorted(set(da['candidate_ids'])-set(sa['candidate_ids'])))))
csvout('precision_all_paths.csv',prec)
ps=[]
for g in names:
 for w in [80,320,1280]:
  for m in ['pagerank_4k','pagerank_5pct']:
   for solver in ['default','strict']:
    rr=[x for x in prec if (x['dataset'],x['W'],x['method'],x['solver'])==(g,w,m,solver)]
    ps.append(dict(dataset=g,W=w,method=m,solver=solver,delta=np.mean([x['delta'] for x in rr]),path_sd=np.std([x['delta'] for x in rr],ddof=1),loss_percent=np.mean([x['loss_percent'] for x in rr]),sets_changed=sum(x['set_changed_by_tolerance'] for x in rr)))
csvout('precision_summary.csv',ps)
old=list(csv.DictReader((P/'review-v3-budget-precision/analysis/precision_budget/summary_by_budget_precision.csv').open(encoding='utf-8-sig')))
for x in ps:
 match=next(y for y in old if (y['dataset'],int(y['W']),y['method'],y['solver'])==(x['dataset'],x['W'],x['method'],x['solver']))
 assert abs(x['delta']-float(match['delta_nodes_mean']))<1e-10
 assert abs(x['loss_percent']-float(match['loss_percent_mean']))<1e-10
for zh,folder in [(False,R/'manuscript'),(True,R/'chinese/manuscript')]:
 caption=('ca-GrQc PageRank-4k的精度控制。每个预算使用原五条路径；差值为受限方法减同预算全候选参照，单位为节点。SD为路径间标准差；集合变化指固定预算下默认与严格容差之间的变化。' if zh else 'Precision control for ca-GrQc PageRank-4k, using the original five paths at each budget. Gaps are restricted minus same-budget full spread, in nodes; SD is across paths. Changed sets compare default and strict tolerance at fixed $W$.')
 lines=[r'\begin{table}[htbp]',r'\caption{'+caption+r'}\label{tab:precision-output}',r'\centering\begin{tabular}{rrrr}\toprule',('$W$ & 默认差值（SD） & 严格差值（SD） & 集合变化' if zh else '$W$ & Default gap (SD) & Strict gap (SD) & Changed sets')+r' \\ \midrule']
 for w in [80,320,1280]:
  d,s=[next(x for x in ps if (x['dataset'],x['W'],x['method'],x['solver'])==('ca_grqc',w,'pagerank_4k',sol)) for sol in ['default','strict']]
  lines.append(f"{w} & {d['delta']:+.5f} ({d['path_sd']:.5f}) & {s['delta']:+.5f} ({s['path_sd']:.5f}) & {s['sets_changed']}/5"+r' \\')
 lines.extend([r'\bottomrule\end{tabular}',r'\end{table}'])
 (folder/'precision_output.tex').write_text('\n'.join(lines),encoding='utf-8')

si=[r'\section{Candidate-to-seed outputs from saved records}',r'The main-text example uses wiki-Vote path 1101 for illustration. The primary table averages paths 1101--1105 separately on each graph. These displays use the frozen step-coupled $W=1280$ results. Machine-readable tables provide every primary arm, including Degree-5\%, weighted pools where defined and all three random pools separately. Random-pool inferential summaries remain the within-path means specified in Methods.',r'\input{precision_output.tex}',r'Tightening ca-GrQc PageRank-4k tolerance removes IDs 1488 and 19865 and admits 17655 and 6610. The table compares the resulting seeds at fixed $W$. The CSV precision\_all\_paths.csv retains both pool sizes, all three networks, every budget and path, selected node IDs, signed gaps and conditional Monte Carlo standard errors. It separates these conditional errors from the across-path SD in the table.',r'\subsection{Seed sequences for the complete ca-GrQc precision comparison}',r'\begin{longtable}{rrll}',r'\caption{ca-GrQc PageRank-4k sequences at default and strict tolerance. Node IDs are in selection order.}\label{tab:precision-seeds}\\',r'\toprule $W$ & Path & Tolerance & Selected IDs \\ \midrule\endfirsthead',r'\toprule $W$ & Path & Tolerance & Selected IDs \\ \midrule\endhead']
for x in prec:
 if x['dataset']=='ca_grqc' and x['method']=='pagerank_4k':
  si.append(f"{x['W']} & {x['path']} & {x['solver']} & {x['selected'].replace(';', ', ')}"+r' \\')
si.extend([r'\bottomrule\end{longtable}',r'Candidate and seed identifiers and the saved round-by-round winner traces are indexed in candidate\_seed\_trace\_index.csv. Full integer candidate-score matrices remain in each original condition NPZ under the key method\_round\_totals; these are selection-world scores, not independently assessed prefix utilities. The corresponding method\_evaluation arrays contain 10,000 total-spread counts. No activation-node paths are reconstructed from those counts.'])
(R/'manuscript/presentation_supplement.tex').write_text('\n'.join(si),encoding='utf-8')
(A/'source_hashes.json').write_text(json.dumps(sources,indent=2),encoding='utf-8')
(R/'qa/numerical_checks.json').write_text(json.dumps(dict(status='PASS',primary_arm_paths=len(rows),precision_arm_paths=len(prec),precision_summaries_matched=len(ps),evaluations_per_arm=10000,new_experiments=False),indent=2),encoding='utf-8')
print('PASS',len(rows),'primary arms;',len(prec),'precision records;',len(ps),'summaries match archived analysis')
