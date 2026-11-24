# 术语与比较方向

| 符号/术语 | 本版固定含义 |
|---|---|
| W / selection-world budget / 选择世界预算 | 同预算条件中同时供全候选和受限候选贪心选择使用；并非只提高参照预算 |
| M / independent evaluation budget / 独立评估预算 | 外部实验及520条件扩展为10,000；最初42条件为2,000；资源预检为1,000，分别说明 |
| τ / ranking tolerance / 排名容差 | PageRank候选构建的数值设置，与W及M分离 |
| q / candidate-pool size / 候选池大小 | 决定候选资格；不裁剪传播图；既定排名下跨W固定 |
| restricted-minus-full difference | 同一W下受限方法减全候选参照，正值表示受限传播量更高 |
| incremental loss | -100 × 配对差值 / 全候选增量传播量；与上述差值反号；先逐路径计算再汇总 |
| reference-transition change | 只比较参照：高W减低W的独立估计传播量，与方法间差值不同 |
| same-budget precision control | 固定W，重算受限臂；复用对应W的冻结参照及评估世界 |

作者确认的标题保持不变；正文将其“Reference Budget”准确解释为两类选择共同使用的W。
