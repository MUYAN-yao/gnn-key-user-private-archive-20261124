"""Generate quantitative LaTeX inserts and auditable reports from analysis CSVs."""
from pathlib import Path
import json, shutil
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'analysis';M=ROOT/'manuscript';M.mkdir(exist_ok=True)
OLD=ROOT.parents[1]/'computing-strengthening-20261015'
for f in ['svjour3.cls','svglov3.clo']:shutil.copy2(OLD/'manuscript'/f,M/f)
for f in (A/'figures').glob('*.pdf'):shutil.copy2(f,M/f.name)
s=pd.read_csv(A/'summary_by_method.csv');p=s[(s.W==1280)&(s.stage=='resolution')];t=pd.read_csv(A/'transition_summary.csv');test=pd.read_csv(A/'primary_tests.csv');paths=pd.read_csv(A/'arm_path.csv');hist=json.loads((OLD/'analysis/summary.json').read_text())
names={'ca_grqc':'ca-GrQc','college_msg':'CollegeMsg','wiki_vote':'wiki-Vote'};methods={'full':'Full','degree_4k':'Degree 4k','degree_5pct':r'Degree 5\%','pagerank_4k':'PageRank 4k','pagerank_5pct':r'PageRank 5\%','history_weighted_4k':'History 4k','history_weighted_5pct':r'History 5\%','random_mean_4k':'Random mean'}
def table(caption,label,header,rows,cols):
    return '\\begin{table}[htbp]\n\\caption{'+caption+'}\\label{'+label+'}\n\\begin{tabular}{'+cols+'}\n\\toprule\n'+header+' \\\\\n\\midrule\n'+'\n'.join(' & '.join(r)+' \\\\' for r in rows)+'\n\\bottomrule\n\\end{tabular}\n\\end{table}\n'
rows=[]
for ds in names:
    q=p[(p.dataset==ds)&(p.method=='pagerank_4k')].iloc[0];d=p[(p.dataset==ds)&(p.method=='degree_4k')].iloc[0];f=p[(p.dataset==ds)&(p.method=='full')].iloc[0]
    rows.append([names[ds],f'{f.incremental_spread_mean:.3f}',f'{q.delta_mean:.5f}',f'{q.loss_percent_mean:.2f}',f'{int(d.same_order_mean*5)}/5'])
(M/'primary_table.tex').write_text(table('Frozen external results at $W=1280$, five paths per graph. PageRank uses a 20-node pool and default solver tolerance. Loss is normalized by full-reference spread beyond the five seeds. Degree agreement is ordered-trajectory agreement.','tab:primary','Graph & Full extra & PR difference & PR loss (\\%) & Degree',rows,'lrrrr'),encoding='utf-8')
rows=[]
for ds in names:
    q=p[(p.dataset==ds)&(p.method=='degree_4k')].iloc[0];f=p[(p.dataset==ds)&(p.method=='full')].iloc[0]
    rows.append([names[ds],f'{f.selection_seconds_mean:.2f}',f'{q.selection_seconds_mean:.3f}',f'{q.selection_saving_percent_mean:.2f}',f'{q.verification_saving_percent_mean:.2f}'])
(M/'cost_table.tex').write_text(table('Degree-4k cost at $W=1280$. Seconds are frozen selection measurements averaged over five paths. Verification savings use the separately measured setup plus frozen world, selection and evaluation times; they are hybrid estimates, not direct end-to-end trials.','tab:cost','Graph & Full (s) & Degree (s) & Selection (\\%) & Verify (\\%)',rows,'lrrrr'),encoding='utf-8')
rows=[]
for ds in names:
    for low,high in [(80,320),(320,1280)]:
        q=t[(t.dataset==ds)&(t.low==low)&(t.high==high)].iloc[0]
        rows.append([names[ds],f'{low}--{high}',f'{int(q.changed)}/5',f'{q.mean_delta:+.5f}',f'{q.min_delta:+.4f}, {q.max_delta:+.4f}'])
