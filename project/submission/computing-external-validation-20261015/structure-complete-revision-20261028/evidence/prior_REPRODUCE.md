# 本轮文稿生成与核验

本轮只修改文字、生成对应中文译稿、编译和检查PDF，不执行任何实验或统计再生成。原实验与分析复现说明保留于evidence/prior_REPRODUCE.md和evidence/prior_EXTERNAL_REPRODUCE_INHERITED.md，其历史命令需在相应原版本路径下运行，不是本轮新增执行。

## 重新编译并检查本版

在本版目录运行（PowerShell）：

```powershell
Push-Location manuscript
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
Pop-Location
Push-Location chinese/manuscript
xelatex -interaction=nonstopmode -halt-on-error manuscript_zh.tex
xelatex -interaction=nonstopmode -halt-on-error manuscript_zh.tex
Pop-Location
& 'C:/Users/36024/Miniconda3/python.exe' src/verify_revision.py
```

依赖TeX Live、Poppler、Python的pypdf/Pillow及Windows中文字体。检查脚本只读取保存的CSV、源码、PDF、哈希及编译日志，并渲染页面；不导入实验引擎。可视检查记录是针对本次PDF哈希的检查，修改文稿后应重新查看渲染页。

## 从上一版重新生成修改文本

src/revise_paper.py保存本轮20处英文修改及对应中文译文。它读取相邻structural-language-revision-20261027和chinese-translation-20261027，在本版本中重新生成英文、中文源码、差异及翻译映射；随后须再次执行上述编译检查。

该入口会重新生成本版文稿，因此后续人工编辑应先保留副本；它不改写旧版本或冻结实验。中文全文映射另存于chinese/translation_map.json，翻译表格映射保存于src/translation_tables.json。

补充材料本轮原样继承，未重新编译或翻译。其PDF与源码哈希通过本轮检查。全部实验数据与证据身份不因本次叙事修改而改变。
