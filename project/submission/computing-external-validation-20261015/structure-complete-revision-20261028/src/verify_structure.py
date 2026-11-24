"""Protect results and assets; check references/translations; render PDFs. No simulation."""
from pathlib import Path
from collections import Counter
import json,re,hashlib,logging,subprocess
from pypdf import PdfReader
from PIL import Image,ImageOps,ImageDraw
from revise_structure import EN
R=Path(__file__).resolve().parents[1];B=R.parent/'problem-led-revision-20261028';Q=R/'qa'
def read(p):return p.read_text(encoding='utf-8-sig')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def numeric(t):
    t=re.sub(r'\\(?:cite|ref|label)\{[^}]*\}','',t)
    t=t.replace('Degree-','Degree ').replace('PageRank-','PageRank ')
    return Counter(re.findall(r'(?<![A-Za-z])-?\d+(?:\.\d+)?',t))
def section(t,name):return t.split('\\section{'+name+'}',1)[1].split('\\section{',1)[0]
def refs(t):return [k for m in re.findall(r'\\cite\{([^}]+)\}',t) for k in m.split(',')]
old=read(B/'manuscript/manuscript.tex');new=read(R/'manuscript/manuscript.tex')
oldlines=old.splitlines();mapping=json.loads(read(R/'chinese/translation_map.json'))
protected={p.name:sha(p)==sha(R/'manuscript'/p.name) for p in (B/'manuscript').iterdir() if p.is_file() and p.name not in ['manuscript.tex','manuscript.pdf'] and p.suffix not in ['.aux','.out','.log']}
bib=re.findall(r'\\bibitem\{([^}]+)\}',read(R/'manuscript/references.tex'))
errors=[]
for key,v in mapping.items():
    a,b=v['english'],v['chinese']
    if not(numeric(a)==numeric(b) and re.findall(r'\$.*?\$',a)==re.findall(r'\$.*?\$',b) and re.findall(r'\\(?:cite|ref|label)\{[^}]+\}',a)==re.findall(r'\\(?:cite|ref|label)\{[^}]+\}',b)):
        errors.append(key)
checks={
 'baseline_unchanged':all(sha(B/p)==h for p,h in json.loads(read(Q/'baseline_hashes.json')).items()),
 'abstract_unchanged':re.search(r'\\begin\{abstract\}.*?\\end\{abstract\}',old,re.S)[0]==re.search(r'\\begin\{abstract\}.*?\\end\{abstract\}',new,re.S)[0],
 'all_main_numeric_tokens_preserved':numeric(old)==numeric(new),
 'all_inline_math_preserved':re.findall(r'\$.*?\$',old)==re.findall(r'\$.*?\$',new),
 'methods_original_body_preserved':section(old,'Methods').strip() in section(new,'Methods'),
 'experimental_setup_preserved':section(old,'Experimental setup').strip()==section(new,'Experimental setup').replace('\\label{sec:experimental-setup}','',1).strip(),
 'result_observations_preserved':all(line in new for i,line in enumerate(oldlines,1) if 147<=i<=193 and i not in EN),
 'direction_result_numbers_preserved':numeric(oldlines[177])==numeric(EN[178]),
 'direction_interpretation_retained':all(x in new for x in ['consistent with a mismatch between incoming importance and outgoing propagation','Direction was not experimentally reversed, so the diagnostic does not isolate a causal mechanism.']),
 'declarations_unchanged':old.split('\\section*{Statements and Declarations}')[1]==new.split('\\section*{Statements and Declarations}')[1],
 'authors_unchanged':old.split('\\author{')[1].split('\\date{}')[0]==new.split('\\author{')[1].split('\\date{}')[0],
 'protected_assets':protected,
 'saved_analysis_unchanged':all(sha(p)==sha(R/p.relative_to(B)) for p in (B/'analysis').rglob('*') if p.is_file()),
 'citation_keys_defined':all(x in bib for x in refs(new)),
 'first_citation_order_matches_bibliography':list(dict.fromkeys(refs(new)))==bib,
 'no_new_bibliographic_entries':sha(B/'manuscript/references.tex')==sha(R/'manuscript/references.tex'),
 'translation_mismatch_blocks':errors,
 'main_sections':re.findall(r'\\section\{([^}]+)\}',new),
 'intro_citations':list(dict.fromkeys(refs(section(new,'Introduction')))),
 'discussion_citations':list(dict.fromkeys(refs(section(new,'Discussion')))),
 'future_tests_explicit':'\\paragraph{Next tests.}' in new,
 'abstract_words':len(re.findall(r"\b[\w]+(?:[-'][\w]+)*\b",re.search(r'\\begin\{abstract\}\s*(.*?)\\keywords',new,re.S)[1])),
 'new_experiments':False,'analysis_rerun':False}
logging.getLogger('pypdf').setLevel(logging.ERROR)
for tag,folder,stem in [('english',R/'manuscript','manuscript'),('chinese',R/'chinese/manuscript','manuscript_zh')]:
    p=folder/(stem+'.pdf');pdf=PdfReader(p);txt='\n'.join(x.extract_text() or '' for x in pdf.pages)
    (Q/(tag+'_text.txt')).write_text(txt,encoding='utf-8')
    log=read(folder/(stem+'.log'))
    issues=[l for l in log.splitlines() if re.search(r'Overfull|Missing character|undefined|Float too large|Fatal error|Rerun to get',l)]
    render=Q/'render'/tag;render.mkdir(parents=True,exist_ok=True)
    subprocess.run(['pdftoppm','-png','-r','115',str(p),str(render/'page')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    tiles=[]
    for i in range(1,len(pdf.pages)+1):
        im=ImageOps.contain(Image.open(render/f'page-{i:02}.png').convert('RGB'),(520,740))
        tile=Image.new('RGB',(540,780),'#eeeeee');tile.paste(im,((540-im.width)//2,5));ImageDraw.Draw(tile).text((15,755),f'{tag} page {i}',fill='black');tiles.append(tile)
    for start in range(0,len(tiles),4):
        sheet=Image.new('RGB',(1080,1560),'white')
        for j,tile in enumerate(tiles[start:start+4]):sheet.paste(tile,((j%2)*540,(j//2)*780))
        sheet.save(render/f'contact-{start//4+1}.png')
    checks[tag]={'pages':len(pdf.pages),'sha256':sha(p),'compile_issues':issues,'unresolved':'??' in txt,'rendered_pages':len(pdf.pages)}
fail=[k for k,v in checks.items() if isinstance(v,bool) and not v and k not in ['new_experiments','analysis_rerun']]
if errors:fail.append('translation_mismatch_blocks')
if not all(protected.values()):fail.append('protected_assets')
for k in ['english','chinese']:
    if checks[k]['compile_issues'] or checks[k]['unresolved']:fail.append(k+'_pdf')
checks['failed_checks']=fail;checks['status']='PASS' if not fail else 'FAIL'
(Q/'structure_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in checks.items() if k!='protected_assets'},ensure_ascii=False,indent=2))
