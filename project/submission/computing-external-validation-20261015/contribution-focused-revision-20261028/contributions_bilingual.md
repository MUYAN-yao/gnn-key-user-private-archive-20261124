# 修订后的贡献

## 1

\textbf{Ranking precision changes the interpretation of an apparent budget effect.} On ca-GrQc, tightening PageRank tolerance exchanges two of 20 candidates. The default mean gain-to-loss reversal then disappears, although budget-dependent seed changes remain. This post-hoc control shows that the reversal cannot be interpreted as a reference-budget effect independent of ranking precision.

\textbf{排名精度改变了对表面预算效应的解释。}在 ca-GrQc 上，收紧 PageRank 容差会替换 20 个候选节点中的两个。默认设置下平均表现由增益转为损失的现象随之消失，但预算相关的种子变化仍然存在。这项事后对照表明，不能将该反转解释为独立于排名精度的参照预算效应。

## 2

\textbf{Reference-set instability can accompany a small average spread improvement.} Increasing $W$ from 1280 to 5120 changes 16 of 40 contact-graph reference sets. The mean independently evaluated spread increase is 0.01111 nodes across all 40 network--path pairs. These measurements distinguish the frequency of seed-set changes from the magnitude of the resulting utility changes.

\textbf{参照集合不稳定可以与较小的平均传播增益同时出现。}将 $W$ 从 1280 增加到 5120 时，40 个接触图参照集合中有 16 个发生变化。在全部 40 个网络与路径配对中，独立评估的传播量平均增加 0.01111 个节点。这些测量将种子集合变化的频率与相应效用变化的大小区分开来。

## 3

\textbf{Degree and PageRank agreement diverge on the external networks.} At $W=1280$, Degree-4k reproduces all 15 full-reference trajectories using 20 candidates and less selection time in this implementation. Default PageRank-4k reproduces none; losses on CollegeMsg and wiki-Vote persist under tighter tolerance. The comparison identifies limits to the earlier contact-graph agreement and ties the observed cost savings to preservation of the tested reference.

\textbf{度与 PageRank 的一致性在外部网络上出现分化。}在 $W=1280$ 时，Degree-4k 使用 20 个候选节点复现了全部 15 条全候选参照轨迹，且在本实现中减少了选择时间。默认 PageRank-4k 未复现其中任何一条轨迹；收紧容差后，CollegeMsg 和 wiki-Vote 上的损失仍然存在。这项比较指出了此前接触图一致性的迁移边界，并将实测计算节省与已测试参照的保留联系起来。