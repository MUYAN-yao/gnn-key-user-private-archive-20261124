from pathlib import Path
import re,json,hashlib,collections,logging,subprocess
from pypdf import PdfReader
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];B=R.parent/'budget-interpretation-revision-20261031';Q=R/'qa'
read=lambda p:p.read_text(encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
baseline=json.loads(read(Q/'baseline_hashes.json'))
assert all(sha(B/p)==h for p,h in baseline.items())
protected={}
for folder in ['manuscript','chinese/manuscript','analysis']:
    for p in (R/folder).rglob('*'):
        if not p.is_file():continue
        rel=p.relative_to(R)
        if p.suffix in ['.png','.svg','.csv','.json'] or (p.suffix=='.pdf' and p.stem not in ['manuscript','manuscript_zh']) or (p.suffix=='.tex' and p.stem not in ['manuscript','manuscript_zh']):
            assert sha(p)==sha(B/rel),str(rel)
            protected[str(rel)]=sha(p)
en=read(R/'manuscript/manuscript.tex');zh=read(R/'chinese/manuscript/manuscript_zh.tex')
num=lambda t:collections.Counter(re.findall(r'(?<![A-Za-z])[-+]?\d+(?:[.,]\d+)*',t[t.index('\\begin{abstract}'):t.index('\\section*')]))
assert num(en)==num(zh)
assert 'OpenAI Codex assisted with basic code development and manuscript drafting.' in en
assert 'OpenAI Codex 协助完成了基础代码与文稿起草。' in zh
for token in ['既不','这些小图对照不会增加','该配对敏感性分析不增加','不是独立成功试验','归档复现记录覆盖','哈希强制校验缺口']:
    assert token not in zh,token
for token in ['neither','The archived reproduction record covers','not independent success trials','The paired sensitivity analysis adds no independent paths']:
    assert token not in en,token
for rel in ['manuscript/manuscript.tex','chinese/manuscript/manuscript_zh.tex']:
    t=read(R/rel);old=read(B/rel)
    assert re.findall(r'\\cite\{([^}]+)\}',t)==re.findall(r'\\cite\{([^}]+)\}',old)
    assert re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}',t,re.S)==re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}',old,re.S)
    assert t.split('\\section*')[-1]==old.split('\\section*')[-1]
    assert '10,000' in t and '0.01111' in t and '0.02608' in t
logging.getLogger('pypdf').setLevel(logging.ERROR)
documents={}
for name,rel in [('english','manuscript/manuscript'),('chinese','chinese/manuscript/manuscript_zh')]:
    p=R/(rel+'.pdf');log=read(R/(rel+'.log'));pages=PdfReader(p).pages
    errors=[s for s in log.splitlines() if any(q in s for q in ['Overfull','undefined','Missing character','Rerun to get'])]
    assert not errors,errors
    text='\n'.join(p.extract_text() or '' for p in pages);assert '??' not in text
    (Q/(name+'_extracted.txt')).write_text(text,encoding='utf-8')
    out=Q/'render'/name;out.mkdir(parents=True,exist_ok=True)
    proc=subprocess.run(['pdftoppm','-r','100','-png',str(p),str(out/'page')],capture_output=True,text=True)
    assert proc.returncode==0
    images=sorted(out.glob('page-*.png'));assert len(images)==len(pages)
    for start in range(0,len(images),4):
        sheet=Image.new('RGB',(1240,1800),'#e8e8e8');draw=ImageDraw.Draw(sheet)
        for j,f in enumerate(images[start:start+4]):
            im=Image.open(f).convert('RGB');im.thumbnail((600,850));x=j%2*620+10;y=j//2*900+35
            sheet.paste(im,(x,y));draw.text((x,y-24),f'{name} / page {start+j+1}',fill='black')
        sheet.save(out/f'contact-{start//4+1:02}.jpg',quality=92)
    documents[name]={'pages':len(pages),'sha256':sha(p),'compile_errors':errors,'underfull_warnings':log.count('Underfull'),'rendered_pages':len(images)}
report={'status':'PASS','baseline_unchanged':True,'protected_asset_count':len(protected),'table_and_figure_files_unchanged':True,'supplement_unchanged':True,'numeric_tokens_bilingual_match':True,'citations_equations_author_declarations_unchanged':True,'requested_AI_footnote_present':True,'specified_defensive_phrases_removed':True,'documents':documents,'no_experiments_executed':True,'visual_inspection':'Recorded separately in render_checks.json'}
(Q/'final_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(Q/'protected_assets.json').write_text(json.dumps(protected,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
