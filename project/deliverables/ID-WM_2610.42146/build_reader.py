import json, re, pathlib, html, hashlib
import pymupdf as fitz
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, KeepTogether, PageBreak, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = pathlib.Path(__file__).parent
SOURCE = ROOT / 'PDFs/Hierarchical_World_Models_with_Implicit_Dynamics.pdf'
doc = fitz.open(SOURCE)
blocks = json.loads((ROOT/'blocks.json').read_text(encoding='utf-8'))
byid = {b['id']: b for b in blocks}
translations = {}
for line in (ROOT/'translations.tsv').read_text(encoding='utf-8-sig').splitlines():
    k, v = line.split('\t', 1)
    translations[k] = v.replace('\\n', '\n')

# Merge PDF fragments into complete paragraphs. Preserve all contributing boxes.
merges = {
    'P01B09':['P02B01'], 'P02B07':['P03B00'], 'P03B09':['P04B01'],
    'P04B03':['P04B04'], 'P04B10':['P04B11','P04B12'],
    'P04B14':['P04B15','P04B16','P04B17'], 'P04B18':['P05B00'],
    'P05B01':[f'P05B{i:02}' for i in range(2,10)], 'P05B10':['P05B11'],
    'P05B21':[f'P05B{i:02}' for i in range(22,26)],
    'P05B28':['P06B00'], 'P06B05':['P06B06'],
    'P07B09':['P07B10'], 'P07B11':['P08B09'], 'P09B10':['P10B00'],
    'P08B00':[f'P08B{i:02}' for i in range(1,8)],
    'P09B00':['P09B01','P09B02','P09B03'], 'P10B08':['P10B09','P10B10'],
}
removed = {s for a in merges.values() for s in a}
entries=[]
for b in blocks:
    if b['id'] in removed: continue
    e = dict(b)
    components = [b]+[byid[x] for x in merges.get(b['id'],[])]
    e['source_boxes']=[{'page':x['page'],'bbox':x['bbox'],'fragment_id':x['id']} for x in components]
    e['pages']=sorted({x['page'] for x in components})
    e['original']=' '.join(x['original'] for x in components)
    e['translation']=translations[b['id']]
    e['confidence']='high'
    entries.append(e)
E={x['id']:x for x in entries}

# Exact, legible math is preserved as original vector-PDF crops below.
E['P05B21']['original'] = ('Subgoal Search via High-level WM. In the first phase, we identify a sequence of latent subgoals '
    's*_0, …, s*_{Hhi} such that s*_0 = s_0 and s*_{Hhi} = s_g. To ensure that each subgoal remains within the '
    'reachable manifold of the low-level WM given its search budget, we constrain the distance between consecutive '
    'subgoals s*_i, s*_{i+1} to be no more than Δ environment steps. We optimize the latent noise variables '
    'z_0, …, z_{Hhi−1} using the Cross-Entropy Method (CEM) to minimize the following planning cost:')
E['P05B10']['original']='where α_j = 1 − β_j and ᾱ_j = ∏_{i=1}^j α_i. This formulation effectively parameterizes the high-level transition dynamics as a deterministic function G_θ(s_t, z_t).'
equations={
 'P04B10':r'q(x_j|x_{j-1}) = N(x_j; sqrt(1-beta_j) x_{j-1}, beta_j I) (1)',
 'P04B14':r'L_diff = E_{x_0,epsilon~N(0,I),j}[||epsilon-epsilon_theta(x_j,j,s_t)||^2] (2)',
 'P05B01':r'x_{j-1} = sqrt(alpha_bar_{j-1}) [(x_j-sqrt(1-alpha_bar_j) epsilon_theta(x_j,j,s_t))/sqrt(alpha_bar_j)] + sqrt(1-alpha_bar_{j-1}) epsilon_theta(x_j,j,s_t) (3)',
}
for k,v in equations.items(): E[k]['original']=v

