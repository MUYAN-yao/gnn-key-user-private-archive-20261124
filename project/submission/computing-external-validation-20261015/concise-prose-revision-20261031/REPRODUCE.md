# 文稿编译与检查

在manuscript目录用pdflatex编译manuscript.tex两次；在chinese/manuscript目录用xelatex编译manuscript_zh.tex两次。
本机TeX目录为C:/texlive/2026/bin/windows。

运行src/verify_concise.py进行文件保留、数字、引用、编译日志与PDF渲染检查。该脚本不执行实验。

前版完整说明保存在evidence/prior_REPRODUCE.md；外部复现说明见EXTERNAL_REPRODUCE_INHERITED.md；历史汇总说明见evidence/HISTORICAL_REPRODUCE_INHERITED.md。本轮未执行这些复现实验入口。
