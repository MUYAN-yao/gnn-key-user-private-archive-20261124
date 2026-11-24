"""Active-verb contribution revision; reuses the saved-evidence validator."""
from pathlib import Path
import importlib.util,json,sys
R=Path(__file__).resolve().parents[1]
B=R.parent/'contribution-focused-revision-20261028'
spec=importlib.util.spec_from_file_location('prior_revision',B/'src/revise_contributions.py')
m=importlib.util.module_from_spec(spec)
prior_code=(B/'src/revise_contributions.py').read_text(encoding='utf-8').replace("B/'qa/structure_checks.json'", "B/'qa/contribution_checks.json'")
exec(compile(prior_code,str(B/'src/revise_contributions.py'),'exec'),m.__dict__)
m.R=R;m.B=B
m.EN=[
r'''\textbf{We identify how ranking precision alters an apparent budget effect.} Through paired budget comparisons and a post-hoc precision control, we distinguish the observed quality reversal from persistent budget-dependent seed changes. On ca-GrQc, tightening PageRank tolerance exchanges two of 20 candidates and removes the default mean gain-to-loss reversal. This identifies a numerical dependence that a budget scan at default tolerance alone would miss.''',
r'''\textbf{We quantify the spread gains associated with changes in the reference seed set.} Independent paired evaluation measures the magnitude and conditional Monte Carlo uncertainty of these gains. In the historical comparison from $W=1280$ to $W=5120$, 16 of 40 reference sets change, while mean spread increases by 0.01111 nodes across all 40 network--path pairs. The measurements separate seed-set instability from the utility gained through additional sampling.''',
r'''\textbf{We identify which tested candidate pools preserve the reference while reducing selection cost.} At $W=1280$, Degree-4k uses 20 candidates to reproduce all 15 external reference trajectories at lower selection cost in this implementation. Default PageRank-4k reproduces none, and losses on CollegeMsg and wiki-Vote persist under tighter tolerance. These comparisons delimit the transfer of earlier contact-graph agreement and relate computational savings to independently evaluated utility.'''
]
m.ZH=[
r'''\textbf{本文识别排名精度如何改变对表面预算效应的判断。}通过配对预算比较与事后精度对照，我们将观察到的质量反转与持续存在的预算相关种子变化区分开来。在 ca-GrQc 上，收紧 PageRank 容差会替换 20 个候选节点中的两个，并使默认设置下平均表现由增益转为损失的现象消失。由此识别出仅在默认容差下扫描预算时会遗漏的数值依赖。''',
r'''\textbf{本文量化参照种子集合变化所对应的传播收益。}通过配对独立评估，我们测量这些收益的大小及其条件 Monte Carlo 不确定性。在 $W=1280$ 到 $W=5120$ 的历史比较中，40 个参照集合有 16 个发生变化，而全部 40 个网络与路径配对的平均传播量增加 0.01111 个节点。这些测量区分了种子集合的不稳定性与增加采样所获得的效用收益。''',
r'''\textbf{本文识别哪些已测试候选池能够在减少选择成本的同时保持参照结果。}在 $W=1280$ 时，Degree-4k 用 20 个候选节点复现全部 15 条外部参照轨迹，并降低本实现中的选择成本。默认 PageRank-4k 未复现其中任何一条轨迹，且收紧容差后 CollegeMsg 和 wiki-Vote 上的损失仍然存在。这些比较明确了此前接触图一致性的迁移边界，并将计算节省与独立评估的效用联系起来。'''
]

if '--build' in sys.argv:
    m.build()
    report='''# 主动动词贡献修订

本版基于 contribution-focused-revision-20261028。按作者要求，将三项贡献改为主动句“本文识别……”“本文量化……”“本文识别哪些……”，同步英文 We identify / We quantify / We identify。

每项依次写研究动作、作用对象、实施方式或具体证据。第一项用配对预算与事后精度控制识别评价的数值依赖；第二项用配对独立评估量化集合变化对应的收益与条件 Monte Carlo 不确定性；第三项识别已测试条件下能够保持参照并节省计算的候选池。没有将“精确识别”写成未经准确率验证的方法保证，也没有将这些评价步骤宣称为新算法。

新增动作表述不改变研究身份。精度分析仍属事后控制；0.01111 的均值分母仍为全部40个配对；15条轨迹仍来自3图×5路径。计时限于本实现，迁移边界限于已测试网络和设置。方法、实验、结果、讨论、机制图和作者声明保持原样。

本轮重算已有CSV的描述性数字，没有执行新实验，也没有重新进行原始NPZ核验或统计推断。英文编译三次以稳定交叉引用，中文编译两次；编译、数值及资源检查见 qa/contribution_checks.json，页面检查见 qa/render_checks.json。
'''
    m.write(R/'revision_report_zh.md',report)
    readme=m.read(R/'README.md').replace('structure-complete-revision-20261028','contribution-focused-revision-20261028').replace('贡献表述修订','主动动词贡献修订')
    m.write(R/'README.md',readme)
    reproduce=m.read(R/'REPRODUCE.md').replace('src\\revise_contributions.py','src\\revise_action.py')
    m.write(R/'REPRODUCE.md',reproduce+'\n脚本复用相邻 contribution-focused-revision-20261028/src/revise_contributions.py 的复制与核验函数，请保留该前版目录。\n')
    # Synchronize the editor's contribution paragraphs with the final manuscript.
    cover=m.read(R/'cover_letter_draft.txt');start=cover.index('The central finding');end=cover.index('We consider this study')
    plain=lambda x:__import__('re').sub(r'\\textbf\{([^}]+)\}',r'\1',x).replace('$','').replace('--','–')
    m.write(R/'cover_letter_draft.txt',cover[:start]+'\n\n'.join(plain(x) for x in m.EN)+'\n\n'+cover[end:])
if '--verify' in sys.argv:m.verify()
