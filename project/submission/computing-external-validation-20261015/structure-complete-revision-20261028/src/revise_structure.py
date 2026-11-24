"""Revise manuscript structure and translate changed passages. No experiment calls."""
from pathlib import Path
import shutil,json,hashlib,difflib,re
R=Path(__file__).resolve().parents[1]
B=R.parent/'problem-led-revision-20261028'
def read(p):return p.read_text(encoding='utf-8-sig')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
EN={
31:r'''Influence maximization selects a limited set of seed vertices to maximize expected spread under a specified diffusion model \cite{ref1}. It formalizes targeted seeding, such as choosing initial adopters in a social network. Greedy selection repeatedly estimates the spread gained by adding a vertex, making computational cost a central concern. Lazy evaluation, reuse of sampled realizations and sampling-based optimization address this cost through different computational strategies \cite{ref7,ref8,ref2}. Candidate restriction reduces the set of vertices eligible for selection. Its practical value depends on how much spread is retained for the computation saved.

Establishing this trade-off is difficult when the full-candidate reference is itself selected from finitely sampled diffusion worlds. The observed gap compares two computed seed sets, and its interpretation depends on how both were obtained. Misattributing that gap can lead to an incorrect judgment about whether a cheaper candidate pool preserves the reference's utility.''',
52:r'''\paragraph{Objectives, sampling and computational efficiency.} Kempe et al. establish monotonicity and submodularity of expected spread under the independent-cascade model, supporting greedy approximation \cite{ref1}. CELF exploits submodularity to avoid unnecessary marginal reevaluations \cite{ref7}. StaticGreedy reuses fixed sampled realizations throughout selection, preserving a consistent sampled coverage objective \cite{ref8}. IMM develops a sampling-based solver with approximation guarantees \cite{ref2}. These approaches address the computational difficulty of optimization under specified objectives. Their results motivate careful treatment of the sampled objective, but do not identify the utility consequence of excluding vertices through a particular truncated ranking. Our comparison holds the simulator and greedy rule fixed while changing eligibility, reference budget or ranking tolerance.''',
54:r'''\paragraph{Influence estimation and seed-selection strategies.} Rui et al. estimate influence from multiple neighbourhood levels \cite{ref12}, while Fan et al. use discrete Harris hawks optimization for seed selection \cite{ref13}. Ko et al.'s MONSTOR+ predicts spread on unseen graphs \cite{ref19}. These studies offer different ways to estimate influence or search for seed sets. Their algorithmic objectives differ from assessing a fixed ranking solely as a filter on seed eligibility. In the latter setting, greedy selection still operates on the complete propagation graph, and candidate coverage becomes part of the comparison. We therefore distinguish a ranking's role in defining the pool from the simulator's role in evaluating its selected seeds.''',
56:r'''\paragraph{Evaluation settings and the remaining question.} Li et al. survey influence-maximization methods \cite{ref9}, and Arora et al. examine their quality and computational cost in a benchmarking study \cite{ref16}. Yanchenko et al. review temporal-network formulations \cite{ref11}; Aral and Dhillon study empirical influence models \cite{ref15}. Together, these research directions place algorithm comparisons within their diffusion models, network representations and evaluation settings. Our experiments use observed topologies with simulated diffusion. They assess sensitivity within that computational setting and do not estimate realized social influence.''',
58:r'''The question addressed here is how a candidate-restriction judgment depends on two numerical components: the sampled full-candidate reference and the ranking that determines eligibility. A comparison at one budget--tolerance setting does not reveal whether its conclusion persists when either component changes. We examine this dependence with paired budget and precision controls and assess seed differences on independent worlds. This extends the evaluation of quality and cost to the stability of the comparison itself. Online Resource 1 relates this question to the cited studies' stated objectives; it does not infer that an unreported check was absent from every implementation.''',
60:r'''\section{Methods}
This is a simulation-based paired evaluation study. We compare full-candidate and candidate-restricted greedy selection under shared conditions, then evaluate the resulting seed sets independently. The design separates reference-budget and ranking-precision sensitivity from candidate coverage, propagation controls and computational cost. Section~\ref{sec:experimental-setup} specifies the networks, condition matrix and execution settings.''',
93:r'''\section{Experimental setup}\label{sec:experimental-setup}''',
178:r'''On wiki-Vote, the default PageRank top 20 have mean in-degree 249.75 and out-degree 56.2; the degree top 20 have mean in-degree 70.3 and out-degree 489.25. The PageRank-4k pool contains none of the five full-reference seeds on any $W=1280$ path, and its 5\% pool contains only one. The seed-level illustration and complete coverage comparisons appear in Online Resource 1.''',
197:r'''The ca-GrQc result changes the interpretation of an apparent budget effect. At default PageRank tolerance, increasing the reference budget changes the restricted method's mean comparison from a gain to a loss. Tightening tolerance exchanges two pool members and removes that pattern, although increasing $W$ still changes selected sets. Thus, the default reversal is not evidence for a budget effect that is independent of ranking precision. The candidate cutoff makes numerical ranking differences relevant to seed eligibility. Pool agreement at $10^{-12}$ and $10^{-14}$ checks membership stability at the tested tolerances, without certifying an exact ranking. Losses persist on CollegeMsg and wiki-Vote, so this explanation does not account for every unfavorable PageRank comparison.

StaticGreedy already makes reuse of sampled realizations central to a consistent finite objective \cite{ref8}. Our fixed-edge control follows the same coverage principle, whereas the primary step-indexed coupling can produce a nonmonotone finite objective. This distinction concerns the sampled construction and does not contradict the expected-spread result of Kempe et al. \cite{ref1}. The additional issue identified here occurs before selection: numerical tolerance can change which vertices enter a truncated pool. Shared worlds control the comparison between eligible sets, but do not remove this dependence on pool construction.''',
200:r'''Benchmarking work examines influence-maximization quality together with computational cost \cite{ref16}. Our paired comparisons add a distinction between preserving a reference's seeds and preserving its independently evaluated utility. A changed trajectory may end at the same set, which gives the same evaluation vector under shared simulation worlds. When sets differ, paired evaluation measures the sign, magnitude and conditional uncertainty of their utility difference. The external ca-GrQc mean change of 0.12720 nodes and the historical step-coupled mean change of 0.01111 nodes illustrate distinct budget transitions. Neither value defines an application-specific equivalence margin.

This distinction changes how a reported speed saving should be read. The degree-pool results identify computation saved while preserving the tested reference. The PageRank results require the corresponding utility loss to be considered alongside that saving. Candidate fraction, ranking tolerance and reference budget specify the quality comparison; included timing stages specify the cost comparison. These observations complement solver-efficiency research by clarifying the measured trade-off, without providing a runtime comparison against CELF or IMM.''',
201:r'''
\subsection{Network direction and transfer of ranking results}
The wiki-Vote observations are consistent with a mismatch between incoming importance and outgoing propagation. The PageRank pool emphasizes vertices with many incoming links, while diffusion in this study follows outgoing arcs. Direction was not experimentally reversed, so the diagnostic does not isolate a causal mechanism. Network structure, candidate coverage and the propagation setting remain relevant to the observed loss. The broader distinction between a simulated objective and an empirical influence model also matters \cite{ref15}. Agreement on contact graphs cannot by itself establish that a ranking will preserve utility on differently directed networks. The increase in PageRank coverage improves the measured comparison, but does not eliminate the wiki-Vote loss.
''',
202:r'''\subsection{Scope, limitations and next tests}''',
208:r'''
\paragraph{Next tests.} Two targeted studies follow from these limits. A joint tolerance--coupling control on the external networks would test whether the precision-sensitive interpretation persists with fixed-edge worlds. A direction intervention, with the remaining settings held constant, would help distinguish the proposed directional explanation from other structural differences. Broader external probability and horizon settings are also needed before extending the contact-graph sensitivity results. These are open tests, not outcomes established by the current data.
''',
210:r'''Candidate-restriction quality must be interpreted relative to both a sampled reference and a numerically constructed candidate pool. Through paired controls and independent evaluation, this study separates numerical sensitivity, seed agreement and utility retention. On ca-GrQc, tightening PageRank tolerance removes the apparent budget-induced quality reversal, while budget-dependent seed changes remain. Across the external sample, Degree-4k preserves the tested $W=1280$ trajectories at lower measured selection cost, while PageRank outcomes depend on precision, coverage and network context. These findings make the basis of a measured quality--cost trade-off explicit. Their scope is the studied networks and settings; matching a finite reference does not establish expected-spread optimality. Joint precision--coupling controls and direction interventions are the next tests of the interpretation beyond the present comparisons.''',
}
ZH={
31:r'''影响力最大化在给定传播模型下选择有限数量的种子节点，以最大化期望传播量 \cite{ref1}。它将定向选择传播起点的问题形式化，例如在社交网络中选择初始采纳者。贪心选择需要反复估计增加一个节点所带来的传播收益，因此计算成本是该领域的重要问题。惰性评估、采样实现复用和基于采样的优化，从不同计算环节降低这一成本 \cite{ref7,ref8,ref2}。候选限制通过减少具有种子资格的节点来缩小搜索范围，其实际价值取决于节省计算的同时保留了多少传播收益。

当全候选参照本身也是从有限个随机传播世界中选出时，这种权衡便不易判断。观测到的差值来自两个计算所得的种子集合，其含义取决于两个集合各自如何得到。若将差值归因于错误的因素，就可能误判一个计算成本较低的候选池是否保留了参照的效用。''',
52:r'''\paragraph{目标函数、采样与计算效率。}Kempe 等证明了独立级联模型下期望传播量的单调性和次模性，为贪心近似提供依据 \cite{ref1}。CELF 利用次模性避免不必要的边际收益重复评估 \cite{ref7}。StaticGreedy 在整个选择过程中复用固定的采样实现，保持一致的采样覆盖目标 \cite{ref8}。IMM 则给出具有近似保证的采样式求解器 \cite{ref2}。这些方法处理指定目标下的优化计算困难，说明需要谨慎对待采样目标，但并未直接给出某个截断排名排除节点后所造成的效用后果。本文固定模拟器与贪心规则，改变候选资格、参照预算或排名容差。''',
54:r'''\paragraph{影响力估计与种子选择策略。}Rui 等利用多层邻域信息估计影响力 \cite{ref12}，Fan 等采用离散哈里斯鹰优化进行种子选择 \cite{ref13}。Ko 等的 MONSTOR+ 预测未见图上的传播量 \cite{ref19}。这些研究提供了不同的影响力估计或种子集合搜索方式，其算法目标与仅将固定排名作为种子资格过滤器进行评价不同。在后一种设置中，贪心选择仍在完整传播图上评估传播，候选覆盖率也成为比较的一部分。因此，本文区分排名在定义候选池中的作用，以及模拟器在评估所选种子中的作用。''',
56:r'''\paragraph{评价设置与仍需回答的问题。}Li 等综述了影响力最大化方法 \cite{ref9}，Arora 等在基准研究中比较了这些方法的质量与计算成本 \cite{ref16}。Yanchenko 等综述了时间网络上的问题形式 \cite{ref11}；Aral 和 Dhillon 研究了实证影响力模型 \cite{ref15}。这些研究方向共同表明，算法比较需要放在相应传播模型、网络表示和评价设置中理解。本文在观测拓扑上模拟传播，考察该计算设置内部的敏感性，并不估计现实中实际发生的社会影响。''',
58:r'''本文考察的问题是：对候选限制的判断如何依赖两个数值计算环节，即采样全候选参照与决定候选资格的排名。仅在一组预算与容差下进行比较，无法判断改变其中任一环节后，结论是否仍然成立。本文通过配对预算与精度控制考察这种依赖，并在独立世界上评估种子差异。这将质量与成本评价延伸到比较结果本身的稳定性。在线补充材料 1 将这一问题与所引研究明确提出的目标对照，不把未报告某项检查推断为所有实现都没有执行该检查。''',
60:r'''\section{研究方法}
本研究采用基于传播模拟的配对评价设计。在共享条件下比较全候选与候选受限的贪心选择，再独立评估得到的种子集合。设计将参照预算和排名精度敏感性，与候选覆盖、传播对照及计算成本分别考察。第~\ref{sec:experimental-setup} 节给出网络、条件矩阵与执行设置。''',
93:r'''\section{实验设置}\label{sec:experimental-setup}''',
178:r'''在 wiki-Vote 上，默认 PageRank 前 20 个节点的平均入度为 249.75、出度为 56.2；按度排名的前 20 个节点平均入度为 70.3、出度为 489.25。在任一 $W=1280$ 路径上，PageRank-4k 候选池都不包含五个全候选参照种子中的任何一个，而其 5\% 候选池仅包含一个。在线补充材料 1 给出了种子层面的图示和完整覆盖率比较。''',
197:r'''ca-GrQc 的结果改变了对表面预算效应的解释。在默认 PageRank 容差下，增加参照预算会使受限方法相对参照的平均表现由增益转为损失。收紧容差替换了两个候选节点，使这一模式消失，但增加 $W$ 仍会改变种子集合。因此，默认设置下的反转不能作为独立于排名精度的预算效应证据。候选池截断使数值排名差异影响种子候选资格。$10^{-12}$ 与 $10^{-14}$ 下的候选池一致性，检验了已测试容差下的成员稳定性，但并未证明排名精确。CollegeMsg 和 wiki-Vote 的损失仍然存在，说明这一解释不能涵盖所有 PageRank 表现不利的比较。

StaticGreedy 已将采样实现的复用作为保持有限目标一致性的核心做法 \cite{ref8}。本文的固定边对照遵循相同的覆盖原则，而主要采用的按步索引耦合可能产生非单调的有限目标。这一区别来自采样构造，并不与 Kempe 等关于期望传播量的结果矛盾 \cite{ref1}。本文进一步识别的问题发生在选择之前：数值容差可能改变进入截断候选池的节点。共享世界控制了不同候选集合之间的比较，但不能消除对候选池构建方式的这种依赖。''',
200:r'''基准研究将影响力最大化的质量与计算成本一同考察 \cite{ref16}。本文的配对比较进一步区分了保持参照种子与保持独立评估效用。不同的选择轨迹可能得到相同的最终集合，在共享模拟世界下产生相同的评估向量。集合不同时，配对评估测量效用差的符号、大小与条件不确定性。外部 ca-GrQc 的平均变化 0.12720 个节点，与历史按步耦合的平均变化 0.01111 个节点，分别对应不同的预算变化区间；二者都没有定义具体应用中的等效界限。

这一区分影响如何理解所报告的时间节省。基于度的候选池结果给出了保持已测试参照时节省的计算量，而 PageRank 结果要求同时考虑对应的传播损失。候选比例、排名容差和参照预算规定质量比较，计时所包含的阶段规定成本比较。这些观察通过明确实测权衡补充求解效率研究，但没有提供与 CELF 或 IMM 的运行时间比较。''',
201:r'''
\subsection{网络方向与排名结果的迁移}
wiki-Vote 的观察与入向重要性和出向传播不匹配的解释一致。PageRank 候选池偏重入链较多的节点，而本文的传播沿出向边进行。实验没有反转传播方向，因此这一诊断不能单独确定因果机制。网络结构、候选覆盖率与传播设置仍然影响所观察到的损失。模拟目标与实证影响力模型之间的区别也需要考虑 \cite{ref15}。仅凭接触图上的一致性，不能确定某种排名在方向定义不同的网络上也会保留效用。增加 PageRank 覆盖率改善了实测比较，但没有消除 wiki-Vote 上的损失。
''',
202:r'''\subsection{适用范围、局限与后续检验}''',
208:r'''
\paragraph{后续检验。}这些限制对应两项有针对性的研究。外部网络上的容差与耦合联合对照，可检验精度敏感性的解释能否在固定边世界下保持。在其他设置不变时干预传播方向，有助于区分所提出的方向性解释与其他结构差异。将接触图敏感性结果推广之前，还需要在外部网络上考察更广的传播概率与期限设置。这些均是尚待检验的问题，不是当前数据已经支持的结果。
''',
210:r'''候选限制的质量需要结合采样参照与数值构建的候选池来解释。本文通过配对对照和独立评估，区分数值敏感性、种子一致性与效用保留。在 ca-GrQc 上，收紧 PageRank 容差使表面上由预算引起的质量反转消失，但与预算有关的种子变化仍然存在。在外部网络样本中，Degree-4k 以更低的实测选择成本保持了已测试的 $W=1280$ 参照轨迹，而 PageRank 结果依赖精度、覆盖率与网络背景。这些发现明确了实测质量与成本权衡的依据。其范围限于所研究的网络和设置；匹配有限参照不意味着期望传播量最优。精度与耦合的联合对照，以及传播方向干预，是在当前比较之外进一步检验这些解释的后续步骤。''',
}

