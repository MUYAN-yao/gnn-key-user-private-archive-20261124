# v7 最近方法差异审查：未关闭的贡献门槛

日期：2026-09-19；范围：本轮开发前的定向原文核对，不是穷尽性文献综述，
也不构成新颖性或录用保证。

## 审查对象与拟议狭义命题

拟议方法不再声称“自适应候选池”或“GNN 候选筛选”本身新颖。待判断的狭义
命题是：对一个**固定、有限、共同的模拟世界集合**，在
`mean - lambda * population_SD + eta * community_coverage` 目标下，利用
有向 h 跳可达的总激活上界和已观测世界的 SSE 下界，对每一轮仍未完整模拟的
候选给出保守上界；只有严格落后于当前胜者的候选被停算。因此，完成时得到的
有序种子与同一 v7 full greedy 完全一致。

该命题不保证总体期望、全局最优、真实传播效应或与 v6 浮点评分逐字节一致。

## 原文比较

| 最近方法 | 已覆盖内容 | 与 v7 狭义机制的差异 | 结论 |
| --- | --- | --- | --- |
| GCOMB（[原文 PDF](https://akash-mittal.netlify.app/publication/gcomb/gcomb.pdf)） | GCN 学习节点质量并结合 Q-learning；昂贵计算集中在高潜力节点；输入包含预算。 | 它是学习型启发式/剪枝流水线，并不由当前固定世界上的候选完成上界来逐轮证明与 full greedy 同解。反过来，这也意味着 v7 不能把排序或预算相关筛选称为新贡献。 | 必须作为学习筛选强对照的来源；仅保留“验证层”才可能有区分。 |
| H-DeepPruner（[SoCS 原文](https://ojs.aaai.org/index.php/SOCS/article/download/35981/38136/40053)） | 两阶段 GNN 与 GNN 引导 MCTS 的自适应搜索空间缩减，覆盖 IM。 | 其适用目标是一般图组合优化的学习剪枝；没有看到它针对本研究的固定世界、风险 SD 目标给出候选完成证书。它使“分层/自适应剪枝”总体叙事不可用。 | 不可用学习剪枝作为论文主贡献。 |
| UBLF（[WWW 2014 原文](https://archives.iw3c2.org/www2014/proceedings/companion/p421.pdf)） | LT 模型下的传播上界，结合 CELF 减少 Monte-Carlo 估计；利用单调次模传播的跨轮边际上界。 | v7 不把先前轮的边际值用作界，也不要求单调/次模；其界是当前候选集合在有限世界上的结构总激活限制，加上已观测 SSE 对全体 SD 的下界。 | 这是最接近的非学习方法。必须在正文中明确两类界的假设与保证不同，且实验证明额外机制有收益。 |
| ExpGreedy/TOPX（[AAAI 原文](https://ojs.aaai.org/index.php/AAAI/article/download/10207/10066)） | 对噪声次模函数自适应重复查询，以 PAC 方式选择高质量候选集合。 | v7 的世界列表先固定，目标可非次模；不做置信区间式的近似 top-1 识别，而是在有限目标上将每一个候选完全计算或安全排除。 | 不能称“逐步采样”新颖；仅可主张不同的确定性完成证书，仍需更广泛检索验证。 |
| Sadeh et al.（[ITCS 摘要/论文页](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITCS.2020.29)） | 对 IC/LT 的影响力估计给出方差相关样本复杂度与数据自适应的较少模拟。 | 与 v7 同样涉及方差和减少模拟，但它处理期望影响力估计与次模贪心近似，不是本项目的样本 SD 风险惩罚和候选完成上界。 | 需要纳入后续完整 related work，避免将“利用方差减少模拟”表述为首次。 |
| Nannicini et al.（[IBM 论文页](https://research.ibm.com/publications/an-exact-algorithm-for-robust-influence-maximization)）与 Chen et al.（[presolving 论文页](https://optimization-online.org/wp-content/uploads/2021/01/8189-1.pdf)） | 前者对不确定阈值/边权的鲁棒 IM 使用 exact Branch-and-Cut；后者对 IM 的 exact Benders 分解使用预处理。 | 优化模型与不确定性定义不同，但它们表明 IM 中已有 exact/branch-and-bound/presolving 路线。v7 不能把“首次 exact BnB”或“首次候选安全排除”作为贡献。 | 扩大了最近方法面；需要将 v7 定位收窄为一种特定的有限世界、风险 SD 评分的计算规则。 |

## 当前判定

**G0 未关闭，不能启动 E2 的真实性能批次。** 已确认的差异是一个可检验的
技术定位，尚非确认的新颖贡献。原因有三点：

1. UBLF 已经显示“传播上界 + 贪心剪枝”是成熟路线；必须证明 SSE 风险界不是
   无实质作用的替换。
2. ExpGreedy/TOPX 和方差相关采样工作说明“逐步评估”与“方差信息”均有先例；
   新增的 exact Branch-and-Cut/Benders 结果也排除了“exact pruning”式叙事。
   仍需检索风险敏感、scenario/fixed-world与 non-submodular branch-and-bound 的
   精确交集，才能判断 SSE 规则是否具备足够的非显然性。
3. 即使理论差异成立，若 E2 仅显示普通结构上界解释全部加速，或总成本不低于
   full/generic bound，则不足以支撑方法论文。

## 允许的下一步

继续做两项低风险工作：

1. 把 SSE 项的严格增益设计成 `check_mean_bound` 对照，并补全与风险敏感、
   fixed-scenario 组合优化文献的定向检索；
2. 实现 E2 runner，但保持所有真实网络矩阵行为 `planned_not_run`，直到差异
   审查形成可辩护的贡献句和明确的停止规则。

E1 的实现正确性见 `audits/v7_e1_micrograph_check_v0_1.json`；它不改变上述
新颖性判定。
