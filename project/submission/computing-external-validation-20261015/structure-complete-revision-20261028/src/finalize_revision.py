"""Write this revision's documentation and provenance; never execute experiments."""
from pathlib import Path
import hashlib
import json
from revise_structure import EN, B, R

def write(name, content):
    (R/name).write_text(content.strip()+'\n', encoding='utf-8')

# Correct output-line locations without rewriting compiled manuscripts.
mp=json.loads((R/'chinese/translation_map.json').read_text(encoding='utf-8'))
current=1
for i,line in enumerate((B/'manuscript/manuscript.tex').read_text(encoding='utf-8').splitlines(),1):
    en=EN.get(i,line)
    if str(i) in mp: mp[str(i)]['english_output_line']=current
    current+=en.count('\n')+1
write('chinese/translation_map.json',json.dumps(mp,ensure_ascii=False,indent=2))

write('README.md',r'''
# 结构修订与中文全文译稿 · 2026-10-28

英文题目：Reference Budgets and Ranking Precision in Candidate-Restricted Influence Maximization

本版基于相邻目录 `problem-led-revision-20261028`，按章节功能完善论文结构。原版本及冻结实验不变。

- 英文正文：`manuscript/manuscript.pdf`（17 页），源码 `manuscript/manuscript.tex`。
- 中文全文阅读译稿：`chinese/manuscript/manuscript_zh.pdf`（20 页），同名 `.tex` 为源码。正文、图表题注和声明均有对应译文；图内文字保留原英文，文献题录保留原文。
- 英文补充材料：`manuscript/Online_Resource_1.pdf`，与基线完全相同，本轮未另译补充材料。
- 修改说明：`revision_report_zh.md`；新增/调整段落双语对照：`revised_passages_bilingual.md`；源码差异：`manuscript_changes.diff`。
- 检查结果：`qa/structure_checks.json`、`qa/render_checks.json`；文献核对范围：`qa/literature_source_check.md`。
- 编译与核验：`REPRODUCE.md`。

本轮没有启动训练、种子搜索、传播模拟、实验 runner 或统计分析重算。机制图、结果图表、保存分析及实验数值均保留。中文稿用于阅读和作者核对；英文稿仍是投稿正文。
''')

write('revision_report_zh.md',r'''
# 按章节功能完成的结构修订

日期：2026-10-28。基线：`problem-led-revision-20261028`。新版：`structure-complete-revision-20261028`。

## 修改落点

| 章节 | 本次修改 | 作用与边界 |
|---|---|---|
| 引言 | 补充影响力最大化的任务背景、定向选择初始节点的应用动机，以及贪心计算成本；连接已有求解策略与候选限制问题，并加入相应引用 | 先说明为什么研究，再提出参照和候选池均受数值选择影响的评价困难；未扩大应用有效性 |
| 相关工作 | 按“目标、采样与计算效率”“影响力估计与种子选择”“评价设置与待解问题”组织；从逐项列举改为比较研究目标及与本文问题的联系 | 明确已有理论、计算策略和本文经验诊断的不同层次；没有声称已有工作全部忽视某问题 |
| 方法 | 增加研究设计总述，说明配对模拟评价的对象、顺序和控制因素；交叉引用实验设置 | 保留原方法主体和参数。Methods 与 Experimental setup 分章，合起来承担完整方法功能，不为套用通用提纲强行合并 |
| 结果 | 保留 wiki-Vote 的入度、出度、候选覆盖和种子重合数据，将方向不匹配的解释移入讨论 | 结果报告观察，讨论分析解释；未改变效应、符号、显著性或不确定性 |
| 讨论 | 联系经典期望传播量结果、StaticGreedy 的样本复用及质量—成本评价；新增网络方向与迁移小节 | 说明本文证据补充了什么，同时区分采样目标、期望目标与候选池构造；方向解释仍未获得干预实验验证 |
| 局限与后续检验 | 保留原局限；具体提出外部网络的容差×耦合对照、传播方向干预和更宽参数设置 | 都明确属于未开展的后续检验，不计为本研究证据 |
| 结论 | 按问题、设计、发现、价值及后续检验重组 | 结论限于已研究网络与参数，没有新增最优性、等效性或推广保证 |

摘要保持上一轮已修改的 172 词版本；三项主要贡献保留。此次不再借结构调整反复重写已明确的研究主线。

## 中文版本

中文稿对应修订后的英文全文，包括摘要、各级正文、图表题注、作者声明和参考文献入口；文献题录与图内英文保留。术语保持一致：reference budget 为参照预算，ranking precision 为排名精度，full-candidate reference 为全候选参照，incremental spread 为增量传播量，independent evaluation 为独立评估。新增段落的双语对应和位置记录见 `revised_passages_bilingual.md`、`chinese/translation_map.json`。

## 检查结果及实际范围

- 英文和中文各编译两次，分别 17 页和 20 页；无未定义引用、未解决交叉引用、缺字或 Overfull 警告。
- 已渲染全部 37 页并逐页检查页面缩略图；重点查看表图密集页面。未发现遮挡、裁切、空白页或缺失图表。正常模板分页保留，未通过缩字号或版心压缩页数。
- 源码数字及行内数学表达式核对通过。原方法主体、实验设置和结果观察保留；中英文数字、公式及引用对应检查通过。
- 机制图和其他受保护稿件资源的 SHA-256 与基线一致；英文补充材料及保存分析未改动。旧版本文件哈希核对通过。
- 文献核实仅覆盖本轮新增比较所依赖的内容，范围见 `qa/literature_source_check.md`；未声称重新审计了全部文献全文。
- 本轮没有运行任何新实验，也没有重跑原实验或重新进行统计推断。已有实验、复现和作者声明沿用原记录，文字修订不增加这些证据的强度。

## 仍保留的边界

外部网络是少量选定样本；PageRank 精度控制属于事后分析并复用原路径；种子变化不等于实质效用变化；入向排名与出向传播不匹配是与观察一致的解释，尚非因果证明；成本仅相对本实现参照；历史固定边结果不证明外部严格容差结论在固定边条件下成立。后续检验需要新的证据，本轮未补做。
''')

