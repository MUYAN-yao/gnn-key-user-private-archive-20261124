# 精度敏感性与符号回归：严格分析

主要比较：在整张留出图上，受限SR是否比验证选定的简单模型更好地预测最终种子集合不稳定程度。单位是图，测试8图，每图12个相关条件；不把96行当96个独立网络。

| model | mse | mae |
| --- | --- | --- |
| constant | 0.108252 | 0.297462 |
| linear_structure | 0.034275 | 0.145109 |
| ratio_linear | 0.077699 | 0.221907 |
| symbolic | 0.077699 | 0.221907 |

按图的完整误差：

| graph | constant | linear_structure | ratio_linear | symbolic |
| --- | --- | --- | --- | --- |
| SBM_0 | 0.044452 | 0.061301 | 0.070711 | 0.070711 |
| SBM_1 | 0.084931 | 0.007869 | 0.016179 | 0.016179 |
| SBM_2 | 0.071938 | 0.051307 | 0.04781 | 0.04781 |
| WS_0 | 0.105036 | 0.031829 | 0.034338 | 0.034338 |
| WS_1 | 0.089628 | 0.019769 | 0.016765 | 0.016765 |
| WS_2 | 0.094867 | 0.033722 | 0.033362 | 0.033362 |
| ca_grqc | 0.160482 | 0.032305 | 0.143806 | 0.143806 |
| wiki_vote | 0.214686 | 0.036102 | 0.258621 | 0.258621 |

## 主要读数

- PR150条件中19条件候选有替换，68条件满足gap>2 residual/.15，全部无替换；82个未满足条件中63个仍稳定。界能给出保守充分保证，未充分解释不稳定幅度；不成立不能判定发生变化。无必要立即另开PR符号拟合。
- 所有15图的两个候选池在tol1e-14与1e-15间保持成员一致；最大分数差约1.07e-11，残差详见graphs.json。数值检查不是含舍入误差的严格证书。
- 120个受限跨预算转移中100个改变种子集合、115个改变顺序；其中46个集合变化的效用差CI跨0，尚无法区分。54个条件可在逐比较条件95%区间区分。多重比较未校正，不作总体显著性宣称。全候选12转移中7个集合变化、11个顺序变化，6个效用差可区分。
- SR=单变量x基线；留出MSE比结构线性模型高126.7%，只3/8图改善；三次训练整图重采样仅1次留出整体更好。未达预声明继续门槛。
- 结构模型相对ratio基线整体MSE下降55.9%，但仅合成留出6图下降6.1%（0.036527到0.034299），3/6图更好；不能称稳定跨族收益，更不能对特征系数作因果解释。

## Claim Candidates

- Claim：残差/边界差距能作保守稳定诊断。
  - Source evidence：pagerank.csv、diagnostic_summary.json、graphs.json。
  - Allowed wording：本轮68个满足充分判据的条件均未替换。
  - Forbidden stronger wording：判据失败就会改变候选；tol就是节点误差；判据解释了所有替换数量。
  - Uncertainty：同图多个条件非独立，浮点残差未校正舍入。
  - Next check：局部误差界是否更少保守。
  - Decision：keep。
- Claim：身份/顺序变动不能直接代替效用变动。
  - Source evidence：budget_transitions.csv、pagerank_utility.csv、独立评价NPZ。
  - Allowed wording：本轮46/100受限集合改变的预算转移尚无法区分传播收益；有序轨迹变化且最终集合相同的条件效用精确相同。
  - Forbidden stronger wording：身份变化无影响；提高精度必然改善传播；CI跨0说明等效。
  - Uncertainty：CI条件于选出集合和图，未作多重修正。
  - Next check：更多独立图及接近应用阈值条件的评价精度。
  - Decision：keep。
- Claim：当前特征/目标/受限SR搜索没有稳定增量。
  - Source evidence：selected_models.json、model_metrics_by_graph.csv、formula_stability.json。
  - Allowed wording：本轮搜索未超过验证选定的简单结构回归，建议停止扩充SR搜索预算。
  - Forbidden stronger wording：所有SR算法无效；发现普适公式；线性模型已能部署节省预算。
  - Uncertainty：仅5训练、2验证、8留出图，参考解本身有噪声，表达式语法有限。
  - Next check：先检验结构基线跨更多真实图及多参考路径稳定性。
  - Decision：keep。
