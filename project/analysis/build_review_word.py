"""Create a editable Word review manuscript from the maintained Markdown source."""
from pathlib import Path
import re,json,shutil
from copy import deepcopy
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'manuscript/resolution_aware_candidate_truncation_submission_v0_1'
DEST=P/'manuscript_review_20260921.docx'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'

def el(tag,*children,**attrs):
    node=OxmlElement('m:'+tag)
    for key,value in attrs.items():node.set(qn('m:'+key),value)
    for c in children:node.append(c)
    return node
def mr(text):
    t=el('t');t.text=text
    if ' ' in text:t.set(qn('xml:space'),'preserve')
    return el('r',t)

class Math:
    """Restricted TeX grammar for this manuscript, failing on unknown commands."""
    def __init__(self,text):
        self.tokens=re.findall(r'\\[A-Za-z]+|\\.|[{}_^]|[^\\{}_^]',text)
        self.i=0
    def peek(self):return self.tokens[self.i] if self.i<len(self.tokens) else None
    def next(self):
        t=self.peek();self.i+=1;return t
    def sequence(self,stop=None):
        result=[]
        while self.peek() is not None and self.peek()!=stop:
            if self.peek().isspace():self.next();continue
            result.extend(self.atom())
        if stop:
            assert self.next()==stop
        return result
    def argument(self):
        while self.peek() and self.peek().isspace():self.next()
        if self.peek()=='{':self.next();return self.sequence('}')
        return self.atom(False)
    def atom(self,script=True):
        token=self.next()
        syms={r'\sigma':'σ',r'\omega':'ω',r'\Delta':'Δ',r'\in':'∈',r'\subseteq':'⊆',r'\subset':'⊂',r'\cap':'∩',r'\cup':'∪',r'\pm':'±',r'\{':'{',r'\}':'}',r'\,':' ',r'\;':' '}
        if token=='{':base=self.sequence('}')
        elif token in syms:base=[mr(syms[token])]
        elif token in [r'\left',r'\right']:return self.atom(script)
        elif token==r'\frac':base=[el('f',el('num',*self.argument()),el('den',*self.argument()))]
        elif token==r'\sqrt':base=[el('rad',el('radPr',el('degHide',val='1')),el('deg'),el('e',*self.argument()))]
        elif token in [r'\widehat',r'\bar']:
            base=[el('acc',el('accPr',el('chr',val='̂' if token==r'\widehat' else '̅')),el('e',*self.argument()))]
        elif token in [r'\mathbf',r'\mathcal']:
            base=self.argument()
            for r in base:
                if r.tag==qn('m:r'):
                    r.insert(0,el('rPr',el('sty',val='b')) if token==r'\mathbf' else el('rPr',el('scr',val='script')))
        elif token==r'\sum':base=[mr('∑')]
        elif token==r'\min':base=[mr('min')]
        elif token and token.startswith('\\'):raise ValueError('Unsupported math command '+token)
        else:base=[mr(token or '')]
        if script:
            sub=sup=None
            while self.peek() in ['_','^']:
                op=self.next();arg=self.argument()
                if op=='_':sub=arg
                else:sup=arg
            if sub is not None and sup is not None:base=[el('sSubSup',el('e',*base),el('sub',*sub),el('sup',*sup))]
            elif sub is not None:base=[el('sSub',el('e',*base),el('sub',*sub))]
            elif sup is not None:base=[el('sSup',el('e',*base),el('sup',*sup))]
        return base

doc=Document()
sec=doc.sections[0]
sec.page_width=Inches(8.5);sec.page_height=Inches(11)
sec.left_margin=sec.right_margin=Inches(.75)
sec.top_margin=sec.bottom_margin=Inches(.72)
sec.footer_distance=Inches(.3)
normal=doc.styles['Normal'];normal.font.name='Times New Roman';normal.font.size=Pt(11)
normal.paragraph_format.line_spacing=1.12
normal.paragraph_format.space_after=Pt(6)
normal.paragraph_format.widow_control=True
for name,size in [('Title',17),('Heading 1',13),('Heading 2',11.5),('Heading 3',11)]:
    st=doc.styles[name];st.font.name='Times New Roman';st.font.size=Pt(size);st.font.color.rgb=RGBColor(0,0,0);st.font.bold=True
    st.paragraph_format.space_before=Pt(12 if name!='Title' else 0);st.paragraph_format.space_after=Pt(6)
    st.paragraph_format.keep_with_next=True
cap=doc.styles['Caption'];cap.font.name='Times New Roman';cap.font.size=Pt(9.5);cap.font.italic=False
cap.font.color.rgb=RGBColor(0,0,0)
cap.font.bold=False
cap.paragraph_format.line_spacing=1.04;cap.paragraph_format.space_after=Pt(9)
cap.paragraph_format.keep_with_next=False
# Clear theme font/color overrides and decorative template borders.
for name in ['Normal','Title','Heading 1','Heading 2','Heading 3','Caption']:
    st=doc.styles[name]
    for fonts in st.element.xpath('./w:rPr/w:rFonts'):
        for key in list(fonts.attrib):
            if 'Theme' in key or 'theme' in key:del fonts.attrib[key]
    for color in st.element.xpath('./w:rPr/w:color'):
        for key in list(color.attrib):
            if 'theme' in key:del color.attrib[key]
    for border in st.element.xpath('./w:pPr/w:pBdr'):border.getparent().remove(border)
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)
equations=0

