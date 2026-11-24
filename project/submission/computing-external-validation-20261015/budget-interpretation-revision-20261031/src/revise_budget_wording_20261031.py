from pathlib import Path
import shutil, json, re, hashlib, difflib

P=Path('submission/computing-external-validation-20261015')
B=P/'contribution-action-revision-20261028'
R=P/'budget-interpretation-revision-20261031'
if (R/'qa/change_log.json').exists(): raise SystemExit('Completed revision exists; refusing overwrite')
R.mkdir(exist_ok=True)
for folder in ['manuscript','chinese/manuscript','analysis']:
    shutil.copytree(B/folder,R/folder,dirs_exist_ok=True)
for name in ['cover_letter_draft.txt','summary_for_editor.txt','REPRODUCE.md','claim_evidence_matrix.md']:
    shutil.copy2(B/name,R/name)
(R/'qa').mkdir(exist_ok=True); (R/'src').mkdir(exist_ok=True); (R/'evidence').mkdir(exist_ok=True)
shutil.copy2(__file__,R/'src'/Path(__file__).name)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
baseline={str(p.relative_to(B)):sha(p) for p in B.rglob('*') if p.is_file()}
(R/'qa/baseline_manifest.json').write_text(json.dumps(baseline,indent=2),encoding='utf-8')
changes=[]
def edit(rel,old,new,reason='统一预算解释及中性差异措辞'):
    p=R/rel; t=p.read_text(encoding='utf-8')
    assert old in t,(rel,old[:100])
    t=t.replace(old,new)
    p.write_text(t,encoding='utf-8')
    changes.append(dict(file=rel,old=old,new=new,reason=reason))
EN='manuscript/manuscript.tex'; ZH='chinese/manuscript/manuscript_zh.tex'
def para(rel,prefix,new,reason='纠正设计解释、明确比较方向或合并重复限制'):
    text=(R/rel).read_text(encoding='utf-8')
    matches=[p for p in text.splitlines() if p.startswith(prefix)]
    assert len(matches)==1,(prefix,len(matches))
    edit(rel,matches[0],new,reason)

