# 研究问题卡：社交网络计算精度与选择效用的符号规律

日期：2026-10-31。
状态：研究方向讨论与探索性设计，尚未运行符号回归或新增实验。

## Question

在给定传播模型、候选规则和种子数的条件下，能否用少量可解释变量，得到跨网络可检验的简洁公式，预测 PageRank 候选截断敏感性、Monte Carlo 贪心选择敏感性，以及由此产生的独立传播收益变化？进一步，该公式能否帮助确定足够的求解精度和选择预算？

## Type

exploratory；取得新数据并冻结验证协议后，才能进入 confirmatory。

## Hypothesis

两类敏感性都与“误差或噪声相对于决策分数差距”有关，但误差来源和目标不同。网络结构与候选边界拥挤程度、候选传播重叠会调节身份变化对应的效用变化。存在低复杂度的经验关系可以在未参与公式选择的网络上优于预先声明的简单基线；这一点目前尚无实验支持。

## Why it matters

把“调整精度后结果改变”的事后现象，推进为可验证的预测及预算决策：什么时候需要更严格的 PageRank 收敛、什么时候增加模拟预算有实际收益。

## Current evidence

1. 最新本地中文正文记录：ca-GrQc 的默认 PageRank-4k 在 W=80/320/1280 扫描中出现相对全候选参照的平均传播差异符号反转；严格 PageRank 控制中该反转消失。20 个候选中替换两个。不能据此推出跨网络定律。
2. 原精度分析是三个主要外部网络、五条配对路径的事后控制。路径不是独立网络。项目另有四张小规模接触图补充证据，其作用需依其原协议单独判定。
3. GNN+符号回归有方法先例：Cranmer et al. 的 NeurIPS 2020 工作在物理系统中从 GNN 提取公式。仅核查官方摘要，本卡不扩展其社交网络适用性。
4. Märtens et al. 的作者全文以符号回归近似网络直径、等周数，支持复杂网络+SR的可行性，不支持本问题已解决或尚无人研究的断言。
5. Wills & Ipsen, Ordinal Ranking for Google's PageRank (2009) 的作者托管搜索摘录明确涉及排序正确性和 top-k 判据；全文抓取超时，本卡只使用该范围。
6. Gleich, PageRank Beyond the Web (2015) 作者全文给出残差对应的 1 范数误差界。
7. Lu, Tao & Zhang, Variance-Dependent Best Arm Identification (UAI 2021) 原始论文显示方差与收益差距已有采样复杂度理论；不能将类似关系当成 SR 首次发现。

本地证据入口：
- `submission/computing-external-validation-20261015/concise-prose-revision-20261031/chinese/manuscript/manuscript_zh.tex`
- `submission/computing-external-validation-20261015/review-v3-budget-precision/analysis/precision_budget/analysis-report.md`
- 同目录 `candidate_pool_precision_diagnostics.csv`、`budget_transitions_summary.csv`。

## Mechanistic starting points

### PageRank 候选集合

对当前近似分数排序，令 Delta_cut = s_hat_(m) - s_hat_(m+1)，epsilon 为各节点分数绝对误差的共同有效上界。如果 Delta_cut > 2 epsilon，则前 m 个候选的成员资格得到一个保守充分保证；否则该判据不确定，不能断言一定发生替换。它不保证池内所有节点的先后次序。若边界存在精确同分，需要明确定义同分规则。

标准 PageRank 在固定列随机转移矩阵 P、固定个性化向量 v、0<alpha<1 下，r = alpha P s_hat + (1-alpha)v - s_hat 给出 ||s_hat-s_star||_1 <= ||r||_1/(1-alpha)。该值也可作为较保守的逐节点误差上界；严谨有限精度证书还需计入残差计算的舍入误差。

epsilon 不等于求解器参数 tol。NetworkX 官方文档的幂迭代停止条件依赖 len(G)*tol；跨网络比较需记录实际残差和迭代次数。

### Monte Carlo 贪心选择

先固定某一贪心阶段的已选集合和待比较候选对。令 D_w 为同一个随机世界中两候选的边际传播收益之差，Delta_gain = E[D_w]，sigma_D 为 D_w 的标准差。在独立世界间抽样的条件下，样本均值差的标准误为 sigma_D/sqrt(W)。共同随机世界意味着必须使用成对差方差，不能默认两候选独立。

可先检查无量纲量 R_MC = sigma_D/(sqrt(W)*|Delta_gain|)。Delta_gain 未知，需要独立先导样本及不确定性估计；从同一批世界选出胜者再估其差距会产生选择偏差。最终算法比较涉及多候选、多轮、适应性及同分，不能仅凭一对候选的正态近似给出全流程保证。最高预算输出也不是数学真值。

## Missing evidence

