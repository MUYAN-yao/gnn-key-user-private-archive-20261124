# v7 G0 文献与机制判定：方法论文线止损

日期：2026-09-20。工作流：multi-source-search。检索目标是检验以下狭义
主张能否支撑一篇新的算法论文：在固定有限模拟世界的
`mean - lambda*population_SD + eta*coverage` 目标下，以结构上界和部分
世界 SSE 下界提前停止候选评估，并重现同一有限目标上的 full greedy。

本记录是定向、多源检索与原文核对，不是穷尽性证明；“未找到逐字相同公式”
不等于不存在先例。

## 查询与证据

| 查询主题 | 直接相关来源 | 对判定的作用 |
| --- | --- | --- |
| 风险敏感影响最大化 | NasehiMoghaddam et al., *Risk-Averse Influence Maximization*（[DOI 元数据](https://dblp.org/rec/journals/tjs/NasehiMoghaddam23)；[摘要记录](https://doi.org/10.1016/j.swevo.2023.101424)） | 风险规避目标已是 IM 中已有问题，不能把“风险项”本身作为贡献。该工作使用的风险度量不同，不能据此声称与 v7 完全等价。 |
| 固定情景/样本平均影响最大化 | Güney, *On the optimal solution of budgeted influence maximization*（[记录](https://ideas.repec.org/a/spr/operea/v19y2019i3d10.1007_s12351-017-0305-x.html)）；Tanınmış et al., *Influence Maximization With Deactivation*（[arXiv](https://arxiv.org/abs/1904.08628)）；TipTop（[原文](https://par.nsf.gov/servlets/purl/10112851)） | 固定传播样本/场景构成确定性优化对象是成熟路线；v7 不能把“固定世界”或“完整世界比较”称为新的优化框架。 |
| 场景精确求解、预处理、分支定界 | Chen et al., *Efficient presolving methods*（[原文](https://optimization-online.org/wp-content/uploads/2021/01/8189-1.pdf)）；Nannicini et al., *An exact algorithm for robust influence maximization*（[IBM 论文页](https://research.ibm.com/publications/an-exact-algorithm-for-robust-influence-maximization)） | IM 中已有 scenario-level reachability、变量排除、exact branch-and-bound/Benders 路线。它们的模型不同，却排除“首次安全剪枝/首次 exact search”的叙事。 |
| 非次模风险目标 | Khan et al., *A Multi-criteria Approximation Algorithm for Influence Maximization*（[原文](https://par.nsf.gov/servlets/purl/10163555)） | IM 的风险/概率型目标可失去次模性，已有工作需专门处理；v7 不能从非次模性本身推出创新。 |
| 上界贪心与自适应采样 | UBLF（[原文](https://archives.iw3c2.org/www2014/proceedings/companion/p421.pdf)）；ExpGreedy/TOPX（[原文](https://ojs.aaai.org/index.php/AAAI/article/download/10207/10066)） | 上界削减 MC 与逐步评估均已有直接方法族。 |

## 判定

**G0 不通过：停止把 v7 写作独立的新算法论文，也不启动 E2 的方法性能批次。**

理由并非已证明 v7 的 SSE 上界与任何一篇论文完全相同，而是：

1. 它是既有 SAA/场景优化、上界剪枝和风险目标要素的直接组合；当前没有
   足以证明该组合非显然、且具有独立工程价值的理论或实证证据。
2. E1 只证明代码在小图上没有错误剪枝；它没有给出速度收益或比通用
   branch-and-bound 更强的机制收益。
3. 继续 E2 并在结果后寻找差异，会把探索性结果误用于补造创新叙事。

## 允许保留的材料

- v6 已审计事实：固定 60/120 候选池保持 full 结果，30 候选池在相同第五
  节点处失败；不能宣称 GNN 超过度数筛选。
- v7 E1：一个可复现的软件正确性核验，不能单独作为性能或新颖性证据。
- 完整的候选池、世界、数值和成本审计框架，可转为**方法评估协议**，而非
  新算法贡献。

## 后续转向：评估研究而非方法论文

可探索的研究问题是：在风险敏感的共同世界贪心协议中，固定候选截断、
结构排序、学习排序和简单扩容分别何时偏离 full 结果，质量损失和总成本
如何变化。该方向必须满足：

1. 不预设学习排序优于度数，也不把同一节点的多随机种子当作多网络机制；
2. 使用冻结的完整搜索参照，报告全部失败、首次分叉、遗漏候选的排名、
   独立世界质量差和冷启动总成本；
3. 至少补充多个具准入记录的网络，且将现有 Digg/Higgs 视为开发/探索材料；
4. 若只形成一个狭窄的案例复盘，不将其包装为足以投 Applied Intelligence 的
   原创算法论文。

该转向需要另行设计研究问题和投稿定位；不能沿用 v7 的“算法贡献”标题。
