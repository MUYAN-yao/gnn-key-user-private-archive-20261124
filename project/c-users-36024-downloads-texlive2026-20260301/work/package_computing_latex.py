from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from pypdf import PdfReader
import shutil, json, re, hashlib

root=Path(__file__).resolve().parent.parent
out=root/'outputs'/'computing_latex'
source=Path(r'D:\校创\基于GNN的关键用户识别\manuscript\resolution_aware_candidate_truncation_submission_v0_1')
revised_pdf=out/'manuscript_大纲修订版.pdf'
shutil.copy2(root/'work'/'computing-build'/'manuscript.pdf',revised_pdf)
shutil.copy2(source/'figures'/'Fig1-mechanism-editable.vsdx',out/'Fig1.vsdx')
shutil.copy2(source/'figures'/'Fig2-experimental-design.vsdx',out/'Fig2.vsdx')
audit=json.loads((root/'work'/'latex-conversion-audit.json').read_text(encoding='utf-8'))
tex=(out/'manuscript.tex').read_text(encoding='utf-8')
log=(root/'work'/'computing-build'/'manuscript.log').read_text(encoding='utf-8',errors='replace')
pdf=PdfReader(revised_pdf)
cited={x for group in re.findall(r'\\cite\{([^}]+)\}',tex) for x in group.split(',')}
bib=set(re.findall(r'\\bibitem\{([^}]+)\}',tex))
assert cited==bib and len(cited)==16
assert 'Overfull' not in log and 'undefined' not in log.lower()
assert len(pdf.pages)<=25
assert all((out/f'Fig{i}.pdf').is_file() for i in range(1,9))
report=f'''# Computing 格式核对记录

核对日期：2026-09-28。

## 转换完整性

| 内容 | 原 Word / 转换后 |
| --- | --- |
| Word OMML 数学对象 | {audit['math_objects']} / {audit['math_objects']} |
| 正文图 | 8 / 8 |
| 正文表 | 4 / 4 |
| 参考文献 | 16 / 16 |
| 已在正文引用的文献 | 16 |
| 未定义引用 | 0 |

65 处数学对象中，三处独立展示公式使用 LaTeX equation 环境，其余使用行内数学。上下标、求和、分式、根号、数学花体以及帽号/横线由原 OMML 结构转换。公式和表格均可编辑。

原 Word 图片与同目录 PNG 的 SHA-256 逐一匹配后，采用对应的现有矢量 PDF 文件。图号按正文顺序为 Fig. 1–8。原 Fig. 4 图注的 CSV 路径改为同层文件名，以符合期刊源文件不使用子目录的要求。

## 格式检查

| 检查项 | 结果 |
| --- | --- |
| 期刊模板 | SVJour3，smallextended 单栏 |
| 正文版心 | 模板默认 11.9 cm × 19.4 cm |
| 总页数 | {len(pdf.pages)}，不超过 25 页 |
| 摘要词数 | {audit['abstract_words']}，位于 150–250 词范围 |
| 关键词 | {audit['keywords']} 个，位于 4–6 个范围 |
| 标题层级 | 十进制编号，最多三级 |
| 正文引用 | 方括号数字，连续引用合并 |
| 超出页边界警告 | 0 |
| 公式、图、表和参考文献丢失 | 数量核对未发现 |
| 页图检查 | 已渲染并逐页检查 18 页 |

采用原版模板的字体和排版尺寸，未缩小正文字号或改变页边距来减少页数。图 5 和图 6 按正文位置排版，图 4 的显示宽度调整为栏宽的 90%，避免两图浮动形成留白较大的独立图片页，也未产生版心溢出。原始图形内容和数据保留，矢量图可继续由作者编辑。

投稿 PDF 的页面为 A4（约 595 × 842 pt），模板单栏正文宽度约 337 pt（11.9 cm），正文从左侧约 72 pt 开始，因而右侧保留约 186 pt 的白边。这是 `smallextended` 模板的默认页面几何；同刊范文的已发表版本是约 439 pt 宽的成品页面，正文宽度约 338 pt。请勿为了填满 A4 擅自扩宽投稿版正文。

单独提供的 `manuscript_紧凑阅读版_非投稿.pdf` 只调整 PDF 页面裁切框，不改变文本、图表或页序；它不在投稿工程压缩包内，不能替代符合模板要求的投稿 PDF。

## 导师建议对应的大纲修订

参照同刊开放获取论文的章节组织，现采用 Introduction、Related work、Methods、Experiments、Discussion and limitations、Conclusion 六个主章节。原稿的研究内容和实验结果保留；改动是将相关工作独立成章、将实验设计和结果归入同一实验主线，并更新自动交叉引用。逐项对照见 `outline_revision.md`。

## 作者首页

署名顺序为 Jiayue Sun、Binbin Yong、Junjie An、Tianyu Bo、Shuai Li。Binbin Yong 为通讯作者，邮箱 yongbb14@lzu.edu.cn。

Jiayue Sun 和 Binbin Yong 的学院、邮编按同目录记录填写。后三位作者按用户明确提供的“都是兰州大学”填写 Lanzhou University, Lanzhou, China，未推断具体学院。

## 验证范围和待填内容

此次工作是转换和排版：没有重新运行实验，也没有另行核验参考文献的出版元数据。原稿研究叙述、结果及声明内容按来源保留。

资助项目名称与编号、代码仓库长期链接、AI 工具声明仍为原稿待填内容；全体作者的贡献、利益冲突和最终稿批准也需要作者本人确认。Online Resource 1、cover letter 和投稿摘要须另行准备。

Codex 内置编译器本次因运行环境问题未能编译；本机 TeX Live 2026 的 PDFLaTeX 已成功连续编译，引用全部解析。mathptmx 关于缺少粗体数学字体的通用提示不影响本稿的正常数学显示；未发现影响输出的编译错误。

格式来源：https://link.springer.com/journal/607/submission-guidelines

原 Word SHA-256：`{audit['source_sha256']}`。
'''
(out/'formatting_check.md').write_text(report,encoding='utf-8')
archive=root/'outputs'/'Computing_LaTeX_导师建议大纲修订版.zip'
with ZipFile(archive,'w',ZIP_DEFLATED) as z:
    for file in sorted(out.iterdir()):
        if file.is_file() and file.name not in ('manuscript.pdf','manuscript_排版修订版.pdf','manuscript_大纲修订版.pdf','manuscript_紧凑阅读版_非投稿.pdf'):
            z.write(file,arcname=file.name)
    z.write(revised_pdf,arcname='manuscript.pdf')
with ZipFile(archive) as z:
    assert z.testzip() is None
    assert 'manuscript.tex' in z.namelist() and all('/' not in n for n in z.namelist())
print(json.dumps({'pages':len(pdf.pages),'pdf':str(revised_pdf),'zip':str(archive),'zip_files':len(z.namelist()),'zip_size':archive.stat().st_size,'pdf_sha256':hashlib.sha256(revised_pdf.read_bytes()).hexdigest()},ensure_ascii=False))
