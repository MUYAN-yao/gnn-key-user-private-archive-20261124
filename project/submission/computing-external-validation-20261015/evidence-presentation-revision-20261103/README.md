# 贡献、输入输出与讨论修订 · 2026-11-03
基线：concise-prose-revision-20261031，由README及修订链确认，原版保留。

- 英文正文：manuscript/manuscript.tex、manuscript.pdf。
- 中文正文：chinese/manuscript/manuscript_zh.tex、manuscript_zh.pdf。
- 英文补充材料：manuscript/Online_Resource_1.tex、Online_Resource_1.pdf。没有独立中文补充稿。
- 编辑材料：cover_letter_draft.txt、summary_for_editor.txt。
- 修改说明：revision_report_zh.md；证据对应：claim_evidence_matrix.md。
- 新表源数据：analysis/presentation；生成入口：src/generate_presentation.py。
- 核验：qa/numerical_checks.json、final_checks.json、render_checks.json。
- 文本差异：qa/english.diff、chinese.diff、prose_changes.json。

本轮只读取保存结果并重算表格，没有运行新实验。机制图和原有结果图保持不变。复制的历史脚本和说明不代表本轮执行记录。再生成见REPRODUCE.md。
