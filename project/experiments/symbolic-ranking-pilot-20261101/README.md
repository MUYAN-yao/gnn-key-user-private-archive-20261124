# 复现与文件索引
本目录是独立探索实验，不修改原论文、协议、结果或快照。原文件SHA256见readonly-input-manifest.json，执行结束再次核对。原snapshot两个.py复制到本目录，逐字节一致。全部随机性命名空间为symbolic-ranking-pilot-20261101-v1。

## 先读
- `protocol.md`：新增结果前保存的假设、整图划分、指标、搜索约束、成败标准。
- `preflight-record.md`、`preflight.json`、`preflight.log`：实际预检与冻结矩阵；无预检选择或效用结果。
- `config.json`、`environment.json`：实际矩阵、版本、Python路径。
- `execution_status.json`、`execution.log`、`qa.json`：执行完成与验证。
- 中文报告：`2026-11-01--symbolic-ranking--r1--round-review.md`。
- `analysis-report.md`、`stats-appendix.md`、`figure-catalog.md`：严格分析及解释边界。
- `sources.md`：方法的原始来源核查及未能读取的范围。

## 复现分析
在本目录，用environment.json所列Python执行：
```powershell
python -B analyze.py
python -B validate.py
```
以上覆盖本目录可再生的分析输出；若要保留交付文件，请先复制本目录到新兄弟目录。分析直接使用CSV与raw/里的逐世界评价数组，不需再次运行模拟。

## 从头复现实验（创建新版本）
在项目experiments下新建如symbolic-ranking-pilot-20261101-reproduction的目录，复制pilot.py,engine.py,legacy_engine.py,run.py,analyze.py,validate.py,config.json,protocol.md及vendor目录。新目录必须仍处于项目experiments内（代码以父级父级定位原数据）。执行：
```powershell
python -B pilot.py   # 仅耗时预检，生成environment.json
python -B run.py     # 固定config矩阵
python -B analyze.py
python -B validate.py
```
复现者不要按结果修改协议/矩阵。原始数据读取位置为项目submission/computing-external-validation-20261015/data/raw/snap；源hash均已记录。必要时安装Numba0.68.1和llvmlite0.50.0到新目录vendor：`python -m pip install --target vendor --no-deps numba==0.68.1 llvmlite==0.50.0`。其余环境版本见environment.json。Numba首次编译会增加耗时。

## 数据表
- pagerank.csv：每图/容差/候选数的残差、迭代、gap、epsilon、充分证书、近边界数、替换与参考误差。
- runs.csv：全部完整选种子条件、顺序、独立spread/SE、相对有限参考的Jaccard与传播差。
- rounds.csv：每轮胜者/次佳、同分数、同世界成对差SD/SE；winner margin有选择偏差，不是真gap。
- features.csv、timings.csv、graphs.json：独立先导、成本、生成机制与参考稳定证据。
- budget_transitions.csv：各臂自身跨W变化、逐世界配对区间；pagerank_utility.csv为默认/严格PR代表条件。
- selected_models.json：验证选定公式/系数及简单基线；formula_stability.json为3次训练整图重采样。
- model_metrics_by_graph.csv、model_metrics_summary.csv、predictions.csv、model_decision.json：逐图误差、原始预测和预声明判定。
- raw/：每图CSR、每条件逐轮全部候选总分、种子、world IDs、先导逐候选逐世界传播值、独立评价逐种子集合的10000结果与索引。结合继承hash和CSR可重建每个随机世界，不保存大型布尔世界张量。

`/`符号表达式算子专指protected divide(a,b)=a/(1+abs(b))；AST节点数按这个原语计，不含允许的外层仿射校准与clip。表达式搜索是受限SR的一种实现，不等同于全面评估PySR、遗传编程等。

无Obsidian写回；用户指定的独立实验目录为唯一交付目的地。未执行GNN训练或自适应预算策略，没有声称已节省端到端计算成本。
