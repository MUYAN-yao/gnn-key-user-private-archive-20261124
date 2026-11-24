"""Read-only manuscript validation and PDF rendering. No experiment imports."""
from pathlib import Path
import json,hashlib,re,collections,subprocess,sys,logging
from pypdf import PdfReader
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).resolve().parents[1]
B=R.parent/'contribution-action-revision-20261028'
Q=R/'qa'
def read(p): return p.read_text(encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
baseline=json.loads(read(Q/'baseline_manifest.json'))
checks['original_version_unchanged']=all((B/p).exists() and sha(B/p)==h for p,h in baseline.items())
assert checks['original_version_unchanged']
sources=json.loads(read(Q/'read_source_hashes.json'))
checks['read_evidence_unchanged']=all(sha(Path(p))==h for p,h in sources.items())
assert checks['read_evidence_unchanged']
assets={}
for folder in ['manuscript','chinese/manuscript','analysis']:
    for p in (R/folder).rglob('*'):
        if not p.is_file():continue
        rel=p.relative_to(R); old=B/rel
        if not old.exists(): continue
        if p.suffix.lower() in ['.png','.svg','.jpg','.csv','.npz','.json'] or (p.suffix.lower()=='.pdf' and p.stem not in ['manuscript','manuscript_zh','Online_Resource_1']):
            assert sha(p)==sha(old),str(rel)
            assets[str(rel)]=sha(p)
checks['unchanged_graphs_and_saved_analysis_files']=len(assets)
(Q/'protected_assets.json').write_text(json.dumps(assets,indent=2),encoding='utf-8')
num=lambda s: re.findall(r'(?<![A-Za-z])[-+]?\d+(?:[.,]\d+)*',s)
table_checks={}
for p in (R/'manuscript').glob('*table*.tex'):
    old=B/'manuscript'/p.name
    # Numeric table contents only, excluding captions and labels.
    body=lambda t: '\n'.join(l for l in t.splitlines() if not l.startswith('\\caption'))
    assert num(body(read(p)))==num(body(read(old))),p.name
    table_checks[p.name]=True
checks['numeric_table_contents_unchanged']=table_checks
for rel in ['manuscript/manuscript.tex','chinese/manuscript/manuscript_zh.tex']:
    text=read(R/rel); old=read(B/rel)
    assert text.split('\\section*')[-1]==old.split('\\section*')[-1]
    assert sorted(re.findall(r'\\cite\{([^}]+)\}',text))==sorted(re.findall(r'\\cite\{([^}]+)\}',old))
    assert re.findall(r'\\includegraphics[^\n]+',text)==re.findall(r'\\includegraphics[^\n]+',old)
    # Core scientific formulas unchanged; extra budget identifiers are plain inline text.
    assert re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}',text,re.S)==re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}',old,re.S)
    assert sha((R/rel).parent/'references.tex')==sha((B/rel).parent/'references.tex')
checks['declarations_citations_figure_inputs_equations_unchanged']=True
en=read(R/'manuscript/manuscript.tex'); zh=read(R/'chinese/manuscript/manuscript_zh.tex')
checks['main_text_numeric_tokens_bilingual_match']=collections.Counter(num(en[en.index('\\begin{abstract}'):en.index('\\section*')]))==collections.Counter(num(zh[zh.index('\\begin{abstract}'):zh.index('\\section*')]))
# Translation may include explicit values where English uses spelled-out words.
checks['key_values_present_in_both_languages']=all(v in en and v in zh for v in ['5.61','5.07','0.02608','0.01111','0.061845','0.12720','0.05336','98.40--99.67','10,000','117','132','43'])
assert checks['key_values_present_in_both_languages']
checks['both_arm_budget_explicit']=all(s in en for s in ['for both full-candidate and candidate-restricted','every restricted arm','same-budget full reference','fixed across arms and budgets'])
assert checks['both_arm_budget_explicit']
checks['neutral_contribution']= 'spread gains' not in en and 'spread gains' not in read(R/'cover_letter_draft.txt') and '传播收益。}' not in zh
assert checks['neutral_contribution']
checks['direction_definitions']=all(s in en for s in ['d_i=f_h(S_C;\\eta_i)-f_h(S_F;\\eta_i)','-100\\widehat\\Delta','higher-budget minus lower-budget'])
assert checks['direction_definitions']
title=re.search(r'\\title\{([^}]+)\}',en).group(1)
assert title in read(R/'cover_letter_draft.txt') and title in read(R/'summary_for_editor.txt')
checks['editorial_titles_consistent']=True
abstract=en.split('\\begin{abstract}')[1].split('\\keywords')[0]
checks['english_abstract_words']=len(re.findall(r"\b[\w]+(?:[-'][\w]+)*\b",re.sub(r'\\[A-Za-z]+','',abstract)))
logging.getLogger('pypdf').setLevel(logging.ERROR)
docs={}
for name,rel in [('english','manuscript/manuscript'),('chinese','chinese/manuscript/manuscript_zh'),('supplement','manuscript/Online_Resource_1')]:
    p=R/(rel+'.pdf');log=read(R/(rel+'.log'))
    failures=[line for line in log.splitlines() if any(s in line for s in ['Overfull','undefined','Missing character','Rerun to get','There were undefined'])]
    assert not failures,(name,failures)
    pages=PdfReader(p).pages
    text='\n'.join(x.extract_text() or '' for x in pages)
    assert '??' not in text
    (Q/(name+'_extracted.txt')).write_text(text,encoding='utf-8')
    out=Q/'render'/name;out.mkdir(parents=True,exist_ok=True)
    result=subprocess.run(['pdftoppm','-r','110','-png',str(p),str(out/'page')],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    images=sorted(out.glob('page-*.png'))
    assert len(images)==len(pages)
    sheets=[]
    for start in range(0,len(images),4):
        canvas=Image.new('RGB',(1240,1800),'#e8e8e8');draw=ImageDraw.Draw(canvas)
        for slot,source in enumerate(images[start:start+4]):
            im=Image.open(source).convert('RGB');im.thumbnail((600,850))
            x=(slot%2)*620+10;y=(slot//2)*900+35
            canvas.paste(im,(x,y));draw.text((x,y-24),f'{name} / page {start+slot+1}',fill='black')
        target=out/f'contact-{start//4+1:02}.jpg';canvas.save(target,quality=92);sheets.append(str(target))
    docs[name]=dict(pages=len(pages),sha256=sha(p),compile_errors=failures,underfull_warnings=log.count('Underfull'),font_warning='There are no bold math fonts' in log,rendered_pages=len(images),contact_sheets=sheets,renderer_stderr=result.stderr[:1500])
checks['documents']=docs
checks['scope']='No new experiments. No seed search, propagation, training, or runner execution. PDF compilation and saved-result metadata/CSV checks only.'
checks['visual_review']='See render_checks.json; rendering alone is not visual approval.'
(Q/'final_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in checks.items() if k!='documents'},ensure_ascii=False,indent=2))
print(json.dumps({k:{'pages':v['pages'],'rendered':v['rendered_pages']} for k,v in docs.items()},indent=2))