(M/'transition_table.tex').write_text(table('Full-reference transitions under step coupling. Gain is the paired independent change in total spread; seed counts are constant. The range is across paths, not a confidence interval.','tab:transitions','Graph & Budgets & Set changed & Mean gain & Path range',rows,'llrrr'),encoding='utf-8')
supp=[]
for ds in names:
    rows=[]
    for stage,W in [('resolution',80),('resolution',320),('resolution',1280),('fixed_edge_control',320)]:
        g=s[(s.dataset==ds)&(s.stage==stage)&(s.W==W)]
        for _,q in g.iterrows():
            rows.append([f'{W}'+('E' if stage.startswith('fixed') else ''),methods[q.method],f'{q.total_spread_mean:.3f}',f'{q.delta_mean:+.3f}',f'{q.delta_path_sd:.3f}',f'{q.loss_percent_mean:.2f}',f'{int(round(q.same_order_mean*q.paths))}/{int(q.paths)}' if q.method!='random_mean_4k' else f'{q.same_order_mean:.2f}'])
    supp.append('\\clearpage\n'+table(names[ds]+': complete frozen aggregate matrix; PageRank uses default tolerance. E means fixed-edge coupling (three paths); other rows use five step-coupled paths. SD is across path mean differences. Random pools are averaged within each path; their agreement entry is a fraction.','tab:s-'+ds,'$W$ & Method & Total & $\\Delta$ & SD & Loss (\\%) & Order',rows,'rlrrrrr'))
rows=[[names[q.dataset],methods[q.method],f'{q.mean_delta:.5f}',str(q.zero_paths),f'{q.p_raw:.4f}',f'{q.p_holm:.4f}'] for q in test.itertuples()]
supp.insert(0,table('Prespecified primary exact two-sided sign tests at $W=1280$. Holm correction is across three methods within each fixed graph. Zero path differences are dropped from the sign test.','tab:tests','Graph & Method & Mean $\\Delta$ & Zeros & $p$ & Holm $p$',rows,'llrrrr'))
(M/'supp_tables.tex').write_text('\n'.join(supp),encoding='utf-8')
macros=[]
for ds,prefix in [('college_msg','College'),('ca_grqc','Grqc'),('wiki_vote','Wiki')]:
    for method,suffix in [('pagerank_4k','PR'),('pagerank_5pct','PRfive'),('degree_4k','Degree')]:
        q=p[(p.dataset==ds)&(p.method==method)].iloc[0]
        for key,field,precision in [('Delta','delta_mean',5),('Loss','loss_percent_mean',2),('Saving','verification_saving_percent_mean',2)]:macros.append('\\newcommand{\\'+prefix+suffix+key+'}{'+f'{q[field]:.{precision}f}'+'}')
(M/'numbers.tex').write_text('\n'.join(macros)+'\n',encoding='utf-8')
def md(df):
    cols=list(df.columns);return '| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'+'\n'.join('| '+' | '.join(str(v) for v in r)+' |' for r in df.itertuples(index=False,name=None))
