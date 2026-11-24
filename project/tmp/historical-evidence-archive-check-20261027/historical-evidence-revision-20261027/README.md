# 历史证据整合修订稿（2026-10-27）

题目保持 **Reference Budgets and Ranking Precision in Candidate-Restricted Influence Maximization**。

本版以相邻目录 `narrative-revision-20261027` 为正文基线。已根据版本说明与目录内容确认该基线，没有覆盖任何旧稿、冻结协议、源码或结果。机制图和已有外部结果资产保持原字节。

## 先看这些文件

- `manuscript/manuscript.pdf`：修订正文，外部网络和 PageRank 精度仍为主线。
- `manuscript/Online_Resource_1.pdf`：补充材料，第12节为本轮历史证据；新增5张表与2张图。
- `revision_report_zh.md`：中文修改说明与证据来源。
- `claim_evidence_matrix.md`：结论—实验来源—适用范围。
- `REPRODUCE.md`：本轮只读保存结果的再生成命令。
- `qa/historical_integration_validation.json`：历史数值及文件核验。
- `qa/revision_checks.json`：编译、引用、资产和PDF检查。
- `qa/final_checks.json`：最终汇总及再生成记录。

## 本版做了什么

核对520个历史条件的1,040个JSON/NPZ哈希，重算4,680臂的传播均值、配对差和条件MC标准误；按路径内随机池平均后核对3,640条路径汇总、378条分组汇总及240条预算转移。新增参数、耦合、种子预算和固定合成实例的表图，保留正负结果。正文没有据此增加新颖性或泛化强度。

**本轮没有运行任何训练、种子搜索、传播模拟、实验runner或新的计时实验。** `src/integrate_historical.py` 仅读取已保存文件。`src/reproduce.py` 是从旧版继承、供另行授权复验使用的工具，本轮未调用；即使其某些选项不重复种子选择，审计也可能包含传播回放，不属于本轮允许的入口。

## 文件范围

本目录及其ZIP是完整的文稿修订包：包含LaTeX所需模板、图表、引用、PDF，以及本轮生成脚本与核验记录。它不是冻结实验原始结果的第二份副本；再生成历史表图需要同一项目内的 `submission/computing-strengthening-20261015` 和外部包的 legacy engine（只计算哈希）。来源及预期结果哈希已列入QA记录。第三方原始数据未复制进本版。

`evidence/`、`EXTERNAL_REPRODUCE_INHERITED.md` 和 `claim_language_audit.md` 保留上一版外部复验与主张核验依据；本轮新增结论及边界见 `claim_evidence_matrix.md`。继承的代表性重跑记录不等同于本轮新执行或全部实验重跑。

作者信息与既有声明沿用已确认稿件，不由本轮数值核验替代作者责任。发布、上传、投稿均未执行。
