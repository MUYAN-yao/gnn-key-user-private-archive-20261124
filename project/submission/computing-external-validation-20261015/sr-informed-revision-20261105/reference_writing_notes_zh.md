# 参考材料中的实验与讨论写法，以及在本文中的取舍

按本地PDF页序定位。21份文件对应20个不同题目，含一份中译对照；RAG-SR为演示稿。以下是对材料写作方式的归纳，不评价其方法优劣。

**实验部分。** 有的论文按研究问题组织，例如Neural Symbolic Regression that Scales先列出要检验的三个方面；有的按任务或输入条件组织，例如AI Feynman先定义方程库和求解标准，再看噪声水平，Learning Interpretable Network Dynamics先给出从观测到方程的映射。共同可借鉴的是让每项指标对应具体输出。本文把种子ID作为选择输出，把独立评估下的激活节点数作为效用输出。个例展示过程，跨路径统计回答比较问题。

**讨论部分。** In-Context KAN讨论固定配置的随机重复和单因素扰动各测量什么。Boolformer用一个具体操作符解释输出表达式为何冗长。ParFam把表示带来的搜索便利和表达范围放在同一处讨论。这些处理比反复声明“本文不能证明……”更有效。本文将ca-GrQc的预算与容差比较分开解释，把wiki-Vote的候选资格、传播方向和实际效用放在同一段论证中，并保留验证方向解释所需的对照。

**写法取舍。** 符号回归论文有可恢复的参考公式；本文比较的是同预算的贪心种子集合，因此不用公式恢复率类比影响力最大化的最优性。写作参照仅列在这份说明中，稿内引用沿用影响力最大化与网络评价文献。

