"""Revise contribution statements from saved evidence; no experimental execution."""
from pathlib import Path
from collections import Counter
import argparse,csv,difflib,hashlib,json,re,shutil,subprocess
from pypdf import PdfReader
from PIL import Image,ImageOps,ImageDraw

R=Path(__file__).resolve().parents[1]
B=R.parent/'structure-complete-revision-20261028'
P=R.parent/'review-v3-budget-precision/analysis/precision_budget'
E=R.parent/'review-v3-budget-precision/analysis/summary_by_method.csv'

EN=[
r'''\textbf{Ranking precision changes the interpretation of an apparent budget effect.} On ca-GrQc, tightening PageRank tolerance exchanges two of 20 candidates. The default mean gain-to-loss reversal then disappears, although budget-dependent seed changes remain. This post-hoc control shows that the reversal cannot be interpreted as a reference-budget effect independent of ranking precision.''',
r'''\textbf{Reference-set instability can accompany a small average spread improvement.} Increasing $W$ from 1280 to 5120 changes 16 of 40 contact-graph reference sets. The mean independently evaluated spread increase is 0.01111 nodes across all 40 network--path pairs. These measurements distinguish the frequency of seed-set changes from the magnitude of the resulting utility changes.''',
r'''\textbf{Degree and PageRank agreement diverge on the external networks.} At $W=1280$, Degree-4k reproduces all 15 full-reference trajectories using 20 candidates and less selection time in this implementation. Default PageRank-4k reproduces none; losses on CollegeMsg and wiki-Vote persist under tighter tolerance. The comparison identifies limits to the earlier contact-graph agreement and ties the observed cost savings to preservation of the tested reference.'''
]
ZH=[
r'''\textbf{排名精度改变了对表面预算效应的解释。}在 ca-GrQc 上，收紧 PageRank 容差会替换 20 个候选节点中的两个。默认设置下平均表现由增益转为损失的现象随之消失，但预算相关的种子变化仍然存在。这项事后对照表明，不能将该反转解释为独立于排名精度的参照预算效应。''',
r'''\textbf{参照集合不稳定可以与较小的平均传播增益同时出现。}将 $W$ 从 1280 增加到 5120 时，40 个接触图参照集合中有 16 个发生变化。在全部 40 个网络与路径配对中，独立评估的传播量平均增加 0.01111 个节点。这些测量将种子集合变化的频率与相应效用变化的大小区分开来。''',
r'''\textbf{度与 PageRank 的一致性在外部网络上出现分化。}在 $W=1280$ 时，Degree-4k 使用 20 个候选节点复现了全部 15 条全候选参照轨迹，且在本实现中减少了选择时间。默认 PageRank-4k 未复现其中任何一条轨迹；收紧容差后，CollegeMsg 和 wiki-Vote 上的损失仍然存在。这项比较指出了此前接触图一致性的迁移边界，并将实测计算节省与已测试参照的保留联系起来。'''
]

def read(p):return p.read_text(encoding='utf-8-sig')
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def block(t):return re.search(r'\\begin\{enumerate\}.*?\\end\{enumerate\}',t,re.S)[0]
def strip_block(t):return t.replace(block(t),'CONTRIBUTIONS')
def numeric(t):
    t=t.replace('Degree-','Degree ').replace('PageRank-','PageRank ')
    return Counter(re.findall(r'(?<![A-Za-z])-?\d+(?:\.\d+)?',t))

