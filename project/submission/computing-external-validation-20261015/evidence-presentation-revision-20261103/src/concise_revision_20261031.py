from pathlib import Path
import shutil,json,re,hashlib,difflib
P=Path('submission/computing-external-validation-20261015')
B=P/'budget-interpretation-revision-20261031';R=P/'concise-prose-revision-20261031'
assert not R.exists()
R.mkdir();(R/'qa').mkdir();(R/'src').mkdir();(R/'evidence').mkdir()
for folder in ['manuscript','chinese/manuscript','analysis']:
    shutil.copytree(B/folder,R/folder)
for name in ['cover_letter_draft.txt','summary_for_editor.txt','claim_evidence_matrix.md','terminology_ledger.md','EXTERNAL_REPRODUCE_INHERITED.md','requirements.txt']:
    shutil.copy2(B/name,R/name)
for name in ['reproduce.py','integrate_historical.py']:
    shutil.copy2(B/'src'/name,R/'src'/name)
for name in ['README.md','REPRODUCE.md','revision_report_zh.md','consistency_check_zh.md']:
    shutil.copy2(B/name,R/'evidence'/('prior_'+name))
shutil.copy2(B/'evidence/HISTORICAL_REPRODUCE_INHERITED.md',R/'evidence/HISTORICAL_REPRODUCE_INHERITED.md')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(R/'qa/baseline_hashes.json').write_text(json.dumps({str(p.relative_to(B)):sha(p) for p in B.rglob('*') if p.is_file()},indent=2),encoding='utf-8')
en='manuscript/manuscript.tex';zh='chinese/manuscript/manuscript_zh.tex';changes=[]
def edit(rel,a,b):
    p=R/rel;t=p.read_text(encoding='utf-8');assert a in t,(rel,a)
    p.write_text(t.replace(a,b),encoding='utf-8')
    changes.append({'file':rel,'before':a,'after':b})