def inline(p,text):
    global equations
    pattern=r'(\\\(.*?\\\)|\*\*.*?\*\*|`[^`]+`|\*[^*]+\*)'
    for token in re.split(pattern,text):
        if not token:continue
        if token.startswith(r'\('):
            p._p.append(el('oMath',*Math(token[2:-2]).sequence()));equations+=1
        elif token.startswith('**'):p.add_run(token[2:-2]).bold=True
        elif token.startswith('`'):p.add_run(token[1:-1])
        elif token.startswith('*'):p.add_run(token[1:-1]).italic=True
        else:p.add_run(token)

def paragraph(text,style=None):
    p=doc.add_paragraph(style=style);inline(p,text);return p

text=(P/'manuscript.md').read_text(encoding='utf-8')
lines=text.splitlines();i=0;reference=False;tables=images=0
while i<len(lines):
    line=lines[i].strip()
    if not line:i+=1;continue
    if line.startswith('#'):
        m=re.match(r'(#+)\s+(.*)',line);level=len(m[1]);title=m[2]
        if title=='References':reference=True
        p=paragraph(title,'Title' if level==1 else f'Heading {min(level-1,3)}')
        if level==1:p.alignment=WD_ALIGN_PARAGRAPH.LEFT
        i+=1;continue
    if line==r'\[':
        if doc.paragraphs:doc.paragraphs[-1].paragraph_format.keep_with_next=True
        j=i+1;parts=[]
        while lines[j].strip()!=r'\]':parts.append(lines[j]);j+=1
        p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        math=el('oMath',*Math(' '.join(parts)).sequence())
        p._p.append(el('oMathPara',math));equations+=1
        p.paragraph_format.space_after=Pt(9);i=j+1;continue
    image=re.match(r'!\[([^]]*)\]\(([^)]+)\)',line)
    if image:
        path=P/image[2];p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next=True;p.paragraph_format.space_before=Pt(7);p.paragraph_format.space_after=Pt(5)
        width=7 if images in (0,1,3) else 6.6
        picture=p.add_run().add_picture(str(path),width=Inches(width))
        picture._inline.docPr.set('descr',image[1]);images+=1;i+=1;continue
    if line.startswith('|'):
        data=[]
        while i<len(lines) and lines[i].strip().startswith('|'):
            row=[v.strip() for v in lines[i].strip().strip('|').split('|')]
            if not all(re.fullmatch(r':?-+:?',v) for v in row):data.append(row)
            i+=1
        tables+=1;table=doc.add_table(rows=0,cols=len(data[0]));table.autofit=False
        widths={1:[1.65,2.45,2.9],2:[1.8,1,1.4,1.4,1.4],3:[1.4,2.8,2.8],4:[1,0.65,1.05,1.2,1.35,1.75]}[tables]
        for col,w in zip(table.columns,widths):col.width=Inches(w)
        for ri,values in enumerate(data):
            cells=table.add_row().cells
            for ci,(cell,value) in enumerate(zip(cells,values)):
                cell.width=Inches(widths[ci]);p=cell.paragraphs[0];inline(p,value)
                p.paragraph_format.space_after=Pt(5);p.paragraph_format.space_before=Pt(4);p.paragraph_format.line_spacing=1
                p.paragraph_format.keep_with_next=ri<len(data)-1
                for run in p.runs:run.font.size=Pt(9.5);run.bold=ri==0
                if ri==0:
                    shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'F0F2F4');cell._tc.get_or_add_tcPr().append(shade)
            trPr=table.rows[-1]._tr.get_or_add_trPr();trPr.append(OxmlElement('w:cantSplit'))
            if ri==0:trPr.append(OxmlElement('w:tblHeader'))
        # Thin horizontal rules; no vertical grid.
        borders=OxmlElement('w:tblBorders')
        for tag in ['top','bottom','insideH']:
            edge=OxmlElement('w:'+tag);edge.set(qn('w:val'),'single');edge.set(qn('w:sz'),'4');edge.set(qn('w:color'),'B8BEC4');borders.append(edge)
        table._tbl.tblPr.append(borders)
        continue
    parts=[line];i+=1
    while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','![')) and lines[i].strip()!=r'\[':
        if reference and re.match(r'\d+\. ',lines[i].strip()):break
        parts.append(lines[i].strip());i+=1
    content=' '.join(parts)
    iscaption=content.startswith(('**Fig.','**Table'))
    p=paragraph(content,'Caption' if iscaption else None)
    if content.startswith('**Table'):p.paragraph_format.keep_with_next=True
    if reference:
        p.paragraph_format.left_indent=Inches(.24);p.paragraph_format.first_line_indent=Inches(-.24)
        p.paragraph_format.line_spacing=1.0;p.paragraph_format.space_after=Pt(5)
        for r in p.runs:r.font.size=Pt(10)
    if iscaption:p.paragraph_format.keep_together=True
    if r'\(' in content:p.paragraph_format.keep_together=True

doc.core_properties.title=text.splitlines()[0][2:]
doc.core_properties.author=''
doc.core_properties.subject='Selection resolution and candidate restriction in simulated influence maximization'
assert images==8 and tables==4 and equations>20
if DEST.exists():shutil.copy2(DEST,DEST.with_suffix('.previous.docx'))
doc.save(DEST)
(P/'word_build_audit.json').write_text(json.dumps({'figures':images,'tables':tables,'native_math_objects':equations,'paragraphs':len(doc.paragraphs),'source':'manuscript.md'},indent=2),encoding='utf-8')
print(json.dumps({'docx':str(DEST),'figures':images,'tables':tables,'native_math_objects':equations}))