def evidence():
    hs=B/'analysis/historical_reference_transitions.csv'
    hist=[x for x in rows(hs) if x['stage']=='resolution' and x['coupling']=='step' and x['low']=='1280' and x['high']=='5120' and x['k']=='5']
    s=rows(P/'summary_by_budget_precision.csv')
    ca=[x for x in s if x['dataset']=='ca_grqc' and x['method']=='pagerank_4k']
    pool=next(x for x in rows(P/'candidate_pool_precision_diagnostics.csv') if x['dataset']=='ca_grqc' and x['method']=='pagerank_4k')
    ext=[x for x in rows(E) if x['W']=='1280' and x['coupling']=='step' and x['method'] in ['degree_4k','pagerank_4k']]
    assert len(ext)==6
    matches={m:sum(round(float(x['same_order_mean'])*int(x['paths'])) for x in ext if x['method']==m) for m in ['degree_4k','pagerank_4k']}
    mean=sum(float(x['delta_full_high_low']) for x in hist)/len(hist)
    strict=[x for x in s if x['solver']=='strict' and x['dataset'] in ['college_msg','wiki_vote'] and x['method']=='pagerank_4k']
    facts={'history':{'pairs':len(hist),'graphs':len(set(x['dataset'] for x in hist)),'changed_sets':sum(x['same_set']=='0' for x in hist),'mean_delta_nodes':mean,'min_delta':min(float(x['delta_full_high_low']) for x in hist),'max_delta':max(float(x['delta_full_high_low']) for x in hist)},'ca_precision':{'candidate_count':int(pool['candidate_count']),'exchanged_members':int(pool['candidate_count'])-int(pool['default_vs_strict_overlap']),'summary':ca},'external':{'matches':matches,'degree_selection_savings_percent':[float(x['selection_saving_percent_mean']) for x in ext if x['method']=='degree_4k'],'directed_strict_deltas':[{'dataset':x['dataset'],'W':int(x['W']),'delta':float(x['delta_nodes_mean'])} for x in strict]},'sources':{str(p):sha(p) for p in [hs,P/'summary_by_budget_precision.csv',P/'candidate_pool_precision_diagnostics.csv',E]},'scope':'Recomputed descriptive summaries from saved CSVs only; no raw simulation or inference rerun.'}
    assert len(hist)==40 and facts['history']['changed_sets']==16 and abs(mean-.01111)<1e-10
    assert facts['ca_precision']['exchanged_members']==2 and facts['ca_precision']['candidate_count']==20
    assert matches=={'degree_4k':15,'pagerank_4k':0}
    assert all(x['delta']<0 for x in facts['external']['directed_strict_deltas']) and len(strict)==6
    assert all(float(x['delta_nodes_mean'])>0 for x in ca if x['solver']=='strict')
    assert float(next(x for x in ca if x['solver']=='default' and x['W']=='80')['delta_nodes_mean'])>0
    assert float(next(x for x in ca if x['solver']=='default' and x['W']=='1280')['delta_nodes_mean'])<0
    assert min(facts['external']['degree_selection_savings_percent'])>0
    return facts

