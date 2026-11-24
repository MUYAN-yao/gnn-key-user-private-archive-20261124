# 查证记录

## 本地证据
- README：项目最初是基于传播概率及不确定性的种子用户集合选择；当前计算精度研究应以最新提交版本为准。
- `submission/computing-external-validation-20261015/review-v3-budget-precision/analysis/precision_budget/analysis-report.md`：三个网络、五条配对计算路径；W=80/320/1280；default/strict PageRank。
- PageRank 精度控制是事后分析，未添加独立网络或计算路径。不能把路径重复当成跨网络样本量。
- ca_grqc 的 pagerank_4k 下 default/strict 的损失不同；college_msg 相同；wiki_vote 的损失整体较高。不能用单一严格度单调解释所有收益结果。
- `related_work_evidence.md` 指出最新研究的对象是候选集合限制与有限世界参考选择，独立 10,000 世界评估，以及选择集合/顺序和效用的区别。
- 用户已明确关心两类计算精度，而不是用户重要性预测准确率。

## 初步文献定位（尚未完成全文核查）
- Cranmer et al., NeurIPS 2020, Discovering Symbolic Models from Deep Learning with Inductive Biases：GNN 后接符号回归的先例，研究物理系统，不能直接作为社交排名规律的证据。
- Märtens, Kuipers & Van Mieghem, Symbolic Regression on Network Properties, EvoStar 2017：对网络性质做符号回归，不能宣称社交网络+SR本身是空白。

## 拟议研究逻辑
- PageRank：连续分数误差相对于候选截断间隔决定集合稳定性；单独记录求解器残差，勿把 tol 当实际误差或浮点位数。
- Monte Carlo：成对边际收益差相对于其标准误决定可辨识性；共同随机世界意味着要使用成对差方差。
- 研究输出可以是可解释的风险/预算关系式，但现有三个网络不足以声称普适规律。

## 已核查原始来源
- NetworkX 官方 PageRank 文档：https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html 。明确停止条件依赖 `len(G)*tol`；不能将 tol 直接当作每个节点分数误差。冻结源 `snapshot/engine.py:197` 使用默认 nx.pagerank。
- Cranmer et al. 官方 NeurIPS 摘要：https://papers.neurips.cc/paper_files/paper/2020/hash/c9f2f917078bd2db12f23c3b413d9cba-Abstract.html 。支持 GNN+SR 的可行方法先例；不支持社交网络精度规律的现成结论。
- Märtens et al. 作者托管全文：https://www.nas.ewi.tudelft.nl/people/Piet/papers/Evostar2017_Symbolic_Regression.pdf 。以图谱特征预测直径、等周数，有训练图族/特征选择和泛化实验；不直接研究本项目两类计算误差。
- 搜索定位到 Gleich, PageRank Beyond the Web，残差的 1 范数除以 (1-alpha) 为解误差的保守上界；待核对作者原版。
- 搜索定位到 UAI 2021 Variance-Dependent Best Arm Identification：样本复杂度已有方差/差距依赖理论。即使 SR 找到类似结构，也不能当成全新发现。

## 本地进一步核查
- 最新中文正文：ca-GrQc 默认 PageRank-4k 相对同预算全候选参照的逐路径相对增量传播差异均值从 +5.61% 变为 -5.07%；严格精度控制下该符号反转消失。20 个候选中替换两个。
- 最新正文另有四张小规模接触图的单独补充对照；不可简单写成整个项目只有三张图。主要精度控制仍是三个外部网络。
- 选定 CSV 字段时曾用错 intersection/jaccard/changed 名称，返回 null；不使用这些 null 作结果，改核对实际字段再读。

## 完成核查与结论
- Gleich 作者全文已打开，明确给出 residual/(1-alpha) 的全局 1 范数误差界。
- Wills & Ipsen (2009) 作者托管搜索摘要已核对排序判据研究范围；全文打开超时，只按摘要/摘录范围使用。
- UAI 2021 Variance-Dependent Best Arm Identification 原始全文已打开；方差/差距依赖是已有理论。
- CSV 真实字段为 default_vs_strict_overlap、default_vs_strict_jaccard、strict_vs_tighter_same_pool、strict_added_ids、strict_removed_ids；已改用实际字段，不采用先前误选字段产生的 null。
- 已写 `docs/research/symbolic-ranking-20261031/research-question-card.md`：将 SR 定位为解释条件性敏感性和指导成本/效用决策的待验证工具；保留理论基线、独立网络验证、适应性/同分及后见特征风险。

## 研究价值追问
- 定向检索补查 UAI 2025 Chen/Xing/Crawford, Adaptive Threshold Sampling for Pure Exploration in Submodular Bandits；官方摘要明确包含 IM 应用和高效噪声查询/近似保证。仅“自适应模拟预算”已有直接相关工作。
- 价值定位：从算法参数敏感性，推进到跨网络的计算误差—选择变化—效用变化解释与预测。能否形成独立论文尚待完整新颖性检索和先导结果。
- PageRank 作者 PDF 再次打开超时；2026 SymRanker 出版商页面打开 403，均不据此声称完成全文核查，后者不作为核心论据。
