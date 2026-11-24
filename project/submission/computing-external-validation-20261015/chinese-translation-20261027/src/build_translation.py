from pathlib import Path
import json, re, hashlib, subprocess, shutil, logging
from collections import Counter
from pypdf import PdfReader
from PIL import Image
from translation_text import MAIN, PRIMARY, COST, GLOSSARY
R=Path(__file__).resolve().parents[1]
B=R.parent/'structural-language-revision-20261027'
S=B/'manuscript';M=R/'manuscript';A=R/'assets';Q=R/'qa'
def read(p):return p.read_text(encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(S/'manuscript.pdf')=='849dbefb6f25fce96c82fdaa4b3fc09ac76f89a6c7eabfc49f4d31687ece9e18'
source=read(S/'manuscript.tex').splitlines()
for name,mapping,out in [('manuscript.tex',MAIN,'manuscript_zh.tex'),('primary_table.tex',PRIMARY,'primary_table.tex'),('cost_table.tex',COST,'cost_table.tex')]:
    lines=read(S/name).splitlines()
    for n,t in mapping.items():lines[n-1]=t
    text='\n'.join(lines)+'\n'
    if name=='manuscript.tex':
        text=text.replace('\\usepackage[T1]{fontenc}\n','').replace('\\usepackage[utf8]{inputenc}\n','').replace('\\usepackage{mathptmx}',r'\usepackage[UTF8,fontset=windows]{ctex}'+'\n'+r'\setmainfont{Times New Roman}')
        text=text.replace('\\journalname{Computing}','\\journalname{Computing（中文阅读译稿）}')
        text=text.replace('\\begin{document}',r'''\begin{document}
\def\abstractname{摘要}
\def\keywordname{\textbf{关键词}}
\def\figurename{图}
\def\tablename{表}
\def\refname{参考文献}
''')
    (M/out).write_text(text,encoding='utf-8')

# Numeric/semantic preservation: Arabic numerals, symbolic expressions, citations,
# and figure/reference labels are carried directly into each translated block.
checks=[]
def tokens(t):
    t=t.replace('Degree-','Degree ').replace('PageRank-','PageRank ')
    return re.findall(r'(?<![A-Za-z])-?\d+(?:\.\d+)?',t)
for name,mapping in [('manuscript.tex',MAIN),('primary_table.tex',PRIMARY),('cost_table.tex',COST)]:
    lines=read(S/name).splitlines()
    for n,t in mapping.items():
        old=lines[n-1]
        checks.append({'file':name,'line':n,'numbers_equal':Counter(tokens(old))==Counter(tokens(t)),
          'numeric_order_changed_for_chinese_syntax':tokens(old)!=tokens(t),
          'math_equal':re.findall(r'\$.*?\$',old)==re.findall(r'\$.*?\$',t),
          'citations_equal':re.findall(r'\\cite\{[^}]+\}',old)==re.findall(r'\\cite\{[^}]+\}',t),
          'crossrefs_equal':re.findall(r'\\(?:ref|label)\{[^}]+\}',old)==re.findall(r'\\(?:ref|label)\{[^}]+\}',t)})

# Resolve displayed values and source citation numbers for the bilingual reader.
macros=dict(re.findall(r'\\newcommand\{\\(\w+)\}\{([^}]+)\}',read(S/'numbers.tex')))
refs=list(re.finditer(r'\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem|\\end\{thebibliography\})',read(S/'references.tex'),re.S))
cite={m.group(1):str(i+1) for i,m in enumerate(refs)}
labels={'fig:evaluation-mechanism':'1','fig:precision-budget':'2','fig:transitions':'3','tab:data':'1','tab:settings':'2','tab:primary':'3','tab:cost':'4','sec:coupling':'3.2'}
def plain(t):
    for k,v in macros.items():t=t.replace('\\'+k+'{}',v)
    t=re.sub(r'\\cite\{([^}]+)\}',lambda m:'['+', '.join(cite[x] for x in m[1].split(','))+']',t)
    t=re.sub(r'\\ref\{([^}]+)\}',lambda m:labels[m[1]],t)
    t=re.sub(r'\\label\{[^}]+\}','',t)
    t=re.sub(r'\\item\[([^]]+)\]',r'\1 ',t)
    t=re.sub(r'\\(?:section\*?|subsection|paragraph|title|keywords|caption)\{(.*)\}',r'\1',t)
    t=re.sub(r'\\textbf\{([^}]+)\}',r'**\1**',t)
    t=re.sub(r'\\(?:texttt|textit|mbox)\{([^}]+)\}',r'\1',t)
    t=t.replace('\\and','；').replace('\\%','%').replace('~',' ').replace('---','—').replace('--','–')
    t=t.replace('\\footnote{','（脚注：')
    if '（脚注：' in t and t.endswith('}'):t=t[:-1]+'）'
    return t.strip()
logging.getLogger('pypdf').setLevel(logging.ERROR)
pages=[p.extract_text() or '' for p in PdfReader(S/'manuscript.pdf').pages]
def norm(t):return re.sub('[^a-z0-9]','',t.lower())
pn=[norm(x) for x in pages]
def pageof(t):
    t=plain(t);t=re.sub(r'\$.*?\$','',t)
    t=norm(t)
    for length in (80,50,30):
        matches=[i+1 for i,p in enumerate(pn) if t[:length] and t[:length] in p]
        if len(matches)==1:return matches[0]
    return None

figs=[('F001','FigEvaluationMechanism.pdf',35,48,3),('F002','Fig4.pdf',149,156,9),('F003','Fig2.pdf',160,167,10)]
for ident,file,_,_,_ in figs:
    shutil.copy2(S/file,A/file)
    subprocess.run(['pdftoppm','-png','-r','180','-singlefile',str(S/file),str(A/ident)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
tables=[('T001',95,97,6,(110,184,450,269),source[97:107]),('T002',116,119,7,(110,168,658,345),source[119:134]),('T003',171,2,11,(110,214,506,313),read(S/'primary_table.tex').splitlines()),('T004',181,2,11,(110,671,510,770),read(S/'cost_table.tex').splitlines())]
for ident,_,_,page,box,_ in tables:
    Image.open(B/'qa/render-final/manuscript'/f'page-{page:02}.png').crop(box).save(A/(ident+'.png'))

blocks=[];figrecords=[]
md=['# 候选受限影响力最大化中的参照预算与排名精度','',
    '**正文全文中英对照译稿**。基线：structural-language-revision-20261027；英文正文 15 页。中文 PDF 另见 manuscript/manuscript_zh.pdf。',
    '本文件覆盖摘要、全部正文、3 幅图、4 张表、作者声明和参考文献。补充材料全文不在本次翻译范围；文中对其引用译为“在线补充材料 1”。',
    '作者姓名保留英文拼写，避免擅自推定中文姓名。参考文献保留原始书目信息。','',
    '## 章节索引','[摘要](#S026) · [引言](#S030) · [相关工作](#S051) · [方法](#S060) · [设置](#S093) · [结果](#S147) · [讨论](#S195) · [结论](#S209) · [声明](#S213)','']
def block(ident,old,new,file,line,kind='paragraph',page=None):
    rec={'id':ident,'page':page if page else pageof(old),'type':kind,'order':len(blocks)+1,'source_file':str(S/file),'source_line':line,'original_text':old,'translation':new,'confidence':'high','refs':re.findall(r'\\ref\{([^}]+)\}',old)}
    blocks.append(rec)
    loc=f'英文 p.{rec["page"]}' if rec['page'] else 'PDF 页码未自动定位；以源码行号为准'
    md.extend([f'<a id="{ident}"></a>',f'**Source:** {loc}；{file}:{line}；{ident}','',f'**Original:** {plain(old)}','',f'**中文:** {plain(new)}',''])
def mtable(lines):
    rows=[]
    for line in lines:
        if '&' not in line:continue
        line=re.sub(r'\\shortstack\{([^}]+)\}',lambda m:m[1].replace('\\\\',' '),line)
        line=line.replace('\\toprule','').replace('\\midrule','')
        rows.append([plain(x.strip()) for x in line.replace('\\\\','').split('&')])
    return '\n'.join(['| '+' | '.join(row)+' |'+ ('\n| '+' | '.join(['---']*len(row))+' |' if i==0 else '') for i,row in enumerate(rows)])
for i,old in enumerate(source,1):
    if i<15 or i in (16,17,18,19,20,21,22) or 96<=i<=107 or 118<=i<=134 or i in (48,156,167):continue
    if i in MAIN:
        new=MAIN[i];kind='heading' if re.match(r'\\(?:section|subsection|title)',old) else 'paragraph'
        block(f'S{i:03}',old,new,'manuscript.tex',i,kind)
    elif i in (64,77,78):block(f'S{i:03}',old,old,'manuscript.tex',i,'equation')
    else:continue
    if i==15:
        block('META01','Jiayue Sun; Binbin Yong (corresponding author); Junjie An; Tianyu Bo; Shuai Li. School of Artificial Intelligence / School of Information Science and Engineering, Lanzhou University, Lanzhou 730000, China; Lanzhou University, Lanzhou, China. Email: yongbb14@lzu.edu.cn','Jiayue Sun；Binbin Yong（通讯作者）；Junjie An；Tianyu Bo；Shuai Li。单位按英文原文：兰州大学人工智能学院、信息科学与工程学院，中国兰州 730000；其余作者单位为兰州大学，中国兰州。邮箱：yongbb14@lzu.edu.cn','manuscript.tex',17,'metadata',1)
    for ident,file,after,caption,page in figs:
        if i!=after:continue
        md.extend([f'<a id="{ident}"></a>',f'### 图 {ident[-1]}',f'**Source:** 英文 p.{page}；置于 S{i:03} 后','',f'![{ident}]({(A/(ident+".png")).as_posix()})',''])
        cid='C'+ident[1:];block(cid,source[caption-1],MAIN[caption],'manuscript.tex',caption,'caption',page)
        figrecords.append({'id':ident,'page':page,'caption_id':cid,'image_path':str(A/(ident+'.png')),'vector_path':str(A/file),'placed_after':f'S{i:03}'})
    for ident,after,caption,page,box,lines in tables:
        if i!=after:continue
        file='manuscript.tex' if ident in ('T001','T002') else ('primary_table.tex' if ident=='T003' else 'cost_table.tex')
        trans=MAIN if file=='manuscript.tex' else (PRIMARY if ident=='T003' else COST)
        orig=source if file=='manuscript.tex' else read(S/file).splitlines()
        md.extend([f'<a id="{ident}"></a>',f'### 表 {ident[-1]}',f'**Source:** 英文 p.{page}；置于 S{i:03} 后','',f'![{ident}]({(A/(ident+".png")).as_posix()})',''])
        block('CT'+ident[1:],orig[caption-1],trans[caption],file,caption,'caption',page)
        tlines=[trans.get(j+1,line) for j,line in enumerate(orig)] if file!='manuscript.tex' else [MAIN.get(j+1,line) for j,line in enumerate(source)]
        if ident=='T001':tlines=tlines[97:107]
        if ident=='T002':tlines=tlines[119:134]
        block(ident+'DATA',mtable(lines),mtable(tlines),file,caption+1,'table',page)
        figrecords.append({'id':ident,'page':page,'caption_id':'CT'+ident[1:],'image_path':str(A/(ident+'.png')),'bbox_pixels_115dpi':box,'placed_after':f'S{i:03}'})
md.extend(['## 参考文献（保留原始书目信息）',''])
for i,m in enumerate(refs,1):block(f'R{i:03}',m[2].strip(),m[2].strip(),'references.tex',read(S/'references.tex')[:m.start()].count('\n')+1,'reference')
md.extend(['## 术语表','','| English | 中文 | 含义与边界 |','|---|---|---|'])
md.extend('| '+' | '.join(row)+' |' for row in GLOSSARY)
md.extend(['','## 阅读提示','本文的“世界”指随机传播实现，“路径”指计算重复；二者都不是独立真实网络。译文保留事后分析身份与条件不确定性的含义，没有把集合一致性译为期望最优性。',''])
(R/'paper.md').write_text('\n'.join(md),encoding='utf-8')
(R/'source_map.json').write_text(json.dumps({'status':'complete main-manuscript translation','paper':{'title':plain(source[14]),'source_type':'pdf-text with authoritative TeX','source_path':str(S/'manuscript.pdf'),'source_pdf_sha256':sha(S/'manuscript.pdf')},'blocks':blocks,'figures':figrecords,'pages':[{'page':i+1,'block_ids':[b['id'] for b in blocks if b['page']==i+1]} for i in range(15)],'glossary':[dict(zip(('term','translation','note'),x)) for x in GLOSSARY]},ensure_ascii=False,indent=2),encoding='utf-8')
(Q/'translation_preservation.json').write_text(json.dumps({'blocks':checks,'mechanism_sha256_identical':sha(S/'FigEvaluationMechanism.pdf')==sha(M/'FigEvaluationMechanism.pdf'),'all_numeric_math_citation_ref_checks':all(all(x[k] for k in ('numbers_equal','math_equal','citations_equal','crossrefs_equal')) for x in checks)},indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'translated_blocks':len(checks),'reader_blocks':len(blocks),'figures_and_tables':len(figrecords),'failed_checks':[x for x in checks if not all(x[k] for k in ('numbers_equal','math_equal','citations_equal','crossrefs_equal'))]},ensure_ascii=False,indent=2))
