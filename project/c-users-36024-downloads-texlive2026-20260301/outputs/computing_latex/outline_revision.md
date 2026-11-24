# 按导师建议核对 Computing 范文与稿件大纲

核对日期：2026-09-28。

导师截图中的建议是“找个 LaTeX 模板排版会好看些”“下个范文对着改大纲”。本工程已经使用 *Computing* 投稿指南所列的 Springer SVJour3 单栏模板；此次进一步参照该刊已发表的开放获取常规论文核对章节组织。

## 对照论文

Martha Garzón, Lindsay Álvarez-Pomar, Sergio Rojas-Galeano. “From collective intelligence to global optimisation: an agent-based model approach.” *Computing* 107, article 83 (2025). DOI: [10.1007/s00607-025-01429-8](https://doi.org/10.1007/s00607-025-01429-8)。[期刊页面](https://link.springer.com/article/10.1007/s00607-025-01429-8) · [官方 PDF](https://link.springer.com/content/pdf/10.1007/s00607-025-01429-8.pdf)。

已将这篇已发表论文的 27 页 PDF 单独保存为 `Computing_范文_Garzon_2025.pdf`，并核对首页期刊名、文章题目和 DOI。该文件不在投稿工程压缩包中。

该文的主线是 Introduction → Related work → Methods → Experiments → Discussion → Conclusion。它研究的是新元启发式算法；本稿研究的是既定实验矩阵下，有限模拟分辨率对候选截断评估结论的影响。因此只借鉴章节功能和证据组织，不照搬其算法贡献叙述、实验或措辞。已发表论文的最终版页数也不作为投稿稿件的页数标准。

## 本稿大纲调整

| 原稿 | 修订后 | 目的 |
| --- | --- | --- |
| 1 Introduction，内含 1.1 Related work | 1 Introduction；2 Related work | 让研究问题、贡献与文献定位分开，方便审稿人查找。 |
| 2 Resolution-aware evaluation | 3 Methods | 以有限世界贪心选择、参照细化、独立评价和代价定义组成方法章节。 |
| 3 Experimental design；4 Results | 4 Experiments | 将数据、候选池、评价指标和相应结果放在同一实验主线下。 |
| 5 Implications and limits | 5 Discussion and limitations | 明确区分结果、解释、适用边界及后续工作。 |
| 6 Conclusion | 6 Conclusion | 保留原有结论。 |

实验节的顺序现为：网络与模拟传播 → 候选池和比较矩阵 → 评价指标与分析 → 参照轨迹稳定性 → 候选池一致性与时间成本 → 独立效用 → 最终种子集变化。这样先交代对照条件，再按研究问题给出证据。两处原来写死的“Section 4.4 / Section 4.2”已改为自动交叉引用，章节编号变动后仍能正确指向。

此次为结构修订：没有增加文献、编造实验、改变图表数据或加强原稿的证据结论。投稿格式仍以 [*Computing* 官方指南](https://link.springer.com/journal/607/submission-guidelines) 为准；对照论文只是已发表文章的结构例子。