- 分数、残差、边界邻域间隔、迭代次数及近同分候选数的系统记录。
- 固定阶段候选之间的逐世界成对边际差，及独立重复世界族。
- 网络结构和候选传播重叠的预先声明特征。
- 足够多的独立图及图族，覆盖不同规模、有向性、社区和度异质性。
- 公式在整张留出网络上的精度、概率校准（若输出概率）、结构稳定性及决策成本收益。

## What would support it

- 一个复杂度受限的公式在未参与搜索与调参的网络上，稳定改善预先定义的预测指标。
- 相比残差/差距判据、单变量模型及简单线性/逻辑回归，SR 带来可复现的增益。
- 公式指导的精度/预算决策满足预先设定的独立传播效用容忍度，并减少实测总成本；特征提取和先导采样成本纳入统计。
- 在独立随机重复和网络扰动下保留主要结构，而不是每次得到完全不同的公式。

## What would falsify it

- 新网络上的预测显著失效，或只能记忆网络身份/规模。
- 公式主要依赖只在高精度参考运行后才能取得的特征，无法支持廉价的事前决策。
- 简单已有判据同样有效，复杂 SR 没有稳定增益。这否定新增 SR 的必要性，不否定原有误差分析。
- 稳定性改善与传播效用改善没有可复现关联，或节省预算小于特征/校准成本。

## Minimal next action

先做独立于现有论文的 PageRank 边界诊断小实验：在明确的图集合中固定传播与贪心条件，预先列出求解容差和候选比例，记录实际残差、边界分数间隔、候选成员变化及独立评估效用变化。先检验“误差/间隔”基线是否解释现象，再决定是否投入 SR。随后固定精确度稳定的候选池，单独研究 W 与成对选择波动，最后研究交互。

候选变化是固定图和固定求解条件下的确定性标签。若建模“变化概率”，必须明确随机性来自预设图总体/扰动分布，或独立模拟世界批次，不能把单次确定性翻转当作概率真值。

## Decision

explore。建议作为新的机制探索线，不把事后公式直接写为现有研究的确认性结论。本次不启动计算。

## Research value assessment — 2026-10-31

判断：有明确的问题价值，值得做有成败标准的小规模先导实验。现有证据尚不足以确认独立论文的新颖性或跨网络规律。

- 较弱贡献：再次发现默认收敛设置导致候选变化；用 SR 拟合已有误差/间隔或方差/差距关系。若现象可由简单停止条件完整处理，SR 可能没有必要。
- 较强研究问题：解释候选/种子身份变化为何在不同图和传播条件下对应不同的独立效用变化，并检验简洁模型是否能跨网络预测这种差异。
- 更进一步的应用价值：在预先定义的效用容忍度下，依据廉价先导特征选择精度和模拟预算；须计入特征提取、公式搜索/校准、先导采样及运行成本。
- 最新相关工作已直接研究带噪声次模优化的高效采样：Chen, Xing & Crawford (UAI 2025), Adaptive Threshold Sampling for Pure Exploration in Submodular Bandits，官方摘要指出其应用包括影响力最大化。因此“自适应增加采样”本身不能视为新颖性；若走预算方法线，应核对适用假设并与相关方法作有意义比较。
- 本研究首先解释给定传播模型中的计算决策，不直接识别真实社交传播因果规律。

继续投入的门槛：留出网络预测有效；相对简单已有基线有稳定增量；实测总成本/效用权衡改善。若只在原图中拟合好、所需特征必须事先运行高精度参考、或简单判据同样有效，应缩小为现有研究的诊断分析。

新增原始来源：[Chen et al., UAI 2025 官方摘要](https://proceedings.mlr.press/v286/chen25c.html)。该来源核查限于官方摘要，未据此声明其覆盖本项目的 PageRank 候选截断与效用联动问题。当前检索为定向初查，不构成完整的新颖性审查。

## Primary sources

- [NetworkX PageRank 官方文档](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html)
- [Cranmer et al., NeurIPS 2020 官方摘要](https://papers.neurips.cc/paper_files/paper/2020/hash/c9f2f917078bd2db12f23c3b413d9cba-Abstract.html)
- [Märtens et al., Symbolic Regression on Network Properties 作者全文](https://www.nas.ewi.tudelft.nl/people/Piet/papers/Evostar2017_Symbolic_Regression.pdf)
- [Wills & Ipsen, 2009，作者托管地址；全文抓取超时，仅搜索摘录范围](https://ipsen.math.ncsu.edu/ps/simax69812.pdf)
- [Gleich, 2015 作者全文](https://www.cs.purdue.edu/homes/dgleich/publications/Gleich%202015%20-%20prbeyond.pdf)
- [Lu, Tao & Zhang, UAI 2021 原始论文](https://www.auai.org/uai2021/pdf/uai2021.445.pdf)
