# Computing LaTeX 排版稿

本工程以用户指定的 `manuscript_review_20260921 - 副本.docx` 为正文依据。作者首页根据同目录作者信息记录和用户随后确认的信息补充。原 Word 文件未被修改。

## 打开和编译

1. 解压完整工程，保留文件在同一个目录中。
2. 用 TeXworks 打开 `manuscript.tex`。
3. 在左上角选择 **pdfLaTeX**，点击绿色运行按钮，连续编译两次。第一遍生成引用记录，第二遍更新引用编号。
4. 也可以双击 `build.bat`，自动编译两次。

本稿为英文论文，采用 pdfLaTeX。正文参考文献已写在 `thebibliography` 环境中，无须运行 BibTeX 或 Biber。修改参考文献时，在 `manuscript.tex` 末尾编辑对应 `\bibitem`。

## 工程文件

- `manuscript.tex`：可编辑的完整 LaTeX 正文、公式、表格和参考文献。
- `manuscript.pdf`、`manuscript_大纲修订版.pdf`：内容相同，均为按导师大纲建议修订并经 TeX Live 2026 编译检查的 18 页排版稿。压缩包内保留前者。
- `svjour3.cls`、`svglov3.clo`：Springer SVJour3 原版模板文件。
- `Fig1.pdf` 至 `Fig8.pdf`：与原 Word 嵌入图片对应的现有矢量 PDF 导出。
- `Fig1.vsdx`、`Fig2.vsdx`：前两幅示意图的原生 Visio 源文件。
- `FigS1-tie-trajectories-source.csv`：原图注所引用的轨迹数据。
- `formatting_check.md`：格式核对、转换记录及仍待作者补充的信息。
- `outline_revision.md`：与同刊已发表范文的章节对照及本次大纲调整记录。

正式上传稿件源文件时，保留 `manuscript.tex`、两个模板文件和八幅 PDF 图在同一层级，不创建图表子目录。Visio 文件、CSV、说明文档和编译脚本应按投稿系统要求作为补充材料或留作本地资料。

## 格式依据

已采用 `\documentclass[smallextended]{svjour3}`，保持模板的正文尺寸、字体大小、页边距及页眉规则。表格使用可编辑的 LaTeX 表格，数学公式由 Word OMML 对象逐项转换；正文采用方括号数字引用。

**关于 PDF 右侧的大块空白：**投稿模板默认输出 A4 页面，但 `smallextended` 单栏版心宽度只有 11.9 cm，并从左边约 2.54 cm 处起排。正文没有缺失；右边宽白边是这一模板的默认页面几何。已发表的 *Computing* 范文使用更窄的期刊成品页面，正文宽度与本稿几乎相同，因此它看上去没有同样宽的右白边。投稿版请保留模板尺寸，不要为填满 A4 而自行扩宽正文或缩小页边距。

另有 `manuscript_紧凑阅读版_非投稿.pdf` 供阅读和发给导师查看。它只裁去 A4 页面四周未使用的白边，变为与已发表范文相近的 439 × 666 pt 页面；18 页的文字、图表和次序均未改动。**此文件不要作为 Computing 投稿 PDF 上传**，应使用 `manuscript.pdf` 和完整 LaTeX 源文件。阅读版单独提供，不包含在投稿工程压缩包中。

导师建议对应的大纲现为 Introduction → Related work → Methods → Experiments → Discussion and limitations → Conclusion。实验原始材料、数据、图表和结论未因本次章节调整而改写。范文的期刊页面、官方 PDF 和对应关系见 `outline_revision.md`。

Computing 官方指南：https://link.springer.com/journal/607/submission-guidelines

Springer 的旧 SVJour3 下载链接当前返回网页或不可访问。本工程保留原版模板文件，获取自公开保存的副本：

- https://raw.githubusercontent.com/DanySK/Template-LaTeX-Springer-svjour3/master/svjour3.cls
- https://raw.githubusercontent.com/DanySK/Template-LaTeX-Springer-svjour3/master/svglov3.clo

两个模板文件的原始内容与版本标识均保留。

Codex 内置 LaTeX 编译器本次报错 `Unable to find standard directories for platform`；最终 PDF 的编译验证使用本机已安装的 TeX Live 2026 完成。该问题不影响在 TeXworks 中打开和编译工程。

## 正式投稿前仍需补充

- 资助项目的正式名称与编号。
- 可公开访问的代码/可复现资料仓库 DOI 或长期链接。
- 依据实际使用情况填写 AI 工具声明；原稿占位文字暂时保留。
- 确认全体作者姓名、署名顺序、贡献、利益冲突及最终稿批准情况。
- 正文所指的 Online Resource 1 须另行作为补充材料准备和上传。
- 按期刊要求准备工作独特性与评估方式摘要，以及说明为何适合 Computing 的 cover letter。

这些是原稿的待填信息和投稿材料需求，不属于本次排版中新增的研究结果。