selected=p[['dataset','method','delta_mean','delta_path_sd','loss_percent_mean','same_order_mean','verification_saving_percent_mean']].copy();selected.iloc[:,2:]=selected.iloc[:,2:].round(5)
report='''# Strict external-validation analysis

This report is regenerated from all 54 frozen JSON/NPZ pairs. There are 468
executed arms, plus 54 derived within-path random-pool means. No failed or adverse
condition is excluded. Audit acceptance is separately recorded in
`../audit/full_validation.json`; generating this report alone does not certify it.

## Primary results (W=1280; frozen default PageRank tolerance)

Important qualification: the separately frozen post-hoc precision control changes
ca-GrQc PageRank4k from -.25082 to +.02608 when tolerance is tightened. CollegeMsg
is unchanged and wiki-Vote's large loss persists. The original ca-GrQc loss is not
precision-robust; default and tightened results are not interchangeable. Full
control results appear below and in supplement-pr-precision/summary.csv.

'''+md(selected)+'''

Degree-4k reproduces all 15 ordered references across the three fixed graphs.
PageRank-4k does not reproduce any of these trajectories. These are finite-reference
statements; the references are not optimal expected-spread sets. Selection budgets
stop at 1280. Standard incoming PageRank and outgoing IC are different objectives.
On wiki-Vote, the PageRank top 20 have mean out-degree 56.2 versus 489.25 for degree;
they cover 0/5 full seeds on each path. At 5% coverage PageRank still loses 24.28%
of incremental spread. This is evidence of sensitivity to ranking, coverage and
topology, not a causal isolation of direction or a universal failure of PageRank.

## Full-reference budget transitions

'''+md(t.round(5))+'''

At 320→1280, six of fifteen final sets change. Four changed-set contrasts have
positive pointwise normal 95% conditional MC intervals; two ca-GrQc contrasts
cross zero. These are unadjusted exploratory diagnostics, not six hypothesis tests
or an application-specific materiality criterion. Nine same-set transitions have
identical per-world values; some ordered traces still change. The three graphs
are reported separately and are not pooled for population inference.

## Inference and cost limits

'''+md(test.round(6))+'''

No primary sign-test comparison passes Holm 0.05. With five nonzero paths even all
five negative signs yield p=.0625 before correction. That low-powered test does
not erase a large measured effect or prove equivalence. Conditional MC uncertainty
and between-path variability answer different questions; path t intervals are
post-hoc descriptive intervals, not cross-network confidence statements.

Selection-only savings require prepared graph and worlds. Hybrid deployment adds
supplementary method-specific setup and frozen selection-world preparation;
verification further adds independent-world preparation and evaluation. The
setup contribution is newly measured; no direct cold-start or end-to-end trial is
claimed. All repeated frozen timings are in timing_repeats.csv/timing_summary.csv.
Tolerance curves report point-estimate eligibility and do not certify a loss bound.
Random-mean cost is the average cost of deploying one random pool, not the cost
of executing all three research repetitions. Negative loss remains visible.

## Provenance and claim ledger

| Claim | Evidence | Allowed wording | Unsupported stronger wording |
| --- | --- | --- | --- |
| Three default PageRank losses | arm_path.csv; primary_tests.csv; original NPZ; full_validation.json | Measured default-tolerance differences; ca-GrQc is precision-sensitive | PageRank universally fails or ca-GrQc loss is solver-robust |
| Degree agreement | arm_path.csv; direction_diagnostics.csv; replayed round totals | Reproduces W1280 reference for 15 paths | Expected-optimal or universally lossless |
| Resolution sensitivity | full_reference_transitions.csv; Fig2_source.csv | ca-GrQc and CollegeMsg references change in utility on some paths | Every network is budget-sensitive |
| Coverage control | summary_by_method.csv; Fig1_source.csv | 5% restores ca-GrQc PageRank agreement, not wiki-Vote | A universal 5% threshold |
| Coupling | coupling_transitions.csv; FigS1_source.csv | PR losses persist in the preselected W320 edge control | Coupling never matters |
| Cost savings | arm_path.csv; supplement_setup_timing.csv; timing_repeats.csv; Fig3_source.csv | Savings in explicitly assembled warm-process scenarios | Guaranteed production acceleration |
| Smaller high-budget gains in historical graphs | historical analysis/summary.json | Historical 1280→5120 evidence retained | External graphs converge by 1280 |
'''
precision_file=ROOT/'supplement-pr-precision/summary.csv'
if precision_file.exists():
    precision=pd.read_csv(precision_file)
    report+='\n## Post-hoc PageRank numerical-precision control\n\nThe separately frozen precision protocol reruns both PageRank pool sizes on all three graphs and all five original W1280 paths, with tol1e-12 (pool membership also agrees at1e-14). It adds15 diagnostic conditions/30 restricted-arm executions, not independent paths or primary tests. Main results are preserved.\n\n'+md(precision.round(6))+'\n'
    rr=[[names[q.dataset],methods[q.method],f'{q.delta_vs_full:.5f}',f'{q.mean_loss_percent:.2f}',f'{q.delta_vs_default:+.5f}',f'{int(q.same_order_as_default)}/5'] for q in precision.itertuples()]
    (M/'precision_table.tex').write_text(table('Post-hoc precision control at $W=1280$, tolerance $10^{-12}$. Difference is versus frozen full greedy; change is versus the default PageRank implementation. Order compares with default PageRank, not full eligibility. These are the original five paths, not new independent samples.','tab:precision','Graph & Pool & Difference & Loss (\\%) & Change & Order',rr,'llrrrr'),encoding='utf-8')