def main():
    assert EN.keys()==ZH.keys()
    for d in ['manuscript','analysis','chinese']:
        shutil.copytree(B/d,R/d,dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.aux','*.log','*.out'))
    (R/'qa').mkdir(exist_ok=True);(R/'evidence').mkdir(exist_ok=True)
    for name in ['README.md','REPRODUCE.md','revision_report_zh.md','claim_evidence_matrix.md']:
        shutil.copy2(B/name,R/'evidence'/('prior_'+name))
    for name in ['summary_for_editor.txt','cover_letter_draft.txt','claim_evidence_matrix.md']:
        shutil.copy2(B/name,R/name)
    shutil.copy2(B/'qa/revision_checks.json',R/'evidence/prior_revision_checks.json')
    source=read(B/'manuscript/manuscript.tex').splitlines()
    prior=json.loads(read(B/'chinese/translation_map.json'))
    english=[];chinese=[];mapping={};current=1
    for i,line in enumerate(source,1):
        en=EN.get(i,line);zh=ZH.get(i,prior.get(str(i),{}).get('chinese',line))
        english.append(en);chinese.append(zh)
        if str(i) in prior or i in EN:
            mapping[str(i)]={'baseline_line':i,'english_output_line':current,'english':en,'chinese':zh}
        current+=en.count('\n')+1
    et='\n'.join(english)+'\n';zt='\n'.join(chinese)+'\n'
    (R/'manuscript/manuscript.tex').write_text(et,encoding='utf-8')
    zt=zt.replace('\\usepackage[T1]{fontenc}\n','').replace('\\usepackage[utf8]{inputenc}\n','').replace('\\usepackage{mathptmx}',r'\usepackage[UTF8,fontset=windows]{ctex}'+'\n'+r'\setmainfont{Times New Roman}')
    zt=zt.replace('\\journalname{Computing}','\\journalname{Computing（中文阅读译稿）}')
    zt=zt.replace('\\begin{document}',r'\begin{document}'+'\n'+r'\def\abstractname{摘要}\def\keywordname{\textbf{关键词}}\def\figurename{图}\def\tablename{表}\def\refname{参考文献}')
    (R/'chinese/manuscript/manuscript_zh.tex').write_text(zt,encoding='utf-8')
    (R/'chinese/translation_map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
    (R/'manuscript_changes.diff').write_text(''.join(difflib.unified_diff(read(B/'manuscript/manuscript.tex').splitlines(True),et.splitlines(True),fromfile=B.name,tofile=R.name)),encoding='utf-8')
    blocks=['# 本轮新增和调整段落中英对照','完整正文见中英文PDF。位置按上一版源码行号标识。']
    for n in EN:blocks.extend([f'## 基线行 {n}','### English',EN[n],'### 中文',ZH[n]])
    (R/'revised_passages_bilingual.md').write_text('\n\n'.join(blocks),encoding='utf-8')
    (R/'qa/baseline_hashes.json').write_text(json.dumps({str(p.relative_to(B)):sha(p) for p in (B/'manuscript').iterdir() if p.is_file() and p.suffix not in ['.log','.aux','.out']},indent=2),encoding='utf-8')
    print(json.dumps({'changed_blocks':len(EN),'new_experiments':False}))
if __name__=='__main__':main()
