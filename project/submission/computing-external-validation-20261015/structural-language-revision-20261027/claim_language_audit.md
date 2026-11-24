# 措辞—证据审查

本轮只重组表达。所有路径相对于本版本目录；历史证据位于`../../computing-strengthening-20261015/`。数字的程序核对见`qa/claim_checks.json`。本表同时作为更新后的主张—证据对照表的具体语言审查。

| 位置与最终核心措辞 | 直接证据与结果 | 身份与适用范围 | 未采用的更强表述 |
|---|---|---|---|
| 标题：Reference Budgets and Ranking Precision in Candidate-Restricted Influence Maximization | `../config.json`，`../review-v3-budget-precision/supplement-pr-budget-precision/protocol.md`；预算80/320/1280、默认与严格PageRank并列控制 | 冻结主实验＋事后数值敏感性；同一IC实现 | 新算法、双分辨率理论、通用评价机制 |
| 摘要/贡献1：tightening PageRank tolerance removes the apparent budget-induced gain-to-loss reversal | `../review-v3-budget-precision/analysis/precision_budget/summary_by_budget_precision.csv`；ca-GrQc默认损失−5.61/2.53/5.07%，严格−11.25/−2.96/−0.54% | 同一三网络、原五路径的事后配对控制；这里的反转指跨路径平均百分比差的符号 | 普遍预算反转、预算没有影响、严格PageRank证明更优或等价 |
| 贡献1：while leaving budget-dependent seed changes | `../review-v3-budget-precision/analysis/precision_budget/budget_transitions_summary.csv`；严格ca-GrQc 4k集合改变3/5与2/5 | 同一事后控制；集合改变不等于实质效用改变 | 所有变化都具有实际意义、达到收敛 |
| 摘要/贡献2：Separating seed agreement from utility differences | `../review-v2/analysis/full_reference_transitions.csv`及`transition_summary.csv`；ca-GrQc320→1280集合5/5改变，平均收益+0.12720节点，路径−0.0266至+0.2411 | 冻结主实验上的描述性转移分析；区间为条件MC，不是网络总体区间 | 集合变化没有价值、每次集合改变都无效、未显著就等价 |
| 结果的历史支撑：16/40 sets changed while mean gain was 0.01111 nodes | `../../computing-strengthening-20261015/analysis/summary.json`的1280→5120条目 | 历史520条件扩展，与外部图不同 | 外部网络在1280已收敛 |
| 摘要/贡献3：degree-based pools reproduce all 15 highest-budget external trajectories | `../review-v2/analysis/arm_path.csv`，`../results/main/conditions/resolution__*__w1280__step.json`及NPZ；15/15有序轨迹一致 | 冻结主实验；三图、k5、p.01、h3、W1280、20候选 | 普遍无损、期望最优、非劣保证 |
| 贡献3：earlier PageRank agreement does not transfer uniformly | 历史summary；外部`../review-v2/analysis/summary_by_method.csv`与严格`summary_by_budget_precision.csv`；历史最高预算40/40、外部默认0/15 | 历史与外部是不同设置的证据层；外部精度控制为事后 | 拓扑是唯一原因、PageRank普遍失败、未控制设置的因果比较 |
| 摘要：The two directed networks retain PageRank losses with a tighter PageRank convergence tolerance | 严格summary：CollegeMsg4k约9%，wiki-Vote4k约74%；原数组见两批precision条件目录 | 按存储方向模拟传播；仅这些图和设置 | 方向失配已被因果证明 |
| 贡献3与结论：lower measured selection cost / scoped timing comparisons | `../review-v2/analysis/arm_path.csv`与`supplement_setup_timing.csv`；选择节省98.40–99.67%，拼接验证成本86.59–96.26% | 冻结选择计时＋独立设置开销拼接；相对于同一实现全枚举 | 优于所有高效IM系统、直接端到端速度提升 |
| 结论：reporting these factors separately makes the basis and limits ... explicit | 以上配对比较及方法定义；属于由结果导出的报告建议 | 对使用截断排名和采样参照的评价有针对性的建议 | 新通用标准、保证评价可靠或不发生误判 |
| 复现说明：26 October check ... representative mode and complete analysis regeneration | `evidence/reproduction-20261026.json`；54条件主记录审计，严格90臂统计，12条件64臂重跑，30CSV/PNG再生成 | 继承的本机核验；本轮没有新实验 | 全部历史重跑、跨平台认证、独立团队复现 |

## 用词审查

- 用“paired evaluation design”描述实验组织，替代“develop a ... framework”可能造成的方法创新暗示。
- 用“mean incremental-spread gain/loss”明确默认反转的指标和聚合层级，避免被理解成每条路径的反转。
- 对ca-GrQc严格最高预算保留+0.02608节点、路径标准差0.09155及范围，未把均值正号描述为优势。
- 用数值“above one fifth of full-reference incremental spread”替代孤立的“substantial”。
- “stable”仅指实际检查的1e-12与1e-14候选池一致，不表示精确PageRank排名已获数学认证。
- 新稿不使用首次、唯一、普遍无损、理论保证、等价或非劣作为肯定性结果主张。
- 作者声明延用已经确认的稿件内容；其真实性来自作者确认，不由实验核验替代。

## 结构语言版补充核对（2026-10-27）

| 本版措辞 | 直接依据 | 范围与避免的更强表述 |
|---|---|---|
| identical final sets yield identical spread evaluations | 模型定义与共享 evaluation worlds；外部已保存数组的同集合检查记录 | 相同模拟器与同一世界族；不推导不同集合必然有不同效用 |
| candidate membership stability at the tested tolerances | `../review-v3-budget-precision/analysis/precision_budget/candidate_pool_precision_diagnostics.csv`；保存的 1e-12/1e-14 池比较 | 事后数值诊断；不是精确向量收敛或数值最优认证 |
| Full incremental spread (nodes) | `manuscript/primary_table.tex` 原值；full 总传播量减 k=5 | 只纠正指标名称；表内数值未变，SI 通用定义保留 k |
| Saving including evaluation (%) | 原 `cost_table.tex` 与既有 setup/selection/evaluation 分项记录 | 分项拼接的暖进程估计，非直接端到端，非紧容差方法成本 |
| 多层邻域影响力估计 | Rui 等出版社摘要；见 `qa/related_work_source_check.md` | 不再把摘要直接当作匹配本文候选池控制的证据 |

结果正文的数值、符号与比较方向同直接上一版一致；`qa/structural_revision_checks.json` 记录本轮实际检查。历史执行记录未改称本轮复现。