para(EN,'Candidate restriction can reduce',r'''Candidate restriction can reduce influence-maximization search costs, but evaluating its quality requires comparing two seed sets selected from finite samples. We vary the selection-world budget $W$ for both full-candidate and candidate-restricted greedy selection, separately from ranking precision, and evaluate spread on 10,000 independent worlds. Evidence comes from three external topologies, with four small contact graphs providing separate controls. On ca-GrQc, default PageRank-4k changes from 5.61\% higher to 5.07\% lower mean incremental spread relative to the same-budget full reference. This sign reversal disappears in a post-hoc control that tightens PageRank tolerance. Budget-dependent seed changes persist, but set changes alone do not determine the direction or magnitude of independently estimated spread changes. Across the external networks, degree-based pools reproduce all 15 highest-budget reference trajectories at lower measured selection cost, whereas PageRank losses persist on the two directed networks. These findings distinguish selection-budget sensitivity from candidate-ranking sensitivity. Reporting both selection procedures, candidate-pool stability and independently evaluated spread makes the basis of a measured quality--cost trade-off explicit.''')
para(ZH,'候选限制能够降低',r'''候选限制能够降低影响力最大化的搜索成本，但评价其质量需要比较两个由有限采样选出的种子集合。本文同时改变全候选与候选受限贪心选择的选择世界预算 $W$，单独控制排名精度，并在 10,000 个独立世界上评估传播量。三张外部网络用于主要比较，四张小规模接触图提供单独的补充对照。在 ca-GrQc 上，默认 PageRank-4k 相对同预算全候选参照的平均增量传播量，从高于参照 5.61\% 转为低于参照 5.07\%。这一符号反转在收紧 PageRank 容差的事后控制中消失。预算相关的种子变化仍然存在，但仅凭集合变化无法确定独立估计传播量变化的方向与大小。在外部网络上，基于度的候选池以更低的实测选择成本复现了最高测试预算下全部 15 条参照轨迹，两个有向网络上的 PageRank 损失则仍然存在。这些发现区分了选择预算敏感性与候选排名敏感性。同时报告两类选择过程、候选池稳定性和独立评估传播量，能够明确实测质量与成本权衡的依据。''')
para(EN,'Reference sampling and candidate ranking',r'''Selection sampling and candidate ranking enter this comparison at different stages. In the budget sweeps, increasing $W$ can change the seeds selected by both the full-candidate reference and the restricted methods. Their relative spread difference therefore reflects budget-dependent changes in both selection procedures. Ranking precision acts before selection, where small score changes can exchange vertices at the candidate-pool boundary. Seed disagreement alone cannot resolve these effects because different sets can have similar independently evaluated spread.''')
para(ZH,'参照采样与候选排名',r'''选择采样与候选排名在比较的不同阶段发挥作用。在预算扫描中，增大 $W$ 可能同时改变全候选参照和受限方法选出的种子。因此，相对传播差异反映了两类选择过程随预算发生的共同变化。排名精度则在选择之前起作用，分数的小幅变化可能使候选池边界处的节点发生替换。仅凭种子不一致无法辨别这些影响，因为不同集合的独立评估传播量可能相近。''')
edit(EN,'separating the construction of the reference, the construction of the candidate pool and the assessment of selected seeds','separating seed selection in both arms, candidate-pool construction and independent assessment of the selected seeds')
edit(ZH,'将参照构建、候选池构建与种子效用评估分开考察','将两类方法的种子选择、候选池构建与种子独立效用评估分开考察')
edit(EN,'Through paired budget comparisons and a post-hoc precision control, we distinguish the observed quality reversal from persistent budget-dependent seed changes.','We vary the selection budget for both full and restricted arms and use a post-hoc precision control to examine the resulting relative spread differences.')
edit(ZH,'通过配对预算比较与事后精度对照，我们将观察到的质量反转与持续存在的预算相关种子变化区分开来。','同时改变全候选与受限实验臂的选择预算，并通过事后精度对照考察相对传播差异。')
edit(EN,'We quantify the spread gains associated with changes in the reference seed set.','We quantify independently estimated spread changes associated with reference-set changes.')
edit(EN,'Independent paired evaluation measures the magnitude and conditional Monte Carlo uncertainty of these gains.','Independent paired evaluation measures their direction, magnitude and conditional Monte Carlo uncertainty.')
edit(EN,'The measurements separate seed-set instability from the utility gained through additional sampling.','Individual changes include negative, positive and zero differences; the measurements separate seed-set instability from changes in estimated utility.')
edit(ZH,'本文量化参照种子集合变化所对应的传播收益。','本文量化参照集合变化所对应的独立估计传播量变化。')
edit(ZH,'通过配对独立评估，我们测量这些收益的大小及其条件 Monte Carlo 不确定性。','通过配对独立评估，测量变化的方向、大小及其条件 Monte Carlo 不确定性。')
edit(ZH,'这些测量区分了种子集合的不稳定性与增加采样所获得的效用收益。','各配对包含负、正及零差值；这些测量区分了种子集合的不稳定性与估计效用的变化。')
edit(EN,r'Paired evaluation separates reference resolution, ranking resolution and restriction quality. (a) The selection budget $W$ and ranking tolerance $\tau$ determine the finite-world reference and the top-$q$ pool $C(\tau,q)$. Both arms share the graph, world prefix, seed budget and tie rule. (b) Shared evaluation worlds, independent of selection, yield the utility difference $\Delta U$.',r'Paired evaluation separates selection sampling, candidate ranking and independent utility assessment. (a) Both arms select seeds using the same $W$ worlds. Ranking tolerance $\tau$ and cutoff $q$ define the restricted pool $C(\tau,q)$. Both arms share the graph, world prefix, seed budget and tie rule. (b) A separate, shared family of $M=10,000$ evaluation worlds yields $\Delta U$, restricted minus full-reference spread.')
edit(ZH,r'配对评价区分参照分辨率、排名分辨率与候选限制的质量。（a）选择预算 $W$ 与排名容差 $\tau$ 分别决定有限世界参照和前 $q$ 名候选池 $C(\tau,q)$。两实验臂共享图、世界前缀、种子预算与同分规则。（b）共享且独立于选择过程的评估世界给出效用差 $\Delta U$。',r'配对评价区分选择采样、候选排名与独立效用评估。（a）两实验臂均使用相同的 $W$ 个世界选择种子，排名容差 $\tau$ 与截断值 $q$ 定义受限候选池 $C(\tau,q)$。两实验臂共享图、世界前缀、种子预算与同分规则。（b）单独且共享的 $M=10,000$ 个评估世界给出效用差 $\Delta U$，方向为受限方法减去全候选参照。')
edit(EN,'changing eligibility, reference budget or ranking tolerance','changing eligibility, the shared selection budget or ranking tolerance')
edit(ZH,'改变候选资格、参照预算或排名容差','改变候选资格、共享选择预算或排名容差')
edit(EN,'the sampled full-candidate reference and the ranking that determines eligibility','finite-world seed selection in both arms and the ranking that determines restricted eligibility')
edit(ZH,'即采样全候选参照与决定候选资格的排名','即两类方法的有限世界种子选择与决定受限候选资格的排名')
edit(EN,'reference-budget and ranking-precision sensitivity','selection-budget and ranking-precision sensitivity')
edit(ZH,'参照预算和排名精度敏感性','选择预算和排名精度敏感性')
edit(EN,r'We vary reference resolution through $W$ and ranking resolution through the numerical tolerance $\tau$.',r'''In the budget sweeps, $W$ governs seed selection for both the full-candidate reference and every restricted arm. Each arm selects its seeds anew at each $W$, using the same nested world prefix. Candidate pools remain fixed across $W$ within a given ranking setting; ranking tolerance $\tau$ and pool size $q$ are controlled separately. The resulting relative differences reflect changes in both selection procedures, rather than improvement of the reference alone.''')
edit(ZH,r'我们通过 $W$ 改变参照分辨率，通过数值容差 $\tau$ 改变排名分辨率。',r'''在预算扫描中，$W$ 同时控制全候选参照和所有受限实验臂的种子选择。每个实验臂在各个 $W$ 下重新选择种子，并使用相同的嵌套世界前缀。在给定排名设置下，候选池在不同 $W$ 间保持固定；排名容差 $\tau$ 和池大小 $q$ 单独控制。因此，相对差异反映两类选择过程的共同变化，不能仅归因于参照的改善。''')
edit(EN,'Evaluation uses a disjoint family of $M=10,000$ worlds per path, shared by all seed sets and held fixed across budgets.','In the external study and the 520-condition historical extension, evaluation uses $M=10,000$ worlds per graph/path/coupling, disjoint from selection and fixed across arms and budgets.')
edit(ZH,r'每条路径的评估使用独立且不与选择世界重叠的 $M=10,000$ 个世界；所有种子集合共享这些评估世界，并在不同预算下保持不变。',r'外部研究及 520 条件历史扩展对每个图、路径与耦合组合使用 $M=10,000$ 个评估世界；它们与选择世界不重叠，并在不同实验臂与预算下保持不变。')
edit(EN,'The utility gap in Fig.', 'Both sets are selected at the same $W$; positive $d_i$ favors the restricted method. The utility gap in Fig.')
edit(ZH,r'。图~\ref{fig:evaluation-mechanism} 中的效用差为',r'。两个集合均在相同的 $W$ 下选出；$d_i$ 为正表示受限方法的传播量更高。图~\ref{fig:evaluation-mechanism} 中的效用差为')
edit(EN,'The seed budget and propagation setting are held constant to isolate reference budget, eligibility and coupling.','The seed count and propagation setting are held constant while selection budget, eligibility and coupling vary. Within every budget condition, both full and restricted arms use that condition\'s $W$.')
edit(ZH,'种子预算和传播设置保持固定，以单独考察参照预算、候选资格和耦合方式。','种子数量与传播设置保持不变，选择预算、候选资格和耦合方式按条件变化。每个预算条件中的全候选臂与受限臂均使用该条件的 $W$。')
edit(EN,'reusing the original five paths, full references and evaluation worlds.','reusing the original five paths, same-budget full references and evaluation worlds. At a fixed $W$, this tolerance control recomputes only the restricted arms; across $W$, it uses the full reference previously selected at each respective budget.')
edit(ZH,'复用原五条路径、全候选参照与评估世界。','复用原五条路径、同预算全候选参照与评估世界。在固定 $W$ 下，容差对照仅重算受限臂；跨 $W$ 比较则使用此前在各自预算下选出的全候选参照。')
edit(EN,'using the same full reference and independent evaluation worlds.','reusing the same-budget full reference for the tolerance comparison. Across budgets, both arms select anew, while the independent evaluation worlds remain fixed.')
edit(ZH,'使用相同全候选参照和独立评估世界，比较默认与较紧容差的 PageRank。','复用同预算全候选参照，比较默认与较紧容差的 PageRank。跨预算时，两类方法均重新选择种子，独立评估世界保持固定。')
edit(EN,'Tightening tolerance exchanges two of 20 candidates and yields gains of','Tightening tolerance exchanges two of 20 candidates; the corresponding mean relative incremental-spread differences are positive at')
edit(ZH,'此时三个预算下的增益分别为','此时三个预算下相对同预算参照的平均增量传播差异均为正，分别为')
edit(EN,'The positive mean includes both gains and losses across paths; it does not by itself establish a utility advantage.','The small positive mean combines positive and negative path differences.')
edit(ZH,'正均值同时包含不同路径上的增益和损失，不能单独据此确立效用优势。','这一较小的正均值包含不同路径上的正、负差异。')
edit(EN,'Budget and ranking precision have distinct effects on candidate-restriction quality.','Selection budget and ranking precision have distinct effects on candidate-restriction quality. At each $W$, restricted methods are compared with the full reference selected at that same $W$; evaluation uses fixed independent worlds.')
edit(ZH,'预算与排名精度对候选限制质量产生不同影响。','选择预算与排名精度对候选限制质量产生不同影响。每个 $W$ 下，受限方法均与该预算下选出的全候选参照比较；独立评估世界保持固定。')
edit(EN,'Figure~\\ref{fig:transitions} compares reference-set changes with independent utility changes.','Figure~\\ref{fig:transitions} isolates full-reference transitions, comparing independently estimated spread at the higher budget minus that at the lower budget. This within-reference diagnostic is separate from the same-budget restricted-minus-full comparison.')
edit(ZH,'图~\\ref{fig:transitions} 比较参照集合变化与独立效用变化。','图~\\ref{fig:transitions} 单独考察全候选参照的预算转移，差值为高预算参照减去低预算参照的独立估计传播量。这一参照内部诊断与同预算的受限方法减全候选参照比较不同。')
for a,b in [('their mean gain is','their mean spread change is'),('exactly zero paired gain','exactly zero paired difference'),('mean high-minus-low budget gain','mean high-minus-low budget spread change'),('their mean gains do not estimate','their mean changes do not estimate')]: edit(EN,a,b)
for a,b in [('平均增益为 0.12720','平均传播量变化为 0.12720'),('配对增益严格为零','配对差值严格为零'),('高预算减低预算的平均增益','高预算减低预算的平均传播量变化'),('平均高减低预算增益','高预算减低预算的平均传播量变化'),('其平均增益估计耦合效应','其平均变化估计耦合效应')]: edit(ZH,a,b)
edit(EN,'Reference-set changes and independent spread changes. Filled circles','Reference-set changes and independent spread changes, defined as higher-budget minus lower-budget full-reference spread. Filled circles')
edit(ZH,'参照集合变化与独立传播量变化。实心圆','参照集合变化与独立传播量变化，差值为高预算减低预算的全候选参照传播量。实心圆')
edit(EN,'Historical-weighted CollegeMsg pools similarly improve from a mean difference of','At the same budget, historical-weighted CollegeMsg pools move from a negative mean difference of')
edit(ZH,'CollegeMsg 的历史加权池也由 4k 下平均差','同预算下，CollegeMsg 的历史加权池由 4k 下平均差')
edit(ZH,'改善为 5\\% 下完全复现参照','变为 5\\% 下完全复现参照')