(ROOT/'analysis-report.md').write_text(report,encoding='utf-8')
(ROOT/'stats-appendix.md').write_text('''# Statistical specification and data dictionary

Prespecified family: W1280 step coupling, degree4k/PageRank4k/random mean versus
full, separately per graph; two-sided exact binomial sign tests on nonzero path
differences; Holm across 3 contrasts per graph, 9 tests total. Exact zeros are
reported. Sign tests concern sign balance, not expected effect size.

For each method/path, d_i = spread(method,i) - spread(full,i) on the same 10000
independent evaluation worlds. Delta=mean(d_i), MC SE=sd(d_i,ddof=1)/sqrt(10000).
The normal interval Delta +/-1.96 SE is conditional on the selected sets, graph,
and propagation law; it is not a selection-path or real-network interval.
Spread includes k=5 seeds. Incremental spread=spread-5. Loss percent=-100*Delta /
(mean(full)-5). Every observed denominator is positive; these plug-in ratios do
not have MC confidence bounds attached. A negative loss denotes measured gain.

Random repeats are coupled through shared evaluation worlds. First average all
three evaluation vectors within a path and compute its paired difference/SE,
preserving covariance; then aggregate path means. within_path_random_delta_sd
describes candidate-pool variability. Across-path SD includes the realized
evaluation noise as well as selection-path changes; it is not a deconvolved
selection-only variance. Post-hoc t intervals use df=n_paths-1 and are descriptive
with only 5 (or 3 control) computational paths. There is no network-population CI.

Agreement: same_order compares full sequences; same_set compares unordered sets;
Jaccard=intersection/union. first_divergence is one-based and zero means identical.
For random_mean rows agreement and Jaccard are repeat fractions/averages; there is
no single averaged seed set, so first_divergence is NA. Full-reference transitions
use shared evaluation IDs at both W values. Coupling contrasts compare separately
generated step/edge outcomes with shared IDs; they are post-hoc descriptive and
not a causal estimate of one algorithmic change independent of seed changes.

Tolerance curves use thresholds 0,1,2.5,5,10,20% of incremental spread. All paths
are retained; passing_paths and passing_mean_saving_percent describe realized
point estimates, with no simultaneous loss guarantee or noninferiority test.

The separately frozen post-hoc PageRank precision control reuses all five original
paths atW1280;15 conditions/30 restricted arms are not added to primary tests or
independent sample size. It compares tol1e-12 versus the frozen default1e-6. Full
results/protocol/hashes are in supplement-pr-precision, outside the main CSVs.

CSV inventory: arm_path (468 executed+54 random means); summary_by_method (graph/
stage/W/method averages and path SD); primary_tests; full_reference_transitions
(45 including direct80→1280); transition_summary; coupling_transitions;
direction_diagnostics; timing_repeats (130); timing_summary;
supplement_setup_timing (100 post-hoc); tolerance_cost_curves. Figure source CSVs
are filtered copies with all observations required for the indicated panels.
''',encoding='utf-8')
(ROOT/'figure-catalog.md').write_text('''# Figure catalog and QA contract

All four figures show the frozen main matrix with default PageRank tolerance.
The separate tightened-tolerance diagnostic is tabulated in the supplement and
must not be silently substituted into these cost or coupling curves.
Python/matplotlib quantitative grids, 119 mm width; editable PDF/SVG, 300 dpi PNG
preview. Raster previews are not submission masters; no TIFF is required for
these vector charts. Font size is at least 8 pt. Width-preflight warning is a
literal-expression parser error (119/25.4 inches is exactly119 mm); PDF MediaBox
is checked independently. Log x-values are the positive budgets80,320,1280.

| Figure | Claim | Statistics and source |
| --- | --- | --- |
| Fig1 | Ranking/coverage loss depends on topology and budget | Each point mean of five paths; bars are path SD; random repeats averaged first; Fig1_source.csv |
| Fig2 | Set changes and independent gains differ | All five paths for each graph and adjacent budget pair; filled circles changed set, hollow squares same set; bars unadjusted conditional MC95%; Fig2_source.csv |
| Fig3 | Large speed savings do not ensure tolerated loss | Counts of five paths passing point-estimate tolerances at W1280; label is mean hybrid verification saving across all five; not a noninferiority test; Fig3_source.csv |
| FigS1 | Coupling control preserves key losses but changes some references | Three preselected paths, W320; circle step/square fixed-edge; no inferential bars; FigS1_source.csv |

No train/validation optimization uses final evaluation worlds. No image manipulation
or data exclusions beyond the stated stage/method selections; complete tables keep
all methods, budgets and coupling controls. See qa/visual-review.md for actual
render inspection; source preflight alone is not a visual-quality certificate.
''',encoding='utf-8')
print('tables, macros, reports generated')
