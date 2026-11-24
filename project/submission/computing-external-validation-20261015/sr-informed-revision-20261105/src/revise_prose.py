from pathlib import Path
import re,json,difflib
R=Path(__file__).resolve().parents[1];B=R.parent/'concise-prose-revision-20261031'
changes=[]
def segment(s,start,end,new,tag):
 a=s.index(start);b=s.index(end,a);old=s[a:b];changes.append(dict(location=tag,before=old,after=new));return s[:a]+new+s[b:]

abstract_en=r'''Restricting seed candidates can reduce influence-maximization cost, but the resulting quality judgment depends on how both compared seed sets are computed. We separate the shared selection-world budget from candidate-ranking precision and assess selected seeds on 10,000 independent worlds. Three external networks provide the main comparison, with four small contact graphs supplying separate controls. On ca-GrQc, default PageRank-4k changes from a mean relative incremental-spread difference of $+5.61$\% to $-5.07$\% as the selection budget increases. A post-hoc tolerance control replaces two candidates and removes this mean sign reversal, while budget-dependent seed changes persist. Independent evaluation also distinguishes set instability from utility change: 16 of 40 historical reference sets change, with a mean spread increase of 0.01111 nodes across all pairs. At the highest external budget, 20-node degree pools reproduce all 15 reference trajectories at lower measured selection cost. PageRank losses remain on the directed networks. These results identify a precision-sensitive quality judgment and quantify when different seed outputs correspond to different spread, linking candidate compression to its measured utility and cost.'''
abstract_zh=r'''限制种子候选范围能够降低影响力最大化的计算成本，但对其质量的判断取决于参与比较的两个种子集合如何计算得到。本文分别控制两类方法共享的选择世界预算与候选排名精度，并在10,000个独立世界上评估已选种子。三张外部网络提供主要比较，四张小规模接触图提供单独对照。在ca-GrQc上，随着选择预算增加，默认PageRank-4k的平均相对增量传播差异由$+5.61$\%变为$-5.07$\%。事后容差控制替换两个候选节点后，这一平均符号反转消失，但预算相关的种子变化仍然存在。独立评估进一步区分了集合不稳定性与效用变化：40个历史参照集合中有16个改变，而全部配对的平均传播量增加0.01111个节点。在最高外部预算下，含20个节点的度候选池以更低的实测选择成本复现全部15条参照轨迹；有向网络上的PageRank损失仍然存在。这些结果识别了对精度敏感的质量判断，量化不同种子输出所对应的传播差异，并将候选压缩与其实际效用和计算代价联系起来。'''
contrib_en=r'''\item[(1)] \textbf{We distinguish ranking-precision sensitivity from the shared-budget response.} On ca-GrQc, a post-hoc tolerance control replaces two of 20 candidates and removes the default mean gain-to-loss reversal. Comparing tolerances at fixed $W$ identifies this dependence; comparing budgets at fixed tolerance separately tracks changes in both selection procedures.
\item[(2)] \textbf{We quantify the utility consequences of seed-set changes.} Independent paired evaluation measures signed spread differences alongside trajectory and set agreement. In the historical $W=1280$ to 5120 transition, 16/40 sets change, but mean spread increases by only 0.01111 nodes across all pairs, with negative, positive and zero differences. This quantifies what a set-change count alone leaves unresolved.
\item[(3)] \textbf{We measure the utility and computational cost of candidate compression.} Degree-4k retains all 15 external reference trajectories at $W=1280$ using 20 candidates and lower measured selection time. Default PageRank-4k retains none; expanding its pool reduces the directed-network losses without eliminating them. These contrasts identify reference-preserving and lossy restrictions within the tested settings.
'''
contrib_zh=r'''\item[(1)] \textbf{区分排名精度敏感性与共享预算变化的影响。}在ca-GrQc上，事后容差控制替换20个候选节点中的两个，使默认设置下平均表现由增益转为损失的现象消失。固定$W$比较容差识别了这种依赖；固定容差比较预算，则单独追踪两类选择过程的变化。
\item[(2)] \textbf{量化种子集合变化对应的效用差异。}通过配对独立评估，将有符号的传播差值与轨迹、集合一致性对应起来。在历史$W=1280$到5120的比较中，16/40个集合改变，但全部配对的平均传播量仅增加0.01111个节点，同时包含负、正及零差值。这给出了仅凭集合变化次数无法确定的效用变化大小。
\item[(3)] \textbf{测量候选压缩的传播质量与计算代价。}在$W=1280$时，Degree-4k用20个候选节点保持全部15条外部参照轨迹，并降低实测选择时间。默认PageRank-4k未保持任何一条轨迹；扩大其候选池降低了有向网络上的损失，但未消除损失。这些对照识别了已测试设置中保持参照与产生损失的候选限制。
'''
io_en=r'''\paragraph{Inputs and outputs.} Each run takes the processed graph $G$, its arc directions, $k$, $p$, $h$, the shared selection budget $W$ and a candidate rule. Ranking tolerance $\tau$ and cutoff $q$ determine the restricted pool $C$; they leave the propagation graph intact. Selection returns an ordered sequence of $k$ seeds and its final set, together with selection time. Independent evaluation takes that set and $M$ held-out worlds, returning total spread, incremental spread and paired differences from the same-budget full reference. Tables~\ref{tab:primary} and~\ref{tab:case} connect these outputs to candidate counts and original node IDs.

'''
io_zh=r'''\paragraph{输入与输出。}每次运行输入处理后的图$G$及边方向、$k$、$p$、$h$、共享选择预算$W$和候选规则。排名容差$\tau$与截断值$q$决定受限候选池$C$，传播图保持完整。选择阶段输出$k$个种子的有序序列、最终集合及选择耗时。独立评估以该集合和$M$个留出世界为输入，输出总传播量、增量传播量及相对同预算全候选参照的配对差值。表~\ref{tab:primary}和表~\ref{tab:case}将这些输出与候选数量及原始节点编号对应起来。

'''
precision_en=r'''The exchanged candidate IDs make the precision effect explicit: IDs 1488 and 19865 leave the ca-GrQc pool, while 17655 and 6610 enter. Table~\ref{tab:precision-output} links this fixed pool change to seed-set changes and signed spread differences at all three budgets. Online Resource 1 lists every paired seed sequence and conditional Monte Carlo error. Figure~\ref{fig:precision-budget} retains the corresponding comparisons on all three networks.
\input{precision_output.tex}

'''
precision_zh=r'''候选节点编号明确了精度控制改变的对象：ca-GrQc池中的1488和19865被移出，17655和6610被纳入。表~\ref{tab:precision-output}将这一固定候选池变化与三个预算下的种子集合变化、有符号传播差值对应起来。在线补充材料1列出全部配对种子序列及条件Monte Carlo误差。图~\ref{fig:precision-budget}保留三张网络上的对应比较。
\input{precision_output.tex}

'''
case_en=r'''Table~\ref{tab:case} traces one saved input through selection and evaluation. For wiki-Vote path 1101, Degree-4k returns the same five seeds as full selection and the same total spread, 60.8455. Default PageRank-4k returns five different seeds and total spread 19.9366. Expanding its pool to 356 candidates returns total spread 47.2095. The case illustrates the outputs; the five-path means are 60.73602, 20.04268 and 47.20590, respectively. Table~\ref{tab:primary} reports their incremental counterparts and signed gaps for every external graph.
\input{input_output_case.tex}

'''
case_zh=r'''表~\ref{tab:case}追踪一个已保存输入从选择到评估的输出。在wiki-Vote路径1101上，Degree-4k与全候选选择返回相同的五个种子，总传播量均为60.8455。默认PageRank-4k返回五个不同的种子，总传播量为19.9366；将候选池扩大至356个节点后，总传播量为47.2095。该案例说明具体输出；对应的五路径均值分别为60.73602、20.04268和47.20590。表~\ref{tab:primary}报告所有外部图的对应增量传播量及有符号差值。
\input{input_output_case.tex}

'''
discussion_en=r'''\section{Discussion}
\subsection{A budget comparison can depend on candidate-pool precision}
The ca-GrQc reversal disappears after two candidates are exchanged by a tighter PageRank tolerance. This changes the interpretation of the default budget scan. At fixed $W$, the full reference and evaluation worlds are unchanged, so the tolerance comparison isolates the consequence of the revised restricted pool. Across $W$, both methods select anew. The remaining budget-dependent seed changes therefore concern selection within each pool, whereas the lost mean sign reversal depends on which pool is used. The positive strict-tolerance mean at $W=1280$ also combines positive and negative path differences; it does not establish a uniform advantage.

StaticGreedy uses shared fixed realizations to maintain a consistent sampled objective \cite{ref8}. The present comparison adds an earlier computational step: numerical ranking determines eligibility before that objective is searched. Fixing the sampled worlds cannot hold eligibility constant when the truncated ranking changes. The two controls answer different questions and both matter for interpreting this example. Our fixed-edge control follows the coverage construction; the step-indexed objective has the finite-sample limitation described in Methods. These sampled objectives must be distinguished from the expected-spread guarantee of Kempe et al. \cite{ref1}.

\subsection{Seed differences need an independent utility scale}
On ca-GrQc, all five reference sets change between $W=320$ and 1280, yet their mean spread change is 0.12720 nodes. On wiki-Vote, some selection orders change while the final sets and evaluated spread remain identical. These observations separate two sources of apparent instability: changing the order of the same seeds and changing the seeds themselves. Even in the latter case, the signed utility difference requires measurement. The historical mean of 0.01111 nodes accompanies 16 changed sets across 40 pairs and includes both positive and negative changes.

Quality--cost benchmarking compares achieved influence with computation \cite{ref16}. Here, reporting the actual spread alongside agreement distinguishes preservation of the sampled solution from similarity in utility. The wiki-Vote example makes the distinction concrete: the degree pool reproduces the reference seeds, whereas the PageRank pools return different seeds and lower spread. Across all five paths, enlarging the default PageRank pool raises mean total spread from 20.04268 to 47.20590, against 60.73602 for full selection. An agreement count alone would miss the size of that recovery.

\subsection{Coverage and direction explain different parts of the comparison}
The default wiki-Vote PageRank-4k pool excludes every full-reference seed at $W=1280$; the 5\% pool contains only one. Reproducing the full set is therefore impossible within either pool. Increasing coverage still reduces incremental loss from 73.01\% to 24.28\%, showing that membership overlap and recovered utility describe different outcomes. The degree pool contains and selects the reference seeds with only 20 candidates. Pool size alone does not explain the contrast between the two rankings.

The structural diagnostic is consistent with the direction of the ranking and propagation: PageRank candidates have higher mean in-degree, while degree candidates have higher mean out-degree. Diffusion follows outgoing arcs in this experiment. Because direction was not intervened on, this remains an explanation consistent with the observations rather than an isolated causal effect. The simulated objective also differs from estimating influence from observed adoption, as in empirical influence modelling \cite{ref15}.

Selection-time savings have different meanings for these outputs. Degree-4k saves time while reproducing the tested reference; the PageRank savings accompany the reported spread losses. Setup and independent evaluation reduce the savings when included in assembled costs. The relevant comparison therefore depends on whether a user needs seed selection with prepared worlds or the full evaluated workflow.

\subsection{Scope and unresolved comparisons}
The external sample comprises three graphs with $k=5$, $p=.01$, $h=3$ and $W\le1280$. Historical contact graphs extend parameter and coupling coverage, but do not establish the same sensitivity on larger directed networks. At historical $k=20$, Kenya's 4k pool is the complete 75-node graph and invs2013 retains 80/91 vertices. These high-coverage cases provide limited evidence for aggressive candidate reduction.

The precision control is post-hoc and reuses the original five paths. Paths describe computational variation on each graph; conditional Monte Carlo errors describe fixed seed sets. Reference agreement is with a sampled greedy solution, and timings compare this implementation's exhaustive selection. The saved experiments leave two specific explanations unresolved: whether the external precision result persists under fixed-edge coupling, and whether changing propagation direction changes the directed-network ranking contrast. Wider external probability and horizon settings would also be required to assess transfer of the historical parameter controls.

'''
discussion_zh=r'''\section{讨论}
\subsection{预算比较依赖候选池的数值精度}
更严格的PageRank容差替换两个候选节点后，ca-GrQc上的反转消失，改变了对默认预算扫描的解释。固定$W$时，全候选参照和评估世界不变，因此容差比较分离出了受限候选池变化的后果。跨$W$时，两类方法都重新选择种子。因此，仍然存在的预算相关种子变化对应各候选池内部的选择，而消失的平均符号反转依赖所使用的候选池。在$W=1280$时，严格容差下的正均值也包含正、负路径差值，不能据此确定一致优势。

StaticGreedy通过共享固定采样实现保持采样目标的一致性\cite{ref8}。本文的比较增加了对更早计算环节的考察：在搜索目标函数之前，数值排名已经决定了候选资格。截断排名改变时，固定采样世界不能使候选资格保持不变。这两种控制回答不同问题，理解该案例需要同时考虑二者。固定边对照遵循覆盖构造，按步索引目标则具有研究方法所述的有限样本限制；这些采样目标需要与Kempe等关于期望传播量的保证区分\cite{ref1}。

\subsection{种子差异需要独立的效用尺度}
在ca-GrQc上，$W$从320增加到1280时，五个参照集合全部改变，但平均传播量仅变化0.12720个节点。在wiki-Vote上，部分选择顺序改变，而最终集合和评估传播量完全相同。这些观察区分了两种表面不稳定性：相同种子的顺序改变，以及种子成员本身改变。即使成员改变，仍需测量有符号的效用差值。历史比较中，40个配对有16个集合改变，平均传播量变化为0.01111个节点，同时包含正、负变化。

质量与成本基准研究将达到的传播效果与计算量对应起来\cite{ref16}。本文同时报告实际传播量与一致性，以区分复现采样解和效用相近。wiki-Vote案例具体展示了这一区别：度候选池复现参照种子，PageRank候选池则返回不同种子和较低传播量。在全部五条路径上，扩大默认PageRank候选池使平均总传播量从20.04268增至47.20590，全候选结果为60.73602。仅报告一致性次数无法反映这一恢复幅度。

\subsection{覆盖率与方向解释比较中的不同方面}
默认wiki-Vote PageRank-4k候选池在$W=1280$时排除了全部参照种子，5\%池也仅包含一个。因此，两种池内都无法复现完整参照集合。扩大覆盖率仍使增量传播损失由73.01\%降至24.28\%，说明成员重叠与恢复的效用描述不同结果。度候选池仅用20个候选节点便包含并选出参照种子，因而候选池大小本身不足以解释两种排名的差别。

结构诊断与排名和传播的方向一致：PageRank候选节点的平均入度较高，度候选节点的平均出度较高，而本实验沿出向边传播。由于未干预方向，这仍是与观察一致的解释，而非已被单独识别的因果效应。该模拟目标也不同于实证影响力建模中根据实际采纳行为估计影响力的目标\cite{ref15}。

选择时间节省对这些输出具有不同含义。Degree-4k在复现已测试参照的同时节省时间，PageRank的时间节省则伴随所报告的传播损失。将准备和独立评估计入拼接成本后，节省比例降低。因此，需要区分使用者是在已有世界上选择种子，还是执行包含独立评估的完整流程。

\subsection{适用范围与尚未解决的比较}
外部样本包含三张图，设置为$k=5$、$p=.01$、$h=3$和$W\le1280$。历史接触图扩展了参数与耦合覆盖，但不能确定较大有向网络具有相同敏感性。在历史$k=20$时，Kenya的4k池即完整75节点图，invs2013保留80/91个节点。这些高覆盖率条件对大幅压缩候选范围的支持有限。

精度控制属于事后分析，复用原五条路径。路径描述各图上的计算变异，条件Monte Carlo误差描述固定种子集合的不确定性。参照一致性针对采样贪心解，计时比较针对本实现的完整枚举选择。已保存实验仍留下两个具体问题：外部精度结果能否在固定边耦合下保持，以及改变传播方向是否会改变有向网络上的排名差异。评估历史参数对照的迁移还需要更广的外部传播概率与期限设置。

'''
conclusion_en=r'''The paired comparisons identify a ranking-precision dependence in a budget-based quality judgment and quantify the spread consequences of seed changes. On ca-GrQc, the default mean reversal disappears after the candidate pool changes under tighter tolerance; budget-dependent seed changes remain. Independent evaluation distinguishes these changes from their signed utility effects. On the external networks, degree pools preserve the highest-budget reference at lower selection cost, while PageRank illustrates losses and partial recovery through greater coverage. For the tested simulation settings, reporting candidate membership, both methods' selection budget, independent spread and scoped costs makes the quality of candidate compression assessable.

'''
conclusion_zh=r'''配对比较识别了预算相关质量判断对排名精度的依赖，并量化种子变化的传播后果。在ca-GrQc上，更严格容差改变候选池后，默认设置下的平均反转消失，但预算相关种子变化仍存在。独立评估将这些变化与其有符号效用差异区分开来。在外部网络上，度候选池以更低选择成本保持最高预算参照，而PageRank展示了传播损失及增加覆盖率后的部分恢复。对于已测试的模拟设置，同时报告候选成员、两类方法的选择预算、独立传播量与明确范围的成本，可以使候选压缩的质量得到具体评价。

'''
for zh,rel in [(False,'manuscript/manuscript.tex'),(True,'chinese/manuscript/manuscript_zh.tex')]:
 s=(B/rel).read_text(encoding='utf-8')
 s=segment(s,r'\begin{abstract}',r'\keywords',r'\begin{abstract}'+'\n'+(abstract_zh if zh else abstract_en)+'\n',rel+':abstract')
 s=segment(s,r'\item[(1)]',r'\end{enumerate}',contrib_zh if zh else contrib_en,rel+':contributions')
 key=r'\subsection{网络与预处理}' if zh else r'\subsection{Networks and preprocessing}'
 # Find first experimental subsection directly if Chinese heading differs.
 if key not in s:
  a=s.index(r'\section{实验设置}');key=s[s.index(r'\subsection{',a):s.index('\n',s.index(r'\subsection{',a))]
 s=s.replace(key,(io_zh if zh else io_en)+key,1)
 key='CollegeMsg' if not zh else 'CollegeMsg'
 a=s.index(r'\section{研究结果}') if r'\section{研究结果}' in s else s.index(r'\section{结果}') if zh else s.index(r'\section{Results}')
 # Insert before precision figure, after all network results.
 point=s.index(r'\begin{figure}',a)
 s=s[:point]+(precision_zh if zh else precision_en)+s[point:]
 s=s.replace(r'\input{primary_table.tex}',r'\input{primary_table.tex}'+'\n\n'+(case_zh if zh else case_en),1)
 start=r'\section{讨论}' if zh else r'\section{Discussion}'
 end=r'\section{结论}' if zh else r'\section{Conclusion}'
 s=segment(s,start,end,discussion_zh if zh else discussion_en,rel+':discussion')
 endpara=r'\paragraph{补充信息。}' if zh else r'\paragraph{Supplementary information.}'
 s=segment(s,end,endpara,end+'\n'+(conclusion_zh if zh else conclusion_en),rel+':conclusion')
 (R/rel).write_text(s,encoding='utf-8')
 (R/'qa'/('chinese.diff' if zh else 'english.diff')).write_text(''.join(difflib.unified_diff((B/rel).read_text(encoding='utf-8').splitlines(True),s.splitlines(True),fromfile=str(B/rel),tofile=str(R/rel))),encoding='utf-8')
