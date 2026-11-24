# 本版文稿编译与核验

本文件仅说明结构修订版文稿流程，不启动实验。完整实验和既有复现记录见 `evidence/prior_REPRODUCE.md` 及其引用的冻结版本。不要把本轮编译检查等同于重新完成实验复现。

在本版目录打开 PowerShell，英文和中文各执行两遍（分次运行以下相应命令）：

```powershell
Set-Location manuscript
& 'C:\texlive\2026\bin\windows\pdflatex.exe' -interaction=nonstopmode -halt-on-error manuscript.tex
& 'C:\texlive\2026\bin\windows\pdflatex.exe' -interaction=nonstopmode -halt-on-error manuscript.tex
Set-Location ..\chinese\manuscript
& 'C:\texlive\2026\bin\windows\xelatex.exe' -interaction=nonstopmode -halt-on-error manuscript_zh.tex
& 'C:\texlive\2026\bin\windows\xelatex.exe' -interaction=nonstopmode -halt-on-error manuscript_zh.tex
Set-Location ..\..
& 'C:\Users\36024\Miniconda3\python.exe' src\verify_structure.py
```

验证脚本读取原版与新版源码、资源及 PDF，使用 pypdf、Pillow 和 pdftoppm 检查并渲染页面。它不会调用实验 runner；运行后仍须人工查看渲染页面。当前人工查看记录见 `qa/render_checks.json`。

`src/revise_structure.py` 保存基于原版的替换块与中文对应，可重建本次修改，但会将原版资源复制到本目录并覆盖生成文件，包括复制原版 PDF 和编辑材料。仅在准备重新生成并重新编译时执行，不作为日常检查命令。`src/finalize_revision.py` 整理本轮说明和译文行号映射，不改写已编译正文。

`manuscript_changes.diff`、`revised_passages_bilingual.md` 和 `chinese/translation_map.json` 可用于逐项复核。页码由各语言排版独立生成，不要求中英文同页对应。
