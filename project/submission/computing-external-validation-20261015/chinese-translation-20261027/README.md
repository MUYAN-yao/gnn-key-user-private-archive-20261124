# 中文正文阅读译稿

题目：候选受限影响力最大化中的参照预算与排名精度

英文基线：structural-language-revision-20261027。原英文稿未修改。

## 阅读入口

- `manuscript/manuscript_zh.pdf`：18 页中文正文，包含图表、声明及原始参考文献。
- `paper.md`：逐段中英对照，附原图、原表截图与术语表。
- `manuscript/manuscript_zh.tex`：中文 LaTeX 源码。
- `source_map.json`：原文、译文和源文件定位。
- `translation_notes.md`：翻译范围与处理说明。
- `qa/translation_checks.json`、`qa/render_checks.json`：自动检查和可视检查记录。

本次翻译正文全文，未翻译补充材料全文。图内英文标签保留，图注和表头已译成中文。

## 本地重新生成

在本目录下运行以下 PowerShell 命令；依赖 Python（pypdf、Pillow）、Poppler、XeLaTeX 和 Windows 中文字体。生成脚本会读取相邻英文基线目录及其已保存的 PDF 渲染文件。

```powershell
& 'C:\Users\36024\Miniconda3\python.exe' src/build_translation.py
Push-Location manuscript
xelatex -interaction=nonstopmode -halt-on-error manuscript_zh.tex
xelatex -interaction=nonstopmode -halt-on-error manuscript_zh.tex
Pop-Location
& 'C:\Users\36024\Miniconda3\python.exe' src/verify_translation.py
```

上述脚本仅生成翻译文件、检查保存文件和渲染 PDF，不调用任何实验 runner。修改译文后需重新检查其研究含义与数值对应关系；自动检查不能单独证明翻译准确性。
