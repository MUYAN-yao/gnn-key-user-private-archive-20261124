# 本轮文稿编译与核验

在本版 manuscript 目录运行 pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex 两次，再对 Online_Resource_1.tex 同样编译两次。
在 chinese/manuscript 目录运行 xelatex -interaction=nonstopmode -halt-on-error manuscript_zh.tex 两次。
TeX程序：C:\texlive\2026\bin\windows；Python：C:\Users\36024\Miniconda3\python.exe。

在本版根目录执行：
```powershell
& 'C:\Users\36024\Miniconda3\python.exe' src\verify_revision.py
```
该核验脚本只读取原稿、修订稿、已有结果哈希、编译日志和PDF，并调用pdftoppm渲染。不会导入或执行实验代码。它检查原版未变、资产和表格数字、声明、引用、关键措辞及中英数值，并生成逐页缩略图；可视核验另存qa/render_checks.json。

src中的两个revision脚本是创建此次稿件的工作记录，使用项目根目录相对路径；完成版不应再次运行其构建步骤。没有机械调用旧版的贡献段限定验证器。实验复现记录仍在原始冻结包；本轮没有新实验或新增复现范围。


## 既有实验及历史汇总的复现入口（本轮未执行）

EXTERNAL_REPRODUCE_INHERITED.md 原样保留外部实验的输入检查、环境与隔离复验说明。文内命令以外部冻结包根目录为工作目录，仍指向已存在的 narrative-revision-20261027/src/reproduce.py。本版 src/reproduce.py 为已有入口的逐字节副本；不是本轮检查脚本，不要把执行它算作文稿编译。参数 --base 指外部冻结包根目录，--output 必须为新目录，--replay 模式及其执行范围见继承指南。

历史汇总指令及统计口径见 evidence/HISTORICAL_REPRODUCE_INHERITED.md。该指南中的历史整合脚本位于 ../historical-evidence-revision-20261027/src/integrate_historical.py；本版也保留其已有副本 src/integrate_historical.py。它读取已保存数组而不运行传播模拟，但会生成表图，未来需要再生成时应在独立工作副本中操作，随后恢复本轮已编辑的表头和图注。不能让历史生成器覆盖当前正式稿。

这些入口、requirements.txt 和说明文件的原始路径与SHA-256见qa/inherited_reproduction_sources.json。复制不表示本轮再次执行复现；本轮只运行src/verify_revision.py中的文稿检查。
