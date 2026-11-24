# 文稿重编译与本轮核验

以本版为工作目录，分别在 manuscript 中用 pdflatex 编译 manuscript.tex 两次，在 chinese/manuscript 中用 xelatex 编译 manuscript_zh.tex 两次。

本机 TeX 程序目录：C:\texlive\2026\bin\windows。
Python：C:\Users\36024\Miniconda3\python.exe。

本版根目录执行：
```powershell
& 'C:\Users\36024\Miniconda3\python.exe' src\revise_contributions.py --verify
```

此命令核查保存 CSV 的描述性计数与均值、原版未变动、贡献段之外全文一致、图表资源一致、中英数字及公式一致、引用和编译日志，并渲染 PDF；不会执行实验。图像仍须人工查看。

--build 是创建新版本的首次操作；目录已有稿件时会拒绝覆盖。冻结实验与历史复现记录见 evidence/prior_REPRODUCE.md 及前版说明，本轮未重新进行实验复现。