# Figure/table boxes were checked against all source pages. Captions remain live text.
visuals={
 'P02B00':('F001',2,(108,69,506,226),'fig_01.png'),
 'P04B00':('F002',4,(108,69,506,234),'fig_02.png'),
 'P06B15':('F003',6,(108,624,506,686),'fig_03.png'),
 'P07B06':('F004',7,(108,355,506,436),'fig_04.png'),
 'P08B08':('F005',8,(108,275,506,451),'fig_05.png'),
 'P09B04':('F006',9,(143,156,467,243),'fig_06.png'),
 'P09B05':('F007',9,(108,280,506,421),'fig_07.png'),
 'P10B06':('F008',10,(162,358,450,448),'fig_08.png'),
 'P08B00':('T001',8,(108,113,506,263),'table_01.png'),
 'P09B00':('T002',9,(227,94,385,152),'table_02.png'),
 'P10B08':('T003',10,(193,660,420,713),'table_03.png'),
 'P04B02':('M001',4,(216,326,396,359),'model_hierarchy.png'),
 'P04B06':('M002',4,(210,426,402,474),'model_components.png'),
 'P04B10':('Q001',4,(220,608,506,624),'equation_01.png'),
 'P04B14':('Q002',4,(216,661,506,682),'equation_02.png'),
 'P05B01':('Q003',5,(207,100,506,168),'equation_03.png'),
 'P05B16':('Q004',5,(261,373,506,392),'equation_04.png'),
 'P05B26':('Q005',5,(239,646,506,662),'equation_05.png'),
 'P06B02':('Q006',6,(238,148,506,169),'equation_06.png'),
 'P06B05':('A001',6,(107,232,506,380),'algorithm_01.png'),
}
assets=ROOT/'assets';assets.mkdir(exist_ok=True)
for key,(vid,page,rect,name) in visuals.items():
    doc[page-1].get_pixmap(matrix=fitz.Matrix(3,3),clip=fitz.Rect(rect)).save(assets/name)
    E[key]['visual']={'id':vid,'page':page,'bbox':rect,'path':'assets/'+name,'confidence':'high'}
    E[key]['type']='caption' if vid[0] in 'FT' else ('algorithm' if vid[0]=='A' else 'equation')
for e in entries:
    e.setdefault('type','heading' if re.match(r'^\d+(?:\.\d+)*\s',e['original']) or e['id'] in ['P01B04','P06B04','P11B03'] else 'text')

# Keep visual evidence beside the paragraph that uses it.
def move_after(key,after):
    e=E[key];entries.remove(e);entries.insert(entries.index(E[after])+1,e)
move_after('P09B04','P09B06')
move_after('P09B05','P10B02')

terms=[
 ('world model (WM)','世界模型'),('implicit dynamics','隐式动力学'),
 ('hierarchical planning','层次化规划'),('reachability','可达性'),
 ('subgoal','子目标'),('long-horizon','长时域'),('inverse dynamics solver','逆动力学求解器'),
 ('latent space','潜在空间'),('Cross-Entropy Method (CEM)','交叉熵方法'),
 ('Model Predictive Control (MPC)','模型预测控制'),('frameskip','跳帧间隔'),
 ('DDPM','去噪扩散概率模型'),('DDIM','去噪扩散隐式模型'),
 ('out-of-distribution (OOD)','分布外'),('coverage (Cov)','覆盖率'),('success rate (SR)','成功率')]
preface=('本译本对应 arXiv:2610.42146v1（2026-10-30）。作者：Gaoyue Zhou、Yvonne Wu、Zichen Jeff Cui、Nicolas Ballas、Mido Assran、Lerrel Pinto、Yann LeCun。'
 '按用户“只下载论文正文”的要求，完整翻译原文第 1–11 页，包括摘要、引言、相关工作、方法、实验、结论、局限性及致谢；参考文献第 12–16 页保留英文，附录第 17–26 页不翻译，也未另行下载 SI。'
 '图表与公式保留原图，图注和算法说明已译为中文。译文为 AI 辅助制作的非官方中文译本；保留作者署名及原文引文编号，具体技术含义以英文原文为准。')
license_note=('原文：https://arxiv.org/abs/2610.42146v1 。许可：CC BY 4.0（https://creativecommons.org/licenses/by/4.0/）。'
 '本版本对原文进行了中文翻译、段落重排和图表裁切；原作者未参与或认可本译本。')
md=['# 具有隐式动力学的层次化世界模型\n','## 译本说明\n',preface+'\n',license_note+'\n',
    '## 页码索引\n',' | '.join(f'[原文 p.{p}](#page-{p})' for p in range(1,12))+'\n',
    '## 术语表\n','| 英文 | 中文 |\n| --- | --- |']+[f'| {a} | {b} |' for a,b in terms]
