# 本轮再生成
在本目录执行 `python src/generate_presentation.py`，从相邻冻结包读取已有JSON/NPZ/CSV并生成表格和源数据。脚本不导入模拟器或runner。

在manuscript目录分别执行两遍：
```
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error Online_Resource_1.tex
```
在chinese/manuscript目录执行两遍：
```
xelatex -interaction=nonstopmode -halt-on-error manuscript_zh.tex
```
回到本目录执行 `python src/verify_presentation.py`。它重新生成表格并检查哈希、旧版保护、英中数字、图形资源、公式、引用和声明，然后渲染全部页面。可视核验另记render_checks.json。

依赖：NumPy、Pillow、pypdf、Poppler和TeX Live。当前Python为C:/Users/36024/Miniconda3/python.exe，TeX为C:/texlive/2026/bin/windows。src/revise_prose.py保存本轮文字转换；它从基线重建文稿，后续人工编辑后不要误执行覆盖。

实验复现设计见补充材料及前版REPRODUCE.md。本轮没有执行选择回放或传播模拟。
