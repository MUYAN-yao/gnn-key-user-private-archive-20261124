from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import re, json, shutil, hashlib, unicodedata

ROOT=Path(__file__).resolve().parent.parent
WORK=ROOT/'work'
OUT=ROOT/'outputs'/'computing_latex'
OUT.mkdir(parents=True,exist_ok=True)
SOURCE=Path(r'D:\校创\基于GNN的关键用户识别\manuscript\resolution_aware_candidate_truncation_submission_v0_1')
DOCX=SOURCE/'manuscript_review_20260921 - 副本.docx'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
def plain(e): return ''.join(e.xpath('.//w:t/text() | .//m:t/text()',namespaces=NS))
def esc(s):
    # Represent source typography in portable PDFLaTeX syntax.
    s=s.replace('–','--').replace('—','---').replace('−','-').replace('’',"'").replace('‘',"'").replace('“','``').replace('”',"''")
    chars={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}','\u00a0':'~','×':r'\(\times\)','±':r'\(\pm\)'}
    return ''.join(chars.get(c,c) for c in s)
MATH_CHARS={'σ':r'\sigma ','ω':r'\omega ','Δ':r'\Delta ','∑':r'\sum ','∈':r'\in ','⊆':r'\subseteq ','⊂':r'\subset ','∩':r'\cap ','∪':r'\cup ','±':r'\pm ','−':'-','ℰ':r'\mathcal{E}','{':r'\{','}':r'\}'}
def mtext(s):
    s=''.join(MATH_CHARS.get(c,c) for c in s)
    return re.sub(r'\bmin\(',r'\\min(',s)
def omml(e):
    name=etree.QName(e).localname
    if name.endswith('Pr'): return ''
    if name=='r':
        text=''.join(e.xpath('m:t/text()',namespaces=NS))
        value=mtext(text)
        script=e.xpath('m:rPr/m:scr/@m:val',namespaces=NS)
        if script==['script'] and text!='ℰ': value=r'\mathcal{'+value+'}'
        if e.xpath('m:rPr/m:sty/@m:val',namespaces=NS)==['p']: value=r'\mathrm{'+value+'}'
        return value
    def arg(n):
        x=e.find('m:'+n,NS)
        return omml(x) if x is not None else ''
    if name=='sSub': return arg('e')+'_{'+arg('sub')+'}'
    if name=='sSup': return arg('e')+'^{'+arg('sup')+'}'
    if name=='sSubSup': return arg('e')+'_{'+arg('sub')+'}^{'+arg('sup')+'}'
    if name=='f': return r'\frac{'+arg('num')+'}{'+arg('den')+'}'
    if name=='rad': return r'\sqrt'+('['+arg('deg')+']' if arg('deg') else '')+'{'+arg('e')+'}'
    if name=='acc':
        char=e.xpath('m:accPr/m:chr/@m:val',namespaces=NS)
        accent=r'\bar' if char and char[0] in ('̅','¯') else r'\widehat'
        return accent+'{'+arg('e')+'}'
    if name in ('oMath','e','sub','sup','num','den','deg'):
        return ''.join(omml(c) for c in e)
    raise ValueError('Unsupported OMML node: '+name)

math_audit=[]
def inline(e,formatting=True,cites=True):
    parts=[]
    for child in e:
        q=etree.QName(child)
        if q.namespace==NS['m'] and q.localname=='oMath':
            result=omml(child)
            math_audit.append({'source':plain(child),'latex':result})
            parts.append(r'\('+result+r'\)')
        elif q.namespace==NS['m'] and q.localname=='oMathPara':
            parts.append(inline(child,formatting,cites))
        elif q.localname=='r' and q.namespace==NS['w']:
            text=''.join(child.xpath('w:t/text()',namespaces=NS))
            result=esc(text)
            if formatting and text.strip():
                props=child.find('w:rPr',NS)
                if props is not None:
                    if props.find('w:i',NS) is not None: result=r'\emph{'+result+'}'
                    if props.find('w:b',NS) is not None: result=r'\textbf{'+result+'}'
                    if props.find('w:vertAlign',NS) is not None:
                        val=props.find('w:vertAlign',NS).get('{'+NS['w']+'}val')
                        if val=='superscript':result=r'\textsuperscript{'+result+'}'
                        elif val=='subscript':result=r'\textsubscript{'+result+'}'
            parts.append(result)
            if child.find('w:br',NS) is not None: parts.append(r'\\ ')
        elif q.localname in ('hyperlink','smartTag','sdt','sdtContent','ins'):
            parts.append(inline(child,formatting,cites))
    result=''.join(parts)
    if cites:
        def cite(match):
            numbers=[]
            for fragment in match.group(1).split(','):
                bounds=re.split(r'--|-',fragment.strip())
                if len(bounds)==2: numbers.extend(range(int(bounds[0]),int(bounds[1])+1))
                else:numbers.append(int(bounds[0]))
            if not all(1<=n<=16 for n in numbers):return match.group()
            return r'\cite{'+','.join('ref'+str(n) for n in numbers)+'}'
        result=re.sub(r'\[([0-9]+(?:\s*(?:--|-|,)\s*[0-9]+)*)\]',cite,result)
    return result

