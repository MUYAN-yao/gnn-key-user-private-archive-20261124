# 本版贡献（正文对应原文）

\textbf{We identify how ranking precision alters an apparent budget effect.} We vary the selection budget for both full and restricted arms and use a post-hoc precision control to examine the resulting relative spread differences. On ca-GrQc, tightening PageRank tolerance exchanges two of 20 candidates and removes the default mean gain-to-loss reversal. This identifies a numerical dependence that a budget scan at default tolerance alone would miss.

\textbf{We quantify independently estimated spread changes associated with reference-set changes.} Independent paired evaluation measures their direction, magnitude and conditional Monte Carlo uncertainty. In the historical comparison from $W=1280$ to $W=5120$, 16 of 40 reference sets change, while mean spread increases by 0.01111 nodes across all 40 network--path pairs. Individual changes include negative, positive and zero differences; the measurements separate seed-set instability from changes in estimated utility.

\textbf{We identify which tested candidate pools preserve the reference while reducing selection cost.} At $W=1280$, Degree-4k uses 20 candidates to reproduce all 15 external reference trajectories at lower selection cost in this implementation. Default PageRank-4k reproduces none, and losses on CollegeMsg and wiki-Vote persist under tighter tolerance. These comparisons delimit the transfer of earlier contact-graph agreement and relate computational savings to independently evaluated utility.

\textbf{本文识别排名精度如何改变对表面预算效应的判断。}同时改变全候选与受限实验臂的选择预算，并通过事后精度对照考察相对传播差异。在 ca-GrQc 上，收紧 PageRank 容差会替换 20 个候选节点中的两个，并使默认设置下平均表现由增益转为损失的现象消失。由此识别出仅在默认容差下扫描预算时会遗漏的数值依赖。

\textbf{本文量化参照集合变化所对应的独立估计传播量变化。}通过配对独立评估，测量变化的方向、大小及其条件 Monte Carlo 不确定性。在 $W=1280$ 到 $W=5120$ 的历史比较中，40 个参照集合有 16 个发生变化，而全部 40 个网络与路径配对的平均传播量增加 0.01111 个节点。各配对包含负、正及零差值；这些测量区分了种子集合的不稳定性与估计效用的变化。

\textbf{本文识别哪些已测试候选池能够在减少选择成本的同时保持参照结果。}在 $W=1280$ 时，Degree-4k 用 20 个候选节点复现全部 15 条外部参照轨迹，并降低本实现中的选择成本。默认 PageRank-4k 未复现其中任何一条轨迹，且收紧容差后 CollegeMsg 和 wiki-Vote 上的损失仍然存在。这些比较明确了此前接触图一致性的迁移边界，并将计算节省与独立评估的效用联系起来。