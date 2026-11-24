# 证据约束的叙事修订版（2026-10-27）

**Reference Budgets and Ranking Precision in Candidate-Restricted Influence Maximization**

本版本从 `../reproducible-revision-20261026` 独立建立。主要改变是标题、摘要、三项编号贡献、结果的论证顺序，以及讨论/结论和编辑材料。实验设置、方法、作者信息及正式声明、机制图、统计图和数字表保留。

## 阅读入口

- `manuscript/manuscript.pdf`、`manuscript/manuscript.tex`：正文。
- `manuscript/Online_Resource_1.pdf`、`.tex`：同步标题和复现身份说明的补充材料。
- `title_and_positioning.md`：三个备选标题和采用理由。
- `claim_language_audit.md`、`claim_evidence_matrix.md`：主张、直接证据、身份和不能支持的更强表述。
- `summary_for_editor.txt`、`cover_letter_draft.txt`、`novelty_and_scope_statement.txt`：同步编辑材料。
- `revision_report_zh.md`：修改与核验范围。
- `REPRODUCE.md`：以外部验证包为根目录的复现命令。

## 本轮与继承的验证

`qa/claim_checks.json`为本轮从原始JSON/NPZ读取并重算关键统计、核对措辞所用数值和资产一致性的记录；没有运行新的传播实验。`qa/revision_checks.json`为本轮编译、引用、摘要、页数与渲染检查。

`evidence/reproduction-20261026.json`为上一轮代表性重跑和分析再生成的原记录副本，哈希一致。它不是2026-10-27的新执行记录。复现源码`src/reproduce.py`逐字节保持不变。

本版本使用父目录的冻结外部结果和历史包作为证据依赖。单独复制本目录不能替代完整科研包；它提供最终稿件、材料与审核记录，不重复打包原始第三方数据。原始数据按提供方来源和哈希获取。没有新增公开网址、许可证声明或投稿行为。