def build():
    facts=evidence()
    if (R/'manuscript').exists():raise RuntimeError('New-version directory already authored; do not overwrite.')
    for d in ['manuscript','chinese/manuscript','analysis']:
        shutil.copytree(B/d,R/d,ignore=shutil.ignore_patterns('*.aux','*.log','*.out'))
    (R/'qa').mkdir(exist_ok=True);(R/'evidence').mkdir(exist_ok=True)
    for name in ['README.md','REPRODUCE.md','claim_evidence_matrix.md','revision_report_zh.md']:
        shutil.copy2(B/name,R/'evidence'/('prior_'+name))
    shutil.copy2(B/'qa/structure_checks.json',R/'evidence/prior_structure_checks.json')
    changes={}
    for lang,rel,items in [('english','manuscript/manuscript.tex',EN),('chinese','chinese/manuscript/manuscript_zh.tex',ZH)]:
        old=read(B/rel);newblock='\\begin{enumerate}\n'+'\n'.join(f'\\item[({i})] '+v for i,v in enumerate(items,1))+'\n\\end{enumerate}'
        new=old.replace(block(old),newblock,1)
        write(R/rel,new)
        changes[lang]={'old':block(old),'new':newblock}
        write(R/(lang+'_contribution_changes.diff'),''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=B.name,tofile=R.name)))
    write(R/'qa/evidence_checks.json',json.dumps(facts,ensure_ascii=False,indent=2))
    write(R/'contributions_bilingual.md','# 修订后的贡献\n\n'+ '\n\n'.join(f'## {i}\n\n{en}\n\n{zh}' for i,(en,zh) in enumerate(zip(EN,ZH),1)))
    write(R/'qa/baseline_hashes.json',json.dumps({str(p.relative_to(B)):sha(p) for d in ['manuscript','chinese/manuscript','analysis'] for p in (B/d).rglob('*') if p.is_file()},indent=2))
    for name in ['summary_for_editor.txt','cover_letter_draft.txt','claim_evidence_matrix.md']:
        shutil.copy2(B/name,R/name)
    summary=read(R/'summary_for_editor.txt')
    start=summary.index('Principal findings');end=summary.index('Scope and value')
    plain=lambda s:re.sub(r'\\textbf\{([^}]+)\}',r'\1',s).replace('$','').replace('--','–')
    write(R/'summary_for_editor.txt',summary[:start]+'Principal findings\n'+'\n\n'.join(plain(x) for x in EN)+'\n\n'+summary[end:])
    cover=read(R/'cover_letter_draft.txt')
    start=cover.index('The central finding');end=cover.index('We consider this study')
    replacement='The central finding is a numerical dependence in an apparent budget effect: tightening PageRank tolerance exchanges two of 20 ca-GrQc candidates and removes the default mean gain-to-loss reversal. Two supporting findings quantify the spread consequence of reference changes and the limits of ranking transfer. In the historical high-budget comparison, 16 of 40 reference sets change while the mean spread gain across all 40 pairs is 0.01111 nodes. At the highest tested external budget, degree-based pools reproduce all 15 reference trajectories at lower selection cost, whereas PageRank losses persist on the directed graphs after tightening tolerance. These findings clarify when a quality comparison can be interpreted and what its computational savings preserve.\n\n'
    write(R/'cover_letter_draft.txt',cover[:start]+replacement+cover[end:])
    write(R/'README.md','''# 贡献表述修订 · 2026-10-28

基线：相邻目录 structure-complete-revision-20261028。此次只改写引言的三项贡献，英文与中文同步；同步编辑摘要和 cover letter。原稿其余正文、作者声明、机制图、分析结果和英文补充材料保持不变。

- 英文正文：manuscript/manuscript.pdf；同名 .tex 为源码。
- 中文正文：chinese/manuscript/manuscript_zh.pdf；同名 .tex 为源码。
- 修改说明：revision_report_zh.md。
- 新贡献双语文本：contributions_bilingual.md。
- 数值来源与核对：qa/evidence_checks.json、claim_evidence_matrix.md。
- 本轮检查：qa/contribution_checks.json、qa/render_checks.json。
- 编译及文件核验：REPRODUCE.md。

本轮没有新实验。仅从已保存 CSV 重算支持贡献句的描述性计数和均值，没有重新分析 NPZ，也没有重新进行显著性检验。中文稿用于阅读核对，图内英文和文献题录保留；补充材料沿用英文原版。
''')
    write(R/'revision_report_zh.md','''# 贡献段为什么重写

原来的第二项“需要单独评价效用”和第三项“节省具有范围”主要描述报告要求。它们没有把结果说出来，也容易让配对评价、独立评估这些通行做法看起来像创新。本轮将三项改为可对应具体结果的经验发现。

1. 核心发现：ca-GrQc 的表面预算反转依赖排名精度。严格容差替换两个候选节点后，平均增益转损失现象消失；种子仍随预算变化。贡献在于识别了原来预算扫描会混淆的数值依赖，不能泛化为所有预算效应均由 PageRank 误差造成。
2. 支撑发现：参照集合变化的频率与传播收益变化的大小可以分离。历史高预算比较中 16/40 个集合变化，但全部 40 个配对的平均收益增加为 0.01111 个节点。此均值不是仅对变化的 16 个集合求得；它不证明等效，也不代表每条路径收益都接近零。原结果中的范围与不确定性继续保留。
3. 支撑发现：相同 4k 候选规模下，度与 PageRank 在外部网络上呈现不同结果。最高外部预算下前者保持全部 15 条参照轨迹并减少本实现选择时间；默认 PageRank 不匹配这些轨迹，严格容差下两个有向网络仍有损失。它限定了接触图结果的迁移，不能用于宣称度方法普遍无损或网络方向的因果机制已被证明。

第一项承担论文最集中的贡献，后两项提供效用解释和外部适用边界。三项并不等于三种新算法、三个理论定理或三项同等强度的新颖性声明。文字修改不能增加科学证据；其新颖性是否足以支撑期刊发表仍需作者和同行判断。

改动位置限于中英文引言的贡献枚举段。摘要、Methods、Experimental setup、Results、Discussion、Conclusion、作者声明和图表均未改动。没有新增引用；没有变动实验或分析代码。

术语继续沿用既定形式：reference budget（参照预算）、ranking precision（排名精度）、full-candidate reference（全候选参照）、independent spread evaluation（独立传播评估）。避免将“集合不一致”“效用损失”“排名失效”混作同一个结论。
''')
    write(R/'REPRODUCE.md',r'''# 文稿重编译与本轮核验

以本版为工作目录，分别在 manuscript 中用 pdflatex 编译 manuscript.tex 两次，在 chinese/manuscript 中用 xelatex 编译 manuscript_zh.tex 两次。

本机 TeX 程序目录：C:\texlive\2026\bin\windows。
Python：C:\Users\36024\Miniconda3\python.exe。

本版根目录执行：
```powershell
& 'C:\Users\36024\Miniconda3\python.exe' src\revise_contributions.py --verify
```

此命令核查保存 CSV 的描述性计数与均值、原版未变动、贡献段之外全文一致、图表资源一致、中英数字及公式一致、引用和编译日志，并渲染 PDF；不会执行实验。图像仍须人工查看。

--build 是创建新版本的首次操作；目录已有稿件时会拒绝覆盖。冻结实验与历史复现记录见 evidence/prior_REPRODUCE.md 及前版说明，本轮未重新进行实验复现。
''')
    matrix=read(R/'claim_evidence_matrix.md')
    matrix+='''\n\n## 本轮贡献句的直接证据（2026-10-28）\n\n| 贡献 | 来源与筛选 | 范围 |\n|---|---|---|\n| 排名精度影响反转解释 | review-v3-budget-precision/analysis/precision_budget/summary_by_budget_precision.csv，ca_grqc，pagerank_4k，default/strict，W=80/320/1280；candidate_pool_precision_diagnostics.csv 对应候选重叠 | 事后敏感性控制；五条既有路径；不证明所有预算效应均为数值误差 |\n| 集合变化与平均收益分离 | analysis/historical_reference_transitions.csv，stage=resolution，step，k=5，low=1280，high=5120 | 四接触图×十路径；均值分母全部40配对，不是16个变化配对；无等效保证 |\n| 外部排名表现分化 | review-v3-budget-precision/analysis/summary_by_method.csv，step，W=1280，degree_4k/pagerank_4k；精度汇总中两有向图 strict/pagerank_4k | 3图×5路径；对应本实现选择时间；不确立跨图普遍性、期望最优或方向因果解释 |\n\n本轮读取的绝对路径、SHA-256 和重算值保存在 qa/evidence_checks.json。保留原主张表，其上轮记录不等于本轮新执行。\n'''
    write(R/'claim_evidence_matrix.md',matrix)
    print(json.dumps({'created':str(R),'new_experiments':False,'history':facts['history'],'external_matches':facts['external']['matches']}))

