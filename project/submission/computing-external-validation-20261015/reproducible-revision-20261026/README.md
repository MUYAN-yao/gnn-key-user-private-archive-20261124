# 实验设置与可复现性修订版

本版本从 `../editorial-revision-20261026` 独立建立，保留用户机制图、摘要和主要结论。正文补充数据截取、参数矩阵、随机化与运行环境；补充材料增加完整复现说明。

- 正文：`manuscript/manuscript.pdf` / `manuscript.tex`
- 补充材料：`manuscript/Online_Resource_1.pdf` / `.tex`
- 执行指南：`REPRODUCE.md`
- 安全复现入口：`src/reproduce.py`
- 本次实际复验：`qa/reproduction-final/verification.json`
- 排版及数字一致性：`qa/revision_checks.json`

复现入口以父目录的冻结数据、源码和结果为输入，在指定的新目录中重跑、重建并核对，不覆盖原实验。单独复制本版本目录不能替代完整的外部验证包。历史研究仍按相邻历史包中的 README 复现。

本轮不修改科学结论，不新增实验样本；代表性重跑是工程复验，不能计为新的证据。