# Consolidate general caveats, retaining result-specific and statistical qualifiers.
edit(EN,' These contact-graph controls do not test the joint effect of the tighter PageRank tolerance and fixed-edge sampling on the external graphs.','', '联合控制缺口集中保留在讨论局限段')
edit(ZH,'这些接触图对照没有检验外部图上较紧 PageRank 容差与固定边采样的联合效应。','','联合控制缺口集中保留在讨论局限段')
edit(EN,"At default PageRank tolerance, increasing the reference budget changes the restricted method's mean comparison from a gain to a loss.","At default PageRank tolerance, increasing the shared selection budget changes the restricted-minus-full mean difference from positive to negative. Both seed-selection procedures vary with $W$, so this contrast cannot be attributed solely to an improving full reference.")
edit(ZH,'在默认 PageRank 容差下，增加参照预算会使受限方法相对参照的平均表现由增益转为损失。','在默认 PageRank 容差下，增加共享选择预算使受限方法减全候选参照的平均差值由正转负。两类种子选择过程均随 $W$ 变化，因此不能将这一比较完全归因于全候选参照的改善。')
edit(EN,' Pool agreement at $10^{-12}$ and $10^{-14}$ checks membership stability at the tested tolerances, without certifying an exact ranking.','', '容差成员稳定性及边界已在实验设置说明')
edit(ZH,'$10^{-12}$ 与 $10^{-14}$ 下的候选池一致性，检验了已测试容差下的成员稳定性，但并未证明排名精确。','','容差成员稳定性及边界已在实验设置说明')
edit(EN,'Candidate fraction, ranking tolerance and reference budget specify the quality comparison; included timing stages specify the cost comparison. These observations complement solver-efficiency research by clarifying the measured trade-off, without providing a runtime comparison against CELF or IMM.','Candidate fraction, ranking tolerance and the shared selection budget specify the quality comparison; included timing stages specify the cost comparison. Reporting these settings connects the measured computational savings to their associated spread differences.')
edit(ZH,'候选比例、排名容差和参照预算规定质量比较，计时所包含的阶段规定成本比较。这些观察通过明确实测权衡补充求解效率研究，但没有提供与 CELF 或 IMM 的运行时间比较。','候选比例、排名容差和共享选择预算规定质量比较，计时所包含的阶段规定成本比较。报告这些设置，可将实测计算节省与对应传播差异联系起来。')
edit(EN,' The direction diagnostic is consistent with the measured wiki-Vote loss but does not establish a causal explanation.','', '方向诊断的非因果边界已保留在紧邻解释的讨论段')
edit(ZH,'方向诊断与 wiki-Vote 的实测损失一致，但不能确立因果解释。','','方向诊断的非因果边界已保留在紧邻解释的讨论段')
edit(EN,'Reference agreement establishes neither optimality with respect to expected spread nor convergence as the world budget increases.','Reference agreement establishes neither optimality with respect to expected spread nor convergence as the world budget increases. A positive mean difference with mixed path signs is not sufficient evidence of superiority, and nonsignificance is not equivalence.')
edit(ZH,'参照一致性既不证明相对于期望传播量的最优性，也不证明随世界预算增加而收敛。','参照一致性既不证明相对于期望传播量的最优性，也不证明随世界预算增加而收敛。路径差值正负并存时，正均值不足以确立优势；未显著也不等于等效。')
edit(EN,' These are open tests, not outcomes established by the current data.','')
edit(ZH,'这些均是尚待检验的问题，不是当前数据已经支持的结果。','')
para(EN,'Candidate-restriction quality must',r'''Candidate-restriction quality depends on finite-world seed selection in both methods and on the ranking that defines the restricted pool. Increasing $W$ changes both selection procedures; independently evaluated relative differences therefore describe their joint response to the selection budget. On ca-GrQc, tightening PageRank tolerance removes the apparent budget-induced sign reversal, while budget-dependent seed changes remain. Separate reference-transition comparisons show that set changes can accompany positive, negative or zero estimated spread changes. Across the external sample, Degree-4k preserves the tested $W=1280$ trajectories at lower measured selection cost, whereas PageRank outcomes depend on precision, coverage and network context. Evaluation reports should distinguish the shared selection budget, the independent evaluation budget and candidate-pool construction, and report signed spread differences alongside scoped costs. These findings apply to the networks, propagation settings and implementations examined here.''')
para(ZH,'候选限制的质量需要',r'''候选限制的质量取决于两类方法的有限世界种子选择，以及定义受限候选池的排名。增加 $W$ 会改变两类选择过程，因此，独立评估的相对差异描述了二者对选择预算的共同响应。在 ca-GrQc 上，收紧 PageRank 容差使表面上由预算引起的符号反转消失，但预算相关的种子变化仍然存在。单独的参照预算转移比较表明，集合变化可伴随正、负或零的估计传播量变化。在外部网络样本中，Degree-4k 以更低的实测选择成本保持了已测试的 $W=1280$ 参照轨迹，而 PageRank 结果依赖精度、覆盖率与网络背景。评价报告应区分共享选择预算、独立评估预算与候选池构建，并同时报告有符号的传播差值和明确范围的计算成本。这些发现适用于本文考察的网络、传播设置与实现。''')

