# 方法来源核查（2026-11-01）
仅核查原始来源及官方文档；不是系统综述或完整新颖性审查。

- NetworkX PageRank 官方文档：https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html 。核查到默认alpha=.85、tol=1e-6、迭代停止阈值len(G)*tol。故tol不能直接当节点误差。2026-11-01在线读取。实际安装版本见environment.json；另用validate.py验证分数一致。
- Gleich, PageRank Beyond the Web, SIAM Review 57(3),2015, DOI 10.1137/140976649，作者全文：https://www.cs.purdue.edu/homes/dgleich/publications/Gleich%202015%20-%20prbeyond.pdf 。第3页附近Remark 2.3给出残差L1/(1-alpha)界；同文指出排序可能先于全向量收敛。本轮充分判据由该界及三角不等式推导，不声称新理论。
- Lu, Tao & Zhang, Variance-Dependent Best Arm Identification, UAI2021，原始全文：https://www.auai.org/uai2021/pdf/uai2021.445.pdf 。其有界独立臂设定中复杂度包含variance/gap^2。本文共同世界、多轮适应性流程不自动满足其保证，仅以方差/差距作为已有机制起点。
- Chen, Xing & Crawford, Adaptive Threshold Sampling for Pure Exploration in Submodular Bandits, UAI2025，官方摘要：https://proceedings.mlr.press/v286/chen25c.html 。摘要明确覆盖带噪次模最大化并列出影响力最大化；本轮不把自适应采样构想视为新颖，也未验证当前step-indexed有限步传播符合该算法理论条件。
- Cranmer et al., Discovering Symbolic Models from Deep Learning with Inductive Biases, NeurIPS2020，官方摘要：https://papers.neurips.cc/paper_files/paper/2020/hash/c9f2f917078bd2db12f23c3b413d9cba-Abstract.html 。从带归纳偏置GNN中提取物理关系是相关先例；不能作为本社交计算敏感性问题的效果证据。
- Wills & Ipsen 作者全文 https://ipsen.math.ncsu.edu/ps/simax69812.pdf 本次抓取超时；未将其当作已读全文，不基于此做具体新颖性结论。

研究卡中的其他来源未扩展为本轮已核实证据。所有本轮经验结论只依据本目录实验。