write('qa/literature_source_check.md',r'''
# 本轮新增文献比较的核对范围

检查日期：2026-10-28。没有新增参考文献条目。以下是新增背景、综合和讨论所依赖的核对，不代表全部题录或全文重审。

| 来源 | 本轮访问材料 | 支持内容及边界 |
|---|---|---|
| Kempe, Kleinberg & Tardos (2003) | https://www.cs.cornell.edu/home/kleinber/kdd03-inf.pdf （作者单位全文） | IM 任务、独立级联期望传播量的次模性与贪心近似、活边覆盖解释；本文有限按步目标的诊断来自自己的已有结果 |
| Leskovec et al. (2007), CELF | https://snap.stanford.edu/class/cs224w-readings/leskovec07outbreak.pdf （Stanford 全文） | lazy-forward 借助次模性减少边际收益重复评估；不据此声称本文优于 CELF |
| Cheng et al. (2013), StaticGreedy | https://www.junminghuang.com/publications/2013-cikm-cheng.pdf （作者全文） | 固定采样实现并在选择过程中复用，保持一致覆盖目标；本文不将该已有原则包装为新方法 |
| Arora, Galhotra & Ranu (2017) | https://sainyamgalhotra.com/publication/dblp-confsigmod-arora-gr-17/ （作者题录）；https://mitdbg.github.io/nedbday/2017/talks/galhotr.pdf （作者报告） | 仅用于“研究质量与计算成本的基准评价”这一宽泛研究目标。本轮未成功获取 SIGMOD 全文，不采用其具体方法优劣结论 |
| Tang, Shi & Xiao (2015), IMM | https://www.comp.nus.edu.sg/~xiaoxk/publications.html （作者题录） | 核对题录；保留上一版对采样求解器的概括。本轮没有据此新增具体定理或实验结论 |

Rui、Fan、Ko、Li、Yanchenko 与 Aral 的宽泛研究内容沿用此前稿件和来源记录，本轮没有将其标为全文重新核验。新增综合句属于作者对研究目标和本研究问题关系的讨论，不声称每篇文献都检验过本研究的所有因素，也不从未报告推断不存在。
''')

