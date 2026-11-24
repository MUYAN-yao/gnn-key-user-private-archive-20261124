# 候选受限影响力最大化中的参照预算与排名精度

**正文全文中英对照译稿**。基线：structural-language-revision-20261027；英文正文 15 页。中文 PDF 另见 manuscript/manuscript_zh.pdf。
本文件覆盖摘要、全部正文、3 幅图、4 张表、作者声明和参考文献。补充材料全文不在本次翻译范围；文中对其引用译为“在线补充材料 1”。
作者姓名保留英文拼写，避免擅自推定中文姓名。参考文献保留原始书目信息。

## 章节索引
[摘要](#S026) · [引言](#S030) · [相关工作](#S051) · [方法](#S060) · [设置](#S093) · [结果](#S147) · [讨论](#S195) · [结论](#S209) · [声明](#S213)

<a id="S015"></a>
**Source:** 英文 p.1；manuscript.tex:15；S015

**Original:** Reference Budgets and Ranking Precision in Candidate-Restricted Influence Maximization

**中文:** 候选受限影响力最大化中的参照预算与排名精度

<a id="META01"></a>
**Source:** 英文 p.1；manuscript.tex:17；META01

**Original:** Jiayue Sun; Binbin Yong (corresponding author); Junjie An; Tianyu Bo; Shuai Li. School of Artificial Intelligence / School of Information Science and Engineering, Lanzhou University, Lanzhou 730000, China; Lanzhou University, Lanzhou, China. Email: yongbb14@lzu.edu.cn

**中文:** Jiayue Sun；Binbin Yong（通讯作者）；Junjie An；Tianyu Bo；Shuai Li。单位按英文原文：兰州大学人工智能学院、信息科学与工程学院，中国兰州 730000；其余作者单位为兰州大学，中国兰州。邮箱：yongbb14@lzu.edu.cn

<a id="S026"></a>
**Source:** 英文 p.1；manuscript.tex:26；S026

**Original:** Candidate restriction reduces greedy search cost in influence maximization, but evaluating its quality involves two numerical choices: the sampling budget of the full-candidate reference and the precision of the ranking used to construct the pool. We examine their consequences through paired selection and independent spread evaluation on three real network topologies. On ca-GrQc, default PageRank yields a mean incremental-spread gain of 5.61% at 80 selection worlds and a loss of 5.07% at 1280. A post-hoc tolerance control removes this reversal, while budget-dependent seed changes remain. The two directed networks retain PageRank losses with a tighter PageRank convergence tolerance. Changes in reference sets also need not imply comparable utility changes: all five ca-GrQc sets change between 320 and 1280 worlds, with a mean spread gain of 0.12720 nodes. At 1280 worlds, degree-based pools reproduce all 15 full-reference trajectories at lower measured selection cost. These results support reporting reference budget and ranking precision alongside candidate coverage, seed agreement, independent utility and the scope of computational cost.

**中文:** 候选限制能够降低影响力最大化中贪心搜索的成本，但其质量评价涉及两项数值选择：全候选参照的采样预算，以及用于构建候选池的排名精度。我们在三个真实网络拓扑上，通过配对选择和独立传播评价考察这两项选择的影响。在 ca-GrQc 上，默认 PageRank 在使用 80 个选择世界时，平均增量传播量比参照高 5.61%；使用 1280 个选择世界时则低 5.07%。事后容差控制使这一反转消失，但与预算有关的种子变化仍然存在。在两个有向网络上，收紧 PageRank 收敛容差后仍保留传播损失。参照集合的变化也不必然对应相近程度的效用变化：ca-GrQc 的全部五个集合在选择世界数从 320 增至 1280 时均发生变化，平均传播增益为 0.12720 个节点。在 1280 个选择世界下，基于度的候选池以更低的实测选择成本复现了全部 15 条全候选参照轨迹。这些结果支持同时报告参照预算、排名精度、候选覆盖率、种子一致性、独立评估的效用以及计算成本的计量范围。

<a id="S027"></a>
**Source:** 英文 p.1；manuscript.tex:27；S027

**Original:** influence maximization ； Monte Carlo simulation ； candidate restriction ； evaluation methodology ； reproducibility

**中文:** 影响力最大化 ； 蒙特卡洛模拟 ； 候选限制 ； 评价方法 ； 可复现性

<a id="S030"></a>
**Source:** 英文 p.1；manuscript.tex:30；S030

**Original:** Introduction

**中文:** 引言

<a id="S031"></a>
**Source:** 英文 p.1；manuscript.tex:31；S031

**Original:** Restricting which vertices may become seeds reduces the search space of greedy influence maximization. A useful evaluation must establish what that reduction preserves: the reference's selected seeds, its independently evaluated spread, or a specified quality–cost trade-off. These outcomes are related, but seed agreement alone does not quantify the utility consequence of a restriction.

**中文:** 限制哪些节点可以成为种子，能够缩小贪心影响力最大化的搜索空间。有效的评价需要明确，这种缩减保留了什么：参照选出的种子、参照经独立评估得到的传播量，还是某种指定的质量与成本权衡。这些结果彼此相关，但仅凭种子一致性，无法量化候选限制对效用的影响。

<a id="S033"></a>
**Source:** 英文 p.2；manuscript.tex:33；S033

**Original:** Two numerical choices enter this comparison at different stages. The full-candidate reference is selected using finitely sampled diffusion worlds, so increasing its budget can change both its seeds and the measured gap to a restricted method. A ranking determines eligibility before selection: changes in numerical scores can exchange vertices at the pool boundary and alter the restricted search. A quality change observed across budgets therefore needs to be examined together with the precision used to form the pool.

**中文:** 两项数值选择在比较的不同阶段发挥作用。全候选参照根据有限个采样传播世界选出种子，因此，提高其预算可能同时改变参照种子以及候选受限方法相对参照的实测差值。排名则在选择之前决定候选资格：数值分数的变化可能使候选池边界处的节点发生替换，从而改变受限搜索。因此，对跨预算观察到的质量变化，需要结合构建候选池时采用的数值精度进行考察。

<a id="S035"></a>
**Source:** 英文 p.2；manuscript.tex:35；S035

**Original:** We ask which candidate-restriction results persist when reference budget and ranking precision are varied separately, and how seed changes affect independently evaluated spread. Full and restricted selection share the graph, selection-world prefix and tie rule (Fig. 1). Their selected seeds are evaluated on a shared set of worlds independent of selection.

**中文:** 我们考察：分别改变参照预算与排名精度后，哪些候选限制结果仍然成立，以及种子变化如何影响独立评估的传播量。全候选选择与受限选择共享图、选择世界前缀和同分规则（图 1）。两者选出的种子在一组共享且独立于选择过程的世界上接受评估。

<a id="F001"></a>
### 图 1
**Source:** 英文 p.3；置于 S035 后

![F001](D:/校创/基于GNN的关键用户识别/submission/computing-external-validation-20261015/chinese-translation-20261027/assets/F001.png)

<a id="C001"></a>
**Source:** 英文 p.3；manuscript.tex:48；C001

**Original:** Paired evaluation separates reference resolution, ranking resolution and restriction quality. (a) The selection budget $W$ and ranking tolerance $\tau$ determine the finite-world reference and the top-$q$ pool $C(\tau,q)$. Both arms share the graph, world prefix, seed budget and tie rule. (b) Shared evaluation worlds, independent of selection, yield the utility difference $\Delta U$. Set agreement $J$ and selection-cost ratio $\rho_T$ complete the quality–cost comparison.

**中文:** 配对评价区分参照分辨率、排名分辨率与候选限制的质量。（a）选择预算 $W$ 与排名容差 $\tau$ 分别决定有限世界参照和前 $q$ 名候选池 $C(\tau,q)$。两实验臂共享图、世界前缀、种子预算与同分规则。（b）共享且独立于选择过程的评估世界给出效用差 $\Delta U$。集合一致性 $J$ 与选择成本比 $\rho_T$ 共同构成质量与成本比较。

<a id="S037"></a>
**Source:** 英文 p.2；manuscript.tex:37；S037

**Original:** The external study uses communication, collaboration and voting topologies to examine whether candidate-ranking results from smaller contact graphs transfer to different network structures. A post-hoc PageRank control separates changes in pool membership caused by solver tolerance from changes in seed selection caused by the reference budget.

**中文:** 外部研究采用通信、合作和投票拓扑，考察较小接触图上的候选排名结果能否迁移到不同网络结构。事后 PageRank 控制将求解容差引起的候选池成员变化，与参照预算引起的种子选择变化区分开来。

<a id="S039"></a>
**Source:** 英文 p.2；manuscript.tex:39；S039

**Original:** The study makes three empirical contributions:

**中文:** 本研究有三项实证贡献：

<a id="S041"></a>
**Source:** 英文 p.2；manuscript.tex:41；S041

**Original:** (1)  **Distinguishing budget effects from ranking-precision effects.** On ca-GrQc, tightening PageRank tolerance removes the apparent budget-induced gain-to-loss reversal while leaving budget-dependent seed changes.

**中文:** (1)  **区分预算效应与排名精度效应。**在 ca-GrQc 上，收紧 PageRank 容差使表面上由预算引起的增益转损失现象消失，但与预算有关的种子变化仍然存在。

<a id="S042"></a>
**Source:** 英文 p.2；manuscript.tex:42；S042

**Original:** (2)  **Separating seed agreement from utility differences.** Reference-budget transitions produce set changes with differing spread consequences. Paired evaluation quantifies their magnitudes and uncertainty, rather than treating a changed set as sufficient evidence of a quality change.

**中文:** (2)  **区分种子一致性与效用差异。**参照预算变化引起的集合变化，对传播量的影响并不相同。配对评估能够量化差值及其不确定性，而不是将集合发生变化直接视为质量变化的充分证据。

<a id="S043"></a>
**Source:** 英文 p.2；manuscript.tex:43；S043

**Original:** (3)  **Qualifying transfer and computational savings.** Degree-based pools reproduce all 15 highest-budget external trajectories at lower measured selection cost, whereas the earlier PageRank agreement does not transfer uniformly. Candidate coverage and the included timing stages delimit these comparisons.

**中文:** (3)  **明确结果迁移与计算节省的适用范围。**基于度的候选池以更低的实测选择成本复现了外部研究最高预算下的全部 15 条轨迹，而先前观察到的 PageRank 一致性并未在所有外部网络上保持。候选覆盖率与计时所包含的阶段限定了这些比较的含义。

<a id="S051"></a>
**Source:** 英文 p.2；manuscript.tex:51；S051

**Original:** Related work

**中文:** 相关工作

<a id="S052"></a>
**Source:** 英文 p.2；manuscript.tex:52；S052

**Original:** Kempe et al. connect expected spread under the independent-cascade model to greedy seed selection [1]. CELF reduces repeated marginal evaluations using objective structure [2]; StaticGreedy reuses fixed realizations [3]; IMM provides a sampling-based solver with approximation guarantees [4]. In our comparison, full and restricted selection share one finite-world objective and use exhaustive per-round enumeration; only seed eligibility differs.

**中文:** Kempe 等将独立级联模型下的期望传播量与贪心种子选择联系起来 [1]。CELF 利用目标函数的结构减少重复的边际收益评价 [2]；StaticGreedy 复用固定的随机实现 [3]；IMM 提供具有近似保证的采样式求解器 [4]。在本文比较中，全候选选择和受限选择共享同一个有限世界目标，并在每轮进行完整枚举；二者仅在种子候选资格上不同。

<a id="S054"></a>
**Source:** 英文 p.2；manuscript.tex:54；S054

**Original:** Rui et al. estimate node influence from multiple neighbourhood levels [5], while Fan et al. use discrete Harris hawks optimization [6]. Ko et al.'s MONSTOR+ predicts spread on unseen graphs [7]. These approaches change how nodes or seed sets are assessed. Here, a ranking only determines seed eligibility; the simulator and greedy rule remain the same across candidate pools.

**中文:** Rui 等利用多层邻域信息估计节点影响力 [5]，Fan 等采用离散哈里斯鹰优化 [6]。Ko 等的 MONSTOR+ 预测未见图上的传播量 [7]。这些方法改变了节点或种子集合的评价方式。本文的排名仅决定种子候选资格；不同候选池使用相同的模拟器和贪心规则。

<a id="S056"></a>
**Source:** 英文 p.3；manuscript.tex:56；S056

**Original:** Li et al. survey influence-maximization methods [8], and Arora et al. benchmark algorithms with attention to model and implementation scope [9]. Yanchenko et al. review temporal-network formulations [10]; Aral and Dhillon study empirical influence models [11]. Our experiments use observed topologies with simulated diffusion. Online Resource 1 compares the cited studies' stated focus with our analysis of reference budget, ranking precision, coverage, seed agreement, independent spread and cost.

**中文:** Li 等综述了影响力最大化方法 [8]；Arora 等在算法基准比较中关注模型与实现的适用范围 [9]。Yanchenko 等综述了时间网络上的问题形式 [10]；Aral 和 Dhillon 研究了实证影响力模型 [11]。本文在观测拓扑上模拟传播。在线补充材料 1 将所引研究明确提出的研究重点，与本文对参照预算、排名精度、覆盖率、种子一致性、独立传播量和成本的分析进行比较。

<a id="S058"></a>
**Source:** 英文 p.3；manuscript.tex:58；S058

**Original:** These lines of work address different questions: solver studies reduce the cost of selecting seeds under a specified objective, ranking methods estimate which vertices are influential, and benchmarking compares the quality and cost of implemented methods. Our question concerns the interpretation of a restricted method's gap to a sampled full-candidate reference. Spread and runtime at a single configuration do not identify whether that gap changes because the reference uses different selection worlds or because ranking tolerance changes which vertices are eligible. We vary these choices separately and retain paired seed and spread comparisons. This makes the dependence of a quality judgment on the reference and the pool explicit, without treating either as an exact expected-spread optimum.

**中文:** 这些研究方向回答不同的问题：求解器研究降低给定目标下的种子选择成本，排名方法估计哪些节点具有影响力，基准研究则比较已实现方法的质量和成本。本文关注的是，如何解释受限方法与采样全候选参照之间的差值。仅报告单一配置下的传播量和运行时间，无法辨别差值的变化究竟来自参照使用了不同的选择世界，还是排名容差改变了候选节点资格。我们分别改变这两项选择，并保留种子与传播量的配对比较。这样能够明确质量判断对参照与候选池的依赖，而不将任一选择结果视为期望传播量的精确最优解。

<a id="S060"></a>
**Source:** PDF 页码未自动定位；以源码行号为准；manuscript.tex:60；S060

**Original:** Methods

**中文:** 研究方法

<a id="S061"></a>
**Source:** 英文 p.3；manuscript.tex:61；S061

**Original:** Paired selection at controlled resolutions

**中文:** 控制分辨率的配对选择

<a id="S062"></a>
**Source:** PDF 页码未自动定位；以源码行号为准；manuscript.tex:62；S062

**Original:** Let $G=(V,E)$ be a directed propagation graph and $S$ a seed set of size $k$. Under the independent-cascade model, each newly activated vertex gets one opportunity to activate each inactive outgoing neighbour with probability $p$. Propagation stops after $h$ rounds. For a random world $\omega$, let $f_h(S;\omega)$ denote total activated vertices, including seeds. Greedy selection uses the sampled objective

**中文:** 设 $G=(V,E)$ 为有向传播图，$S$ 为大小为 $k$ 的种子集合。在独立级联模型中，每个新激活节点都有一次机会，以概率 $p$ 激活其每个尚未激活的出向邻居。传播在 $h$ 轮后停止。对随机世界 $\omega$，用 $f_h(S;\omega)$ 表示包括种子在内的激活节点总数。贪心选择采用以下采样目标：

<a id="S064"></a>
**Source:** PDF 页码未自动定位；以源码行号为准；manuscript.tex:64；S064

**Original:** \widehat\sigma_W(S)=\frac{1}{W}\sum_{w=1}^{W}f_h(S;\omega_w).

**中文:** \widehat\sigma_W(S)=\frac{1}{W}\sum_{w=1}^{W}f_h(S;\omega_w).

<a id="S066"></a>
**Source:** 英文 p.4；manuscript.tex:66；S066

**Original:** At each round, greedy selection enumerates every unselected eligible vertex and chooses the largest integer total $W\widehat\sigma_W$. Ties resolve by lexicographic original node ID. Full selection uses $C=V$; restricted selection uses $C\subseteq V$. All vertices remain in the propagation graph. A path identifies one computational repetition and its random-world families. A condition fixes the graph, path and experimental settings; an arm specifies a seed-eligibility rule within that condition. Full and restricted arms share $G$, the world prefix, $k$ and the tie rule.

**中文:** 每轮贪心选择枚举所有尚未选中的合资格节点，并选择整数总分 $W\widehat\sigma_W$ 最大的节点。同分时按原始节点 ID 的字典序处理。全候选选择采用 $C=V$，受限选择采用 $C\subseteq V$；所有节点均保留在传播图中。一条随机路径标识一次计算重复及其随机世界族；一个实验条件固定图、路径和实验设置；一个实验臂规定该条件下的种子候选资格规则。全候选臂和受限臂共享 $G$、世界前缀、$k$ 与同分规则。

<a id="S068"></a>
**Source:** 英文 p.4；manuscript.tex:68；S068

**Original:** We vary reference resolution through $W$ and ranking resolution through the numerical tolerance $\tau$. Degree ranks distinct outgoing neighbours. PageRank uses the unweighted directed topology and NetworkX 3.5 defaults: damping .85, uniform personalization and dangling-node treatment, tolerance $10^{-6}$ and at most 100 iterations [12]. Its stopping criterion is successive-vector $L_1$ change below $n\tau$, where $n=|V|$. Scores are sorted decreasingly with lexical ties. A top-$q$ pool contains $q=\min(n,4k)$ or $q=\lceil .05n\rceil$ vertices. Historical weighted degree counts outgoing observed events where such counts exist. Three random pools are independently generated within each graph/path and fixed across budgets and coupling controls.

**中文:** 我们通过 $W$ 改变参照分辨率，通过数值容差 $\tau$ 改变排名分辨率。Degree 按不同出向邻居的数量排名。PageRank 使用无权有向拓扑及 NetworkX 3.5 的默认设置：阻尼系数 .85、均匀的个性化分布和悬挂节点处理、容差 $10^{-6}$，最多迭代 100 次 [12]。其停止条件为相邻两次向量的 $L_1$ 变化小于 $n\tau$，其中 $n=|V|$。分数按降序排列，同分时采用字典序。前 $q$ 名候选池包含 $q=\min(n,4k)$ 或 $q=\lceil .05n\rceil$ 个节点。在存在事件计数的网络中，历史加权度统计观测到的出向事件数。每个图与路径组合独立生成三个随机候选池，并在不同预算与耦合对照之间保持不变。

<a id="S070"></a>
**Source:** 英文 p.4；manuscript.tex:70；S070

**Original:** World coupling and independent evaluation

**中文:** 世界耦合与独立评估

<a id="S071"></a>
**Source:** 英文 p.4；manuscript.tex:71；S071

**Original:** Primary selection worlds share draws indexed by world, propagation step, source and target. This coupling preserves the independent-cascade marginal law for each fixed seed set, but the realized finite-world objective can be nonmonotone. For example, initially activating an intermediate vertex can move its outgoing attempt to an earlier step with a different sampled outcome. Online Resource 1 gives the explicit counterexample. A separate fixed-edge control draws once per edge and world; its finite objective is coverage by vertices reachable within $h$ edges and is monotone and submodular. Both implementations use exhaustive enumeration.

**中文:** 主要选择世界共享以世界、传播步、源节点和目标节点为索引的随机抽样。对每个固定种子集合，这种耦合保留独立级联模型的边际分布，但实现后的有限世界目标可能不具单调性。例如，将某个中间节点设为初始激活节点，可能使其出向激活尝试提前到具有不同采样结果的传播步。在线补充材料 1 给出了明确反例。另设的固定边对照对每条边在每个世界中只抽样一次，其有限目标是各世界中沿至多 $h$ 条边可达的节点覆盖量，具有单调性和次模性。两种实现均使用完整枚举。

<a id="S073"></a>
**Source:** 英文 p.4；manuscript.tex:73；S073

**Original:** Selection-world identifiers form nested prefixes as $W$ increases. Evaluation uses a disjoint family of $M=10,000$ worlds per path, shared by all seed sets and held fixed across budgets. Keys also separate graphs, paths and candidate-pool randomization. Coupling schemes are compared within their own full references.

**中文:** 随着 $W$ 增大，选择世界标识符形成嵌套前缀。每条路径的评估使用独立且不与选择世界重叠的 $M=10,000$ 个世界；所有种子集合共享这些评估世界，并在不同预算下保持不变。随机键也将不同图、路径以及候选池随机化彼此区分。每种耦合方式下的方法均与该耦合方式自身的全候选参照比较。

<a id="S075"></a>
**Source:** PDF 页码未自动定位；以源码行号为准；manuscript.tex:75；S075

**Original:** For restricted seeds $S_C$ and full-reference seeds $S_F$, define the paired evaluation difference on world $i$ as $d_i=f_h(S_C;\eta_i)-f_h(S_F;\eta_i)$. The utility gap in Fig. 1 is

**中文:** 对受限种子 $S_C$ 和全候选参照种子 $S_F$，定义世界 $i$ 上的配对评估差为 $d_i=f_h(S_C;\eta_i)-f_h(S_F;\eta_i)$。图 1 中的效用差为

<a id="S077"></a>
**Source:** PDF 页码未自动定位；以源码行号为准；manuscript.tex:77；S077

**Original:** \widehat\Delta=\frac{1}{M}\sum_{i=1}^{M}d_i,

**中文:** \widehat\Delta=\frac{1}{M}\sum_{i=1}^{M}d_i,

<a id="S078"></a>
**Source:** PDF 页码未自动定位；以源码行号为准；manuscript.tex:78；S078

**Original:** \qquad \operatorname{SE}_{\rm MC}=s(d_i)/\sqrt M.

**中文:** \qquad \operatorname{SE}_{\rm MC}=s(d_i)/\sqrt M.

<a id="S080"></a>
**Source:** PDF 页码未自动定位；以源码行号为准；manuscript.tex:80；S080

**Original:** The interval $\widehat\Delta\pm1.96\operatorname{SE}_{\rm MC}$ describes conditional Monte Carlo uncertainty for fixed selected sets. Across-path standard deviation describes variation across computational paths, including finite evaluation noise. The three random-pool evaluation vectors are averaged within each path before either calculation.

**中文:** 区间 $\widehat\Delta\pm1.96\operatorname{SE}_{\rm MC}$ 描述给定已选集合时的条件蒙特卡洛不确定性。路径间标准差描述不同计算路径之间的变异，其中也包含有限评估带来的噪声。在进行上述任一种计算之前，先在每条路径内对三个随机池的评估向量取平均。

<a id="S082"></a>
**Source:** 英文 p.5；manuscript.tex:82；S082

**Original:** We report ordered-trajectory agreement, final-set agreement, Jaccard similarity and the first divergent round. Incremental spread subtracts $k$ from total spread; percentage incremental loss is $-100\widehat\Delta/(\widehat\sigma_{\rm full}-k)$. Negative loss favors the restricted set. All observed denominators are positive.

**中文:** 我们报告有序轨迹一致性、最终集合一致性、Jaccard 相似度和首次分歧轮次。增量传播量为总传播量减去 $k$；增量传播损失百分比为 $-100\widehat\Delta/(\widehat\sigma_{\rm full}-k)$。负损失表示受限集合的评估结果更高。所有观测分母均为正。

<a id="S084"></a>
**Source:** 英文 p.5；manuscript.tex:84；S084

**Original:** The frozen primary tests compare Degree-4k, PageRank-4k and the within-path random mean with full selection at $W=1280$. Each comparison uses a two-sided exact sign test; Holm correction covers the three comparisons within each graph. Zero differences are excluded from the tests and reported separately. Coverage, coupling and transition analyses are descriptive; worlds and paths are not independent network samples.

**中文:** 冻结的主要检验在 $W=1280$ 时，将 Degree-4k、PageRank-4k 和路径内随机池均值分别与全候选选择比较。每项比较采用双侧精确符号检验；Holm 校正在每个图内覆盖这三项比较。零差值不纳入检验，并单独报告。覆盖率、耦合和预算转移分析均为描述性分析；世界与路径都不是独立的网络样本。

<a id="S086"></a>
**Source:** 英文 p.5；manuscript.tex:86；S086

**Original:** Implementation and cost measurement

**中文:** 实现与成本测量

<a id="S087"></a>
**Source:** 英文 p.5；manuscript.tex:87；S087

**Original:** The Numba implementation stores candidate IDs, selected sequences, integer round totals and per-world evaluation values. The archived audits reconstruct argmax and tie decisions, replay external full-reference scores and evaluations, and compare predetermined worlds with a separate scalar oracle. Identical seed sets must yield identical evaluation vectors. Online Resource 1 details the audit coverage, the retrospective correction to raw-file hash enforcement and the executable reproduction procedure.（脚注：OpenAI Codex assisted code, verification, analysis, figure generation and drafting. The authors reviewed the outputs and take responsibility for the manuscript.）

**中文:** Numba 实现保存候选节点 ID、已选序列、各轮整数总分和逐世界评估值。归档审计重建最大值选择及同分决策，回放外部全候选参照的分数和评估，并在预先指定的世界上与独立的标量参考实现比较。相同种子集合必须产生相同的评估向量。在线补充材料 1 详细说明审计覆盖范围、对原始文件哈希强制校验缺口的回溯修正，以及可执行的复现流程。（脚注：OpenAI Codex 协助代码、核验、分析、图形生成与文稿起草。作者审核了输出，并对稿件承担责任。）

<a id="S089"></a>
**Source:** 英文 p.5；manuscript.tex:89；S089

**Original:** Selection time includes greedy search and lexical candidate sorting, but excludes graph preparation, world generation and evaluation. We also estimate the cost of a warm-process run that includes independent evaluation. Separately measured parsing, graph construction and one method's ranking/pool generation are added to the recorded costs of selection-world preparation, seed selection, evaluation-world preparation and evaluation. Setup uses the median of five repeats. These assembled estimates exclude imports, just-in-time compilation, downloads and output writing.

**中文:** 选择时间包括贪心搜索和候选节点的字典序排序，但不包括图准备、世界生成和评估。我们还估计包含独立评估的暖进程运行成本：将单独测量的解析、建图以及一个方法的排名和候选池生成成本，与记录的选择世界准备、种子选择、评估世界准备及评估成本相加。准备阶段采用五次重复的中位数。上述分项拼接估计不包括导入、即时编译、下载和输出写入。

<a id="S091"></a>
**Source:** 英文 p.5；manuscript.tex:91；S091

**Original:** Five randomized repeats at path 1101 and $W=320$ assess timing variability. Cost comparisons use this implementation's exhaustive full-candidate reference. Results at the tighter PageRank tolerance are used only for quality sensitivity; the timing comparison uses default tolerance.

**中文:** 在路径 1101、$W=320$ 下进行五次随机顺序的重复计时，以评估时间变异。成本比较采用本实现逐轮完整枚举的全候选参照。较紧 PageRank 容差的结果仅用于质量敏感性分析；计时比较采用默认容差。

<a id="S093"></a>
**Source:** 英文 p.5；manuscript.tex:93；S093

**Original:** Experimental setup

**中文:** 实验设置

<a id="S094"></a>
**Source:** 英文 p.5；manuscript.tex:94；S094

**Original:** Networks and preprocessing

**中文:** 网络与预处理

<a id="S095"></a>
**Source:** 英文 p.5；manuscript.tex:95；S095

**Original:** We selected three larger SNAP topologies before inspecting seed sets or utilities [13]: CollegeMsg communication, ca-GrQc collaboration and wiki-Vote voting. Table 1 reports the processed sizes and candidate coverage. All retained components are included.

**中文:** 我们在查看种子集合或效用之前，选定三个较大的 SNAP 拓扑 [13]：CollegeMsg 通信网络、ca-GrQc 合作网络和 wiki-Vote 投票网络。表 1 给出处理后的规模与候选覆盖率。所有保留的连通分量均纳入实验。

<a id="T001"></a>
### 表 1
**Source:** 英文 p.6；置于 S095 后

![T001](D:/校创/基于GNN的关键用户识别/submission/computing-external-validation-20261015/chinese-translation-20261027/assets/T001.png)

<a id="CT001"></a>
**Source:** 英文 p.6；manuscript.tex:97；CT001

**Original:** Processed external networks and candidate coverage. Arcs are directed propagation arcs; the 5% pool contains $\lceil .05n\rceil$ vertices.

**中文:** 处理后的外部网络与候选覆盖率。弧指有向传播弧；5% 候选池包含 $\lceil .05n\rceil$ 个节点。

<a id="T001DATA"></a>
**Source:** 英文 p.6；manuscript.tex:98；T001DATA

**Original:** | Graph | Nodes | Arcs | 4k fraction | 5% pool |
| — | — | — | — | — |
| CollegeMsg | 1,438 | 13,397 | 1.391% | 72 |
| ca-GrQc | 5,241 | 28,968 | 0.382% | 263 |
| wiki-Vote | 7,115 | 103,689 | 0.281% | 356 |

**中文:** | 网络 | 节点数 | 弧数 | 4k 占比 | 5% 池大小 |
| — | — | — | — | — |
| CollegeMsg | 1,438 | 13,397 | 1.391% | 72 |
| ca-GrQc | 5,241 | 28,968 | 0.382% | 263 |
| wiki-Vote | 7,115 | 103,689 | 0.281% | 356 |

<a id="S109"></a>
**Source:** 英文 p.5；manuscript.tex:109；S109

**Original:** CollegeMsg records timestamped sender-to-receiver messages [14]. We sort its 58,911 distinct timestamps, retain the first $\lfloor .65\times58,911\rfloor=38,292$ complete groups, and include events through Unix timestamp 1085640224. Removing self-messages leaves 38,939 events. Repeated sender–receiver pairs contribute to historical outgoing-message counts but form a single propagation arc. Propagation uses uniform $p$, independently of the message count; later events are not used for candidate construction or treated as observed influence outcomes.

**中文:** CollegeMsg 记录带时间戳的发送者至接收者消息 [14]。我们对 58,911 个不同时间戳排序，保留前 $\lfloor .65\times58,911\rfloor=38,292$ 个完整时间戳组，纳入截至 Unix 时间戳 1085640224 的事件。去除发给自身的消息后，剩余 38,939 个事件。重复的发送者–接收者对计入历史出向消息数，但在传播图中仅形成一条弧。传播采用统一概率 $p$，不依赖消息次数；后续事件既不用于构建候选池，也不作为观测到的影响力传播结果。

<a id="S111"></a>
**Source:** 英文 p.6；manuscript.tex:111；S111

**Original:** ca-GrQc links coauthors [15]; we remove self-loops, deduplicate pairs and create reciprocal arcs. Vertices are collected after loop removal, excluding the self-loop-only vertex 12295 and giving 5,241 rather than the source page's 5,242 vertices. wiki-Vote arcs run from voter to votee [16, 17]; self-loops and duplicate arcs are removed without reversing the remaining arcs. Outgoing diffusion on these arcs is a simulation assumption. The two static datasets supply neither event counts nor observed cascades and receive no historical-weighted ranking. We retain all weak components: 2 in CollegeMsg, 354 in ca-GrQc and 24 in wiki-Vote. No largest-component extraction or node subsampling is applied. Original IDs are stored as strings and sorted lexicographically for graph indexing, ranking ties and greedy ties. Raw-file and processed-graph hashes are supplied in the data manifest.

**中文:** ca-GrQc 的边连接共同作者 [15]；我们去除自环、对节点对去重，并建立双向弧。在移除自环后收集节点，因此排除了仅出现在自环中的节点 12295，得到 5,241 个节点，而非数据源页面的 5,242 个。wiki-Vote 的弧从投票者指向被投票者 [16, 17]；去除自环与重复弧，不反转其余弧的方向。沿这些弧进行出向传播是模拟假设。两个静态数据集既不提供事件次数，也不提供观测级联，因此不采用历史加权排名。我们保留所有弱连通分量：CollegeMsg 为 2 个，ca-GrQc 为 354 个，wiki-Vote 为 24 个。不提取最大连通分量，也不对子节点集采样。原始 ID 以字符串保存，图索引、排名同分和贪心同分均按字典序处理。数据清单提供原始文件和预处理图的哈希。

<a id="S113"></a>
**Source:** 英文 p.6；manuscript.tex:113；S113

**Original:** Historical context comes from four contact-derived graphs with 75–402 vertices, constructed from workplace, conference and rural Kenya data [18, 19, 20, 21]. We distinguish four evidence layers: the initial 42-condition study; a 520-condition historical extension; the external matrix below; and its post-hoc PageRank precision control. The extension uses ten paths per contact graph and adds a budget scan up to $W=5120$, four local changes to $(p,h)$, fixed-edge sampling, a larger seed budget, and two fixed 2,000-node synthetic instances [22, 23]. The parameter controls reuse the default budget-scan conditions rather than counting them again. Online Resource 1 reports the complete coverage and descriptive results separately; these small-graph controls do not enlarge the external network sample.

**中文:** 历史背景来自四个含 75–402 个节点的接触图，分别由工作场所、会议和肯尼亚乡村接触数据构建 [18, 19, 20, 21]。我们区分四层证据：最初的 42 条件研究、520 条件历史扩展、下述外部实验矩阵，以及事后 PageRank 精度控制。历史扩展在每张接触图上使用十条路径，增加了最高至 $W=5120$ 的预算扫描、四种对 $(p,h)$ 的局部调整、固定边采样、更大的种子预算，以及两个固定的 2,000 节点合成实例 [22, 23]。参数对照复用预算扫描中的默认条件，不重复计数。在线补充材料 1 单独报告完整实验覆盖与描述性结果；这些小图对照不会增加外部网络样本量。

<a id="S115"></a>
**Source:** 英文 p.6；manuscript.tex:115；S115

**Original:** Primary matrix and numerical sensitivity control

**中文:** 主要实验矩阵与数值敏感性控制

<a id="S116"></a>
**Source:** 英文 p.6；manuscript.tex:116；S116

**Original:** Table 2 specifies the external design. Here, conditions vary graph, path, selection budget and coupling; the remaining propagation settings are fixed. Three graphs, five paths and three selection budgets define 45 primary conditions. Nine fixed-edge conditions provide a matched coupling control. Every condition includes full selection, Degree-4k, PageRank-4k, Degree-5%, PageRank-5% and three random-4k pools; CollegeMsg also includes Weighted-4k and Weighted-5% pools based on outgoing message counts. This gives 18 conditions per graph, with 10 arms for CollegeMsg and 8 for each static graph: $18(10+8+8)=468$ arms. All 54 conditions were completed and retained.

**中文:** 表 2 给出外部研究设计。实验条件改变图、路径、选择预算与耦合方式，其余传播设置固定。三个图、五条路径和三个选择预算构成 45 个主要条件，另有九个固定边条件作为匹配的耦合对照。每个条件均包括全候选选择、Degree-4k、PageRank-4k、Degree-5%、PageRank-5% 以及三个 random-4k 池；CollegeMsg 还包括按出向消息次数构建的 Weighted-4k 和 Weighted-5% 池。因此，每个图有 18 个条件，CollegeMsg 每条件有 10 个实验臂，两个静态图各有 8 个，共 $18(10+8+8)=468$ 个实验臂。全部 54 个条件均已完成并保留。

<a id="T002"></a>
### 表 2
**Source:** 英文 p.7；置于 S116 后

![T002](D:/校创/基于GNN的关键用户识别/submission/computing-external-validation-20261015/chinese-translation-20261027/assets/T002.png)

<a id="CT002"></a>
**Source:** 英文 p.7；manuscript.tex:119；CT002

**Original:** External experiment settings. Paths identify computational repetitions, not additional networks.

**中文:** 外部实验设置。路径标识计算重复，不代表新增网络。

<a id="T002DATA"></a>
**Source:** 英文 p.7；manuscript.tex:120；T002DATA

**Original:** | Quantity | Setting |
| — | — |
| Diffusion | Independent cascade; uniform $p=0.01$; horizon $h=3$; $k=5$ seeds |
| Primary selection | Step coupling; $W\in\{80,320,1280\}$; paths 1101–1105 |
| Independent evaluation | $M=10,000$ worlds per graph/path/coupling, shared across arms and budgets |
| Candidate sizes | $4k=20$; alternatively $\lceil0.05n\rceil$; three random pools of size 20 per path |
| Coupling control | Fixed edge; $W=320$; paths 1101–1103 |
| Default PageRank | Damping 0.85; $\tau=10^{-6}$; at most 100 iterations |
| Precision control | $\tau=10^{-12}$; at most 1,000 iterations; pool stability checked at $10^{-14}$ |
| Repeated timing | Five repeats per arm; path 1101, $W=320$; randomized arm order |

**中文:** | 项目 | 设置 |
| — | — |
| 传播 | 独立级联；统一 $p=0.01$；传播期限 $h=3$；$k=5$ 个种子 |
| 主要选择 | 按步耦合；$W\in\{80,320,1280\}$；路径 1101–1105 |
| 独立评估 | 每个图/路径/耦合组合使用 $M=10,000$ 个世界；实验臂与预算之间共享 |
| 候选池大小 | $4k=20$；另一设置为 $\lceil0.05n\rceil$；每条路径有三个大小为 20 的随机池 |
| 耦合对照 | 固定边；$W=320$；路径 1101–1103 |
| 默认 PageRank | 阻尼系数 0.85；$\tau=10^{-6}$；最多迭代 100 次 |
| 精度控制 | $\tau=10^{-12}$；最多迭代 1,000 次；在 $10^{-14}$ 下检查池成员稳定性 |
| 重复计时 | 每个实验臂重复五次；路径 1101，$W=320$；实验臂顺序随机化 |

<a id="S136"></a>
**Source:** 英文 p.7；manuscript.tex:136；S136

**Original:** The seed budget and propagation setting are held constant to isolate reference budget, eligibility and coupling. They define a finite-horizon simulation regime rather than parameters fitted to observed cascades. Resource-only preflight measured full selection at $W=80,320$ and evaluation at $M=1000$; it recorded no selected sets or utilities. Those measurements informed the feasible main matrix, whose evaluation budget is $M=10,000$. The protocol was locally frozen before main outcomes were inspected. No network or condition was excluded on the basis of its results. The external budget ceiling is 1280; the historical 5120-world study is reported separately.

**中文:** 种子预算和传播设置保持固定，以单独考察参照预算、候选资格和耦合方式。它们定义了一个有限传播期限的模拟情境，而不是根据观测级联拟合得到的参数。仅测资源的预检测量了 $W=80,320$ 下的全候选选择和 $M=1000$ 下的评估，未记录已选集合或效用。这些测量用于确定可执行的主要矩阵，其评估预算为 $M=10,000$。协议在查看主要结果前于本地冻结。没有因结果而排除任何网络或条件。外部研究的预算上限为 1280；历史 5120 世界研究单独报告。

<a id="S138"></a>
**Source:** 英文 p.7；manuscript.tex:138；S138

**Original:** A post-hoc numerical control tightens PageRank tolerance to $10^{-12}$ with at most 1,000 iterations. Its two protocols were frozen before the corresponding new utility outputs: the first covers $W=1280$, and the second adds $W=80,320$. Together they contain 45 conditions and 90 restricted arms, reusing the original five paths, full references and evaluation worlds. All pools at the tighter tolerance agree in membership with those at $10^{-14}$. This checks candidate membership stability at the tested tolerances, not exact convergence of the PageRank vector. The paired sensitivity analysis adds no independent paths and leaves the primary test family unchanged.

**中文:** 事后数值控制将 PageRank 容差收紧至 $10^{-12}$，最多迭代 1,000 次。两份协议均在查看各自新增效用输出前冻结：第一份覆盖 $W=1280$，第二份增加 $W=80,320$。合计包含 45 个条件、90 个受限实验臂，复用原五条路径、全候选参照与评估世界。所有较紧容差下的候选池都与 $10^{-14}$ 下的池成员一致。这检验的是所测容差下的候选成员稳定性，而不是 PageRank 向量的精确收敛。该配对敏感性分析不增加独立路径，也不改变主要检验族。

<a id="S140"></a>
**Source:** 英文 p.7；manuscript.tex:140；S140

**Original:** Randomization, execution and reproducibility

**中文:** 随机化、执行与可复现性

<a id="S141"></a>
**Source:** 英文 p.7；manuscript.tex:141；S141

**Original:** World identifiers separate graphs, paths and selection/evaluation families. Increasing $W$ appends selection worlds without resampling the prefix; the selection and evaluation identifiers are checked for overlap. Random candidate pools use a separate randomization key and remain fixed across budgets and coupling controls. Online Resource 1, ``Executable reproduction procedure'', specifies the exact hash keys, identifier construction and hash-to-draw mapping.

**中文:** 世界标识符区分不同图、路径以及选择/评估世界族。增大 $W$ 只追加选择世界，不重新采样已有前缀；同时检查选择与评估标识符是否重叠。随机候选池采用单独的随机化键，并在不同预算和耦合对照间保持固定。在线补充材料 1 的“可执行复现流程”给出了精确哈希键、标识符构造和哈希值到随机抽样的映射。

<a id="S143"></a>
**Source:** 英文 p.7；manuscript.tex:143；S143

**Original:** Experiments use one serial worker on Windows with Python 3.13.0, NumPy 2.3.3, NetworkX 3.5, SciPy 1.16.1 and Numba 0.68.0. BLAS/OpenMP threads are constrained to one. JIT warm-up precedes timed conditions; randomized arm order reduces systematic order effects. The recorded host has 20 physical CPU cores and approximately 32 GiB RAM, although the implementation does not use all cores. Timing and process peak-memory records accompany each condition. Exact wall times are machine-dependent.

**中文:** 实验在 Windows 上使用单个串行工作进程，环境包括 Python 3.13.0、NumPy 2.3.3、NetworkX 3.5、SciPy 1.16.1 和 Numba 0.68.0。BLAS/OpenMP 线程数均限制为一。计时条件执行前完成 JIT 预热；随机化实验臂顺序以减少系统性顺序效应。记录的主机具有 20 个物理 CPU 核心和约 32 GiB 内存，但实现并未使用全部核心。每个条件都保存计时和进程峰值内存记录。实际墙钟时间取决于机器。

<a id="S145"></a>
**Source:** 英文 p.8；manuscript.tex:145；S145

**Original:** The archived reproduction record covers stored-result audits, analysis regeneration and representative external-condition reruns; it does not document a complete rerun of all historical and external conditions. Online Resource 1 and REPRODUCE.md specify the input checks, replay modes, output isolation and acceptance criteria. Historical summaries are recomputed from their separate saved outputs.

**中文:** 归档复现记录覆盖保存结果审计、分析再生成，以及代表性外部条件重跑；它不代表对全部历史和外部条件的完整重跑。在线补充材料 1 和 REPRODUCE.md 说明输入检查、回放模式、输出隔离及验收标准。历史汇总从各自单独保存的输出重新计算。

<a id="S147"></a>
**Source:** PDF 页码未自动定位；以源码行号为准；manuscript.tex:147；S147

**Original:** Results

**中文:** 研究结果

<a id="S148"></a>
**Source:** 英文 p.8；manuscript.tex:148；S148

**Original:** The ca-GrQc budget reversal depends on ranking precision

**中文:** ca-GrQc 的预算反转依赖排名精度

<a id="S149"></a>
**Source:** 英文 p.8；manuscript.tex:149；S149

**Original:** Figure 2 compares PageRank at default and tighter tolerances at each selection budget, using the same full reference and independent evaluation worlds. On ca-GrQc, default PageRank-4k changes from a mean incremental-spread gain of 5.61% at $W=80$ to losses of 2.53% and 5.07% at 320 and 1280. Tightening tolerance exchanges two of 20 candidates and yields gains of 11.25%, 2.96% and 0.54%. The mean gain-to-loss reversal therefore disappears in this numerical control.

**中文:** 图 2 在每个选择预算下，使用相同全候选参照和独立评估世界，比较默认与较紧容差的 PageRank。在 ca-GrQc 上，默认 PageRank-4k 从 $W=80$ 时平均增量传播量高于参照 5.61%，转为在 320 和 1280 时分别低于参照 2.53% 和 5.07%。收紧容差替换了 20 个候选节点中的两个，此时三个预算下的增益分别为 11.25%、2.96% 和 0.54%。因此，平均增益转损失的反转在该数值控制下消失。

<a id="F002"></a>
### 图 2
**Source:** 英文 p.9；置于 S149 后

![F002](D:/校创/基于GNN的关键用户识别/submission/computing-external-validation-20261015/chinese-translation-20261027/assets/F002.png)

<a id="C002"></a>
**Source:** 英文 p.9；manuscript.tex:156；C002

**Original:** Budget and ranking precision have distinct effects on candidate-restriction quality. Points are mean incremental losses over five paired paths; bars are path standard deviations. The plotted labels Default and Strict denote tolerances $10^{-6}$ and $10^{-12}$; candidate membership is unchanged between $10^{-12}$ and $10^{-14}$. Negative loss favors the restricted set. The ca-GrQc default reversal disappears with the tighter PageRank tolerance, while the directed-network losses persist. This is a post-hoc paired sensitivity analysis.

**中文:** 预算与排名精度对候选限制质量产生不同影响。点为五条配对路径的平均增量传播损失，误差线为路径标准差。图中的 Default 和 Strict 分别表示容差 $10^{-6}$ 和 $10^{-12}$；候选成员在 $10^{-12}$ 与 $10^{-14}$ 间保持不变。负损失表示受限集合的评估结果更高。收紧 PageRank 容差后，ca-GrQc 的默认反转消失，而有向网络上的损失仍存在。这是事后配对敏感性分析。

<a id="S151"></a>
**Source:** 英文 p.8；manuscript.tex:151；S151

**Original:** Budget still changes selections with the pool formed at the tighter tolerance, whose membership agrees at tolerances $10^{-12}$ and $10^{-14}$. Its selected sets change on 3/5 paths from 80 to 320 and 2/5 from 320 to 1280. At $W=1280$, PageRank-4k at the tighter tolerance minus the same-budget full reference has a mean paired difference of $+0.02608$ nodes, with path values from $-0.0408$ to $+0.1789$ and path standard deviation 0.09155. The positive mean includes both gains and losses across paths; it does not by itself establish a utility advantage. Conditional Monte Carlo uncertainty is reported separately in the per-path supplementary results.

**中文:** 在较紧容差构建的候选池下，预算仍会改变选择结果；该池在容差 $10^{-12}$ 和 $10^{-14}$ 下的成员一致。预算从 80 增至 320 时，3/5 条路径的所选集合发生变化；从 320 增至 1280 时，2/5 条路径发生变化。在 $W=1280$ 时，较紧容差的 PageRank-4k 相对同预算全候选参照的平均配对差为 $+0.02608$ 个节点，路径值范围为 $-0.0408$ 至 $+0.1789$，路径标准差为 0.09155。正均值同时包含不同路径上的增益和损失，不能单独据此确立效用优势。补充材料的逐路径结果另行报告条件蒙特卡洛不确定性。

<a id="S153"></a>
**Source:** 英文 p.8；manuscript.tex:153；S153

**Original:** CollegeMsg's default- and tighter-tolerance pools, seeds and evaluations are identical at every budget, retaining losses of 9.33%, 8.52% and 9.01%. On wiki-Vote, one candidate changes, but losses at the tighter tolerance remain 74.05%, 74.05% and 73.96%. Precision sensitivity is therefore network-specific: it changes the ca-GrQc interpretation while preserving the two directed-network losses.

**中文:** CollegeMsg 在每个预算下的默认容差与较紧容差候选池、种子和评估结果均相同，损失仍为 9.33%、8.52% 和 9.01%。wiki-Vote 有一个候选节点发生变化，但较紧容差下的损失仍为 74.05%、74.05% 和 73.96%。因此，精度敏感性依网络而异：它改变了对 ca-GrQc 的解释，但两个有向网络上的损失仍保留。

<a id="S159"></a>
**Source:** 英文 p.8；manuscript.tex:159；S159

**Original:** Reference-set changes have different utility consequences

**中文:** 参照集合变化具有不同的效用后果

<a id="S160"></a>
**Source:** 英文 p.8；manuscript.tex:160；S160

**Original:** Figure 3 compares reference-set changes with independent utility changes. From $W=320$ to 1280, all five ca-GrQc sets change, but their mean gain is 0.12720 nodes; individual differences range from $-0.0266$ to $+0.2411$. CollegeMsg changes one set and gains 0.05336 nodes averaged across all five paths. wiki-Vote changes no final sets and has exactly zero paired gain, although some ordered sequences change.

**中文:** 图 3 比较参照集合变化与独立效用变化。预算从 $W=320$ 增至 1280 时，ca-GrQc 的全部五个集合均变化，平均增益为 0.12720 个节点；各路径差值为 $-0.0266$ 至 $+0.2411$。CollegeMsg 有一个集合变化，在全部五条路径上平均增加 0.05336 个节点。wiki-Vote 的最终集合均未变化，配对增益严格为零，尽管部分有序选择序列发生了变化。

<a id="F003"></a>
### 图 3
**Source:** 英文 p.10；置于 S160 后

![F003](D:/校创/基于GNN的关键用户识别/submission/computing-external-validation-20261015/chinese-translation-20261027/assets/F003.png)

<a id="C003"></a>
**Source:** 英文 p.10；manuscript.tex:167；C003

**Original:** Reference-set changes and independent spread changes. Filled circles denote changed final sets; hollow squares denote unchanged sets. Paths 1101–1105 run from left to right within each graph. Bars are unadjusted 95% conditional Monte Carlo intervals from 10,000 paired worlds. Panel-specific vertical scales reveal small changes; the intervals condition on selected sets and do not describe variation across networks.

**中文:** 参照集合变化与独立传播量变化。实心圆表示最终集合变化，空心方块表示集合未变。每个图内，路径 1101–1105 从左至右排列。误差线为根据 10,000 个配对世界计算的未经校正的 95% 条件蒙特卡洛区间。各面板采用不同纵轴尺度，以显示较小的变化；区间以已选集合为条件，不描述网络间变异。

<a id="S162"></a>
**Source:** 英文 p.8；manuscript.tex:162；S162

**Original:** Of the six changed sets, four have positive pointwise 95% conditional Monte Carlo intervals; two ca-GrQc intervals include zero. The nine unchanged sets have identical evaluation vectors.

**中文:** 六个发生变化的集合中，四个的逐点 95% 条件蒙特卡洛区间完全位于零以上；ca-GrQc 的另两个区间包含零。九个未变化集合的评估向量完全相同。

<a id="S164"></a>
**Source:** 英文 p.8；manuscript.tex:164；S164

**Original:** In the historical step-coupled comparison from $W=1280$ to 5120, 16/40 sets changed while the mean high-minus-low budget gain was 0.01111 nodes (range $-0.0383$ to $+0.1180$). Historical fixed-edge references also change: from $W=320$ to 1280, 29/40 sets changed, with mean high-minus-low budget gain 0.061845 nodes (range $-0.0110$ to $+0.2572$). Each transition uses a shared evaluation family within its own coupling. Because the two budget intervals differ, their mean gains do not estimate a coupling effect.

**中文:** 在历史按步耦合比较中，预算从 $W=1280$ 增至 5120 时，16/40 个集合发生变化，高预算减低预算的平均增益为 0.01111 个节点，范围为 $-0.0383$ 至 $+0.1180$。历史固定边参照也发生变化：从 $W=320$ 增至 1280 时，29/40 个集合变化，平均高减低预算增益为 0.061845 个节点，范围为 $-0.0110$ 至 $+0.2572$。每项预算转移均在自身耦合方式内使用共享的评估世界族。由于两项比较的预算区间不同，不能用其平均增益估计耦合效应。

<a id="S170"></a>
**Source:** 英文 p.9；manuscript.tex:170；S170

**Original:** External scope, candidate coverage and propagation direction

**中文:** 外部适用范围、候选覆盖率与传播方向

<a id="S171"></a>
**Source:** PDF 页码未自动定位；以源码行号为准；manuscript.tex:171；S171

**Original:** At $W=1280$, Degree-4k reproduces every full-candidate reference trajectory across the three external graphs using only 20 candidates (Table 3). Default PageRank-4k matches none and incurs mean incremental losses of 5.07%, 9.01% and 73.01% on ca-GrQc, CollegeMsg and wiki-Vote. The historical extension showed much broader PageRank agreement: 40/40 trajectories at $W=5120$, compared with 39/40 for degree. The external results therefore limit transfer of the contact-graph ranking result.

**中文:** 在 $W=1280$ 时，Degree-4k 仅用 20 个候选节点便复现了三个外部图上的全部全候选参照轨迹（表 3）。默认 PageRank-4k 未匹配任何轨迹，在 ca-GrQc、CollegeMsg 和 wiki-Vote 上的平均增量传播损失分别为 5.07%、9.01% 和 73.01%。历史扩展中的 PageRank 一致性明显更广：在 $W=5120$ 时匹配 40/40 条轨迹，而基于度的方法为 39/40。外部结果因此限定了接触图排名结果的迁移范围。

<a id="T003"></a>
### 表 3
**Source:** 英文 p.11；置于 S171 后

![T003](D:/校创/基于GNN的关键用户识别/submission/computing-external-validation-20261015/chinese-translation-20261027/assets/T003.png)

<a id="CT003"></a>
**Source:** 英文 p.11；primary_table.tex:2；CT003

**Original:** External results at $W=1280$ (five paths). Degree-4k and PageRank-4k (PR) use 20-node pools; PR uses default tolerance. Full incremental spread is total spread minus $k=5$. PR gap is restricted minus full mean spread; loss is relative to full incremental spread. Degree agreement counts identical ordered trajectories.

**中文:** 外部网络在 $W=1280$ 下的结果（五条路径）。Degree-4k 与 PageRank-4k（PR）使用 20 节点候选池；PR 使用默认容差。全候选参照增量传播量为总传播量减去 $k=5$。PR 差值为受限选择减全候选选择的平均传播量；损失以全候选参照的增量传播量为基准。一致性计数指完全相同的有序轨迹。

<a id="T003DATA"></a>
**Source:** 英文 p.11；primary_table.tex:3；T003DATA

**Original:** | Graph | Full incremental spread (nodes) | PR gap (nodes) | PR loss (%) | Degree agreement |
| — | — | — | — | — |
| ca-GrQc | 4.934 | -0.25082 | 5.07 | 5/5 |
| CollegeMsg | 10.072 | -0.90780 | 9.01 | 5/5 |
| wiki-Vote | 55.736 | -40.69334 | 73.01 | 5/5 |

**中文:** | 网络 | 全候选增量 传播量（节点） | PR 差值 （节点） | PR 损失 （%） | Degree 一致性 |
| — | — | — | — | — |
| ca-GrQc | 4.934 | -0.25082 | 5.07 | 5/5 |
| CollegeMsg | 10.072 | -0.90780 | 9.01 | 5/5 |
| wiki-Vote | 55.736 | -40.69334 | 73.01 | 5/5 |

<a id="S174"></a>
**Source:** 英文 p.9；manuscript.tex:174；S174

**Original:** For the primary comparisons at the highest tested external budget, every default PageRank-4k and within-path random-4k mean difference from full selection is negative, giving unadjusted sign-test $p=.0625$ and within-graph Holm $p=.1875$. Degree-4k differences from full selection are exactly zero. Five paths limit the minimum two-sided sign-test value to .0625; these results establish neither statistical equivalence nor absence of loss. The paired effect sizes, sensitivity controls and complete test results are reported in Online Resource 1.

**中文:** 在最高测试外部预算下的主要比较中，默认 PageRank-4k 和路径内 random-4k 均值相对全候选选择的每个差值都为负，未经校正的符号检验 $p=.0625$，图内 Holm 校正后 $p=.1875$。Degree-4k 与全候选选择的差值严格为零。五条路径使双侧符号检验可达到的最小值限制在 .0625；这些结果既不确立统计等效，也不证明没有损失。在线补充材料 1 报告配对效应量、敏感性控制和完整检验结果。

<a id="S176"></a>
**Source:** 英文 p.10；manuscript.tex:176；S176

**Original:** Increasing the default PageRank pool to 5% reproduces all five ca-GrQc references at $W=1280$ and reduces CollegeMsg loss from 9.01% to 4.28%. On wiki-Vote, loss falls from 73.01% to 24.28%, remaining above one fifth of full-reference incremental spread. Historical-weighted CollegeMsg pools similarly improve from a mean difference of $-0.25224$ nodes at 4k to exact reference reproduction at 5%. Coverage helps in these comparisons, but its effect differs across networks.

**中文:** 将默认 PageRank 池增至 5% 后，在 $W=1280$ 时复现了 ca-GrQc 的全部五个参照，并将 CollegeMsg 的损失从 9.01% 降至 4.28%。wiki-Vote 的损失从 73.01% 降至 24.28%，仍高于全候选参照增量传播量的五分之一。CollegeMsg 的历史加权池也由 4k 下平均差 $-0.25224$ 个节点，改善为 5% 下完全复现参照。在这些比较中，增加覆盖率有所帮助，但作用随网络而异。

<a id="S178"></a>
**Source:** 英文 p.10；manuscript.tex:178；S178

**Original:** On wiki-Vote, the default PageRank top 20 have mean in-degree 249.75 and out-degree 56.2; the degree top 20 have mean in-degree 70.3 and out-degree 489.25. The PageRank-4k pool contains none of the five full-reference seeds on any $W=1280$ path, and its 5% pool contains only one. These observations are consistent with a mismatch between incoming importance and outgoing propagation. Direction was not experimentally reversed, so the diagnostic does not isolate a causal mechanism. The seed-level illustration and complete coverage comparisons appear in Online Resource 1.

**中文:** 在 wiki-Vote 上，默认 PageRank 前 20 个节点的平均入度为 249.75、出度为 56.2；按度排序的前 20 个节点平均入度为 70.3、出度为 489.25。在任一 $W=1280$ 路径上，PageRank-4k 池均不包含五个全候选参照种子中的任何一个，而其 5% 池仅包含一个。这些观察与“入链重要性和出向传播之间不匹配”的解释一致。实验未进行方向反转，因此该诊断不能单独确定因果机制。在线补充材料 1 给出种子层面的图示和完整覆盖率比较。

<a id="S180"></a>
**Source:** 英文 p.11；manuscript.tex:180；S180

**Original:** Computational savings depend on quality and timing scope

**中文:** 计算节省取决于质量与计时范围

<a id="S181"></a>
**Source:** 英文 p.11；manuscript.tex:181；S181

**Original:** Degree-4k reduces measured selection time by 98.40–99.67% relative to this implementation's full-candidate reference at $W=1280$, while reproducing all its trajectories (Table 4). Including setup, both world families and independent evaluation gives assembled cost savings of 86.59–96.26%.

**中文:** 在 $W=1280$ 时，相对本实现的全候选参照，Degree-4k 将实测选择时间降低 98.40–99.67%，同时复现全部参照轨迹（表 4）。计入准备阶段、两类世界准备及独立评估后，分项拼接的成本节省为 86.59–96.26%。

<a id="T004"></a>
### 表 4
**Source:** 英文 p.11；置于 S181 后

![T004](D:/校创/基于GNN的关键用户识别/submission/computing-external-validation-20261015/chinese-translation-20261027/assets/T004.png)

<a id="CT004"></a>
**Source:** 英文 p.11；cost_table.tex:2；CT004

**Original:** Degree-4k cost at $W=1280$, averaged over five paths. Full and Degree columns give measured selection time. The final column estimates savings including setup, preparation of selection and evaluation worlds, selection and independent evaluation. These assembled warm-process costs exclude imports, JIT compilation, downloads and output writing; they are not direct end-to-end timings.

**中文:** Degree-4k 在 $W=1280$ 下的成本，取五条路径平均。Full 与 Degree 列为实测选择时间。最后一列估计包含准备阶段、选择及评估世界准备、种子选择和独立评估的成本节省。这些暖进程拼接成本排除导入、JIT 编译、下载和输出写入，并非直接端到端计时。

<a id="T004DATA"></a>
**Source:** 英文 p.11；cost_table.tex:3；T004DATA

**Original:** | Graph | Full (s) | Degree (s) | Selection saving (%) | Saving including evaluation (%) |
| — | — | — | — | — |
| ca-GrQc | 23.53 | 0.109 | 99.54 | 92.77 |
| CollegeMsg | 5.89 | 0.094 | 98.40 | 86.59 |
| wiki-Vote | 158.94 | 0.520 | 99.67 | 96.26 |

**中文:** | 网络 | Full（s） | Degree（s） | 选择阶段 节省（%） | 含评估成本 节省（%） |
| — | — | — | — | — |
| ca-GrQc | 23.53 | 0.109 | 99.54 | 92.77 |
| CollegeMsg | 5.89 | 0.094 | 98.40 | 86.59 |
| wiki-Vote | 158.94 | 0.520 | 99.67 | 96.26 |

<a id="S184"></a>
**Source:** PDF 页码未自动定位；以源码行号为准；manuscript.tex:184；S184

**Original:** At $W=1280$, Degree-4k meets the zero point-estimate loss threshold relative to full selection on every path. Default PageRank-4k meets 10% on ca-GrQc and CollegeMsg, but fails 20% on every wiki-Vote path. None of the random-pool path means meets 20%. Online Resource 1 reports all six frozen thresholds (0, 1, 2.5, 5, 10 and 20%) and their cost estimates; these are descriptive criteria rather than application-validated tolerances.

**中文:** 在 $W=1280$ 时，Degree-4k 在每条路径上均满足相对全候选选择的零点估计损失阈值。默认 PageRank-4k 在 ca-GrQc 和 CollegeMsg 上满足 10% 阈值，但在 wiki-Vote 的每条路径上均未满足 20% 阈值。所有随机池的路径均值都未满足 20% 阈值。在线补充材料 1 报告全部六个冻结阈值（0、1、2.5、5、10 和 20%）及相应成本估计；它们是描述性标准，而非经实际应用验证的可容忍损失。

<a id="S186"></a>
**Source:** 英文 p.11；manuscript.tex:186；S186

**Original:** Parameter sensitivity and coupling controls

**中文:** 传播参数敏感性与耦合对照

<a id="S188"></a>
**Source:** 英文 p.11；manuscript.tex:188；S188

**Original:** In the external fixed-edge control at $W=320$, default PageRank-4k minus the fixed-edge full reference has mean spread differences of $-0.16240$, $-0.93417$ and $-40.57597$ nodes on ca-GrQc, CollegeMsg and wiki-Vote. Degree-4k reproduces 1/3, 3/3 and 3/3 corresponding trajectories. The PageRank losses persist under this control, while some reference-agreement outcomes change. Complete control paths and repeated timings are supplied in Online Resource 1.

**中文:** 在 $W=320$ 的外部固定边对照中，默认 PageRank-4k 减去固定边全候选参照的平均传播差值，在 ca-GrQc、CollegeMsg 和 wiki-Vote 上分别为 $-0.16240$、$-0.93417$ 和 $-40.57597$ 个节点。Degree-4k 分别复现 1/3、3/3 和 3/3 条对应轨迹。PageRank 损失在此对照下仍存在，而部分参照一致性结果发生变化。在线补充材料 1 提供完整对照路径和重复计时。

<a id="S190"></a>
**Source:** 英文 p.12；manuscript.tex:190；S190

**Original:** Across the 160 historical nondefault parameter conditions at $W=320$, Degree-4k and PageRank-4k reproduce 117 and 132 full-reference trajectories, respectively. Weighted-4k minus full selection has 117 negative and 43 positive paired spread differences. These are descriptive counts of repeated computations, not independent success trials.

**中文:** 在 $W=320$ 的 160 个历史非默认参数条件中，Degree-4k 和 PageRank-4k 分别复现 117 和 132 条全候选参照轨迹。Weighted-4k 减去全候选选择的配对传播差值中，117 个为负，43 个为正。这些是对重复计算的描述性计数，不是独立成功试验。

<a id="S192"></a>
**Source:** 英文 p.12；manuscript.tex:192；S192

**Original:** Under historical fixed-edge sampling at $W=1280$, Degree-4k and PageRank-4k match 38/40 and 40/40 trajectories of the fixed-edge full reference, while Weighted-4k matches 5/40. The supplementary tables retain every graph and setting. These contact-graph controls do not test the joint effect of the tighter PageRank tolerance and fixed-edge sampling on the external graphs.

**中文:** 在 $W=1280$ 的历史固定边采样下，Degree-4k 和 PageRank-4k 分别匹配固定边全候选参照的 38/40 和 40/40 条轨迹，Weighted-4k 匹配 5/40。补充表保留每个图和设置。这些接触图对照没有检验外部图上较紧 PageRank 容差与固定边采样的联合效应。

<a id="S195"></a>
**Source:** 英文 p.12；manuscript.tex:195；S195

**Original:** Discussion

**中文:** 讨论

<a id="S196"></a>
**Source:** 英文 p.12；manuscript.tex:196；S196

**Original:** Interpreting budget and tolerance effects

**中文:** 预算与容差效应的解释

<a id="S197"></a>
**Source:** 英文 p.12；manuscript.tex:197；S197

**Original:** The ca-GrQc control changes how the budget comparison should be read. The default mean gain-to-loss pattern cannot be attributed to reference budget independently of the PageRank stopping tolerance: exchanging two pool members removes that pattern, although increasing $W$ still changes selected sets. Pool truncation turns a numerical ranking change into a change in seed eligibility. Agreement of pool membership at $10^{-12}$ and $10^{-14}$ narrows this diagnostic to the tested cutoffs; it does not certify an exact ranking. The persistent CollegeMsg and wiki-Vote losses show why the tolerance check must be interpreted separately for each graph.

**中文:** ca-GrQc 对照改变了对预算比较的理解。默认设置下平均增益转损失的模式，不能被归因于独立于 PageRank 停止容差的参照预算效应：替换两个候选池成员便使该模式消失，尽管增大 $W$ 仍会改变已选集合。候选池截断将数值排名变化转化为种子资格变化。池成员在 $10^{-12}$ 与 $10^{-14}$ 下保持一致，将该诊断限定在所测截断点，并不认证精确排名。CollegeMsg 和 wiki-Vote 持续存在的损失说明，容差检验必须按图分别解释。

<a id="S199"></a>
**Source:** 英文 p.12；manuscript.tex:199；S199

**Original:** Interpreting seed agreement and spread differences

**中文:** 种子一致性与传播差值的解释

<a id="S200"></a>
**Source:** 英文 p.12；manuscript.tex:200；S200

**Original:** Ordered trajectories, final sets and spread answer different questions. A different selection order can end at the same set, which produces the same evaluation vector under the shared simulator and evaluation worlds. If sets differ, paired evaluation determines the sign, magnitude and conditional uncertainty of the spread difference. The external ca-GrQc mean change of 0.12720 nodes and the historical step-coupled mean change of 0.01111 nodes quantify distinct budget transitions; neither supplies an application-specific equivalence margin. Reporting the three outcomes separately avoids treating every reference change as a utility improvement. Candidate fraction, ranking tolerance and reference budget specify which comparison those outcomes describe.

**中文:** 有序轨迹、最终集合和传播量回答不同问题。不同的选择顺序可能得到相同集合，而在共享模拟器和评估世界下，相同集合产生相同评估向量。若集合不同，则需用配对评估确定传播差值的符号、大小及条件不确定性。外部 ca-GrQc 的平均变化 0.12720 个节点，以及历史按步耦合的平均变化 0.01111 个节点，量化的是不同预算转移；两者均未提供面向具体应用的等效界值。分别报告三种结果，可以避免将每次参照变化都视为效用改善。候选占比、排名容差和参照预算则规定这些结果所描述的具体比较。

<a id="S202"></a>
**Source:** 英文 p.13；manuscript.tex:202；S202

**Original:** Scope and limitations

**中文:** 适用范围与局限

<a id="S203"></a>
**Source:** 英文 p.13；manuscript.tex:203；S203

**Original:** The external evidence covers three selected networks under $k=5$, $p=.01$, $h=3$ and selection budgets up to 1280. Historical contact graphs also probe $p$, $h$, coupling and $k$, but their local parameter changes are not a full factorial design and do not establish sensitivity on the larger directed graphs. At historical $k=20$, the 4k pool contains all 75 Kenya vertices and 80/91 invs2013 vertices; Kenya agreement is a full-pool identity check. The historical fixed-edge controls also do not validate the external tighter-tolerance PageRank results under fixed-edge sampling.

**中文:** 外部证据覆盖三个选定网络，设置为 $k=5$、$p=.01$、$h=3$，选择预算最高为 1280。历史接触图还考察了 $p$、$h$、耦合方式和 $k$，但其局部参数调整不是全因子设计，也不能据此确立较大有向图上的敏感性。在历史 $k=20$ 设置下，4k 池包含 Kenya 的全部 75 个节点和 invs2013 的 80/91 个节点；Kenya 的一致性属于全候选池恒等性检查。历史固定边对照同样没有验证外部较紧容差 PageRank 结果在固定边采样下是否成立。

<a id="S205"></a>
**Source:** 英文 p.13；manuscript.tex:205；S205

**Original:** Paths repeat computations on a fixed graph, and the networks are not a probability sample of social systems. Each synthetic control uses one fixed graph, so repeated paths do not add graph instances. Conditional Monte Carlo uncertainty concerns fixed selected sets; path variation concerns the computational repetitions, not cross-network generalization. Observed relations provide topology, not calibrated causal diffusion. The direction diagnostic is consistent with the measured wiki-Vote loss but does not establish a causal explanation.

**中文:** 路径是在固定图上重复计算，所用网络也不是社会系统的概率样本。每个合成对照只使用一个固定图，因此，重复路径不会增加图实例数。条件蒙特卡洛不确定性针对固定已选集合；路径变异针对计算重复，而非跨网络泛化。观测关系提供拓扑，并不等于经过校准的因果传播。方向诊断与 wiki-Vote 的实测损失一致，但不能确立因果解释。

<a id="S207"></a>
**Source:** 英文 p.13；manuscript.tex:207；S207

**Original:** Reference agreement establishes neither optimality with respect to expected spread nor convergence as the world budget increases. The cost comparison uses this implementation's exhaustive full-candidate reference, not CELF or IMM. Measured selection costs and assembled costs including independent evaluation answer different deployment questions. The latter exclude cold-start overhead and are not direct end-to-end timings; tighter-tolerance PageRank is assessed for quality only.

**中文:** 参照一致性既不证明相对于期望传播量的最优性，也不证明随世界预算增加而收敛。成本比较采用本实现逐轮完整枚举的全候选参照，而非 CELF 或 IMM。实测选择成本和包含独立评估的拼接成本回答不同的部署问题。后者排除冷启动开销，并非直接端到端计时；较紧容差的 PageRank 仅用于质量评价。

<a id="S209"></a>
**Source:** 英文 p.13；manuscript.tex:209；S209

**Original:** Conclusion

**中文:** 结论

<a id="S210"></a>
**Source:** 英文 p.13；manuscript.tex:210；S210

**Original:** On ca-GrQc, PageRank with a tighter convergence tolerance removes the default mean quality reversal across budgets without eliminating seed changes. Across the three external graphs, Degree-4k reproduces the tested $W=1280$ reference trajectories at lower measured selection cost, while PageRank's results vary with tolerance, coverage and topology. Under the shared simulator and evaluation worlds, identical final sets yield identical spread evaluations; different sets require paired evaluation to quantify the utility difference. Ordered-trajectory agreement, final-set agreement and spread should therefore be reported separately. Agreement with the finite reference does not establish optimality with respect to expected spread or performance beyond the tested settings.

**中文:** 在 ca-GrQc 上，收紧 PageRank 收敛容差，使默认设置下跨预算的平均质量反转消失，但并未消除种子变化。在三个外部图上，Degree-4k 以更低的实测选择成本复现了测试中 $W=1280$ 的参照轨迹，而 PageRank 的结果随容差、覆盖率和拓扑变化。共享模拟器与评估世界时，相同最终集合产生相同传播评估；不同集合则需要配对评估，以量化其效用差。因此，应分别报告有序轨迹一致性、最终集合一致性和传播量。与有限参照一致，并不确立相对于期望传播量的最优性，也不能保证测试设置之外的表现。

<a id="S212"></a>
**Source:** 英文 p.13；manuscript.tex:212；S212

**Original:** Supplementary information. Online Resource 1 contains the external result matrix, precision and direction diagnostics, loss–cost curves, and separate historical coverage, parameter, coupling and secondary-control tables with reproducibility details.

**中文:** 补充信息。在线补充材料 1 包含外部结果矩阵、精度与方向诊断、损失–成本曲线，以及单独列出的历史覆盖率、参数、耦合与次要对照表，并提供复现细节。

<a id="S213"></a>
**Source:** 英文 p.13；manuscript.tex:213；S213

**Original:** Statements and Declarations

**中文:** 声明

<a id="S214"></a>
**Source:** 英文 p.13；manuscript.tex:214；S214

**Original:** Funding. This work was supported by a provincial undergraduate innovation and entrepreneurship training project.

**中文:** 基金支持。本研究获得省级大学生创新创业训练项目支持。

<a id="S215"></a>
**Source:** 英文 p.14；manuscript.tex:215；S215

**Original:** Competing interests. The authors declare that they have no competing interests.

**中文:** 利益冲突。作者声明不存在利益冲突。

<a id="S216"></a>
**Source:** 英文 p.14；manuscript.tex:216；S216

**Original:** Author contributions.} Jiayue Sun: conceptualization, methodology, software, validation, formal analysis, investigation, data curation, visualization, and writing—original draft. Binbin Yong: supervision, methodology, project administration, and writing—review and editing. Junjie An: software, data curation, and writing—review and editing. Tianyu Bo: validation, visualization, and writing—review and editing. Shuai Li: formal analysis, validation, and writing—review and editing. All authors read and approved the final manuscript and agreed to its submission to \textit{Computing.

**中文:** 作者贡献。}Jiayue Sun：概念构思、方法设计、软件、验证、正式分析、研究实施、数据整理、可视化及初稿写作。Binbin Yong：指导、方法设计、项目管理及审阅与修改。Junjie An：软件、数据整理及审阅与修改。Tianyu Bo：验证、可视化及审阅与修改。Shuai Li：正式分析、验证及审阅与修改。全体作者已阅读并批准最终稿件，同意向 \textit{Computing 投稿。

<a id="S217"></a>
**Source:** 英文 p.14；manuscript.tex:217；S217

**Original:** Data availability. The third-party datasets are available from the cited providers under their access terms and are not redistributed. Source records, expected SHA-256 hashes and preprocessing instructions accompany the submission.

**中文:** 数据可用性。第三方数据集可按照其访问条款从所引数据提供方获取，本文不再分发这些数据。投稿材料附有来源记录、预期 SHA-256 哈希和预处理说明。

<a id="S218"></a>
**Source:** 英文 p.14；manuscript.tex:218；S218

**Original:** Code availability. Frozen source snapshots, configurations, validators, analysis scripts, condition-level outputs and figure-source tables are supplied with the submission for editorial and peer-review access.

**中文:** 代码可用性。冻结源码快照、配置、验证程序、分析脚本、逐条件输出和图表源数据随投稿材料提供，供编辑及同行评审查阅。

## 参考文献（保留原始书目信息）

<a id="R001"></a>
**Source:** 英文 p.14；references.tex:2；R001

**Original:** Kempe D, Kleinberg J, Tardos É (2003) Maximizing the spread of influence through a social network. In: ACM SIGKDD, pp 137–146. \url{https://doi.org/10.1145/956750.956769}

**中文:** Kempe D, Kleinberg J, Tardos É (2003) Maximizing the spread of influence through a social network. In: ACM SIGKDD, pp 137–146. \url{https://doi.org/10.1145/956750.956769}

<a id="R002"></a>
**Source:** 英文 p.14；references.tex:4；R002

**Original:** Leskovec J, Krause A, Guestrin C, Faloutsos C, VanBriesen J, Glance N (2007) Cost-effective outbreak detection in networks. In: KDD, pp 420–429. \url{https://doi.org/10.1145/1281192.1281239}

**中文:** Leskovec J, Krause A, Guestrin C, Faloutsos C, VanBriesen J, Glance N (2007) Cost-effective outbreak detection in networks. In: KDD, pp 420–429. \url{https://doi.org/10.1145/1281192.1281239}

<a id="R003"></a>
**Source:** 英文 p.14；references.tex:6；R003

**Original:** Cheng S, Shen H, Huang J, Zhang G, Cheng X (2013) StaticGreedy: solving the scalability-accuracy dilemma in influence maximization. In: CIKM, pp 509–518. \url{https://doi.org/10.1145/2505515.2505541}

**中文:** Cheng S, Shen H, Huang J, Zhang G, Cheng X (2013) StaticGreedy: solving the scalability-accuracy dilemma in influence maximization. In: CIKM, pp 509–518. \url{https://doi.org/10.1145/2505515.2505541}

<a id="R004"></a>
**Source:** 英文 p.14；references.tex:8；R004

**Original:** Tang Y, Shi Y, Xiao X (2015) Influence maximization in near-linear time: a martingale approach. In: ACM SIGMOD, pp 1539–1554. \url{https://doi.org/10.1145/2723372.2723734}

**中文:** Tang Y, Shi Y, Xiao X (2015) Influence maximization in near-linear time: a martingale approach. In: ACM SIGMOD, pp 1539–1554. \url{https://doi.org/10.1145/2723372.2723734}

<a id="R005"></a>
**Source:** 英文 p.14；references.tex:10；R005

**Original:** Rui X, Yang X, Fan J, Wang Z (2020) A neighbour scale fixed approach for influence maximization in social networks. Computing 102:427–449. \url{https://doi.org/10.1007/s00607-019-00778-5}

**中文:** Rui X, Yang X, Fan J, Wang Z (2020) A neighbour scale fixed approach for influence maximization in social networks. Computing 102:427–449. \url{https://doi.org/10.1007/s00607-019-00778-5}

<a id="R006"></a>
**Source:** 英文 p.14；references.tex:12；R006

**Original:** Fan C, Wang Z, Zhang J, Zhao J, Rui X (2024) Influence maximization in social networks based on discrete harris hawks optimization algorithm. Computing 106:327–351. \url{https://doi.org/10.1007/s00607-023-01207-4}

**中文:** Fan C, Wang Z, Zhang J, Zhao J, Rui X (2024) Influence maximization in social networks based on discrete harris hawks optimization algorithm. Computing 106:327–351. \url{https://doi.org/10.1007/s00607-023-01207-4}

<a id="R007"></a>
**Source:** 英文 p.14；references.tex:14；R007

**Original:** Ko J, Kim S, Lee K, et al. (2025) Inductive influence estimation and maximization over unseen social networks under two diffusion models. Data Mining and Knowledge Discovery 39:55. \url{https://doi.org/10.1007/s10618-025-01137-z}

**中文:** Ko J, Kim S, Lee K, et al. (2025) Inductive influence estimation and maximization over unseen social networks under two diffusion models. Data Mining and Knowledge Discovery 39:55. \url{https://doi.org/10.1007/s10618-025-01137-z}

<a id="R008"></a>
**Source:** 英文 p.14；references.tex:16；R008

**Original:** Li Y, Fan J, Wang Y, Tan K-L (2018) Influence maximization on social graphs: a survey. IEEE Transactions on Knowledge and Data Engineering 30:1852–1872. \url{https://doi.org/10.1109/TKDE.2018.2807843}

**中文:** Li Y, Fan J, Wang Y, Tan K-L (2018) Influence maximization on social graphs: a survey. IEEE Transactions on Knowledge and Data Engineering 30:1852–1872. \url{https://doi.org/10.1109/TKDE.2018.2807843}

<a id="R009"></a>
**Source:** 英文 p.15；references.tex:18；R009

**Original:** Arora A, Galhotra S, Ranu S (2017) Debunking the myths of influence maximization: an in-depth benchmarking study. In: SIGMOD, pp 651–666. \url{https://doi.org/10.1145/3035918.3035924}

**中文:** Arora A, Galhotra S, Ranu S (2017) Debunking the myths of influence maximization: an in-depth benchmarking study. In: SIGMOD, pp 651–666. \url{https://doi.org/10.1145/3035918.3035924}

<a id="R010"></a>
**Source:** 英文 p.15；references.tex:20；R010

**Original:** Yanchenko E, Murata T, Holme P (2024) Influence maximization on temporal networks: a review. Applied Network Science 9:16. \url{https://doi.org/10.1007/s41109-024-00625-3}

**中文:** Yanchenko E, Murata T, Holme P (2024) Influence maximization on temporal networks: a review. Applied Network Science 9:16. \url{https://doi.org/10.1007/s41109-024-00625-3}

<a id="R011"></a>
**Source:** 英文 p.15；references.tex:22；R011

**Original:** Aral S, Dhillon PS (2018) Social influence maximization under empirical influence models. Nature Human Behaviour 2:375–382. \url{https://doi.org/10.1038/s41562-018-0346-z}

**中文:** Aral S, Dhillon PS (2018) Social influence maximization under empirical influence models. Nature Human Behaviour 2:375–382. \url{https://doi.org/10.1038/s41562-018-0346-z}

<a id="R012"></a>
**Source:** 英文 p.15；references.tex:24；R012

**Original:** NetworkX developers (2025) PageRank, NetworkX 3.5 documentation. \url{https://networkx.org/documentation/networkx-3.5/reference/algorithms/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html}. Accessed 15 October 2026

**中文:** NetworkX developers (2025) PageRank, NetworkX 3.5 documentation. \url{https://networkx.org/documentation/networkx-3.5/reference/algorithms/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html}. Accessed 15 October 2026

<a id="R013"></a>
**Source:** 英文 p.15；references.tex:26；R013

**Original:** Leskovec J, Krevl A (2014) SNAP datasets: Stanford large network dataset collection. \url{https://snap.stanford.edu/data}. Accessed 15 October 2026

**中文:** Leskovec J, Krevl A (2014) SNAP datasets: Stanford large network dataset collection. \url{https://snap.stanford.edu/data}. Accessed 15 October 2026

<a id="R014"></a>
**Source:** 英文 p.15；references.tex:28；R014

**Original:** Panzarasa P, Opsahl T, Carley KM (2009) Patterns and dynamics of users' behavior and interaction: Network analysis of an online community. Journal of the American Society for Information Science and Technology 60:911–932. \url{https://doi.org/10.1002/asi.21015}

**中文:** Panzarasa P, Opsahl T, Carley KM (2009) Patterns and dynamics of users' behavior and interaction: Network analysis of an online community. Journal of the American Society for Information Science and Technology 60:911–932. \url{https://doi.org/10.1002/asi.21015}

<a id="R015"></a>
**Source:** 英文 p.15；references.tex:30；R015

**Original:** Leskovec J, Kleinberg J, Faloutsos C (2007) Graph evolution: densification and shrinking diameters. ACM Transactions on Knowledge Discovery from Data 1(1):2. \url{https://doi.org/10.1145/1217299.1217301}

**中文:** Leskovec J, Kleinberg J, Faloutsos C (2007) Graph evolution: densification and shrinking diameters. ACM Transactions on Knowledge Discovery from Data 1(1):2. \url{https://doi.org/10.1145/1217299.1217301}

<a id="R016"></a>
**Source:** 英文 p.15；references.tex:32；R016

**Original:** Leskovec J, Huttenlocher D, Kleinberg J (2010) Signed networks in social media. In: CHI, pp 1361–1370. \url{https://doi.org/10.1145/1753326.1753532}

**中文:** Leskovec J, Huttenlocher D, Kleinberg J (2010) Signed networks in social media. In: CHI, pp 1361–1370. \url{https://doi.org/10.1145/1753326.1753532}

<a id="R017"></a>
**Source:** 英文 p.15；references.tex:34；R017

**Original:** Leskovec J, Huttenlocher D, Kleinberg J (2010) Predicting positive and negative links in online social networks. In: WWW, pp 641–650. \url{https://doi.org/10.1145/1772690.1772756}

**中文:** Leskovec J, Huttenlocher D, Kleinberg J (2010) Predicting positive and negative links in online social networks. In: WWW, pp 641–650. \url{https://doi.org/10.1145/1772690.1772756}

<a id="R018"></a>
**Source:** 英文 p.15；references.tex:36；R018

**Original:** Génois M, Vestergaard CL, Fournet J, Panisson A, Bonmarin I, Barrat A (2015) Data on face-to-face contacts in an office building suggest a low-cost vaccination strategy based on community linkers. Network Science 3:326–347. \url{https://doi.org/10.1017/nws.2015.10}

**中文:** Génois M, Vestergaard CL, Fournet J, Panisson A, Bonmarin I, Barrat A (2015) Data on face-to-face contacts in an office building suggest a low-cost vaccination strategy based on community linkers. Network Science 3:326–347. \url{https://doi.org/10.1017/nws.2015.10}

<a id="R019"></a>
**Source:** 英文 p.15；references.tex:38；R019

**Original:** Génois M, Barrat A (2018) Can co-location be used as a proxy for face-to-face contacts? EPJ Data Science 7:11. \url{https://doi.org/10.1140/epjds/s13688-018-0140-1}

**中文:** Génois M, Barrat A (2018) Can co-location be used as a proxy for face-to-face contacts? EPJ Data Science 7:11. \url{https://doi.org/10.1140/epjds/s13688-018-0140-1}

<a id="R020"></a>
**Source:** 英文 p.15；references.tex:40；R020

**Original:** Cattuto C, Van den Broeck W, Barrat A, Colizza V, Pinton J-F, Vespignani A (2010) Dynamics of person-to-person interactions from distributed RFID sensor networks. PLoS ONE 5:e11596. \url{https://doi.org/10.1371/journal.pone.0011596}

**中文:** Cattuto C, Van den Broeck W, Barrat A, Colizza V, Pinton J-F, Vespignani A (2010) Dynamics of person-to-person interactions from distributed RFID sensor networks. PLoS ONE 5:e11596. \url{https://doi.org/10.1371/journal.pone.0011596}

<a id="R021"></a>
**Source:** 英文 p.15；references.tex:42；R021

**Original:** Kiti MC, Tizzoni M, Kinyanjui TM, et al. (2016) Quantifying social contacts in a household setting of rural Kenya using wearable proximity sensors. EPJ Data Science 5:21. \url{https://doi.org/10.1140/epjds/s13688-016-0084-2}

**中文:** Kiti MC, Tizzoni M, Kinyanjui TM, et al. (2016) Quantifying social contacts in a household setting of rural Kenya using wearable proximity sensors. EPJ Data Science 5:21. \url{https://doi.org/10.1140/epjds/s13688-016-0084-2}

<a id="R022"></a>
**Source:** 英文 p.15；references.tex:44；R022

**Original:** Barabasi A-L, Albert R (1999) Emergence of scaling in random networks. Science 286:509–512. \url{https://doi.org/10.1126/science.286.5439.509}

**中文:** Barabasi A-L, Albert R (1999) Emergence of scaling in random networks. Science 286:509–512. \url{https://doi.org/10.1126/science.286.5439.509}

<a id="R023"></a>
**Source:** 英文 p.15；references.tex:46；R023

**Original:** Holland PW, Laskey KB, Leinhardt S (1983) Stochastic blockmodels: first steps. Social Networks 5:109–137. \url{https://doi.org/10.1016/0378-8733(83)90021-7}

**中文:** Holland PW, Laskey KB, Leinhardt S (1983) Stochastic blockmodels: first steps. Social Networks 5:109–137. \url{https://doi.org/10.1016/0378-8733(83)90021-7}

## 术语表

| English | 中文 | 含义与边界 |
|---|---|---|
| candidate restriction | 候选限制 | 只限制种子资格，不改变传播图 |
| full-candidate reference | 全候选参照 | 所有节点均有种子资格的有限世界贪心结果 |
| selection worlds | 选择世界 | 用于选择种子的随机传播实现 |
| evaluation worlds | 评估世界 | 独立于选择、用于评估已选集合的随机传播实现 |
| path | 随机路径／计算路径 | 一次计算重复的标识，不指图上的传播路径 |
| condition | 实验条件 | 固定图、路径及实验设置 |
| arm | 实验臂 | 给定条件下的一种候选资格规则 |
| incremental spread | 增量传播量 | 总传播量减去种子数 k |
| paired spread difference | 配对传播差值 | 受限选择减全候选选择；预算转移另按高减低计算 |
| percentage incremental loss | 增量传播损失百分比 | 负值表示受限集合的点估计更高 |
| step coupling | 按步耦合 | 随机抽样索引包含传播步 |
| fixed-edge coupling | 固定边耦合 | 每个世界对每条边只抽样一次 |
| tighter convergence tolerance | 较紧的收敛容差 | 此处指 PageRank 的数值停止容差 |
| conditional Monte Carlo uncertainty | 条件蒙特卡洛不确定性 | 以已选种子集合为条件 |
| post-hoc sensitivity analysis | 事后敏感性分析 | 保留原研究身份，不译为确认性验证 |
| ordered-trajectory agreement | 有序轨迹一致性 | 每轮选种顺序完全相同 |
| final-set agreement | 最终集合一致性 | 最终种子成员相同，不要求顺序相同 |

## 阅读提示
本文的“世界”指随机传播实现，“路径”指计算重复；二者都不是独立真实网络。译文保留事后分析身份与条件不确定性的含义，没有把集合一致性译为期望最优性。
