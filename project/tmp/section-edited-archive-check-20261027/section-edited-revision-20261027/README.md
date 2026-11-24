# 分章节语言修订版（2026-10-27）

基线：相邻 `historical-evidence-revision-20261027`。本版按引言/综述、方法、结果、讨论分别采用不同修改原则。

- `manuscript/manuscript.pdf` / `.tex`：修改后的正文。
- `manuscript/Online_Resource_1.pdf` / `.tex`：保留完整历史证据与外部分析，补充材料内容未改动，本轮重新编译。
- `revision_report_zh.md`：逐章节改动及保护项。
- `manuscript_changes.diff`：相对直接上一版的源码差异，包括仅因首次引用次序而重排的参考文献。
- `qa/section_edit_checks.json`：方法/设置/结果数值、公式、图表、作者声明、分析文件保护检查。
- `qa/revision_checks.json`：编译、引用、模板、机制图与PDF渲染检查。

本轮没有实验、分析再生成或新的文献事实扩展。没有调用实验runner或传播回放。原始实验、历史敏感性图、表S9–S13、机制图、标题、摘要及作者声明保持原内容。正文参考文献只按首次出现排序，条目内容和文献集合不变。

本版以论文修订为目的，`src/verify_section_edit.py`为本轮入口，`src/verify_revision.py --render`用于编译后的PDF检查。其他复制自上一版的分析/复现脚本均属于历史工具，本轮未执行。它们原有说明见 `REPRODUCE.md`，不将历史执行记录冒充本轮核验。

已有历史数组核验及外部复验记录保留在 `evidence/`；本轮执行范围只见 `qa/`。ZIP为完整文稿资源与修订记录，不重复包含冻结实验原始结果或第三方原始数据。
