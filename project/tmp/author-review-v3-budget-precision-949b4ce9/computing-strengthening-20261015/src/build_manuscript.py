"""Assemble the author-review manuscript and supplement from validated outputs."""
import sys,json,re,shutil
from pathlib import Path
import numpy as np
import pandas as pd

TITLE='Selection Resolution, Random-World Coupling, and Utility in Candidate-Restricted Influence Maximization'
REAL=['invs2013','invs2015','kenya2012','sfhh2009']
METHODS=['weighted_2k','weighted_4k','weighted_8k','degree_4k','pagerank_4k','random_4k']
LABELS={'weighted_2k':'Weighted $2k$','weighted_4k':'Weighted $4k$','weighted_8k':'Weighted $8k$','degree_4k':'Degree $4k$','pagerank_4k':'PageRank $4k$','random_4k':'Random $4k$','full':'Full'}

def tex(v):return str(v).replace('_',r'\_').replace('%',r'\%')
def number(x,d=3):return f'{float(x):.{d}f}'
def fig(name,caption,label):
    return '\n\\begin{figure}[htbp]\n\\centering\n\\includegraphics[width=\\linewidth]{'+name+'.pdf}\n\\caption{'+caption.rstrip('.')+'}\\label{'+label+'}\n\\end{figure}\n'
def table(caption,label,head,rows,spec):
    return '\n\\begin{table}[t]\n\\caption{'+caption+'}\\label{'+label+'}\n\\centering\n\\begin{tabular}{'+spec+'}\n\\toprule\n'+' & '.join(head)+' \\\\\n\\midrule\n'+'\n'.join(' & '.join(map(str,r))+' \\\\' for r in rows)+'\n\\bottomrule\n\\end{tabular}\n\\end{table}\n'