zh=['# 具有隐式动力学的层次化世界模型\n',preface+'\n',license_note+'\n']
seen=set()
for idx,e in enumerate(entries,1):
    e['reading_order']=idx
    if e['page'] not in seen:
        seen.add(e['page']);md.append(f'\n<a id="page-{e["page"]}"></a>\n## 原文第 {e["page"]} 页\n')
    pages=', '.join(str(p) for p in e['pages'])
    md.append(f'\n<a id="{e["id"]}"></a>\n**Source:** p.{pages} · {e["id"]}\n')
    if 'visual' in e:
        v=e['visual'];md.append(f'<a id="{v["id"]}"></a>\n![{v["id"]}]({v["path"]})\n')
        zh.append(f'\n![{v["id"]}]({v["path"]})\n')
    md.extend(['**Original:** '+e['original']+'\n','**中文:** '+e['translation']+'\n'])
    zh.append(('## ' if e['type']=='heading' else '')+e['translation']+'\n')

refs=[]
for page in range(12,17):
    text=doc[page-1].get_text(clip=fitz.Rect(100,65,510,730),sort=True)
    text=re.sub(r'-\n(?=[a-z])','',text)
    refs.append({'page':page,'text':text.strip()})
md.append('\n## 参考文献（保留英文书目信息）\n')
zh.append('\n## 参考文献（保留英文书目信息）\n')
for r in refs:
    md.append(f'\n### 原文第 {r["page"]} 页\n\n'+r['text']+'\n')
    zh.append(f'\n### 原文第 {r["page"]} 页\n\n'+r['text']+'\n')
reading_notes=('阅读提示（译者说明，非原文）：低层模型本身进行前向状态预测，规划器通过搜索动作序列把它用于逆动力学求解。'
 '原文有关“任何噪声样本均映射为有效状态”等说法属于作者的模型论述，并非额外给出的严格物理保证。'
 '38.5% 与 135% 均按原文表述保留，为相对性能提升，不应改写为百分点。'
 '视觉实验中 ID-WM 在 d=25 时为 0.90，低于 HWM 的 0.96；原文的视觉优势结论针对较难的长时域设置。'
 '正文对第 6.x 节的引用指向英文 PDF 中的附录，已原样保留。')
