# 主张—证据—适用范围（继承并注明核验来源）

以下路径相对本版。来源文件哈希及实测核对计数见 ../budget-interpretation-revision-20261031/qa/design_evidence.json、../budget-interpretation-revision-20261031/qa/read_source_hashes.json。

| 主张 | 直接证据 | 适用范围及不支持的推断 |
|---|---|---|
| W同时作用于两类选择 | ../snapshot/run_experiment.py:46–56；../../computing-strengthening-20261015/snapshot/run_extension.py:61–76；两包配置与全部54/520个条件JSON | 两类臂在每个W重新选择；不能归因为只改变参照 |
| M与候选池跨W固定 | 同上；条件evaluation_world_count、evaluation_world_sha256及candidate_ids逐组核对 | 按同图/路径/传播设置/耦合比较；不能把不同耦合世界逐元素配对 |
| 精度控制复用同预算参照 | ../review-v3-budget-precision/supplement-pr-budget-precision/protocol.md；../review-v3-budget-precision/src/run_precision_budget_control.py；30个低预算条件的参照及世界哈希 | 固定W只重算受限臂；跨W取各自W参照；不是全参照跨预算固定 |
| ca-GrQc默认符号反转随容差控制消失 | ../review-v3-budget-precision/analysis/precision_budget/summary_by_budget_precision.csv，ca_grqc/pagerank_4k/default及strict | 五条既有路径的事后敏感性研究；不证明普遍收益或每路径反转 |
| 参照集合变化与传播量变化分别量化 | analysis/historical_reference_transitions.csv，resolution/step/k5/1280→5120及coupling/edge/k5/320→1280 | 各40配对，均值+0.01111/+0.061845；同时保留负、正、零差值；不是保证增益 |
| 最高外部预算Degree一致，PR有向损失保留 | ../results/main/conditions/；上述precision summary | k5/p.01/h3、三外部图、五路径、W1280；不扩大独立网络数或声称期望最优 |
| 计算节省对应本实现计时范围 | manuscript/cost_table.tex；原稿方法与计时记录 | 选择实测与分项拼接区别保留；未与CELF/IMM进行运行时间比较 |

本轮没有增加科学证据，仅依据既有记录纠正解释。本轮按作者要求缩短 AI 使用脚注，其余正式声明保持不变；作者声明不属于脚本独立核实的实验事实。
