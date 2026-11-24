# 图 2、6、7 排版修订记录

日期：2026-09-14。目标为 SNAM 工作稿中的三张指定图片。

## 修改范围

- 图 2：重排为共同构建流程与两条版本化评分路径，统一框宽、字号、边距和箭头，消除文字越框。图注明确 v3 完整候选对照跳过筛选步骤，以及选择世界与评估世界的独立性。该修改澄清已有实现，不修改算法。
- 图 6：图例移至绘图区上方；显示种子 42—51 的全部刻度；使用颜色和点形双重编码。每个种子内的三个点采用固定横向偏移，仅用于分辨散点。
- 图 7：图例移至绘图区上方；补充跨种子均值和两条参考线的含义。保持全部散点及原始均值；横向位置依种子排序均匀展开，没有改变 AUC。
- Word 使用当前 SNAM 中文稿和英文摘要，另存 r45，保留 r44。图像嵌入宽度 6.25 英寸；图注整段保持同页；图 6、7 的画布高度调整为 3.65 英寸，使其在 Word 第 11 页连续呈现。图 2 在第 6 页。
- 文档生成器同步从 Markdown 读取标题，并补齐现有内联公式的符号转换，避免将 LaTeX 命令直接显示为正文。未改动公式定义。

## 数据与图形契约

| 项目 | 图 6 | 图 7 |
| --- | --- | --- |
| 原始报告 | audits/higgs-edge-prediction-v1/audit_report.json | audits/edge-prediction-v2-t0-outer-test-v1/report.json |
| 指标字段 | future_edge_prediction.auc | metrics.auc |
| 种子字段 | random_seed | seed |
| 分组字段 | train_fraction | train_fraction |
| 样本 | 每个训练比例 10 个种子，共 30 个点 | 每个外部切分 10 个种子，共 30 个点 |
| 中心/离散度 | 逐次观测，无误差线 | 短横线为算术均值，无误差线 |
| 检验 | 本轮不计算新检验 | 本轮不计算新检验；0.55 为已有均值 95% t 区间下界门槛 |
| 排除或抽样 | 无 | 无 |

重复为同一网络条件下的随机协议重复，不是独立网络样本。图 6 展示冻结 v1 的未来边审计；图 7 展示固定 T0 的隔离外部测试。不能将跨版本差异解释为受控消融。

## 验证

- 两张结果图导出的 CSV 与原始 JSON 按 `(train_fraction, seed)` 逐项比较，60 个 AUC 值完全一致。源文件执行前后 SHA-256 一致；具体哈希在 layout_qa.json。
- 所有来源图、冻结分析和实验输出保留。只写 manuscript 下的新图、工作稿及检查产物。
- matplotlib 文本边界检查：图 2 文字两两无重叠，流程框内文字均被边界包含；图 6、7 图例边界与坐标轴绘图区分离。
- 科研绘图静态检查：13 项通过、0 项失败，唯一警告是静态扫描器无法识别计算形式的画布宽度。导出 PDF 实测宽度为 183.000006 mm，已确认。
- PNG/TIFF 主输出为 600 dpi，SVG/PDF 保留可编辑文字。低分辨率 preview 仅用于预览；Word 使用主 PNG。
- 默认文档渲染器因缺少 LibreOffice 无法启动；使用本机 Microsoft Word 导出 PDF，再以 Python/PyMuPDF 渲染并人工查看全部 20 页。指定三图、图例、轴标签和图注均无重叠、裁切或变形。
- 本轮为指定图形修订，不是整稿最终投稿排版。既有其他图、表与内部工作稿附注沿用；表 2 的说明仍在下一页，未纳入此次三图重排范围。

## 重现

1. 在具备 matplotlib、NumPy 和 Pillow 的 Python 环境执行 `manuscript/revise_figures_2_6_7.py`。
2. 在具备 python-docx 的文档环境执行 `manuscript/build_internal_word_draft.py --output manuscript/temporal_key_user_identification_snam_r45_figure_revision.docx`。
3. 通过 Word 导出供检查的 PDF，执行 `manuscript/qa_r45/render_checks.py` 核对数据、图像分辨率、矢量宽度和文档图片数量。
