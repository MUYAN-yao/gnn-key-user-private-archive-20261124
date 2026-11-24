# 研究项目本地交接包

本包交付现有实验数据、完整研究代码、实验原始输出、统计分析及当前 r44 论文。它是内部研究交接快照，不代表已通过正式投稿验收，也未公开上传。所有纳入的源文件均按原样复制并校验 SHA-256。

## 从这里开始

论文：`project/manuscript/temporal_key_user_identification_internal_draft_r44_mechanisms.docx`。
正文源文件：`project/manuscript/draft_zh_v0_1.md`；英文摘要、参考文献、图源和生成脚本在同目录。未找到当前全文 PDF，故不以旧稿 PDF 替代。附录命名的 Markdown 是历史工作记录，不是要附在论文后的提交内容。

原始数据及处理输入：`project/data/raw/`、`project/data/processed/`；来源、语义限制和处理脚本见 `project/data/README.md`、`project/data_cards/`、`project/scripts/`。Higgs/Digg 原始数据的公开再分发许可未确认，本包仅用于本地内部交接，不能直接作为公开发布包。

代码：`project/backend/`、`project/experiments/`、`project/scripts/`、`project/web/`；测试在 `project/tests/`。预注册协议、环境记录、原始哈希在 `project/protocols/` 和 `project/reproducibility/`。当前代码快照不能替代历史代码版本；历史清单中的哈希不保证与当前代码相同。

## 结果版本索引

| 版本 | results 下目录 | 对应 analysis 目录 |
|---|---|---|
| Digg v1 | large-robust-greedy-digg-20000-v1 | frozen-main-comparison-v1 |
| Higgs v1 | large-robust-greedy-higgs-50000-v1 | frozen-main-comparison-v1 |
| Higgs v2-T0b | large-robust-greedy-higgs-50000-v2-t0b | v2-t0b-strict-paired-v1 |
| Higgs v2-T0d | large-robust-greedy-higgs-50000-v2-t0d-common-world-objective-ablation | v2-t0d-common-world-objective-ablation-v2-null-matrix |
| Higgs v3 | large-robust-greedy-higgs-50000-v3-fairness-sensitivity | v3-fairness-sensitivity-strict-paired-v1 |

以上五组各有 30 个 split JSON，共 150 个主要运行记录。其余结果和审计保留用于溯源，不自动视为最终有效证据。尤其 v2-T0c 是被替代的未完成分支；pilot/smoke 不能混入正式统计。

v2-T0b 的 RIS 比较均未通过 Holm 校正。v2-T0d 的九个消融比较均为零差异。v3 全候选对比和候选池对比均为零；24 个权重比较中 21 个均值为零，另 3 个均值约 10.751，但均未通过 Holm 校正。十次重复是配对随机协议重复，不是十个独立网络样本。GNN Top-K 是受保护返回规则下界，不能视为独立优越性证据。

## 复现入口

解压后在 `project` 目录运行。推荐创建独立 Python 环境，原实验版本见环境记录；requirements 是范围约束，不是精确环境锁文件。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install matplotlib scipy python-docx lxml pillow
python -m pytest -q
python experiments/build_v3_fairness_sensitivity_analysis.py --study-dir results/large-robust-greedy-higgs-50000-v3-fairness-sensitivity --output-dir analysis/reproduced-v3-new
```

统计输出必须写入新的空目录。完整重跑会消耗大量计算资源，请先阅读 v3 协议和执行预检：

```powershell
python experiments/run_v3_fairness_sensitivity.py --dataset data/processed/higgs-twitter/pilot-50000 --output-dir results/reproduced-v3-preflight-new --dry-run
```

所有 v1/v2/v3 原始结果均保持只读；不要在现有目录重新运行 summarize。Web/API 启动说明见项目 README；前端依赖需要另行安装，本包不携带 node_modules 或 Python 环境。

## 尚待投稿前完成的事项

当前交付保留论文现状，没有趁打包改写结论。论文中参数比较计数、配对标准差口径、引用覆盖以及机制图表述仍需一致性复核；统计数值以对应 analysis 表和原始 JSON 为准。旧 reproducibility README 中“尚未完成”等状态是历史记录，不能覆盖本交付包的文件数量检查。

当前全文 Word/PDF 逐页视觉验收未完成；CMYK 图像转换不等于 ICC 印刷打样。作者、基金等信息仍待作者确认，官方模板转换和公开发布许可尚未完成。历史审计文件保留不等于其结论全部有效，尤其最初 audit_r44 存在参考文献参数误用。

## 完整性

`SOURCE_INVENTORY.json` 记录源文件清单、大小及复制时哈希；`SHA256SUMS.txt` 覆盖包内除其自身外的所有文件。旁置 ZIP 校验报告记录每个 ZIP 条目的 SHA-256 与解压目录一致性及 CRC 检查结果。`EXCLUDED_FILES.json` 列出选定目录中被排除的依赖、缓存和旧稿；workspace 临时目录、运行缓存、无关申报文件未纳入。
