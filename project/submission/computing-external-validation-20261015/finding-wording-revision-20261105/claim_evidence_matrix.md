# 主张—证据—范围
| 主张 | 直接来源 | 范围 |
|---|---|---|
| ca-GrQc默认方向反转依赖容差 | analysis/presentation/precision_all_paths.csv及precision_summary.csv | 事后敏感性，同五路径、同预算参照；非普遍优势 |
| 固定预算默认/严格5/5种子集合变化 | precision_all_paths.csv筛选ca_grqc/pagerank_4k | 候选成员替换与下游变化对应，非单节点因果贡献分解 |
| Degree最高预算保持15条轨迹 | all_primary_arms_paths.csv筛选degree_4k | W1280/step/k5/p.01/h3；非最优性证明 |
| wiki-Vote扩大PR池恢复部分传播量 | primary_summary.csv及all_primary_arms_paths.csv | 全五路径均值；非单路径推断 |
| 示例具体种子及传播量 | wiki_case.csv，wiki_vote/p1101/W1280 | 任务指定说明案例，不增加样本 |
| 集合变化不决定传播变化 | 本版analysis/historical_reference_transitions.csv及原Fig2 | 沿用前版核验；0.01111为全部40配对均值 |
| 方向不匹配与损失一致 | 原稿结构诊断、候选池与参照种子覆盖记录 | 无方向干预，不声称已隔离因果机制 |
| 选择与拼接成本有别 | manuscript/cost_table.tex及方法 | 原表保留，本轮不重新计时、未比较CELF/IMM |

所有本轮读取结果哈希见analysis/presentation/source_hashes.json。旧证据链见evidence/previous_claim_evidence_matrix.md，其中qa记录属于前版。本文增加的是组织与展示清晰度，不增加实验性证据。