|本地材料|PDF页|观察到的写法|
|---|---|---|
|[Ab Initio Nonparametric Variable Selection for Scalable Symbolic Regression](<D:/符号回归/SR论文PDF(1)/SR论文PDF/Ab Initio Nonparametric Variable Selection for Scalable Symbolic Regression.pdf>)|6–8|先按黑箱数据与已知方程分组，报告预筛选对不同下游算法的影响及不一致处。讨论回到缩小变量搜索空间的条件。|
|[Ab Initio Nonparametric Variable Selection for Scalable Symbolic Regression_翻译.pdf](<D:/符号回归/SR论文PDF(1)/SR论文PDF/Ab Initio Nonparametric Variable Selection for Scalable Symbolic Regression_翻译.pdf.pdf>)|6–8|英文论文的中译对照，用于核对分组与术语，同一研究只计一次。|
|[AI Feynman_ A physics-inspired method for symbolic regression](<D:/符号回归/SR论文PDF(1)/SR论文PDF/AI Feynman_ A physics-inspired method for symbolic regression.pdf>)|6–13|先定义方程库和求解判据，再列逐方程结果，单独改变噪声水平。结尾从具体成功与失败的方程讨论适用结构。|
|[Boolformer_ Symbolic Regression of Logic Functions with Transformers](<D:/符号回归/SR论文PDF(1)/SR论文PDF/Boolformer_ Symbolic Regression of Logic Functions with Transformers.pdf>)|5–11|按输入缺失、位翻转和真实分类任务组织实验。讨论把表达式冗长追溯到操作符词表缺少显式XOR。|
|[Deep symbolic regression_ Recovering mathematical expressions from data via risk-seeking policy gradients](<D:/符号回归/SR论文PDF(1)/SR论文PDF/Deep symbolic regression_ Recovering mathematical expressions from data via risk-seeking policy gradients.pdf>)|7–9|先交代可比较的表达式评估预算，再给出恢复率与对照结果。结尾从共享表达式树这一具体表示讨论后续搜索方式。|
|[GenSR_ Symbolic regression based on equation generative space](<D:/符号回归/SR论文PDF(1)/SR论文PDF/GenSR_ Symbolic regression based on equation generative space.pdf>)|16–19、32–34|附录把重建结果、噪声条件与编码器分支消融分开呈现，使读者能追踪具体组件改变了哪个输出。|
|[In-Context Symbolic Regression for Robustness-Improved Kolmogorov-Arnold Networks](<D:/符号回归/SR论文PDF(1)/SR论文PDF/In-Context Symbolic Regression for Robustness-Improved Kolmogorov-Arnold Networks.pdf>)|12–22|在固定设置下汇总随机种子变异，再单独考察逐因素变化。讨论分别解释两种分布的含义，界定证据覆盖的设置。|
|[Influence-Guided Symbolic Regression_ Scientific Discovery via LLM-Driven Equation Search with Granular Feedback](<D:/符号回归/SR论文PDF(1)/SR论文PDF/Influence-Guided Symbolic Regression_ Scientific Discovery via LLM-Driven Equation Search with Granular Feedback.pdf>)|5–9|按基准比较、针对性实例和组件对照安排证据，同时给出数值拟合与项恢复。讨论回到逐项反馈与总损失提供的信息差异。|
|[Interaction-Transformation Evolutionary Algorithm for Symbolic Regression](<D:/符号回归/SR论文PDF(1)/SR论文PDF/Interaction-Transformation Evolutionary Algorithm for Symbolic Regression.pdf>)|9–16、20–21|先交代数据和算子问题，再分项讨论变异算子、比较方法及误差；结尾把继续检验的因素落到算法的具体选择。|
|[KAN-SR_ A Kolmogorov-Arnold Network Guided Symbolic Regression Framework](<D:/符号回归/SR论文PDF(1)/SR论文PDF/KAN-SR_ A Kolmogorov-Arnold Network Guided Symbolic Regression Framework.pdf>)|9–13|先区分两类任务，单独展示含干扰变量的条件；结论联系噪声、高维输入与方程恢复。|
|[KAN_ Kolmogorov-Arnold Networks](<D:/符号回归/SR论文PDF(1)/SR论文PDF/KAN_ Kolmogorov-Arnold Networks.pdf>)|12–17、31–33|用具体函数或物理任务展示输入、可视表示及读出的结果，末节按数学、算法和应用讨论限制。|
|[Learning Interpretable Network Dynamics via Universal Neural Symbolic Regression](<D:/符号回归/SR论文PDF(1)/SR论文PDF/Learning Interpretable Network Dynamics via Universal Neural Symbolic Regression.pdf>)|2–10|结果开头把观测量到动力学方程的映射写清，再给出系统级实例与对照。讨论围绕哪些观测足以支持方程识别。|
|[Neural Symbolic Regression that Scales](<D:/符号回归/SR论文PDF(1)/SR论文PDF/Neural Symbolic Regression that Scales.pdf>)|6–8|结果开头明确列出待回答的问题，按预训练规模、基准等对照展开。讨论用结果解释预训练怎样改变重复求解的计算方式。|
|[ParFam_ (Neural Guided) Symbolic Regression via Continuous Global Optimization](<D:/符号回归/SR论文PDF(1)/SR论文PDF/ParFam_ (Neural Guided) Symbolic Regression via Continuous Global Optimization.pdf>)|7–9|用噪声条件、预测质量及时间评价具体模型。讨论将参数化结构的计算优势与所能表达的函数范围放在一起。|
|[RAG-SR_ Retrieval-Augmented Generation for Neural Symbolic Regression](<D:/符号回归/SR论文PDF(1)/SR论文PDF/RAG-SR_ Retrieval-Augmented Generation for Neural Symbolic Regression.pdf>)|28–38|提供的是演示文稿。按设置、基准结果与结论分屏，只借鉴其图表阅读顺序。|
|[Reinforcement Symbolic Regression Machine (RSRM)](<D:/符号回归/SR论文PDF(1)/SR论文PDF/Reinforcement Symbolic Regression Machine (RSRM).pdf>)|6–9|区分基准表达式恢复与泛化误差，各自指定指标；结论将表达式形式的灵活性联系到适用问题。|
|[SNIP_ Bridging Mathematical Symbolic and Numeric Realms with Unified Pre-training](<D:/符号回归/SR论文PDF(1)/SR论文PDF/SNIP_ Bridging Mathematical Symbolic and Numeric Realms with Unified Pre-training.pdf>)|5–9|将跨模态属性估计、表示和回归任务分开评价。结尾分别对应这些任务说明证据。|
|[Symbolic Physics Learner_ Discovering governing equations via Monte Carlo tree search (SPL)](<D:/符号回归/SR论文PDF(1)/SR论文PDF/Symbolic Physics Learner_ Discovering governing equations via Monte Carlo tree search (SPL).pdf>)|6–10|分别改变数据噪声和稀缺程度，给出基准恢复率及实例输出，详细限制由正文指向附录。|
|[Symbolic regression via MDLformer-guided search_ from minimizing prediction error to minimizing description length](<D:/符号回归/SR论文PDF(1)/SR论文PDF/Symbolic regression via MDLformer-guided search_ from minimizing prediction error to minimizing description length.pdf>)|7–10|区分已知真值方程与黑箱任务，再考察噪声及搜索行为。不同任务采用相应评价标准。|
|[Symbolic--KAN_ Kolmogorov-Arnold Networks with Discrete Symbolic Structure for Interpretable Learning](<D:/符号回归/SR论文PDF(1)/SR论文PDF/Symbolic--KAN_ Kolmogorov-Arnold Networks with Discrete Symbolic Structure for Interpretable Learning.pdf>)|8–15|把结果与讨论合并，按回归、动力学识别和物理约束任务解释具体输出。并非所有论文都另设Discussion。|
|[TPSR_ Transformer-based Planning for Symbolic Regression](<D:/符号回归/SR论文PDF(1)/SR论文PDF/TPSR_ Transformer-based Planning for Symbolic Regression.pdf>)|6–10|先比较拟合与表达式复杂度，再用规划参数、缓存等对照解释成本来源。结论回到拟合与复杂度的权衡。|