# Editorial materials: synchronize the exact contribution wording.
en=(R/EN).read_text(encoding='utf-8')
items=re.findall(r'\\item\[\(\d\)\] (.*)',en)
def plain(s):
    s=re.sub(r'\\textbf\{([^{}]*)\}',r'\1',s)
    return s.replace('$','').replace('--','–')
for rel in ['cover_letter_draft.txt','summary_for_editor.txt']:
    for prefix,new in zip(['We identify how ranking precision','We quantify the spread gains','We identify which tested'],items):
        para(rel,prefix,plain(new))
para('cover_letter_draft.txt','The manuscript addresses', 'The manuscript examines how finite selection sampling and candidate-ranking precision affect the evaluation of candidate restriction. In the budget sweeps, W governs seed selection for both the full-candidate reference and the restricted methods. Their relative spread differences therefore reflect budget-dependent changes in both procedures. Independent evaluation uses a fixed, separate family of 10,000 worlds; ranking tolerance and pool size control candidate eligibility. At a fixed W, the post-hoc tolerance control recomputes the restricted arms and reuses the full reference selected at that budget.')
para('cover_letter_draft.txt','We consider this study relevant','We consider this study relevant to Computing because it examines numerical computation in the evaluation of network algorithms. Three external topologies form the main comparison; four small contact graphs provide separate historical sensitivity controls. The manuscript reports signed spread differences, candidate coverage and implementation-specific cost measurements, supported by source snapshots, configurations, saved outputs and validation records.')
para('summary_for_editor.txt','Candidate restriction saves','Candidate restriction narrows seed eligibility, but its measured quality compares two seed sets selected from finite samples. In the budget sweeps, W governs selection in both the full and restricted arms. Their relative differences reflect changes in both procedures. Ranking tolerance and pool size determine eligibility separately, while independent evaluation uses 10,000 fixed worlds. At a fixed W, the post-hoc tolerance control reuses the same-budget full reference and recomputes only restricted selection.')
edit('summary_for_editor.txt','coverage, reference budget, ranking tolerance','coverage, the shared selection budget, ranking tolerance')