s=(B/'manuscript/Online_Resource_1.tex').read_text(encoding='utf-8')
s=s.replace(r'\section{File map and availability}',r'\clearpage'+'\n'+r'\input{presentation_supplement.tex}'+'\n'+r'\section{File map and availability}')
(R/'manuscript/Online_Resource_1.tex').write_text(s,encoding='utf-8')
letter=(B/'cover_letter_draft.txt').read_text(encoding='utf-8')
start=letter.index('The manuscript examines');end=letter.index('All authors have')
letter=letter[:start]+'''Candidate restriction can make seed selection cheaper, but its measured quality depends on both finite-budget selection and the ranking that defines eligibility. This evaluation study distinguishes those effects with same-budget precision controls, shared-budget sweeps and independent spread assessment.

On ca-GrQc, tightening PageRank tolerance changes two candidates and removes the default mean gain-to-loss reversal. The control is post-hoc and reuses the original paths. Separate reference transitions quantify the spread consequences of changed seeds: 16 of 40 historical sets change, with a mean increase of 0.01111 nodes across all pairs and both positive and negative changes. On three external networks, 20-node degree pools reproduce all 15 highest-budget reference trajectories at lower measured selection cost; PageRank losses persist on directed networks.

The revised presentation connects candidate inputs to selected node IDs, independently estimated spread and computational cost. Complete-path summaries accompany a single-path illustration. The contribution is empirical evidence on how numerical choices affect candidate-restriction judgments, situated alongside prior work on sampled objectives and influence-maximization benchmarking. It addresses Computing's readership interested in numerical computation and network-algorithm evaluation. Costs refer to the implemented exhaustive reference, and the observations concern the tested simulation settings.

'''+letter[end:]
(R/'cover_letter_draft.txt').write_text(letter,encoding='utf-8')
(R/'summary_for_editor.txt').write_text('Evaluating Candidate-Restricted Influence Maximization: Effects of Reference Budget and Ranking Precision\n\n'+'''The study identifies a precision-sensitive budget comparison, quantifies the spread consequences of seed-set changes, and measures candidate compression against independently evaluated utility and scoped computation. The ca-GrQc mean sign reversal disappears when tighter PageRank tolerance replaces two pool members. Across the external graphs, degree pools preserve all 15 W=1280 reference trajectories; directed-network PageRank losses remain. Three external graphs provide the main evidence, historical contact graphs supply separate controls, and the precision study is post-hoc on original paths. Tables connect candidate counts, selected node IDs and actual spread. This revision adds no experiments and makes no new algorithmic or theoretical claim.\n''',encoding='utf-8')
(R/'qa/prose_changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
print('Revised English, Chinese, supplement, cover letter and summary')