md.append('\n## 阅读提示\n\n'+reading_notes+'\n')
(ROOT/'paper.md').write_text('\n'.join(md),encoding='utf-8')
(ROOT/'中文版.md').write_text('\n'.join(zh),encoding='utf-8')
(ROOT/'source_map.json').write_text(json.dumps({'title':'Hierarchical World Models with Implicit Dynamics','arxiv':'2610.42146v1','source_url':'https://arxiv.org/pdf/2610.42146v1','license':'CC BY 4.0','translated_pages':list(range(1,12)),'references_original_pages':list(range(12,17)),'excluded_appendix_pages':list(range(17,27)),'glossary':[{'en':a,'zh':b} for a,b in terms],'blocks':entries,'references':refs},ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'translation_notes.md').write_text('# 翻译与核验说明\n\n'+preface+'\n\n'+license_note+'\n\n'+reading_notes+'\n\n提取说明：直接提取可选中文本层，未使用 OCR。删除页边 arXiv 水印和页脚页码；合并跨页段落、上下标碎片及断行连字符。公式和表格采用 216 dpi 原文裁切，避免数学符号文本提取失真。图中英文标签保留，中文图注另列。参考文献保留英文，不翻译作者名和文献题名。原文第 1–11 页未遗漏实质性文本块，所有合并关系均记录在 source_map.json 的 source_boxes 中。\n',encoding='utf-8')

# Chinese reading PDF. All technical illustrations are preserved at their original aspect ratios.
pdfmetrics.registerFont(TTFont('CN',r'C:\Windows\Fonts\simsun.ttc',subfontIndex=0))
styles={
 'body':ParagraphStyle('body',fontName='CN',fontSize=10.1,leading=17.2,spaceAfter=8,wordWrap='CJK',textColor=colors.HexColor('#202831')),
 'heading':ParagraphStyle('heading',fontName='CN',fontSize=13,leading=20,spaceBefore=12,spaceAfter=9,keepWithNext=True,textColor=colors.HexColor('#173a57'),wordWrap='CJK'),
 'title':ParagraphStyle('title',fontName='CN',fontSize=22,leading=31,spaceAfter=15,textColor=colors.HexColor('#173a57'),wordWrap='CJK'),
 'note':ParagraphStyle('note',fontName='CN',fontSize=8.5,leading=14,spaceAfter=8,wordWrap='CJK',textColor=colors.HexColor('#596773')),
 'caption':ParagraphStyle('caption',fontName='CN',fontSize=9.2,leading=15,spaceAfter=10,wordWrap='CJK'),
}
def text_para(text,style='body'):
    # Chinese font provides letters and Chinese; preserve symbols visibly using plain notation.
    for a,b in {'₀':'0','₁':'1','²':'^2','¹':'1','³':'3','˒':',','ŝ':'s_hat','ᾱ':'alpha_bar','≤':'<=','−':'-','∼':'~','‖':'||','∈':' in ','←':' <- ','θ':'theta','ε':'epsilon'}.items():
        text=text.replace(a,b)
    para_style=styles[style]
    if text.endswith('：'):
        para_style=ParagraphStyle('keep_intro',parent=para_style,keepWithNext=True)
    return Paragraph(html.escape(text).replace('\n','<br/>'),para_style)
story=[text_para('具有隐式动力学的\n层次化世界模型','title'),text_para('Hierarchical World Models with Implicit Dynamics','note'),text_para('ID-WM | arXiv:2610.42146v1 | 正文中文译本 | 2026-11-06','note'),text_para(preface,'note'),text_para(license_note,'note'),Spacer(1,8)]
for e in entries:
    if e['id'] in ['P01B00','P06B04']: continue
    if 'visual' in e:
        v=e['visual']; path=ROOT/v['path']; r=fitz.Rect(v['bbox']);w=460
        if v['id'].startswith('Q'):w=min(430,r.width*1.18)
        if v['id'].startswith('M'):w=min(380,r.width*1.25)
        if v['id']=='T002':w=310
        if v['id']=='T003':w=400
        h=w*r.height/r.width
        im=Image(str(path),width=w,height=h)
        im.hAlign='CENTER'
        label=text_para(e['translation'],'caption')
        # Small exhibits and captions stay together; larger algorithms may split by live paragraphs.
        exhibit=[Spacer(1,5),im,Spacer(1,5),label]
        if e['id']=='P06B05':exhibit.insert(0,text_para(E['P06B04']['translation'],'heading'))
        story.append(KeepTogether(exhibit))
    else:
        style='heading' if e['type']=='heading' or e['id'] in ['P01B04','P11B03'] else 'body'
        story.append(text_para(e['translation'],style))
story.extend([Spacer(1,12),text_para('译者阅读提示','heading'),text_para(reading_notes,'note')])
story.append(text_para('参考文献附于后页，保留原文第 12–16 页的版式。','note'))
def footer(canvas,document):
    canvas.setFont('CN',8);canvas.setFillColor(colors.HexColor('#78848d'))
    canvas.drawString(48,815,'ID-WM | 正文中文译本 | 非官方翻译')
    canvas.drawRightString(547,27,str(document.page))
pdf_temp=ROOT/'chinese_body.pdf'
SimpleDocTemplate(str(pdf_temp),pagesize=(595.28,841.89),rightMargin=48,leftMargin=48,topMargin=48,bottomMargin=48,title='具有隐式动力学的层次化世界模型｜正文中文译本',author='Original authors: Gaoyue Zhou et al.; AI-assisted Chinese translation').build(story,onFirstPage=footer,onLaterPages=footer)
out=fitz.open(pdf_temp)
out.insert_pdf(doc,from_page=11,to_page=15)
out.set_metadata({'title':'具有隐式动力学的层次化世界模型 — 正文中文译本','author':'Gaoyue Zhou et al. (original); AI-assisted translation','subject':'arXiv:2610.42146v1; CC BY 4.0; translated main text pp.1–11 and original references pp.12–16'})
out.save(ROOT/'ID-WM_正文中文版.pdf',garbage=4,deflate=True)
print(json.dumps({'translated_blocks':len(entries),'figures':8,'tables':3,'numbered_equations':6,'chinese_body_pages':len(out)-5,'pdf_total_pages':len(out),'missing_translations':[b['id'] for b in entries if not b['translation']]},ensure_ascii=False))
