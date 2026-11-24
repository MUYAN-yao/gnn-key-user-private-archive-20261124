"""Evidence-preserving English revision and Chinese translation. No experiments."""
from pathlib import Path
import shutil, json, hashlib, difflib, importlib.util, re

R=Path(__file__).resolve().parents[1]
B=R.parent/'structural-language-revision-20261027'
T=R.parent/'chinese-translation-20261027'
def read(p): return p.read_text(encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
EN={
26:r'''Candidate restriction can reduce influence-maximization search costs, yet its apparent quality depends on a reference solution that is itself estimated. A measured gain or loss may reflect reference sampling, numerical changes in candidate eligibility, or both. We use paired selection and independent spread evaluation to distinguish these effects by varying reference budget and ranking precision separately. Evidence comes from a small, selected sample of real-world networks: three external topologies, with four small contact graphs providing separate controls. On ca-GrQc, increasing the reference budget changes mean incremental spread from a 5.61\% gain to a 5.07\% loss. This reversal disappears in a post-hoc control that tightens PageRank tolerance. Budget-dependent seed changes persist, and reference-set changes have different utility consequences. Across the external networks, degree-based pools reproduce all 15 highest-budget reference trajectories, whereas PageRank losses persist on the two directed networks. These findings identify how numerical choices can alter judgments of candidate restriction. Reporting candidate-pool stability and independently evaluated spread alongside reference agreement makes the basis of a measured quality--cost trade-off explicit.''',
31:r'''Candidate restriction offers a direct way to reduce the search cost of greedy influence maximization by excluding vertices from seed selection. Its practical value depends on the spread retained for the computation saved. Establishing that trade-off is difficult when the full-candidate reference is itself selected from finitely sampled diffusion worlds. The observed difference then compares two computed seed sets, and its interpretation depends on how both were obtained.''',
33:r'''Reference sampling and candidate ranking enter this comparison at different stages. Increasing the sampling budget can change the full-reference seeds and the measured gap to a restricted method. Ranking precision acts before greedy selection, where small score changes can exchange vertices at the candidate-pool boundary. A change in the apparent quality of a restricted method may therefore depend on either numerical choice. Seed disagreement alone cannot resolve this ambiguity because different sets can have similar independently evaluated spread.''',
35:r'''We address this evaluation problem by separating the construction of the reference, the construction of the candidate pool and the assessment of selected seeds. The analysis asks whether an apparent budget effect survives a ranking-precision control and how reference-set changes translate into spread differences. Full and restricted selection share the propagation graph, sampled-world prefix and tie rule (Fig.~\ref{fig:evaluation-mechanism}). Independent evaluation then measures their paired utility difference. This design makes each comparison explicit while keeping seed eligibility as the only difference between the two selection arms.''',
37:r'''The evidence is drawn from a small, selected sample of real-world networks. Three external communication, collaboration and voting topologies test the transfer of earlier findings from four small contact graphs. The contact-graph results provide separate budget, propagation-parameter and coupling controls. A post-hoc PageRank analysis tests whether the external budget comparison depends on solver tolerance.''',
39:r'''The main contributions are:''',
41:r'''\item[(1)] \textbf{An apparent budget reversal can depend on ranking precision.} On ca-GrQc, a tighter PageRank tolerance removes the mean gain-to-loss reversal across budgets while seed changes persist. The comparison identifies a numerical dependence that would be missed by interpreting the default budget scan alone.''',
42:r'''\item[(2)] \textbf{Reference-set changes need a separate utility assessment.} The external and historical budget comparisons produce set changes with differing spread consequences. Paired independent evaluation quantifies those differences and their conditional uncertainty, so seed disagreement is not used as a proxy for utility loss.''',
43:r'''\item[(3)] \textbf{Reference-preserving savings have a defined scope.} Degree-based pools reproduce all 15 highest-budget external trajectories at lower measured selection cost, whereas earlier PageRank agreement does not transfer uniformly. Coverage and direction diagnostics help interpret these differences; the savings apply to the tested exhaustive-selection implementation.''',
58:r'''The distinction from these studies concerns what an observed quality gap can establish. Solver research addresses the cost of seed selection under a specified objective; ranking research changes how influential vertices are identified. Benchmarking compares implemented methods under stated settings. Here, the reference and candidate pool are themselves numerical components of the comparison. A single budget--tolerance setting cannot reveal whether its quality judgment survives changes to those components. Paired budget and precision controls expose this dependence, while independent evaluation separates changes in selected seeds from changes in spread.''',
148:r'''\subsection{An apparent budget reversal depends on ranking precision}''',
159:r'''\subsection{Changing the reference set does not determine the spread change}''',
170:r'''\subsection{Ranking agreement depends on coverage and network context}''',
180:r'''\subsection{Reference-preserving savings under specified timing scopes}''',
186:r'''\subsection{Parameter and coupling controls delimit the findings}''',
196:r'''\subsection{What a budget comparison can establish}''',
197:r'''The ca-GrQc result changes the interpretation of an apparent budget effect. At default PageRank tolerance, increasing the reference budget changes the restricted method's mean comparison from a gain to a loss. Tightening tolerance exchanges two pool members and removes that pattern, although increasing $W$ still changes selected sets. Thus, the default reversal is not evidence for a budget effect that is independent of ranking precision. The candidate cutoff makes numerical ranking differences relevant to seed eligibility. Pool agreement at $10^{-12}$ and $10^{-14}$ checks membership stability at the tested tolerances, without certifying an exact ranking. Losses persist on CollegeMsg and wiki-Vote, so this explanation does not account for every unfavorable PageRank comparison.''',
199:r'''\subsection{From seed agreement to a quality--cost judgment}''',
200:r'''Reference agreement is useful for describing what candidate restriction preserves, but it does not replace spread evaluation. A changed trajectory may end at the same set, which gives the same evaluation vector under shared simulation worlds. When sets differ, paired evaluation measures the sign, magnitude and conditional uncertainty of their utility difference. The external ca-GrQc mean change of 0.12720 nodes and the historical step-coupled mean change of 0.01111 nodes illustrate distinct budget transitions. Neither value defines an application-specific equivalence margin. For cost comparisons, agreement and independent spread should therefore accompany candidate coverage, reference budget and ranking tolerance. The degree-pool results identify computation saved while preserving the tested reference; the PageRank results show why similar savings cannot be interpreted without the corresponding utility loss.''',
210:r'''Candidate-restriction quality must be interpreted relative to both a sampled reference and a numerically constructed candidate pool. The ca-GrQc control shows why these dependencies matter: tightening PageRank tolerance removes the apparent budget-induced quality reversal, but budget-dependent seed changes remain. Independent spread evaluation determines the utility consequences of those changes. Across the external sample, Degree-4k preserves the tested $W=1280$ trajectories at lower measured selection cost, while PageRank outcomes depend on precision, coverage and network context. The practical contribution is to make these dependencies testable within a paired comparison, so reference agreement and utility retention are not conflated. The conclusions concern the studied networks and settings; matching a finite reference does not establish expected-spread optimality.''',
}
ZH={
26:r'''候选限制能够降低影响力最大化的搜索成本，但其表现需要与一个本身由估计得到的参照解比较。观测到的增益或损失，可能来自参照采样、数值计算引起的候选资格变化，或二者共同作用。本文分别改变参照预算与排名精度，通过配对选择和独立传播评估辨别这些影响。研究基于规模有限、经选择的真实网络样本：三张外部网络用于主要比较，四张小规模接触图提供单独的补充对照。在 ca-GrQc 上，随参照预算增加，平均增量传播量从高于参照 5.61\% 转为低于参照 5.07\%。这一反转在收紧 PageRank 容差的事后控制中消失。与预算有关的种子变化仍然存在，而参照集合变化对应的效用变化并不相同。在外部网络上，基于度的候选池复现了最高测试预算下全部 15 条参照轨迹，两个有向网络上的 PageRank 传播损失则仍然存在。这些发现指出了数值选择如何改变对候选限制的质量判断。将候选池稳定性、独立评估的传播量与参照一致性一同报告，能够明确实测质量与成本权衡的依据。''',
31:r'''候选限制通过排除部分节点的种子资格，直接缩小影响力最大化中贪心搜索的范围。它的实际价值取决于节省计算的同时保留了多少传播收益。当全候选参照本身也是从有限个随机传播世界中选出时，这种权衡便不易判断。此时，观测到的差值来自两个计算所得的种子集合，其含义取决于两个集合各自如何得到。''',
33:r'''参照采样与候选排名在比较的不同阶段发挥作用。增加采样预算可能改变全候选参照的种子，进而改变受限方法相对参照的差值。排名精度则在贪心选择之前起作用：分数的小幅变化可能使候选池边界处的节点发生替换。因此，受限方法表现的变化可能依赖这两项数值选择中的任意一项。仅凭种子不一致无法辨别这些影响，因为不同集合的独立评估传播量可能相近。''',
35:r'''针对这一评价问题，本文将参照构建、候选池构建与种子效用评估分开考察。分析关注两个问题：表面上的预算效应能否在排名精度控制后保持，以及参照集合变化对应多大的传播差异。全候选选择与受限选择共享传播图、采样世界前缀和同分规则（图~\ref{fig:evaluation-mechanism}），再通过独立评估测量二者的配对效用差。这一设计明确了每项比较的依据，并使种子候选资格成为两个选择实验臂之间唯一的差别。''',
37:r'''研究证据来自数量有限、经选择的真实网络样本。三张通信、合作和投票外部网络用于检验此前在四张小规模接触图上观察到的结果能否迁移。接触图结果单独提供预算、传播参数与耦合方式的对照。事后 PageRank 分析进一步检验外部网络的预算比较是否依赖求解容差。''',
39:r'''本文的主要贡献如下：''',
41:r'''\item[(1)] \textbf{表面上的预算反转可能依赖排名精度。}在 ca-GrQc 上，收紧 PageRank 容差使跨预算的平均增益转损失现象消失，但种子变化仍然存在。这项比较识别出仅解释默认设置下的预算扫描时会遗漏的数值依赖。''',
42:r'''\item[(2)] \textbf{参照集合变化需要单独评估其效用。}外部网络与历史预算比较中，集合变化对应的传播差异并不相同。配对独立评估量化这些差异及其条件不确定性，避免用种子不一致代替传播损失的测量。''',
43:r'''\item[(3)] \textbf{保持参照结果的计算节省具有明确范围。}基于度的候选池以更低的实测选择成本复现了最高外部预算下全部 15 条轨迹，而此前的 PageRank 一致性未在所有外部网络上保持。覆盖率与方向诊断帮助解释这些差异；计算节省仅对应所测试的逐轮全枚举选择实现。''',
58:r'''本文与上述研究的区别，在于考察观测到的质量差值能够支持什么判断。求解器研究关注给定目标下的种子选择成本，排名研究改变识别高影响力节点的方式，基准研究则比较指定设置下的方法实现。本文将参照和候选池本身视为比较中的数值计算环节。仅使用一组预算与容差，无法知道改变这些环节后质量判断是否仍然成立。配对预算与精度控制揭示这种依赖，独立评估则区分种子变化与传播量变化。''',
148:r'''\subsection{表面上的预算反转依赖排名精度}''',
159:r'''\subsection{参照集合变化不能决定传播量变化}''',
170:r'''\subsection{排名一致性受覆盖率与网络背景限定}''',
180:r'''\subsection{指定计时范围下保持参照结果的计算节省}''',
186:r'''\subsection{参数与耦合对照限定结论范围}''',
196:r'''\subsection{预算比较能够支持什么判断}''',
197:r'''ca-GrQc 的结果改变了对表面预算效应的解释。在默认 PageRank 容差下，增加参照预算会使受限方法相对参照的平均表现由增益转为损失。收紧容差替换了两个候选节点，使这一模式消失，但增加 $W$ 仍会改变种子集合。因此，默认设置下的反转不能作为独立于排名精度的预算效应证据。候选池截断使数值排名差异影响种子候选资格。$10^{-12}$ 与 $10^{-14}$ 下的候选池一致性，检验了已测试容差下的成员稳定性，但并未证明排名精确。CollegeMsg 和 wiki-Vote 的损失仍然存在，说明这一解释不能涵盖所有 PageRank 表现不利的比较。''',
199:r'''\subsection{从种子一致性到质量与成本判断}''',
200:r'''参照一致性能够描述候选限制保留了什么，但不能替代传播量评估。不同的选择轨迹可能得到相同的最终集合，在共享模拟世界下产生相同的评估向量。集合不同时，配对评估测量效用差的符号、大小与条件不确定性。外部 ca-GrQc 的平均变化 0.12720 个节点，与历史按步耦合的平均变化 0.01111 个节点，分别对应不同的预算变化区间；二者都没有定义具体应用中的等效界限。因此，比较成本时，应将一致性与独立传播量同候选覆盖率、参照预算和排名容差一同报告。基于度的候选池结果给出了保持已测试参照时节省的计算量；PageRank 结果则表明，解释相似的计算节省时，必须同时考虑对应的传播损失。''',
210:r'''候选限制的质量需要结合采样参照与数值构建的候选池来解释。ca-GrQc 对照说明了这些依赖为何重要：收紧 PageRank 容差使表面上由预算引起的质量反转消失，但与预算有关的种子变化仍然存在。独立传播评估用于确定这些变化对应的效用差异。在外部网络样本中，Degree-4k 以更低的实测选择成本保持了已测试的 $W=1280$ 参照轨迹，而 PageRank 结果依赖精度、覆盖率与网络背景。本文的实际贡献，是使这些依赖能够在配对比较中接受检验，避免混淆参照一致性与效用保留。结论限于所研究的网络和设置；匹配有限参照不意味着期望传播量最优。''',
}
assert EN.keys()==ZH.keys()

def main():
    # New version only. All previous manuscripts and frozen outputs remain untouched.
    for directory in ['manuscript','analysis','evidence']:
        shutil.copytree(B/directory,R/directory,dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.aux','*.log','*.out'))
    for name in ['REPRODUCE.md','EXTERNAL_REPRODUCE_INHERITED.md']:
        if (B/name).exists(): shutil.copy2(B/name,R/'evidence'/('prior_'+name))
    (R/'qa').mkdir(exist_ok=True)
    shutil.copytree(B/'qa',R/'evidence/prior-structural-qa',dirs_exist_ok=True)
    src=read(B/'manuscript/manuscript.tex').splitlines()
    out=src.copy()
    for n,value in EN.items():
        assert n in [26,31,33,35,37,39,41,42,43,58,148,159,170,180,186,196,197,199,200,210]
        out[n-1]=value
    (R/'manuscript/manuscript.tex').write_text('\n'.join(out)+'\n',encoding='utf-8')
    (R/'manuscript_changes.diff').write_text(''.join(difflib.unified_diff(read(B/'manuscript/manuscript.tex').splitlines(True),read(R/'manuscript/manuscript.tex').splitlines(True),fromfile='structural-language-revision-20261027',tofile='problem-led-revision-20261028')),encoding='utf-8')
    spec=importlib.util.spec_from_file_location('prior_translation',T/'src/translation_text.py')
    tr=importlib.util.module_from_spec(spec);spec.loader.exec_module(tr)
    translations=tr.MAIN.copy();translations.update(ZH)
    cm=R/'chinese/manuscript';cm.mkdir(parents=True,exist_ok=True)
    for name in ['svjour3.cls','svglov3.clo','numbers.tex','references.tex','FigEvaluationMechanism.pdf','Fig4.pdf','Fig2.pdf']:
        shutil.copy2(R/'manuscript'/name,cm/name)
    for name,mapping,filename in [('manuscript.tex',translations,'manuscript_zh.tex'),('primary_table.tex',tr.PRIMARY,'primary_table.tex'),('cost_table.tex',tr.COST,'cost_table.tex')]:
        ls=read(R/'manuscript'/name).splitlines()
        for n,value in mapping.items(): ls[n-1]=value
        content='\n'.join(ls)+'\n'
        if name=='manuscript.tex':
            content=content.replace('\\usepackage[T1]{fontenc}\n','').replace('\\usepackage[utf8]{inputenc}\n','').replace('\\usepackage{mathptmx}',r'\usepackage[UTF8,fontset=windows]{ctex}'+'\n'+r'\setmainfont{Times New Roman}')
            content=content.replace('\\journalname{Computing}','\\journalname{Computing（中文阅读译稿）}')
            content=content.replace('\\begin{document}',r'\begin{document}'+'\n'+r'\def\abstractname{摘要}\def\keywordname{\textbf{关键词}}\def\figurename{图}\def\tablename{表}\def\refname{参考文献}')
        (cm/filename).write_text(content,encoding='utf-8')
    # Keep the bilingual mapping self-contained for review and later checks.
    (R/'chinese/translation_map.json').write_text(json.dumps({str(n):{'english':out[n-1],'chinese':value} for n,value in translations.items()},ensure_ascii=False,indent=2),encoding='utf-8')
    (R/'src/translation_tables.json').write_text(json.dumps({'primary_table.tex':tr.PRIMARY,'cost_table.tex':tr.COST},ensure_ascii=False,indent=2),encoding='utf-8')
    blocks=['# 本轮修改段落中英对照','本文件列出本轮重写的段落。正文全文见英文及中文 PDF。']
    for n in EN:
        blocks.extend([f'## 正文源码第 {n} 行','### English',EN[n],'### 中文',ZH[n]])
    (R/'revised_passages_bilingual.md').write_text('\n\n'.join(blocks),encoding='utf-8')
    (R/'qa/source_baseline_hashes.json').write_text(json.dumps({str(p.relative_to(B)):sha(p) for p in (B/'manuscript').iterdir() if p.is_file() and p.suffix not in ['.log','.aux','.out']},indent=2),encoding='utf-8')
    print(json.dumps({'new_version':str(R),'changed_main_lines':list(EN),'new_experiments':False},ensure_ascii=False))

if __name__=='__main__': main()


