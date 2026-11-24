# 主张—证据对照表

当前正文、编辑summary、cover letter和结论使用同一主张集合。完整逐项记录见[claim_language_audit.md](claim_language_audit.md)，其中包含最终措辞、直接证据路径、研究身份、适用范围与不支持的更强表述。

核心证据分为：冻结外部主实验、历史接触图扩展、事后严格容差控制，以及描述性结构诊断。预算比较的精度依赖不能扩展成普遍规律；结构方向诊断不能替代因果干预；参考一致性不能替代期望最优性。

作者、单位、基金、贡献、利益冲突、批准及AI披露沿用当前已确认稿件。本轮不重复标注为“待确认”，也不把作者声明当作可由数值脚本证明的事实。

## 本轮新增的结论—来源—范围

下面H指 `submission/computing-strengthening-20261015`，N指本修订目录。所有新增结果最终读取H的 `results/conditions/*.json,*.npz`，中间汇总保存到N/analysis；原表对照H/analysis对应CSV。

| 论文中的表述或结果 | 源文件和筛选条件 | 入稿位置 | 身份与适用范围 | 不支持的更强表述 |
|---|---|---|---|---|
| 历史扩展覆盖预算、局部p/h、固定边、k20和两个固定合成实例 | H/snapshot/config.json；520条件按stage分为200/160/80/60/20；H/protocol.md | 正文4.1；表S9；N/analysis/historical_experiment_coverage.csv | 已冻结历史扩展；初始42只核对协议与元数据 | 不称大规模独立网络验证，不将复用默认40条件再计入160 |
| step 1280→5120：16/40集合改变，均值+0.01111，范围−0.0383…+0.1180节点 | N/analysis/historical_reference_transitions.csv：stage=resolution,low=1280,high=5120；与H/analysis/reference_transitions.csv核对 | 正文5.2；表S12 | 四接触图、k5,p.01,h3、十路径/图的描述性均值 | 不证明收敛；40配对不是40个网络 |
| fixed edge 320→1280：29/40集合改变，均值+0.061845，范围−0.011…+0.2572节点 | 同上：stage=coupling,low=320,high=1280；原数组仅同耦合内配对 | 正文5.2；表S12；图S6 | 历史固定边控制；区间条件于已选集合 | 不能与另一个W区间直接作耦合效应估计，不证明ca-GrQc严格容差×固定边联合效果 |
| 160非默认参数条件：D/P轨迹匹配117/132；Weighted负117、正43 | N/analysis/historical_path_metrics.csv：stage=parameters、各method；参数图额外复用resolution W320默认 | 正文5.4；补充12.2；表S10、图S5 | 冻结历史局部参数变化，非完整全因子；描述性计数 | 不能作独立伯努利成功率推断；不代表外部有向图参数鲁棒性 |
| p=.05,h3下Weighted四图均差−.51309/−1.52602/+.07939/−4.98321 | N/analysis/parameter_sensitivity_display.csv：method=weighted_4k,p=.05,h=3 | 补充12.2 | 同时保留正负差；loss均值先按路径求比例 | 不凭绝对差比较相对损失，不删负面网络 |
| fixed edge W1280：D/P/W轨迹匹配38/40、40/40、5/40；step为38/40、40/40、7/40 | N/analysis/coupling_display.csv：W=1280，按coupling各自统计order_matches | 正文5.4、补充12.3、表S11 | 各coupling与自身full参考比较 | 不作step-edge逐世界相减，不说采样方式不重要 |
| k20 Kenya全池75/75；invs2013为80/91，invs2015为80/212 | H原JSON candidate_count/n；N/analysis/secondary_display.csv：stage=seed_budget | 正文讨论；补充12.4、表S13 | 全池identity或高覆盖控制 | Kenya一致不能当筛选收益；没有sfhh2009 k20证据 |
| 合成BA W320三方法5/5；SBM Degree1/5、PR0/5，均差+.04052/+.03756 | N/analysis/secondary_display.csv：stage=scale,W=320 | 补充12.4、表S13 | BA/SBM各一个固定实例、各五路径，拓扑派生权重 | 不推断整个图族；不把Weighted算为历史事件独立证据 |
| 完整性与所选描述统计一致 | qa/historical_integration_validation.json；全部1040哈希、4680臂、3640路径行、378组、240转移 | 补充12.1及复现说明 | 本轮实际重算，不调用模拟器 | 不等于全部设计问题消除、所有语义重放或独立团队复现 |

外部精度主线保持原 `claim_language_audit.md` 的范围：ca-GrQc默认反转在严格容差下消失；严格容差仍有预算相关种子变化；方向性诊断不是因果干预。新增历史结果没有提高这些主张的统计显著性、新颖性等级或外部效力。
