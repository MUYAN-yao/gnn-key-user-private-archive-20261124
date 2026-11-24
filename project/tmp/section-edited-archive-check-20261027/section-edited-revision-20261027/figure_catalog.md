# 新增历史图目录与绘图检查

原主文3图、补充4图均不改动。历史原Fig4位于冻结历史包，仍保持原文件。

| 编号 | 输出 | 科学问题与来源 | 重复单位/误差 | 解释边界 |
|---|---|---|---|---|
| S5 | HistoryParameters.pdf/svg/png | 四接触图、默认+四局部p/h设置、D/P/W4k；parameter_sensitivity_display.csv | 每点十路径均值；±1样本SD | 离散参数，非连续曲线或全因子；坐标尺度分面不同；零/负结果全部保留 |
| S6 | HistoryEdgeTransitions.pdf/svg/png | edge320→1280全参照预算差；40路径全显示 | 每点一条路径；±1.96×条件MC SE，M=10000 | 区间条件于选定集合，不是路径CI或跨图总体CI；不跨coupling配对 |

Python/Matplotlib，119mm宽度适配当前svjour3版心，轴标签及图例9pt、刻度8pt；Arial与既有结果图一致；两图为PDF矢量入稿，SVG保留可编辑文本，PNG为300dpi预览。字体、样式和误差含义由同一再生成脚本固定。没有采样删行或模拟造数。

技能静态检查原样保留在 `qa/figure-source-preflight.json`。其通用Nature默认89/183mm、TIFF和600dpi不是本稿矢量PDF的硬性规格；119mm按实际版心核实，300dpi PNG仅用于预览。最终判断结合导出尺寸、PDF编译和逐页可视检查，不把启发式告警隐藏或误称为统计核验。
