from pathlib import Path
import hashlib,json,re,collections,subprocess,logging
from pypdf import PdfReader
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];B=R.parent/'concise-prose-revision-20261031';Q=R/'qa'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:p.read_text(encoding='utf-8',errors='replace')
baseline=json.loads(read(Q/'baseline_hashes.json'))
assert all(sha(B/k)==v for k,v in baseline.items())
inputs=json.loads(read(R/'analysis/presentation/source_hashes.json'))
assert all(sha(R.parent/k)==v for k,v in inputs.items())
generated=list((R/'analysis/presentation').glob('*'))+[p for f in ['manuscript','chinese/manuscript'] for p in (R/f).glob('*.tex') if p.name in ['primary_table.tex','input_output_case.tex','precision_output.tex','presentation_supplement.tex']]
before={str(p.relative_to(R)):sha(p) for p in generated}
subprocess.run(['C:/Users/36024/Miniconda3/python.exe',str(R/'src/generate_presentation.py')],check=True)
assert all(sha(R/k)==v for k,v in before.items())
protected={}
for p in (B/'manuscript').iterdir():
 if p.suffix in ['.png','.svg','.pdf'] and p.stem not in ['manuscript','Online_Resource_1']:
  assert sha(p)==sha(R/'manuscript'/p.name);protected[p.name]=sha(p)
for folder in ['manuscript','chinese/manuscript']:
 for name in ['references.tex','numbers.tex','cost_table.tex','FigEvaluationMechanism.pdf']:
  assert sha(R/folder/name)==sha(B/folder/name)
for rel in ['manuscript/manuscript.tex','chinese/manuscript/manuscript_zh.tex']:
 s=read(R/rel);old=read(B/rel)
 assert s.split('\\section*')[-1]==old.split('\\section*')[-1]
 assert re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}',s,re.S)==re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}',old,re.S)
 assert set(re.findall(r'\\cite\{([^}]+)\}',s))==set(re.findall(r'\\cite\{([^}]+)\}',old))
en=read(R/'manuscript/manuscript.tex');zh=read(R/'chinese/manuscript/manuscript_zh.tex')
def nums(s):return collections.Counter(re.findall(r'(?<![A-Za-z])[-+]?\d+(?:[.,]\d+)*',s[s.index('\\begin{abstract}'):s.index('\\section*')]))
diff={'en_only':dict(nums(en)-nums(zh)),'zh_only':dict(nums(zh)-nums(en))}
# Chinese and English use translated syntax but retain the same numeric tokens.
assert not any(diff.values()),diff
logging.getLogger('pypdf').setLevel(logging.ERROR)
docs={}
for name,rel in [('english','manuscript/manuscript'),('chinese','chinese/manuscript/manuscript_zh'),('supplement','manuscript/Online_Resource_1')]:
 pdf=R/(rel+'.pdf');log=read(R/(rel+'.log'));pages=PdfReader(pdf).pages
 errors=[s for s in log.splitlines() if any(k in s for k in ['Overfull','undefined','Missing character','Rerun to get'])]
 assert not errors,(name,errors)
 text='\n'.join(p.extract_text() or '' for p in pages);assert '??' not in text
 (Q/(name+'_extracted.txt')).write_text(text,encoding='utf-8')
 out=Q/'render'/name;out.mkdir(parents=True,exist_ok=True)
 subprocess.run(['pdftoppm','-r','100','-png',str(pdf),str(out/'page')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 images=sorted(out.glob('page-*.png'));assert len(images)==len(pages)
 for start in range(0,len(images),4):
  sheet=Image.new('RGB',(1240,1800),'#e8e8e8');draw=ImageDraw.Draw(sheet)
  for j,f in enumerate(images[start:start+4]):
   im=Image.open(f).convert('RGB');im.thumbnail((600,850));x=j%2*620+10;y=j//2*900+35;sheet.paste(im,(x,y));draw.text((x,y-24),f'{name} page {start+j+1}',fill='black')
  sheet.save(out/f'contact-{start//4+1:02}.jpg',quality=93)
 docs[name]=dict(pages=len(pages),sha256=sha(pdf),compile_errors=errors,rendered_pages=len(images))
abstract=en.split('\\begin{abstract}')[1].split('\\keywords')[0]
count=len(re.findall(r"\b[\w]+(?:[-'][\w]+)*\b",re.sub(r'\\[A-Za-z]+','',abstract)))
report=dict(status='PASS',baseline_unchanged=True,input_hashes_match=True,generated_assets_regenerate_identically=True,mechanism_and_existing_figures_unchanged=True,equations_references_declarations_unchanged=True,bilingual_numeric_tokens_match=True,abstract_word_count_approx=count,documents=docs,no_new_experiments=True,visual_review='See render_checks.json')
(Q/'final_checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(Q/'protected_assets.json').write_text(json.dumps(protected,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
