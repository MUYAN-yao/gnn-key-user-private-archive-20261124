# 结构与学术语言修订版（2026-10-27）

基线：相邻 `section-edited-revision-20261027`。标题保持 Reference Budgets and Ranking Precision in Candidate-Restricted Influence Maximization。

- `manuscript/manuscript.pdf` / `.tex`：新版正文。
- `manuscript/Online_Resource_1.pdf` / `.tex`：新版补充材料，历史表图全部保留。
- `revision_report_zh.md`：按结构、术语、论证、语言说明修改与限制。
- `manuscript_changes.diff`：相对直接上一版的全部 TeX 差异。
- `information_moves.md`：正文、补充材料与复现文件之间的信息去向。
- `qa/structural_revision_checks.json`：结果数字、公式、实验设置、作者声明、分析文件及图资产保护检查。
- `qa/revision_checks.json`、`qa/render_checks.json`：编译、引用、页数、渲染与逐页查看记录。
- `qa/related_work_source_check.md`：本轮相关工作表述的来源及访问限制。

本轮只进行文稿编辑、既有文件读取与一致性检查、LaTeX 编译及 PDF 渲染。没有运行训练、传播模拟、种子搜索、实验 runner、复现回放或统计再生成。所有既有分析数值和图资产保持不变。图中的历史标签 Strict 对应正文的 tighter tolerance，图注已说明；未重绘机制图或结果图。

`src/verify_structural_revision.py` 是本轮保护检查入口；`src/verify_revision.py --render` 为编译后的 PDF 检查入口。其余实验、分析和复现脚本属于继承材料，本轮未调用。历史核验记录位于 `evidence/`，不得将其执行范围或日期当作本轮新增验证。

原始实验输出及第三方原始数据仍在相邻冻结包；本修订目录保存完整论文源码、必要图表、保存的分析表和修订记录。第三方数据不另行再分发。作者信息与正式声明逐字保留，其真实性来自作者确认。
