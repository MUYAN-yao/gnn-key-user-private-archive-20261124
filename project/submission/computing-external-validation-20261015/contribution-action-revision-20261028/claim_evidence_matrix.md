# 本版核心主张—证据—范围

根目录为本版；下列相对路径指向已保存的原始版本。本轮只读取既有汇总及做文字一致性核验。

| 本版主张 | 直接依据 | 研究身份与允许范围 | 不支持的更强说法 |
|---|---|---|---|
| 质量差值依赖有限采样参照与数值构建的候选池 | 正文方法3.1–3.2；../config.json；../review-v3-budget-precision/analysis/precision_budget/summary_by_budget_precision.csv | 方法定义＋冻结外部实验及事后控制；揭示所测比较的依赖 | 全新理论、保证消除一切误判 |
| ca-GrQc默认均值由5.61%增益转为5.07%损失；收紧容差后均值反转消失 | 同一summary，dataset=ca_grqc,method=pagerank_4k,W=80/320/1280，按solver区分 | 事后同路径配对敏感性研究；反转指跨路径平均增量传播损失的符号 | 每条路径都反转；预算无影响；严格容差普遍更优 |
| 严格容差下预算相关种子变化仍存在 | ../review-v3-budget-precision/analysis/precision_budget/budget_transitions_summary.csv | 同一外部网络与原五路径；集合变化与效用变化分开 | 证明实质传播收益变化或收敛 |
| 参照集合变化需单独计算其效用后果 | ../review-v2/analysis/full_reference_transitions.csv；本版analysis/historical_reference_transitions.csv | 冻结主实验上的描述性转移分析与单独历史控制 | 集合变化一律无价值；均值很小即统计等价 |
| degree-4k在最高测试预算复现全部15条外部参照轨迹 | ../review-v2/analysis/arm_path.csv；W=1280,method=degree_4k,coupling=step；same_order全为True | 三外部图、各五条计算路径，k5,p.01,h3，20个候选 | 普遍无损、15个独立网络、期望最优 |
| 有向网络上的PageRank损失在收紧容差后保留 | precision summary；college_msg/wiki_vote,pagerank_4k,strict全部预算 | 按存储方向的模拟传播；保留负面结果 | PageRank普遍失效；方向不匹配已获因果证明 |
| 保持参照的计算节省有明确适用范围 | 本版manuscript/cost_table.tex；../review-v2/analysis/arm_path.csv | 相对同实现全候选逐轮枚举，选择实测与拼接成本区分 | 优于CELF/IMM或直接端到端优势 |
| 规模有限、经选择的真实网络样本 | 正文4.1、表1；analysis/historical_experiment_coverage.csv | 三张外部图与四张小接触图分别分析 | 千级外部图均为小图；随机世界或路径扩大独立网络样本量 |

最终英文措辞与中文对应见revised_passages_bilingual.md。作者声明沿用已确认原稿，未由核验脚本重新证明其真实性。直接核对记录见qa/revision_checks.json；其范围是本轮保留主张的一致性检查，不是重新验证所有实验。


## 2026-10-28 结构修订补记

本轮保留上表全部实验来源和适用范围。新增内容如下：

| 内容 | 来源 | 证据身份与边界 |
|---|---|---|
| IM 背景及经典求解策略 | 本轮 qa/literature_source_check.md 的原文来源 | 既有研究；非本文新增发现 |
| 共享固定采样世界与候选池数值构造的区别 | StaticGreedy 原文、原稿固定边/按步诊断与精度控制 | 文献联系及对已有结果的解释；不增加理论保证 |
| 方向相关解释移入讨论 | 原结果 wiki-Vote 入/出度及候选重合数据 | 结构诊断；没有方向干预因果证据 |
| 精度×耦合与方向干预 | 现有局限导出的研究问题 | 未执行的未来检验，不是实验发现 |


## 本轮贡献句的直接证据（2026-10-28）

| 贡献 | 来源与筛选 | 范围 |
|---|---|---|
| 排名精度影响反转解释 | review-v3-budget-precision/analysis/precision_budget/summary_by_budget_precision.csv，ca_grqc，pagerank_4k，default/strict，W=80/320/1280；candidate_pool_precision_diagnostics.csv 对应候选重叠 | 事后敏感性控制；五条既有路径；不证明所有预算效应均为数值误差 |
| 集合变化与平均收益分离 | analysis/historical_reference_transitions.csv，stage=resolution，step，k=5，low=1280，high=5120 | 四接触图×十路径；均值分母全部40配对，不是16个变化配对；无等效保证 |
| 外部排名表现分化 | review-v3-budget-precision/analysis/summary_by_method.csv，step，W=1280，degree_4k/pagerank_4k；精度汇总中两有向图 strict/pagerank_4k | 3图×5路径；对应本实现选择时间；不确立跨图普遍性、期望最优或方向因果解释 |

本轮读取的绝对路径、SHA-256 和重算值保存在 qa/evidence_checks.json。保留原主张表，其上轮记录不等于本轮新执行。


## 本轮贡献句的直接证据（2026-10-28）

| 贡献 | 来源与筛选 | 范围 |
|---|---|---|
| 排名精度影响反转解释 | review-v3-budget-precision/analysis/precision_budget/summary_by_budget_precision.csv，ca_grqc，pagerank_4k，default/strict，W=80/320/1280；candidate_pool_precision_diagnostics.csv 对应候选重叠 | 事后敏感性控制；五条既有路径；不证明所有预算效应均为数值误差 |
| 集合变化与平均收益分离 | analysis/historical_reference_transitions.csv，stage=resolution，step，k=5，low=1280，high=5120 | 四接触图×十路径；均值分母全部40配对，不是16个变化配对；无等效保证 |
| 外部排名表现分化 | review-v3-budget-precision/analysis/summary_by_method.csv，step，W=1280，degree_4k/pagerank_4k；精度汇总中两有向图 strict/pagerank_4k | 3图×5路径；对应本实现选择时间；不确立跨图普遍性、期望最优或方向因果解释 |

本轮读取的绝对路径、SHA-256 和重算值保存在 qa/evidence_checks.json。保留原主张表，其上轮记录不等于本轮新执行。