# Supplementary exposition and table labels, without changing numeric cells.
SI='manuscript/Online_Resource_1.tex'
edit(SI,'\\section{Statistical interpretation}',r'''\section{Selection and evaluation budgets}
In the external budget sweeps and the 520-condition historical extension, every arm selects its seeds using the same $W$ worlds within a condition. Full and restricted selections are recomputed at each $W$; candidate pools are fixed across budgets for a given ranking setting. Each graph/path/coupling uses a separate $M=10,000$-world evaluation family, fixed across arms and budgets. The initial 42-condition study instead used $M=2000$, as recorded above.

Ranking tolerance and pool cutoff govern candidate construction, separately from $W$ and $M$. At a fixed $W$, the post-hoc precision control recomputes only restricted arms and reuses the verified full-reference result at that budget. Across $W$, the comparator is the corresponding budget-specific full reference. Restricted-minus-full differences and higher-minus-lower-budget full-reference transitions are distinct comparisons.

\section{Statistical interpretation}''')
edit(SI,'Percentage loss is\nminus the paired mean difference', 'The paired difference is restricted minus same-budget full-reference spread. Percentage loss is\nminus the paired mean difference')
edit(SI,'Complete default-tolerance budget comparison. Points','Complete default-tolerance budget comparison. Both arms select at the plotted $W$, with independent evaluation fixed across budgets. Points')
edit(SI,'reusing the frozen full references and disjoint evaluation-world IDs.','reusing the frozen full reference for each corresponding budget and disjoint evaluation-world IDs.')
edit(SI,'These are graph-specific,\npost-hoc sensitivity findings, not an equivalence, superiority or significance claim.','These graph-specific, post-hoc sensitivity findings use paired effect sizes and path variation as described in the statistical interpretation.')
edit('manuscript/history_evidence.tex','Selection budgets use nested world prefixes.','Selection budgets use nested world prefixes for every arm. At each $W$, both full and restricted methods select seeds anew; the 10,000-world evaluation family stays fixed across budgets within each graph/path/coupling.')
edit('manuscript/history_evidence.tex','mean gain','mean high-minus-low spread change')
edit('manuscript/transition_table.tex','Gain is the paired independent change in total spread','Change is the paired independent higher-minus-lower-budget difference in full-reference total spread')
edit('manuscript/transition_table.tex','Mean gain','Mean change')
for rel in ['manuscript/history_parameter_table.tex','manuscript/history_coupling_table.tex','manuscript/history_secondary_table.tex']:
    edit(rel,'negative when restriction gains','negative when restricted spread exceeds full-reference spread')

for rel in [EN,ZH,SI,'cover_letter_draft.txt','summary_for_editor.txt']:
    before=(B/rel).read_text(encoding='utf-8');after=(R/rel).read_text(encoding='utf-8')
    (R/'qa'/((Path(rel).stem)+'.diff')).write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='baseline/'+rel,tofile='revision/'+rel)),encoding='utf-8')
(R/'qa/change_log.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
print(str(R.resolve()))
