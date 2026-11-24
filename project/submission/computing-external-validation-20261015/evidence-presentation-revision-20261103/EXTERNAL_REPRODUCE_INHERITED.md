# 复现指南 / Reproduction guide

这份指南对应当前正文的实验设置和补充材料的复现章节。所有命令在外部验证包根目录 `computing-external-validation-20261015` 执行；不要在旧版本中直接运行会改写稿件的 `build_documents.py`。入口只读取原记录，分析在新输出目录的副本中执行。实验复验记录继承自2026-10-26；2026-10-27只调整叙事、复核关键数值及重新编译，没有执行新实验。

## 1. 环境

已验证环境为 Windows、Python 3.13.0；使用原 `requirements.txt` 中的固定版本。全新机器先准备 Python 3.13，然后：

```powershell
python -m venv .venv-reproduction
& ./.venv-reproduction/Scripts/python.exe -m pip install -r requirements.txt Pillow==12.3.0
$py = (Resolve-Path './.venv-reproduction/Scripts/python.exe').Path
```

上面是环境安装方法，未在全新机器上重新安装。2026-10-26测试复用了原实验隔离依赖：项目根目录的 `tmp/computing-extension-deps` 加入 `PYTHONPATH`，解释器为 Miniconda Python 3.13.0。实际版本和复验结果见 `evidence/reproduction-20261026.json`。不能把本机复验描述为跨平台认证。

## 2. 原始输入

```powershell
& $py review-v2/src/download_data.py
```

脚本从 SNAP 获取 CollegeMsg、ca-GrQc、Wiki-Vote 的原始 gzip，并严格匹配 `data/source_manifest.json` 的预期 SHA-256；已有匹配文件直接复用。来源说明与许可边界见 `data_selection.md` 和原始数据记录。下载后的文件放在 `data/raw/snap/`，不要解压后替换 gzip。提供者的使用条款仍适用，原始第三方数据不加入交付归档。

## 3. 推荐复验：全部记录审计 + 代表性实验重跑 + 全部外部统计和图重建

```powershell
& $py narrative-revision-20261027/src/reproduce.py --base . --output ./reproduction-check-01 --replay representative
```

输出目录必须不存在；重复执行更换为 `reproduction-check-02`，不能覆盖旧记录。脚本在导入数值库之前将 OMP、OPENBLAS、MKL、NUMBA 线程限制为 1。运行包括：

1. 检查冻结源码清单、三个原始数据哈希和重建后的图哈希；检查配置与运行状态对应的完整 54 条件、468 臂。
2. 对全部主实验核对世界前缀、选择/评估分离、候选池、得分矩阵、同分获胜节点、传播均值、配对差、MC 标准误和相同集合的逐世界一致性。
3. 重跑三图路径 1101：W80/按步和 W320/固定边，共 6 条件、52 臂，逐元素核对得分与评估数组。
4. 审核两批严格容差结果的输出哈希、90 臂配对统计；重跑三图路径 1101 的 W80、W1280，6 条件、12 臂，检查 1e-12 与 1e-14 候选池稳定性及完整数组。
5. 在 `workspace/` 副本中调用原分析/绘图脚本，重建默认矩阵与精度—预算分析，核对 CSV 和 PNG。主文图 2 对应精度图 `precision_budget_loss`，主文图 3 对应原 `Fig2`；机制图是作者设计的流程示意，不是实验数组生成的统计图。

`verification.json` 中 `status` 必须为 `PASS`；重跑比较的是种子和数组，不比较耗时。原始时间记录仍用于论文成本图；新计时仅为本次复验记录。

## 4. 仅重建分析或完整重跑

```powershell
& $py narrative-revision-20261027/src/reproduce.py --base . --output ./analysis-check-01 --replay none
& $py narrative-revision-20261027/src/reproduce.py --base . --output ./full-replay-01 --replay all
```

`none` 不重新选择种子，但仍需要原始数据来重建图和方向诊断。`all` 重跑 54 条件/468 臂主实验和 45 条件/90 臂事后严格容差控制。严格容差部分复用原全参照和评估世界，保持原研究身份。2026-10-26执行的是 representative，未执行 all；本轮没有重新运行该入口，源码与已验证版本完全相同。

历史 42 条件和 520 条件证据不属于此入口；其源码、输入和运行方法保留在相邻 `computing-strengthening-20261015` 包中，按该包 README 单独复现，不与外部样本数合并。

## 5. 复现成功的判定

- 种子序列、整数得分及逐世界传播数：精确一致。
- 全部生成 CSV：结构和文字一致，浮点数容差 `rtol=atol=1e-12`。
- 生成 PNG：解码像素精确一致。跨平台字体差异可能导致像素不同，需要检查；不能因此修改数值结果。
- PDF/SVG 元数据、运行时间与内存：不要求逐字节或逐值一致。
- 不能用本轮代表性检查替代对所有条件的完整重跑声明；也没有声称已进行独立团队复现。

## 6. 文稿编译

在 `narrative-revision-20261027/manuscript` 内执行（TeX Live 2026）：

```powershell
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error Online_Resource_1.tex
pdflatex -interaction=nonstopmode -halt-on-error Online_Resource_1.tex
```

模板、机制图、原始数字表和统计图资产保持不变。本轮改动集中于标题、摘要、编号贡献、结果顺序与解释；实验设置和复现入口不变。文稿核验日志位于本版本 `qa/`。