figstems=['Fig1-mechanism-editable','Fig2-experimental-design','Fig2-reference-resolution','FigS1-tie-trajectories','Fig3-candidate-agreement','Fig4-cost-utility','Fig5-set-stability','Fig6-evaluation-uncertainty']
for i,stem in enumerate(figstems,1): shutil.copy2(SOURCE/'figures'/(stem+'.pdf'),OUT/f'Fig{i}.pdf')
shutil.copy2(SOURCE/'figures'/'FigS1-tie-trajectories-source.csv',OUT/'FigS1-tie-trajectories-source.csv')
for name in ('svjour3.cls','svglov3.clo'):shutil.copy2(WORK/'springer-template-mirror'/name,OUT/name)

with ZipFile(DOCX) as z: xml=etree.fromstring(z.read('word/document.xml'))
blocks=list(xml.find('w:body',NS))
title=plain(blocks[0])
abstract=inline(blocks[2])
keywords=plain(blocks[3]).removeprefix('Keywords: ').split('; ')
preamble=r'''% Computing manuscript converted from the user-specified Word copy.
% Compile with PDFLaTeX; all required assets are in this folder.
% Journal-specific requirement: SVJour3, one-column smallextended.
\documentclass[smallextended]{svjour3}
\usepackage{fix-cm}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{mathptmx}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs,tabularx,array}
\usepackage{placeins}
\usepackage{float}
\renewcommand{\topfraction}{0.9}
\renewcommand{\bottomfraction}{0.9}
\renewcommand{\textfraction}{0.05}
\renewcommand{\floatpagefraction}{0.9}
\setlength{\textfloatsep}{8pt plus 2pt minus 2pt}
\usepackage{url}
\usepackage[numbers,sort&compress]{natbib}
\usepackage[hidelinks]{hyperref}
\setlength{\emergencystretch}{2em}
\journalname{Computing}
\smartqed
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}
\begin{document}
'''
header=r'''\title{TITLE}
\titlerunning{Selection resolution and candidate truncation}
\author{\mbox{Jiayue Sun} \and \mbox{Binbin Yong} \and \mbox{Junjie An} \and \mbox{Tianyu Bo} \and \mbox{Shuai Li}}
\authorrunning{Jiayue Sun et al.}
\institute{Jiayue Sun \at School of Artificial Intelligence, Lanzhou University, Lanzhou 730000, China
\and Binbin Yong (corresponding author) \at School of Information Science and Engineering, Lanzhou University, Lanzhou 730000, China \\
\email{yongbb14@lzu.edu.cn}
\and Junjie An, Tianyu Bo and Shuai Li \at Lanzhou University, Lanzhou, China}
\date{}
\maketitle
\begin{abstract}
ABSTRACT
\keywords{KEYWORDS}
\end{abstract}
'''.replace('TITLE',esc(title)).replace('ABSTRACT',abstract).replace('KEYWORDS',r' \and '.join(esc(k) for k in keywords))
output=[preamble,header]
figures=tables=0
pending_table=None
skip=set()
refs=[]
for i,e in enumerate(blocks[4:],4):
    if i in skip:continue
    kind=etree.QName(e).localname
    text=plain(e)
    styles=e.xpath('w:pPr/w:pStyle/@w:val',namespaces=NS)
    if kind=='sectPr':continue
    if kind=='tbl':
        tables+=1
        rows=[]
        for tr in e.findall('w:tr',NS):
            rows.append([' '.join(inline(p,False) for p in cell.findall('w:p',NS)) for cell in tr.findall('w:tc',NS)])
        caption=pending_table or ''
        pending_table=None
        n=len(rows[0])
        if tables==1: spec=r'@{}L{.25\linewidth}L{.32\linewidth}Y@{}'
        elif tables==2:spec=r'@{}lrrrr@{}'
        elif tables==3:spec=r'@{}L{.23\linewidth}L{.34\linewidth}Y@{}'
        else:spec=r'@{}lYYYYY@{}'
        if tables==4:
            rows[0]=[r'Pool',r'Worlds',r'All matches',r'Full-pool controls',r'Restricted matches',r'Median time saving']
            rows=[rows[0]]+[[re.sub(r'Degree (\d+)k',r'Degree \(\1k\)',r[0])]+r[1:] for r in rows[1:]]
        tab=[r'\begin{table}[tbp]',r'\caption{'+caption+'}',r'\label{tab:'+str(tables)+'}',r'\begin{tabularx}{\linewidth}{'+spec+'}',r'\toprule']
        tab.append(' & '.join(r'\textbf{'+x+'}' for x in rows[0])+r' \\')
        tab.append(r'\midrule')
        for row in rows[1:]:tab.append(' & '.join(row)+r' \\')
        tab.extend([r'\bottomrule',r'\end{tabularx}',r'\end{table}'])
        output.append('\n'.join(tab))
        continue
    if re.match(r'^Table \d+\.',text):
        pending_table=re.sub(r'^Table \d+\.\s*','',inline(e,False))
        continue
    if e.xpath('.//*[local-name()="blip"]'):
        figures+=1
        cap=blocks[i+1]
        assert re.match(r'^Fig\. '+str(figures)+r'\b',plain(cap))
        caption=re.sub(r'^Fig\. \d+\s*','',inline(cap,False))
        caption=caption.replace('figures/FigS1-tie-trajectories-source.csv',r'\protect\path{FigS1-tie-trajectories-source.csv}')
        skip.add(i+1)
        placement='H' if figures in (5,6) else '!htbp'
        graphic_width=r'0.9\linewidth' if figures==4 else r'\linewidth'
        output.append('\n'.join([r'\begin{figure}['+placement+']',r'\centering',r'\includegraphics[width='+graphic_width+']{Fig'+str(figures)+'.pdf}',r'\caption{'+caption+'}',r'\label{fig:'+str(figures)+'}',r'\end{figure}']))
        continue
    if styles in (['3'],['4'],['5']):
        heading=re.sub(r'^\d+(?:\.\d+)*\s+','',text)
        if heading=='References':output.append(r'\FloatBarrier');continue
        if heading=='Results':continue  # Results sit within the Experiments section.
        if heading=='Related work and the scope of the present contribution':
            heading,command='Related work','section'
        elif heading=='Statements and Declarations':command='section*'
        elif styles==['3']:command='section'
        elif styles==['4']:command='subsection'
        else:command='subsubsection'
        heading={
            'Resolution-aware evaluation':'Methods',
            'Experimental design':'Experiments',
            'Analysis':'Evaluation measures and analysis',
            'Implications and limits':'Discussion and limitations',
        }.get(heading,heading)
        label={
            'Which pools reproduce the reference, and at what cost?':'sec:candidate-pools-results',
            'Do changed traces also change final sets?':'sec:final-set-changes',
        }.get(heading)
        output.append('\n\\'+command+'{'+esc(heading)+'}'+(r'\label{'+label+'}' if label else ''))
        continue
    if re.match(r'^\d+\. ',text) and i>=115:
        number=int(re.match(r'^(\d+)\.',text)[1])
        ref=re.sub(r'^\d+\.\s*','',text)
        doi=re.search(r'https://doi.org/\S+',ref)
        if doi:ref=esc(ref[:doi.start()].rstrip())+' '+r'\url{'+doi[0]+'}'
        else:ref=esc(ref)
        refs.append(r'\bibitem{ref'+str(number)+'} '+ref)
        continue
    # Source display equations occupy their own Word paragraphs.
    if i in (24,27,33):
        math=e.find('m:oMath',NS)
        if math is None: math=e.find('m:oMathPara/m:oMath',NS)
        formula=omml(math)
        math_audit.append({'source':plain(math),'latex':formula})
        output.append(r'\begin{equation}'+'\n'+formula+'\n'+r'\end{equation}')
    elif text.strip():output.append(inline(e))
output.append(r'\begin{thebibliography}{16}'+'\n'+'\n\n'.join(refs)+'\n'+r'\end{thebibliography}')
output.append(r'\end{document}')
tex='\n\n'.join(output)+'\n'
tex=tex.replace('(Section 4.4)',r'(Section~\ref{sec:final-set-changes})')
tex=tex.replace('identified in Section 4.2',r'identified in Section~\ref{sec:candidate-pools-results}')
(OUT/'manuscript.tex').write_text(tex,encoding='utf-8')
(WORK/'converted-math-audit.json').write_text(json.dumps(math_audit,ensure_ascii=False,indent=2),encoding='utf-8')
assert figures==8 and tables==4 and len(refs)==16 and len(math_audit)==65, (figures,tables,len(refs),len(math_audit))
audit={'source':str(DOCX),'source_sha256':hashlib.sha256(DOCX.read_bytes()).hexdigest(),'math_objects':len(math_audit),'figures':figures,'tables':tables,'references':len(refs),'abstract_words':len(re.findall(r'\b[\w-]+\b',plain(blocks[2]))),'keywords':len(keywords)}
(WORK/'latex-conversion-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(audit,ensure_ascii=False))
