# 2026-10-26 正文精简修订

本目录以 `../mechanism-im-grounded-20261023/manuscript` 为底稿，按作者要求精简叙事、筛选正文图表。英文正文 13 页，补充材料 12 页。先阅读 `manuscript/manuscript.pdf`；修改说明见 `revision_notes_zh.md`。

## 本轮文件

- `manuscript/manuscript.tex` / `.pdf`：修订正文。
- `manuscript/Online_Resource_1.tex` / `.pdf`：完整补充材料，承接从正文移出的图表。
- `qa/revision_checks.json`：摘要、引用、模板、作者信息、图源、表格数值和编译核验。
- `qa/visual_review.md`：实际页面检查记录。
- `qa/render-final`：最终正文 13 页与补充材料 12 页的渲染及缩略总览。
- `src/verify_revision.py`：可重新运行的核验脚本。

## 机制图与证据

正文 Fig. 1 使用作者提供的新版 `im_evaluation_mechanism_v2.vsdx` 对应的矢量 PDF。图源内容、布局和颜色均未修改。

原生 Visio 源文件位于：
`../mechanism-im-grounded-20261023/figures/im_evaluation_mechanism_v2.vsdx`。

原始实验、数据、冻结源码和分析结果继续保存在父目录及原投稿包。本目录是文稿修订包，不是重新执行实验产生的完整数据归档。核验脚本通过相邻的原投稿包比较数值、图源和参考文献；完整复现实验应使用原包中的协议和命令。

## 编译与核验

在 `manuscript` 目录运行：

```powershell
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error Online_Resource_1.tex
pdflatex -interaction=nonstopmode -halt-on-error Online_Resource_1.tex
```

在本目录运行 `python src/verify_revision.py --render`。环境需要 pypdf、Pillow 和 PATH 中的 Poppler `pdftoppm`。实际验证使用 Codex bundled Python 和 TeX Live 2026。模板 `svjour3.cls` 与 `svglov3.clo` 保持原样。

## 期刊要求来源

2026-10-26 查阅 Computing 官方作者指南：
https://link.springer.com/journal/607/submission-guidelines

该页要求单栏 `smallextended`、正文不超过 25 页、摘要 150–250 词，不允许通过缩小排版挤页数。本轮使用原模板正常尺寸。超出辅助文字润色的 LLM 使用需要记录在方法中，因此取消独立 AI 小节和文末重复声明后，在方法中保留一个简短脚注。

相关 Computing 文章的公开页面核对了研究主题、摘要表达及元数据：
https://link.springer.com/article/10.1007/s00607-019-00778-5
https://link.springer.com/article/10.1007/s00607-023-01207-4
这两个页面只有订阅内容预览；不据此声称检查了付费全文排版。排版以官方模板和作者指南为准。