write('REPRODUCE.md',r'''
# 本版文稿编译与核验

本文件仅说明结构修订版文稿流程，不启动实验。完整实验和既有复现记录见 `evidence/prior_REPRODUCE.md` 及其引用的冻结版本。不要把本轮编译检查等同于重新完成实验复现。

在本版目录打开 PowerShell，英文和中文各执行两遍（分次运行以下相应命令）：

```powershell
Set-Location manuscript
& 'C:\texlive\2026\bin\windows\pdflatex.exe' -interaction=nonstopmode -halt-on-error manuscript.tex
& 'C:\texlive\2026\bin\windows\pdflatex.exe' -interaction=nonstopmode -halt-on-error manuscript.tex
Set-Location ..\chinese\manuscript
& 'C:\texlive\2026\bin\windows\xelatex.exe' -interaction=nonstopmode -halt-on-error manuscript_zh.tex
& 'C:\texlive\2026\bin\windows\xelatex.exe' -interaction=nonstopmode -halt-on-error manuscript_zh.tex
Set-Location ..\..
& 'C:\Users\36024\Miniconda3\python.exe' src\verify_structure.py
```

验证脚本读取原版与新版源码、资源及 PDF，使用 pypdf、Pillow 和 pdftoppm 检查并渲染页面。它不会调用实验 runner；运行后仍须人工查看渲染页面。当前人工查看记录见 `qa/render_checks.json`。

`src/revise_structure.py` 保存基于原版的替换块与中文对应，可重建本次修改，但会将原版资源复制到本目录并覆盖生成文件，包括复制原版 PDF 和编辑材料。仅在准备重新生成并重新编译时执行，不作为日常检查命令。`src/finalize_revision.py` 整理本轮说明和译文行号映射，不改写已编译正文。

`manuscript_changes.diff`、`revised_passages_bilingual.md` 和 `chinese/translation_map.json` 可用于逐项复核。页码由各语言排版独立生成，不要求中英文同页对应。
''')

q=json.loads((R/'qa/structure_checks.json').read_text(encoding='utf-8'))
render={'date':'2026-10-28','review_method':'All rendered pages inspected in contact sheets; table/figure pages checked for clipping, overlap and completeness. This is layout review, not a new scientific audit.','english_pages_reviewed':list(range(1,18)),'chinese_pages_reviewed':list(range(1,21)),'clipping_or_overlap_found':False,'missing_figures_or_blank_pages_found':False,'layout_notes':['Normal template whitespace and float placement retained.','Chinese references retain original language and span the final pages.','Figure internals retain original English; translated captions explain them.'],'pdf_hashes':{lang:q[lang]['sha256'] for lang in ['english','chinese']}}
write('qa/render_checks.json',json.dumps(render,ensure_ascii=False,indent=2))

claim=(R/'evidence/prior_claim_evidence_matrix.md').read_text(encoding='utf-8')
claim+='''\n\n## 2026-10-28 结构修订补记\n\n本轮保留上表全部实验来源和适用范围。新增内容如下：\n\n| 内容 | 来源 | 证据身份与边界 |\n|---|---|---|\n| IM 背景及经典求解策略 | 本轮 qa/literature_source_check.md 的原文来源 | 既有研究；非本文新增发现 |\n| 共享固定采样世界与候选池数值构造的区别 | StaticGreedy 原文、原稿固定边/按步诊断与精度控制 | 文献联系及对已有结果的解释；不增加理论保证 |\n| 方向相关解释移入讨论 | 原结果 wiki-Vote 入/出度及候选重合数据 | 结构诊断；没有方向干预因果证据 |\n| 精度×耦合与方向干预 | 现有局限导出的研究问题 | 未执行的未来检验，不是实验发现 |\n'''
write('claim_evidence_matrix.md',claim)

summary=(R/'summary_for_editor.txt').read_text(encoding='utf-8')
if 'Relation to prior work' not in summary:
    summary+='''\nRelation to prior work\nThe revised discussion relates fixed sampled realizations to prior coverage-based optimization and distinguishes that established principle from numerical changes in candidate eligibility. It also separates structural direction diagnostics from causal interventions. Joint precision--coupling controls and direction interventions are stated as future tests, not completed evidence.\n'''
write('summary_for_editor.txt',summary)

# Cover letter already has the unchanged title, findings, sample scope and declarations.
# Preserve it rather than invent a new contribution or author statement.
print(json.dumps({'documentation_written':True,'translation_line_locations_corrected':True,'new_experiments':False}))