def verify():
    facts=evidence();write(R/'qa/evidence_checks.json',json.dumps(facts,ensure_ascii=False,indent=2))
    q={'new_experiments':False,'raw_array_reanalysis':False,'baseline_unchanged':all(sha(B/p)==v for p,v in json.loads(read(R/'qa/baseline_hashes.json')).items())}
    q['numeric_translation_matches']=all(numeric(a)==numeric(b) for a,b in zip(EN,ZH))
    q['math_translation_matches']=all(re.findall(r'\$.*?\$',a)==re.findall(r'\$.*?\$',b) for a,b in zip(EN,ZH))
    q['protected_assets_unchanged']=all(sha(p)==sha(R/p.relative_to(B)) for d in ['manuscript','chinese/manuscript','analysis'] for p in (B/d).rglob('*') if p.is_file() and p.name not in ['manuscript.tex','manuscript.pdf','manuscript_zh.tex','manuscript_zh.pdf'] and p.suffix not in ['.aux','.log','.out'])
    for tag,rel,stem in [('english','manuscript','manuscript'),('chinese','chinese/manuscript','manuscript_zh')]:
        folder=R/rel;old=read(B/rel/(stem+'.tex'));new=read(folder/(stem+'.tex'))
        q[tag+'_outside_contributions_unchanged']=strip_block(old)==strip_block(new)
        assert all(x in new for x in (EN if tag=='english' else ZH))
        log=read(folder/(stem+'.log'))
        issues=[l for l in log.splitlines() if re.search(r'Overfull|Missing character|undefined|Float too large|Fatal error|Rerun to get',l)]
        pdf=PdfReader(folder/(stem+'.pdf'));txt='\n'.join(p.extract_text() or '' for p in pdf.pages)
        write(R/'qa'/(tag+'_text.txt'),txt)
        render=R/'qa/render'/tag;render.mkdir(parents=True,exist_ok=True)
        subprocess.run(['pdftoppm','-png','-r','110',str(folder/(stem+'.pdf')),str(render/'page')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        tiles=[]
        for i in range(1,len(pdf.pages)+1):
            im=ImageOps.contain(Image.open(render/f'page-{i:02}.png').convert('RGB'),(520,740));tile=Image.new('RGB',(540,780),'#eeeeee');tile.paste(im,((540-im.width)//2,5));ImageDraw.Draw(tile).text((15,755),f'{tag} page {i}',fill='black');tiles.append(tile)
        for start in range(0,len(tiles),4):
            sheet=Image.new('RGB',(1080,1560),'white')
            for j,tile in enumerate(tiles[start:start+4]):sheet.paste(tile,((j%2)*540,(j//2)*780))
            sheet.save(render/f'contact-{start//4+1}.png')
        q[tag]={'pages':len(pdf.pages),'pdf_sha256':sha(folder/(stem+'.pdf')),'compile_issues':issues,'unresolved':'??' in txt,'rendered_pages':len(pdf.pages)}
    q['status']='PASS' if all(v for k,v in q.items() if isinstance(v,bool) and k not in ['new_experiments','raw_array_reanalysis']) and all(not q[k]['compile_issues'] and not q[k]['unresolved'] for k in ['english','chinese']) else 'FAIL'
    write(R/'qa/contribution_checks.json',json.dumps(q,indent=2));print(json.dumps(q,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--build',action='store_true');p.add_argument('--verify',action='store_true');args=p.parse_args()
    if args.build:build()
    if args.verify:verify()
