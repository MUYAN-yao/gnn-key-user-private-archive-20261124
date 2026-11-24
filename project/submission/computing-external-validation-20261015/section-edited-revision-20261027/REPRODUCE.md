# 本轮历史证据再生成：不运行实验

**版本说明：** 以下是从历史证据整合版继承的再生成指南。当前 `section-edited-revision-20261027` 只做章节语言修改，没有执行这些分析命令。当前核验入口是 `src/verify_section_edit.py` 和编译后的 `src/verify_revision.py --render`；历史执行证据位于 `evidence/historical-integration-20261027/`。

输入为已有 `computing-strengthening-20261015/results/conditions/`、结果清单、冻结配置、历史CSV、初始42条件的元数据及外部包legacy engine。脚本只读取这些文件；不导入模拟器、调用实验runner、重新选种子或生成传播世界。

在项目根目录执行：

```powershell
$env:PYTHONPATH = (Resolve-Path './tmp/computing-extension-deps').Path
python './submission/computing-external-validation-20261015/historical-evidence-revision-20261027/src/integrate_historical.py'
```

如目录整体移至其他位置，用 `--project-root '实际项目根目录'` 指向仍保留上述两个冻结实验包的位置。输出固定写入脚本所属修订目录的 `analysis/`、`manuscript/history_*_table.tex`、两张历史图及 `qa/historical_*.json`，不写入历史包。

环境为本机Python 3.13、NumPy、pandas、Matplotlib；确切版本由最终QA记录保存。初次安装或跨平台运行未在本轮执行。PDF/SVG含时间元数据，比较图的解码像素和CSV/TeX内容；不要求含时间字段的二进制导出逐字节相同。

## 新表图的数据口径

- 参数图/表：`stage=parameters` 的160条件，加 `stage=resolution,W=320` 的40个默认条件；后者只复用、不计为新增条件。显示D/P/W三种4k方法，共60个网络×参数×方法汇总行。
- 耦合表：`stage=coupling`80条件，及 `stage=resolution,W∈{320,1280}`80条件的三种4k方法；共48行。各自相对自己的全候选参照，不跨耦合逐世界相减。
- 转移表/图：相同图、路径、k、p、h、coupling的相邻W，必须评估世界哈希相同。表显示step1280→5120、edge320→1280；图显示全部40条edge路径。
- 次要表：`stage=seed_budget`60条件和 `stage=scale`20条件；3种4k方法，共30行。
- `historical_arm_metrics.csv`保留4680臂，`historical_path_metrics.csv`保留3640行（随机3池已在路径内平均），`historical_group_summary.csv`保留378行及全部已执行方法。
- SD为路径间样本标准差；loss列为比例，入稿乘100。`delta`为restricted−full，负loss表示候选法点估计更高。预算转移为high−low。

## 编译与文稿核验

进入本修订目录的 `manuscript`：

```powershell
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error Online_Resource_1.tex
pdflatex -interaction=nonstopmode -halt-on-error Online_Resource_1.tex
python ../src/verify_revision.py --render
```

此检查使用pypdf、Pillow及Poppler，不模拟传播。生成全部页面PNG和四页接触表，再进行人工可视核对。新版图的119mm宽度匹配svjour3当前正常版心；无缩小正文或表格字号。

完整数字及资产检查可从项目根目录运行：

```powershell
python './submission/computing-external-validation-20261015/historical-evidence-revision-20261027/src/check_historical_revision.py'
```

增加 `--regenerate` 只会再次运行本轮的保存结果汇总脚本，并核对全部新增CSV/TeX与PNG像素；仍不运行实验。再生成后重新编译PDF，因为矢量导出的时间元数据可能变化。

## 外部复验记录的边界

`EXTERNAL_REPRODUCE_INHERITED.md`是旧版外部复验说明，保留其原命令与历史执行日期。本轮**没有调用其中任何实验或审计回放入口**。此前代表性条件重跑与外部分析再生成记录见 `evidence/`；本轮仅继承，不声称再次执行。