def pair(a,b,c,d):edit(en,a,b);edit(zh,c,d)
pair('OpenAI Codex assisted code, verification, analysis, figure generation and drafting. The authors reviewed the outputs and take responsibility for the manuscript.','OpenAI Codex assisted with basic code development and manuscript drafting.','OpenAI Codex 协助代码、核验、分析、图形生成与文稿起草。作者审核了输出，并对稿件承担责任。','OpenAI Codex 协助完成了基础代码与文稿起草。')
pair('The archived audits reconstruct argmax and tie decisions, replay external full-reference scores and evaluations, and compare predetermined worlds with a separate scalar oracle. Identical seed sets must yield identical evaluation vectors. Online Resource 1 details the audit coverage, the retrospective correction to raw-file hash enforcement and the executable reproduction procedure.','Reproduction and verification procedures are provided in Online Resource 1.','归档审计重建最大值选择及同分决策，回放外部全候选参照的分数和评估，并在预先指定的世界上与独立的标量参考实现比较。相同种子集合必须产生相同的评估向量。在线补充材料 1 详细说明审计覆盖范围、对原始文件哈希强制校验缺口的回溯修正，以及可执行的复现流程。','复现与核验流程见在线补充材料 1。')
pair('; later events are not used for candidate construction or treated as observed influence outcomes.','.','；后续事件既不用于构建候选池，也不作为观测到的影响力传播结果。','。')
pair('The two static datasets supply neither event counts nor observed cascades and receive no historical-weighted ranking.','The two static datasets provide topology-only inputs; historical-weighted ranking requires event counts.','两个静态数据集既不提供事件次数，也不提供观测级联，因此不采用历史加权排名。','两个静态数据集提供拓扑信息；历史加权排名仅用于具有事件计数的数据集。')
pair(' No largest-component extraction or node subsampling is applied.','','不提取最大连通分量，也不对子节点集采样。','')
pair('The parameter controls reuse the default budget-scan conditions rather than counting them again.','The parameter controls reuse the default budget-scan conditions.','参数对照复用预算扫描中的默认条件，不重复计数。','参数对照复用预算扫描中的默认条件。')
pair('; these small-graph controls do not enlarge the external network sample.','.','；这些小图对照不会增加外部网络样本量。','。')
pair('Paths identify computational repetitions, not additional networks.','Paths identify computational repetitions on each graph.','路径标识计算重复，不代表新增网络。','路径标识各图上的计算重复。')
pair('This checks candidate membership stability at the tested tolerances, not exact convergence of the PageRank vector. The paired sensitivity analysis adds no independent paths and leaves the primary test family unchanged.','This comparison assesses candidate membership stability at the tested tolerances.','这检验的是所测容差下的候选成员稳定性，而不是 PageRank 向量的精确收敛。该配对敏感性分析不增加独立路径，也不改变主要检验族。','这一比较检验所测容差下的候选成员稳定性。')
pair('The archived reproduction record covers stored-result audits, analysis regeneration and representative external-condition reruns; it does not document a complete rerun of all historical and external conditions. Online Resource 1 and \\texttt{REPRODUCE.md} specify the input checks, replay modes, output isolation and acceptance criteria. Historical summaries are recomputed from their separate saved outputs.','', '归档复现记录覆盖保存结果审计、分析再生成，以及代表性外部条件重跑；它不代表对全部历史和外部条件的完整重跑。在线补充材料 1 和 \\texttt{REPRODUCE.md} 说明输入检查、回放模式、输出隔离及验收标准。历史汇总从各自单独保存的输出重新计算。','')
pair('Five paths limit the minimum two-sided sign-test value to .0625; these results establish neither statistical equivalence nor absence of loss.','Five paths limit the minimum two-sided sign-test value to .0625.','五条路径使双侧符号检验可达到的最小值限制在 .0625；这些结果既不确立统计等效，也不证明没有损失。','五条路径使双侧符号检验可达到的最小值限制在 .0625。')
pair(' These are descriptive counts of repeated computations, not independent success trials.','','这些是对重复计算的描述性计数，不是独立成功试验。','')
pair('Online Resource 1 relates this question to the cited studies\' stated objectives; it does not infer that an unreported check was absent from every implementation.','Online Resource 1 compares this question with the cited studies\' stated objectives.','在线补充材料 1 将这一问题与所引研究明确提出的目标对照，不把未报告某项检查推断为所有实现都没有执行该检查。','在线补充材料 1 将这一问题与所引研究明确提出的目标对照。')
pair('Paths repeat computations on a fixed graph, and the networks are not a probability sample of social systems. Each synthetic control uses one fixed graph, so repeated paths do not add graph instances. Conditional Monte Carlo uncertainty concerns fixed selected sets; path variation concerns the computational repetitions, not cross-network generalization. Observed relations provide topology, not calibrated causal diffusion.','Paths repeat computations on a fixed graph, and each synthetic control uses one graph instance. Conditional Monte Carlo uncertainty concerns fixed selected sets, while path variation describes computational repetitions. The selected networks provide observed topologies for the specified diffusion model.','路径是在固定图上重复计算，所用网络也不是社会系统的概率样本。每个合成对照只使用一个固定图，因此，重复路径不会增加图实例数。条件蒙特卡洛不确定性针对固定已选集合；路径变异针对计算重复，而非跨网络泛化。观测关系提供拓扑，并不等于经过校准的因果传播。','路径是在固定图上的计算重复，每个合成对照使用一个图实例。条件蒙特卡洛不确定性针对固定已选集合，路径变异描述计算重复之间的变化。所选网络为指定传播模型提供观测拓扑。')
pair('Reference agreement establishes neither optimality with respect to expected spread nor convergence as the world budget increases. A positive mean difference with mixed path signs is not sufficient evidence of superiority, and nonsignificance is not equivalence. The cost comparison uses this implementation\'s exhaustive full-candidate reference, not CELF or IMM. Measured selection costs and assembled costs including independent evaluation answer different deployment questions. The latter exclude cold-start overhead and are not direct end-to-end timings; tighter-tolerance PageRank is assessed for quality only.','Reference agreement measures fidelity to the sampled greedy solution. The cost comparison uses this implementation\'s exhaustive full-candidate reference. Measured selection timings and assembled warm-process costs describe distinct usage scenarios; their components are specified in Methods.','参照一致性既不证明相对于期望传播量的最优性，也不证明随世界预算增加而收敛。路径差值正负并存时，正均值不足以确立优势；未显著也不等于等效。成本比较采用本实现逐轮完整枚举的全候选参照，而非 CELF 或 IMM。实测选择成本和包含独立评估的拼接成本回答不同的部署问题。后者排除冷启动开销，并非直接端到端计时；较紧容差的 PageRank 仅用于质量评价。','参照一致性衡量对采样贪心解的复现程度。成本比较采用本实现逐轮完整枚举的全候选参照。实测选择时间与暖进程拼接成本对应不同使用场景，具体组成见研究方法。')
for rel in [en,zh]:
    p=R/rel;t=p.read_text(encoding='utf-8');p.write_text(re.sub(r'\n{3,}','\n\n',t),encoding='utf-8')
    old=(B/rel).read_text(encoding='utf-8')
    (R/'qa'/(p.stem+'.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True),p.read_text(encoding='utf-8').splitlines(True),fromfile=str(B/rel),tofile=str(p))),encoding='utf-8')
(R/'qa/change_log.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'README.md').write_text('''# 正文精简修订 · 2026-10-31

基于相邻 budget-interpretation-revision-20261031，按作者逐句批注修订英中正文。原版保留。

- 英文：manuscript/manuscript.pdf 及同名 .tex。
- 中文：chinese/manuscript/manuscript_zh.pdf 及同名 .tex。
- 修改说明：revision_report_zh.md；逐处原文/新文：qa/change_log.json。
- 核验：qa/final_checks.json、qa/render_checks.json。
- 英文补充材料、数据表、图像、作者署名和投稿信沿用前版；本轮未改补充材料，未重编其PDF。

AI脚注按作者指定改为“OpenAI Codex 协助完成了基础代码与文稿起草。”英文同步。正文删除重复防御句，将审计回放及哈希修正细节替换为补充材料指引。预算作用对象、比较方向、事后精度身份、路径数和科学数据保留。

本轮没有新实验、数据分析或统计检验。前版检查记录属于前版；本轮核验只覆盖文本改动、资源保留与编译排版。完整复现说明仍见继承文件。
''',encoding='utf-8')
(R/'revision_report_zh.md').write_text('''# 修改说明

1. 中英文AI脚注改为作者指定的基础代码与文稿起草表述。
2. 删除正文关于后续事件、小图不增加外部样本、事后分析不新增路径/检验族、计数不是独立成功试验的重复否定句。数据时间截断、每图路径数、事后分析属性和统计设计仍在原有方法中。
3. 方法中的回放、标量核验、哈希保护修正过程缩为“复现与核验流程见在线补充材料1”；删除实验设置末尾的归档复现汇报段。
4. 数据类型、表注和讨论改为直接说明拓扑输入、计算重复、参照含义与计时对象，去掉“既不……也不……”及同类重复表达。
5. 图、表、原始数据、统计结果、公式、引用与机制图不变。补充材料保留详细设计和复现边界，未经改写。

原版本：../budget-interpretation-revision-20261031。全部逐句差异见qa/change_log.json和两个.diff文件。本轮没有新增实验。
''',encoding='utf-8')
(R/'REPRODUCE.md').write_text('''# 文稿编译与检查

在manuscript目录用pdflatex编译manuscript.tex两次；在chinese/manuscript目录用xelatex编译manuscript_zh.tex两次。
本机TeX目录为C:/texlive/2026/bin/windows。

运行src/verify_concise.py进行文件保留、数字、引用、编译日志与PDF渲染检查。该脚本不执行实验。

前版完整说明保存在evidence/prior_REPRODUCE.md；外部复现说明见EXTERNAL_REPRODUCE_INHERITED.md；历史汇总说明见evidence/HISTORICAL_REPRODUCE_INHERITED.md。本轮未执行这些复现实验入口。
''',encoding='utf-8')
shutil.copy2(__file__,R/'src'/Path(__file__).name)
print(R.resolve())
