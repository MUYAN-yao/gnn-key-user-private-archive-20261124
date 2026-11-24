from pathlib import Path
R=Path(r'D:\校创\基于GNN的关键用户识别\submission\computing-external-validation-20261015\structural-language-revision-20261027')
M=R/'manuscript'
replacements={
 'degree-4k':'Degree-4k','degree-5\\%':'Degree-5\\%',
 'expected-optimality':'optimality with respect to expected spread',
 'under stricter ranking':'with a tighter PageRank convergence tolerance',
 'Strict-tolerance results':'Results at the tighter PageRank tolerance',
 'default and strict PageRank':'PageRank at default and tighter tolerances',
 'under the strict pool':'with the pool formed at the tighter tolerance',
 'strict PageRank-4k minus':'PageRank-4k at the tighter tolerance minus',
 "CollegeMsg's default and strict pools":"CollegeMsg's default- and tighter-tolerance pools",
 'but strict losses remain':'but losses at the tighter tolerance remain',
 'Default and strict tolerances':'Default and tighter tolerances',
 'with strict pools stable at':'with unchanged candidate membership at',
 'under strict ranking':'with the tighter PageRank tolerance',
 'strict PageRank precision':'the tighter PageRank tolerance',
 'full-greedy trajectory':'full-candidate reference trajectory',
 'external ca-GrQc strict-PageRank result':'external ca-GrQc result at the tighter PageRank tolerance',
}
for name in ['manuscript.tex','Online_Resource_1.tex','history_evidence.tex']:
    p=M/name;s=p.read_text(encoding='utf-8')
    for old,new in replacements.items():s=s.replace(old,new)
    p.write_text(s,encoding='utf-8')
p=M/'Online_Resource_1.tex';s=p.read_text(encoding='utf-8')
s=s.replace('strict PageRank-4k and PageRank-5\\% arms','PageRank-4k and PageRank-5\\% arms at the tighter tolerance')
s=s.replace('prior strict $W=1280$ layer','prior tighter-tolerance $W=1280$ layer')
s=s.replace('Strict $10^{-12}$ pools agree with $10^{-14}$ pools for every graph/pool size.', 'Candidate membership agrees between $10^{-12}$ and $10^{-14}$ for every graph/pool size. This checks membership stability at the tested cutoffs, not exact PageRank-vector convergence.')
s=s.replace("CollegeMsg's strict and default pools", "CollegeMsg's tighter- and default-tolerance pools")
s=s.replace('does not survive the stable strict pool: strict losses are', 'disappears with the tighter-tolerance pool: incremental losses are')
s=s.replace('strict 4k losses', '4k losses at the tighter tolerance')
s=s.replace('strict PageRank at', 'PageRank with the tighter tolerance at')
s=s.replace('Strict-tolerance timing', 'Timing at the tighter tolerance')
s=s.replace('seed NumPy\'s \\texttt{default\\_rng}; the first 20 entries', 'seed NumPy\'s \\texttt{default\\_rng}; for the external $k=5$ study, the first 20 entries')
s=s.replace('Hybrid deployment cost','The assembled selection-use cost').replace('Hybrid\nverification cost','The assembled cost including independent evaluation')
s=s.replace('The maximum positive psutil\nprocess-lifetime peak is 3.448822 GiB; it must not be confused with an unverified\nPowerShell display or with preflight measurements using one tenth the evaluation\nworld count.', 'The maximum positive psutil process-lifetime peak is 3.448822 GiB. Preflight\nused one tenth of the evaluation-world count and therefore has a different\nresource scope; the recorded peak is not a condition-specific allocation maximum.')
s=s.replace('The \\texttt{none} mode audits saved results and regenerates\nanalysis without repeating selection.', 'The \\texttt{none} mode audits saved results and regenerates\nanalysis without rerunning seed selection; audit replay may still execute the\nsimulator, so this mode is not a read-only numerical-summary command.')
p.write_text(s,encoding='utf-8')
p=M/'precision_budget_table.tex';s=p.read_text(encoding='utf-8').replace('Default uses NetworkX tolerance $10^{-6}$; strict uses $10^{-12}$, whose pool is unchanged at $10^{-14}$. Pool Jaccard compares default and strict candidates.', 'Default uses NetworkX tolerance $10^{-6}$; Tighter uses $10^{-12}$, with candidate membership unchanged at $10^{-14}$. Pool Jaccard compares default- and tighter-tolerance candidates.').replace('Strict','Tighter');p.write_text(s,encoding='utf-8')
for name in ['summary_for_editor.txt','cover_letter_draft.txt','novelty_and_scope_statement.txt','claim_language_audit.md','claim_evidence_matrix.md']:
    p=R/name
    if not p.exists():continue
    s=p.read_text(encoding='utf-8')
    s=s.replace('under stricter ranking','with a tighter PageRank convergence tolerance').replace('expected-optimality','optimality with respect to expected spread')
    s=s.replace('The present section-specific language revision preserves those results and their scope; it performs no further experimental or statistical analysis.', 'The archived records distinguish stored-result verification, analysis regeneration and representative reruns; they do not establish a complete independent reproduction.')
    p.write_text(s,encoding='utf-8')
print('Applied context-specific terminology edits; numerical result rows and figure assets unchanged.')
