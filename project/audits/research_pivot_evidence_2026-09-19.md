# 研究转向证据与最近邻工作检查

日期：2026-09-19。用途：研究决策；不是系统综述或新颖性认证。
文献仅在实际检查的章节范围内支持下列判断。没有添加未经验证的 BibTeX。

## ER-20260919-v6-omission-01

- Source type: experiment artifact；新增分析为探索性、事后、只读。
- Source: `audits/candidate-reduction-v6-digg-k5-formal/digg/seed-74.json`
  至 `seed-83.json`；派生表 `audits/v6_failure_mechanism_2026-09-19.json`。
- Supports: 十个完整贪心序列均为2241、360、1485、174、290。30池前四个
  节点与完整搜索相同，第五步分叉；290的GNN排名依次为
  39、37、33、41、35、32、36、35、33、44，度数排名恒为34。
- Limitation: 同一图上的同一节点截断，不是十种独立的网络失效机制。
  不能据排名为未运行的度数30/60臂或其他候选数虚构效用结果。
- Claim strength: observed；原v6已验证效用统计不被改写。
- Allowed wording: 本批30池的轨迹偏离涉及同一第五节点的排除。
- Forbidden: 已发现普适候选阈值；已证明GNN比度数差；新策略已验证有效。
- Recheck fields: arms[arm].selection.top_k；
  arms.gnn_pool_120.membership_rank_order；
  arms.weighted_out_degree_pool_120.membership_rank_order。

## ER-20260919-gcomb-01

- Source type: full paper；NeurIPS 2020，正文§3.2。
- Source: https://papers.neurips.cc/paper_files/paper/2020/file/e7532dbeff7ef901f2e70daacb3f452d-Paper.pdf
- Metadata cross-check: https://dblp.org/rec/conf/nips/ManchandaMDMRS20.html
- Supports: GCOMB 的 noise predictor 使用出边权和排序，以训练贪心解中的
  最差节点排名构造预算相关阈值，并讨论对未见预算和图规模的推广。
- Project relevance: “随预算选择候选数”已经有具体先例，必须做机制对照。
- Limitation: 不能从该文推出当前均值—标准差目标的保证；不比较跨论文数值。
- Claim strength: supported，限上述方法事实；不支持本项目的新颖性。

## ER-20260919-temporal-candidates-01

- Source type: preprint full text；2025版本，方法及实验部分。
- Source: https://arxiv.org/html/2503.23713v1
- Metadata cross-check: https://dblp.dagstuhl.de/rec/journals/corr/abs-2503-23713.html
- Title: GNN-Based Candidate Node Predictor for Influence Maximization in Temporal Graphs
- Supports: 研究用影响力容量指标构造候选标签，结合GNN与BiLSTM预测时序
  候选，并比较候选方法与贪心的模拟传播及计算成本。
- Project relevance: “时序GNN候选预测加速”也不是未占据的研究问题。
- Limitation: 预印本身份；未把其时序信息条件等同本项目，亦不推断其无泄漏。
- Claim strength: supported，限所查方法与实验设置。

## ER-20260919-deeppruner-01

- Source type: full paper；SoCS 2025，问题定义与方法部分。
- Source: https://ojs.aaai.org/index.php/SOCS/article/download/35981/38136/40053
- Title: Hierarchical DeepPruner: A Novel Framework for Search Space Reduction
- Supports: 两阶段方法用GNN初筛和神经蒙特卡洛树搜索进一步构造较小候选集，
  评估包含影响力最大化；正文MDP终止使用固定元素数量。
- Project relevance: 比较对象不能只有随机或度数；分层、学习、剪枝的组合也已有先例。
- Limitation: 未独立复现；不能声称其在当前协议上优于或劣于本项目。
- Claim strength: supported，限机制事实；未写入正式参考文献库。

## ER-20260919-submodular-sparsification-01

- Source type: full paper；AISTATS 2017，理论前提部分。
- Source: https://proceedings.mlr.press/v54/zhou17a/zhou17a.pdf
- Title: Scaling Submodular Maximization via Pruned Submodularity Graphs
- Supports: 通过次模图进行候选缩减，主要贪心近似界含单调、非负、次模前提。
- Project relevance: 要研究有保证的筛选，需面对既有剪枝理论，而非声称首次有保证。
- Limitation: 当前风险目标及步数相关随机世界没有被证明满足这些前提。
- Claim strength: supported，限理论适用范围。

## 后续阅读，不晋升为本项目创新结论

2026年预印本 Submodular Ground-Set Pruning: Monotone Tightness and a
Non-Monotone Separation（https://arxiv.org/html/2605.04428v1）也已检索到。
需完整比较其containment目标、预算范围及假设；本次未完成相应证明审读。

## 代码边界核查

`experiments/run_v5_candidate_reduction.py` 的 common-world 随机数带传播步数，
评价目标含标准差罚项；不可不经证明使用固定覆盖函数的次模剪枝理论。
现有artifact保存概率哈希而非可直接重放的完整概率表。

## 对先前投稿建议的修正

此前稿件审计检查的是陈述是否符合实验，而不是贡献是否足够新。
“无需更多训练即可写成窄范围论文”不能等同“已达到目标期刊发表水平”。
将投稿工作优先级改为：贡献与可行性审查 → 条件性的小原型 → 独立验证 → 成稿。
新方向目前是一张研究问题卡；没有新方法性能结果，也没有新训练启动。