def main(project,base):
    project=Path(project);base=Path(base);a=base/'analysis'
    status=json.loads((a/'validation.json').read_text());assert status['status']=='PASS'
    summary=json.loads((a/'summary.json').read_text());g=pd.read_csv(a/'group_summary.csv');d=pd.read_csv(a/'path_level_metrics.csv');tr=pd.read_csv(a/'reference_transitions.csv');tests=pd.read_csv(a/'primary_sign_tests_holm.csv');tol=pd.read_csv(a/'tolerance_sensitivity.csv')
    out=base/'manuscript';out.mkdir(exist_ok=True)
    old=project/'c-users-36024-downloads-texlive2026-20260301/outputs/computing_latex'
    original=(old/'manuscript.tex').read_text(encoding='utf-8')
    for name in ['svjour3.cls','svglov3.clo']:shutil.copy2(old/name,out/name)
    for name in ['Fig1','Fig2','Fig3','Fig4','Fig5']:shutil.copy2(a/'figures'/(name+'.pdf'),out/(name+'.pdf'))
    primary=g[(g.stage=='resolution')&(g.W==5120)]
    tmain=tr[tr.stage=='resolution'];last=tmain[tmain.high==5120]
    w4=primary[primary.method=='weighted_4k'];de=primary[primary.method=='degree_4k']
    lost_range=(-w4.delta_mean.max(),-w4.delta_mean.min())
    changed=int((~last.same_set).sum());same=40-changed
    primary_paths=d[(d.stage=='resolution')&(d.W==5120)]
    degree_matches=int(primary_paths[primary_paths.method=='degree_4k'].same_order.sum())
    pagerank_matches=int(primary_paths[primary_paths.method=='pagerank_4k'].same_order.sum())
    abstract=(
      'Candidate restriction can accelerate greedy influence maximization, but its evaluation depends on the finite simulation reference. '
      'We examine selection resolution, random-world coupling, independently evaluated utility and attributable computation cost in a common protocol. '
      'An archived experiment on four contact-derived networks is extended by 520 conditions and 4,680 arm executions, using ten random paths per real network, selection budgets up to 5,120 worlds and 10,000 disjoint evaluation worlds. '
      'Controls include alternative candidate rankings, propagation parameters, fixed-edge coupling and two synthetic 2,000-node instances. '
      f'Between 1,280 and 5,120 selection worlds, {changed} of 40 full-greedy final sets changed, while average independent spread increased by {last.delta_full_high_low.mean():.3f} nodes. '
      f'At the highest budget, weighted-degree 4k pools had network-specific mean spread differences ranging from {w4.delta_mean.min():.3f} to {w4.delta_mean.max():.3f} activated nodes relative to full greedy. '
      f'Topology-degree and PageRank 4k pools reproduced {degree_matches}/40 and {pagerank_matches}/40 ordered references, respectively, showing that weighted-degree losses do not characterize all restrictions. '
      'A three-node counterexample shows that step-indexed shared randomness need not produce a monotone finite-world objective, motivating an explicit coupling control. '
      'The results separate decision reproduction from utility and expose the dependence of cost-quality interpretations on coverage, ranking and timing scope. '
      'The supplied tolerance curves are descriptive; they do not establish practical equivalence, convergence to expected-influence greedy selection or generality beyond the tested simulated settings.'
    )
    words=len(abstract.split());assert 150<=words<=250,words
    author_start=original.index('\\author{');author_end=original.index('\\date{}',author_start)
    authors=original[author_start:author_end]
    preamble=r'''\documentclass[smallextended]{svjour3}
\usepackage{fix-cm}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{mathptmx}
\usepackage{amsmath,amssymb,graphicx,booktabs,tabularx,url}
\usepackage{placeins}
\usepackage[numbers,sort&compress]{natbib}
\usepackage[hidelinks]{hyperref}
\journalname{Computing}
\smartqed
\begin{document}
'''
    header=preamble+'\\title{'+TITLE+'}\n\\titlerunning{Selection resolution, coupling and utility}\n'+authors+'\\date{}\n\\maketitle\n\\begin{abstract}\n'+abstract+'\n\\keywords{influence maximization \\and Monte Carlo simulation \\and candidate restriction \\and reproducibility \\and network optimization}\n\\end{abstract}\n'
    result=r'\section{Results}'+'\n'+r'\subsection{Implementation validation and evidence continuity}'+'\n'
    result+=('All 42 archived output hashes matched the historical validation ledger. The accelerated engine reproduced 32 archived arm traces and all 64,000 corresponding per-world evaluation values exactly. Boundary checks covered empty seed sets, zero and unit transmission probability, and horizons zero through three. Additional cyclic-graph checks matched the original simulator, while fixed-edge results matched an independent shortest-path reachability oracle. These checks support semantic continuity rather than a new algorithm claim.\n\n')
    result+=('The original experiment changed all 14 full-greedy final sets at each adjacent transition, 20 to 80 and 80 to 320 worlds. Its weighted $2k$, $4k$ and $8k$ pools matched 0/42, 12/42 and 18/42 ordered traces; after excluding full-pool controls, the respective counts were 0/42, 6/36 and 6/30. These historical counts are not combined with new paths as independent replications.\n\n')
    result+=(f'The extension completed all {status["conditions"]} specified conditions and {status["arm_executions"]:,} arm executions, retaining {status["evaluation_values"]:,} evaluation counts. Source and result hashes, per-round greedy choices, full-pool consistency and paired statistics passed the independent output validator. Total serial execution lasted {summary["runtime_minutes"]:.1f} minutes; the recorded peak process working set was {summary["max_peak_mb"]:.0f} MiB. The machine had 20 physical CPU cores and approximately 32 GiB RAM, but experiment computation used one worker. Python 3.13.0, NumPy 2.3.3 and Numba 0.68.0 were used.\n\n')
    result+=r'\subsection{Membership and utility under higher selection resolution}'+'\n'
    for low,high in [(20,80),(80,320),(320,1280),(1280,5120)]:
        b=tmain[(tmain.low==low)&(tmain.high==high)]
        result+=(f'At the {low:,} to {high:,} transition, {int((~b.same_set).sum())}/40 final sets changed; mean Jaccard overlap was {b.jaccard.mean():.3f}. ')
    result+='These summaries describe forty network/path blocks, not forty independently collected networks. Figure~\\ref{fig:reference} juxtaposes membership changes with independently evaluated incremental spread.\n\n'
    rows=[]
    for ds in REAL:
        q=g[(g.stage=='resolution')&(g.dataset==ds)&(g.method=='full')].set_index('W');t=last[last.dataset==ds]
        rows.append([ds,number(q.loc[20,'incremental_spread_mean']),number(q.loc[5120,'incremental_spread_mean']),f'{int(t.same_set.sum())}/10',number(t.delta_full_high_low.mean())])
    result+=table('Full-reference utility and final membership. Incremental spread averages ten paths. Last-column differences compare 5,120 with 1,280 worlds on paired independent evaluations; small means are not equivalence tests.','tab:reference',['Network','Inc. $W=20$','Inc. $W=5120$','Same set','Last $\\Delta$'],rows,'lrrrr')
    result+='The last two budgets therefore provide a direct check on the practical interpretation of changed membership. Membership changes and small average utility changes do not resolve whether greedy selection has converged for the expected objective. Individual path differences and conditional Monte Carlo intervals are retained in the source tables described in Online Resource 1.\n'
    result+=(f'Across these forty blocks, the last transition increased independent spread by {last.delta_full_high_low.mean():.4f} nodes on average. Kenya changed all ten final sets whereas SFHH changed none. Thus the remaining membership instability was strongly network-dependent and did not imply a comparably large mean utility change.\n')
    result+=fig('Fig1','Reference membership and independent utility on four real networks ($k=5$, $p=0.01$, $h=3$, step coupling). (a) Thin lines show all ten path trajectories per network; thick lines show mean adjacent-budget Jaccard overlap. (b) Mean full-greedy incremental spread with 95\\% percentile bootstrap intervals over ten paths. Evaluation uses 10,000 disjoint worlds per path. Intervals concern computational paths on fixed graphs; they are not population-network intervals. Colours and marker shapes identify networks.','fig:reference')
    result+=r'\subsection{Candidate rankings and practical loss}'+'\n'
    result+='At $W=5120$, weighted-degree $4k$ pools had the following mean paired spread differences (candidate minus full): '
    result+=', '.join(f'{ds}: {w4[w4.dataset==ds].delta_mean.iloc[0]:.3f}' for ds in REAL)+'. Figure~\\ref{fig:effects} reports all six candidate types and the across-path intervals, rather than selecting the best pool for each graph.\n\n'
    result+=(f'In contrast, topology-degree and PageRank $4k$ pools reproduced {degree_matches}/40 and {pagerank_matches}/40 ordered full references, respectively. These were genuine restrictions: their twenty eligible nodes represented 5.0--26.7\\% of each graph. PageRank therefore had exactly zero paired differences at this setting; degree differed only on one Kenya path, with a slightly higher independently estimated spread. These observations do not establish a universal ranking advantage or future-path equivalence.\n\n')
    rows=[]
    for ds in REAL:
        q=g[(g.stage=='resolution')&(g.dataset==ds)].set_index(['method','W'])
        rows.append([ds,number(q.loc[('weighted_4k',20),'delta_mean']),number(q.loc[('weighted_4k',5120),'delta_mean']),number(q.loc[('degree_4k',20),'delta_mean']),number(q.loc[('degree_4k',5120),'delta_mean'])])
    result+=table('Mean candidate-minus-full spread changes with reference resolution. W4 and D4 denote weighted-degree and topology-degree $4k$ pools. Each entry averages ten paired path comparisons; signs of means are descriptive, not separate significance claims.','tab:budget-effects',['Network','W4: 20','W4: 5120','D4: 20','D4: 5120'],rows,'lrrrr')
    result+='Weighted $4k$ had positive mean differences against the low-budget full reference on all four graphs, but negative means against the highest-budget reference (Table~\\ref{tab:budget-effects}). The reference quality therefore changes the apparent utility conclusion, not only the trace-match count. Topology degree also gained relative to the low-budget reference, while largely reproducing it at high resolution. This pattern is consistent with a reduced candidate space limiting noisy low-budget choices, but the present contrasts do not isolate that causal mechanism.\n\n'
    primary_d=d[(d.stage=='resolution')&(d.W==5120)&(d.method.isin(METHODS))]
    sig=tests[tests.p_holm<.05];pos=int((sig.mean_delta>0).sum());neg=int((sig.mean_delta<0).sum())
    result+=(f'In the 24-contrast primary sign-test family, {len(sig)} contrasts survived Holm correction at 0.05 ({neg} with negative and {pos} with positive mean differences). The exact tests assess positive/negative balance after dropping zero path differences; they do not test mean equivalence. All unadjusted and adjusted values, zero counts and activated-node effect sizes are supplied in Online Resource 1.\n\n')
    result+='At matched $4k$ coverage, the topology-degree and historical-weighted-degree results can be compared without changing candidate count. Their differences concern the simulator\'s use of distinct edges rather than event-frequency edge probabilities. Random-pool repetitions are averaged within path and do not triple the inferential sample size.\n'
    result+=fig('Fig2','Primary candidate-minus-full spread differences at $W=5120$, $k=5$, $p=0.01$, $h=3$ under step coupling. Points are means of ten path-level differences; horizontal segments are 95\\% percentile bootstrap intervals using 10,000 path resamples. Random $4k$ averages three pools within each path. All six candidate types are shown. Horizontal scales differ by network to retain small effects. Zero denotes the full reference, not an equivalence boundary.','fig:effects')
    result+=r'\subsection{Time savings and loss tolerance}'+'\n'
    result+='For weighted $4k$ at the primary budget, mean selection-time savings were '
    result+=', '.join(f'{ds}: {100*w4[w4.dataset==ds].selection_saving_mean.iloc[0]:.1f}\\%' for ds in REAL)+'. These percentages exclude shared world preparation. The attributed full-pipeline savings, which include preparation and final evaluation, are reported separately in the source tables.\n\n'
    pr=primary[primary.method=='pagerank_4k']
    result+=(f'PageRank $4k$, which reproduced all forty primary references, saved {100*pr.selection_saving_mean.min():.1f}--{100*pr.selection_saving_mean.max():.1f}\\% of selection time across network means; after charging shared preparation and evaluation, savings were {100*pr.end_to_end_saving_mean.min():.1f}--{100*pr.end_to_end_saving_mean.max():.1f}\\%. These are observed cost advantages for this setting, not a guarantee at other budgets or on unseen graphs.\n\n')
    result+='At a loss tolerance of 5\\%, the point estimates met the threshold for '
    tt=tol[(tol.method=='weighted_4k')&(tol.tolerance==.05)]
    result+=', '.join(f'{int(round(tt[tt.dataset==ds].point_fraction.iloc[0]*10))}/10 paths on {ds}' for ds in REAL)+'. This is a description of point estimates at one chosen grid value, not evidence that 5\\% is an acceptable application loss or a successful noninferiority test. Figure~\\ref{fig:tradeoff} shows the entire prespecified tolerance grid.\n'
    result+=fig('Fig3','Cost and descriptive tolerance for the prespecified weighted $4k$ diagnostic at $W=5120$. (a) Every one of ten paths per real network is shown; the horizontal axis is selection-only time saving, and the vertical axis is loss relative to full incremental spread. Negative loss denotes a higher candidate estimate. (b) Fraction of paths whose point estimate meets each illustrative tolerance. These are fixed-grid descriptions with a point-estimate denominator, not inferential preservation decisions. All other candidate types remain in the source tables.','fig:tradeoff')
    result+=r'\subsection{Propagation, coupling and structural sensitivity}'+'\n'
    result+='The predefined parameter and coupling controls extend the primary setting without changing the candidate rankings. Table~\\ref{tab:sensitivity} gives the weighted $4k$ comparison at representative predefined conditions; Figure~\\ref{fig:sensitivity} shows all five propagation settings, both couplings and both synthetic instances for its designated panels.\n'
    rows=[]
    for ds in REAL:
        def grab(p,h,c,W):return g[(g.dataset==ds)&(g.k==5)&(g.p==p)&(g.h==h)&(g.coupling==c)&(g.W==W)&(g.method=='weighted_4k')].iloc[0]
        lo=grab(.005,3,'step',320);hi=grab(.05,3,'step',320);st=grab(.01,3,'step',1280);ed=grab(.01,3,'edge',1280)
        rows.append([ds,number(lo.delta_mean),number(hi.delta_mean),number(st.delta_mean),number(ed.delta_mean)])
    result+=table('Mean weighted $4k$ minus full spread differences. First two columns vary transmission probability at $W=320,h=3$; last two compare couplings at $W=1280,p=0.01,h=3$. Ten paths per cell.','tab:sensitivity',['Network','$p=.005$','$p=.05$','Step','Fixed edge'],rows,'lrrrr')
    result+='These contrasts identify sensitivity within the specified grid. They do not establish that one coupling estimates real diffusion more accurately. The two synthetic instances contain 2,000 nodes each, but have only one generated topology of each type. Their five paths measure computational variability on that topology; their agreement cannot substitute for additional real-network evidence. The $k=20$ results similarly retain saturated pools as controls and are tabulated separately.\n'
    result+=fig('Fig4','Predefined sensitivity panels. (a) Weighted $4k$ mean incremental loss across ten paths at $W=320$ for all five $(p,h)$ settings, including the primary setting. (b) The same candidate type under step and fixed-edge coupling at $W=1280$. (c) All six candidate types on two explicitly synthetic 2,000-node instances at $W=320$, five paths each; W/D/PR/R denote weighted degree, degree, PageRank and random. Lines connect tested settings without implying interpolation. These panels are descriptive means; all path values and uncertainty summaries are supplied as source data.','fig:sensitivity')
    result+=r'\subsection{Repeated timing}'+'\n'
    result+='The five additional repetitions per real graph and arm produced 180 timing observations. Selected sets and all evaluated spreads were unchanged within those repetitions. Figure~\\ref{fig:timing} separates selection and evaluation. Repetition measures execution variability in the compiled implementation; it does not increase the number of independent utility observations. Common world preparation and graph preparation remain outside the stacked bars and inside the separately reported full-pipeline attribution.\n'
    result+=fig('Fig5','Repeated timing at $k=5,W=320$, path 1001, $p=0.01,h=3$, step coupling. Bars stack the median selection and evaluation times over five additional randomized serial repetitions; dots show each repetition\'s total of those phases. Full and all eight restricted executions are retained. W2/W4/W8 denote weighted pools; D4 and PR4 denote topology-degree and PageRank; R0--R2 are separate random pools. Shared preprocessing and JIT compilation are excluded from this figure and reported separately.','fig:timing')
    (out/'results_generated.tex').write_text(result,encoding='utf-8')
    body=(base/'src/paper_body.tex').read_text(encoding='utf-8')
    body=body.replace('a Barabasi--Albert graph with attachment parameter 3','a Barabasi--Albert graph \\cite{ref17} with attachment parameter 3').replace('a stochastic block model with four blocks','a stochastic block model \\cite{ref18} with four blocks')
    funding='Funding: The prior draft reports support from a provincial undergraduate innovation and entrepreneurship training project. The official project title and grant number require author confirmation before submission.'
    declarations=r'''\paragraph{Supplementary information.} Online Resource 1 contains implementation-audit details, the complete primary effect and sign-test tables, round diagnostics, larger-seed-budget summaries and a map to the accompanying reproducibility files.
\section*{Statements and Declarations}
\paragraph{Funding.} This work was supported by a provincial undergraduate innovation and entrepreneurship training project.
\paragraph{Competing interests.} The preceding author draft declares no competing interests.
\paragraph{Author contributions.} The preceding author draft records these roles. Jiayue Sun: conceptualization, methodology, software, validation, analysis, investigation, curation, visualization and original drafting. Binbin Yong: supervision, methodology, project administration, review and editing. Junjie An: software, curation, review and editing. Tianyu Bo: validation, visualization, review and editing. Shuai Li: analysis, validation, review and editing.
\paragraph{Data availability.} The provider records cited above supply the contact data. The accompanying package supplies source references, hashes and preprocessing code; it does not redistribute the provider archives. Synthetic graphs can be regenerated from the documented model parameters and seed. All condition-level results and figure source tables accompany the reproducibility package.
\paragraph{Code availability.} Source snapshots, configuration, validators, analysis and plotting scripts are included in the accompanying reproducibility package.
\paragraph{Use of AI tools.} OpenAI Codex assisted this revision through code development, implementation checks, analysis scripting, figure scripting and manuscript drafting. Verification, scientific interpretation and final approval remain the responsibility of the human authors.
'''
    refs=original[original.index('\\begin{thebibliography}'):original.index('\\end{thebibliography}')]
    refs=refs.replace('Proceedings of the ninth ACM SIGKDD international conference on knowledge discovery and data mining','ACM SIGKDD').replace('Proceedings of the 2015 ACM SIGMOD international conference on management of data','ACM SIGMOD')
    refs+=r'''
\bibitem{ref17} Barabasi A-L, Albert R (1999) Emergence of scaling in random networks. Science 286:509--512. \url{https://doi.org/10.1126/science.286.5439.509}
\bibitem{ref18} Holland PW, Laskey KB, Leinhardt S (1983) Stochastic blockmodels: first steps. Social Networks 5:109--137. \url{https://doi.org/10.1016/0378-8733(83)90021-7}
\bibitem{ref19} Ko J, Kim S, Lee K, et al. (2025) Inductive influence estimation and maximization over unseen social networks under two diffusion models. Data Mining and Knowledge Discovery 39:55. \url{https://doi.org/10.1007/s10618-025-01137-z}
\end{thebibliography}
'''
    (out/'manuscript.tex').write_text(header+body+declarations+refs+'\n\\end{document}\n',encoding='utf-8')
    (out/'abstract.txt').write_text(abstract,encoding='utf-8')
    # Supplement: complete primary contrast tables; full matrix supplied as CSV.
    sup=r'''\documentclass[11pt]{article}
\usepackage[T1]{fontenc}\usepackage[utf8]{inputenc}\usepackage{mathptmx}
\usepackage[a4paper,margin=25mm]{geometry}
\usepackage{amsmath,booktabs,longtable,graphicx,url,hyperref}
\begin{document}
\begin{center}\Large Online Resource 1: Supplementary methods and results\end{center}
'''
    sup+='\\noindent '+TITLE+'\\\\\nComputing; Jiayue Sun, Binbin Yong, Junjie An, Tianyu Bo and Shuai Li.\\\\\nCorrespondence: Binbin Yong, School of Information Science and Engineering, Lanzhou University, Lanzhou 730000, China; yongbb14@lzu.edu.cn\n'
    sup+=r'''\section{Evidence layers and protocol}
The original 42-condition experiment remains an archived layer. Its post-hoc set and uncertainty diagnostics are identified as such. The new 520-condition protocol was frozen before its outcomes, after the original findings and resource timings were known. It is a prospective extension using known datasets. All conditions, random paths, source hashes and outcome files are retained. No outcome-based exclusions were made.
The five components contain 200 resolution, 60 seed-budget, 160 parameter, 80 coupling and 20 synthetic-scale conditions. Each has nine arm executions and 10,000 evaluation worlds. Random-pool repetitions are averaged within path for primary statistical summaries. Selection IDs are nested prefixes, and evaluation uses a separate family. The frozen protocol, configuration and source manifests are included in the reproducibility package.
\section{Implementation audit}
All 42 archived hashes were checked. Thirty-two arm traces and 64,000 evaluation values were exactly reproduced. The small-graph suite contains 108 edge-time uniform comparisons, 9,600 chain outcomes, 720 cyclic-graph outcomes, 720 fixed-edge reachability checks and 15 restricted-greedy comparisons. An initial audit report mislabeled the 108 hash checks as 324; the original record is preserved with a count erratum. This affects the label only, not the computations.
For the chain $a\to b\to c$ under step coupling, $p=.5,h=2$, world 5 and lexicographic endpoint codes, $f(\{a\})=3$ but $f(\{a,b\})=2$. The first seed set activates $b$ one round later, changing the random key for its outgoing edge. This supplies a concrete finite-world nonmonotonicity example. Fixed-edge coupling instead uses the step-zero edge key in every round. Its spread is exactly the union of horizon-limited reachability sets.
\section{Statistical interpretation}
Paired Monte Carlo intervals use the sample standard deviation of the per-world difference divided by $\sqrt{10000}$. The displayed normal-approximation intervals are conditional and pointwise. Across-path intervals resample ten independent pseudorandom paths on each fixed real graph, or five on a fixed synthetic graph, 10,000 times with analysis seed 20261015. These percentile intervals have limited precision and are not simultaneous confidence regions.
The primary family has 24 two-sided exact sign tests: six candidate types against full on four real graphs at $k=5,W=5120,p=.01,h=3$, step coupling. Exact zero path differences are omitted from the binomial sign count and reported; all-zero contrasts receive $p=1$. Holm adjustment is applied to the entire family. This tests sign balance conditional on a fixed network and algorithmic protocol, not mean equivalence. No significance tests are used to select which sensitivity results to report.
\section{Primary numerical effects}
All entries are candidate-minus-full activated nodes. Intervals are percentile bootstrap intervals over ten paths; random pools are averaged within a path. SD denotes sample standard deviation across paths.
\begin{longtable}{llrrrr}
\toprule Network & Pool & Mean & SD & Lower & Upper \\ \midrule\endhead
'''
    for ds in REAL:
        for method in METHODS:
            row=primary[(primary.dataset==ds)&(primary.method==method)].iloc[0]
            sup+=' & '.join([ds,LABELS[method],number(row.delta_mean),number(row.delta_sd),number(row.delta_lo),number(row.delta_hi)])+' \\\\\n'
    sup+='\\bottomrule\\end{longtable}\n\\section{Complete primary sign-test family}\n\\begin{longtable}{llrrrrr}\n\\toprule Network & Pool & $+$ & $-$ & Zero & $p$ & Holm $p$ \\\\ \\midrule\\endhead\n'
    for row in tests.itertuples():
        sup+=' & '.join([row.dataset,LABELS[row.method],str(row.positive),str(row.negative),str(row.n_zero),f'{row.p_two_sided:.4f}',f'{row.p_holm:.4f}'])+' \\\\\n'
    sup+='\\bottomrule\\end{longtable}\n'
    rd=pd.read_csv(a/'round_diagnostics.csv')
    sup+=r'''\section{Round-level resolution diagnostics}
The table describes the full reference at the lowest and highest primary budgets. Tie rates count rounds with more than one maximizer, out of 50 rounds per network/budget (ten paths, five rounds). Gaps are mean differences between the winning and runner-up empirical spread. These descriptive diagnostics do not establish that ties cause the observed membership changes. The complete file round\_diagnostics.csv additionally retains each chosen marginal gain and every method's round diagnostics.
\begin{center}\begin{tabular}{lrrrr}\toprule Network & Ties 20 & Ties 5120 & Gap 20 & Gap 5120 \\ \midrule
'''
    for ds in REAL:
        lo=rd[(rd.stage=='resolution')&(rd.dataset==ds)&(rd.W==20)&(rd.method=='full')]
        hi=rd[(rd.stage=='resolution')&(rd.dataset==ds)&(rd.W==5120)&(rd.method=='full')]
        sup+=' & '.join([ds,f'{int((lo.ties>1).sum())}/50',f'{int((hi.ties>1).sum())}/50',number(lo.winner_runnerup_margin.mean(),4),number(hi.winner_runnerup_margin.mean(),4)])+' \\\\\n'
    sup+='\\bottomrule\\end{tabular}\\end{center}\n'
    sup+=r'''\section{Larger seed budgets and full-pool controls}
The following $k=20,W=1280$ summaries use ten paths. Coverage is actual candidate count divided by graph size. Full coverage is a consistency control, not successful truncation. All lower-budget and individual-path values are retained in the source tables.
\begin{longtable}{llrrr}\toprule Network & Pool & Coverage & Mean $\Delta$ & SD \\ \midrule\endhead
'''
    for row in g[(g.stage=='seed_budget')&(g.W==1280)&(g.method.isin(METHODS))].itertuples():
        sup+=' & '.join([row.dataset,LABELS[row.method],number(row.coverage_mean),number(row.delta_mean),number(row.delta_sd)])+' \\\\\n'
    sup+='\\bottomrule\\end{longtable}\n'
    sup+=r'''\section{Random pools, tolerances and timing}
Three pool permutations are generated per network/path independently of the selection worlds and are held fixed across budgets and propagation parameters. Their individual results remain available. Averaging the three per-world evaluations before calculating a paired MC standard error preserves their shared evaluation-world dependence. Averaging their path-level effects avoids treating the random repeats as independent paths.
The tolerance grid is 0, 1, 2.5, 5, 10 and 20 percent of full incremental spread. The file tolerance\_sensitivity.csv includes both the fraction meeting a point-estimate threshold and a more conservative descriptive conditional-loss-bound readout. The latter divides a pointwise upper loss bound by a point-estimate denominator; it is not a ratio confidence interval or a confirmatory noninferiority test.
Warm compiled selection and independent evaluation are timed separately. A full-pipeline attribution adds graph preparation, common world materialization and the relevant ranking cost. It does not count every other ranking's cost against a single method. Five additional randomized repetitions per real graph and nine arms yield 180 observations; these repeats do not increase utility sample size. Initial compilation, environment and peak working set are recorded separately.
\section{Source-data map and reproduction}
all\_arm\_metrics.csv retains all 4,680 arm rows. path\_level\_metrics.csv additionally expresses random pools as within-path averages. group\_summary.csv contains the complete setting-specific summaries; reference\_transitions.csv contains adjacent-budget reference diagnostics; primary\_sign\_tests\_holm.csv contains the complete primary family; timing\_repeats.csv and tolerance\_sensitivity.csv support their named analyses. Every condition JSON has a companion compressed NumPy archive containing all evaluation outcomes and round-level total scores.
The local package contains the frozen engine and runner, configuration and protocol hashes, independent analysis and plotting scripts, a minimal semantic smoke test, data cards, the original preprocessing script, and command-line reproduction instructions. Provider archives are obtained separately and checked against their recorded hashes. No public archival DOI has yet been assigned. This document is for author review; administrative declarations must be finalized before submission.
\end{document}
'''
    (out/'Online_Resource_1.tex').write_text(sup,encoding='utf-8')
    metadata={'title':TITLE,'abstract_words':words,'keywords':5,'status':'author-review draft; author declarations and archive decision pending','main_results':{'last_transition_changed':changed,'last_transition_n':40,'holm_significant':len(sig),'weighted4k_delta_range':[float(w4.delta_mean.min()),float(w4.delta_mean.max())]}}
    (out/'metadata.json').write_text(json.dumps(metadata,indent=2))
    print(json.dumps(metadata))

if __name__=='__main__':main(sys.argv[1],sys.argv[2])
