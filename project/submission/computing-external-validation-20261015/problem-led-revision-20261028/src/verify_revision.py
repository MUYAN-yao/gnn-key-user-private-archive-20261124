"""Read-only evidence checks plus PDF rendering. Never invokes experiment code."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,csv,subprocess,logging
from pypdf import PdfReader
from PIL import Image,ImageOps,ImageDraw
from revise_paper import EN,ZH
R=Path(__file__).resolve().parents[1];B=R.parent/'structural-language-revision-20261027';Q=R/'qa'
def read(p):return p.read_text(encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def nums(t):return Counter(re.findall(r'(?<![A-Za-z])-?\d+(?:\.\d+)?',t.replace('Degree-','Degree ').replace('PageRank-','PageRank ')))
old=read(B/'manuscript/manuscript.tex');new=read(R/'manuscript/manuscript.tex')
ol=old.splitlines();nl=new.splitlines()
changed=[i+1 for i,(a,b) in enumerate(zip(ol,nl)) if a!=b]
static=[p.name for p in (B/'manuscript').iterdir() if p.is_file() and p.name!='manuscript.tex' and p.suffix in ['.tex','.cls','.clo','.csv']]
static += [p.name for p in (B/'manuscript').glob('*.pdf') if p.name!='manuscript.pdf']
checks={'changed_lines_expected':changed==sorted(EN),'methods_and_setup_unchanged':ol[59:146]==nl[59:146],
 'results_prose_and_numbers_unchanged':all(ol[i-1]==nl[i-1] for i in range(147,194) if i not in EN),
 'statements_unchanged':ol[212:]==nl[212:],'author_block_unchanged':ol[16:24]==nl[16:24],
 'unchanged_assets':{n:sha(B/'manuscript'/n)==sha(R/'manuscript'/n) for n in static},
 'inherited_analysis_unchanged':all(sha(p)==sha(R/p.relative_to(B)) for p in (B/'analysis').rglob('*') if p.is_file()),
 'baseline_unchanged':all(sha(B/p)==h for p,h in json.loads(read(Q/'source_baseline_hashes.json')).items()),
 'figure_count':new.count('\\begin{figure}'),'section_count':new.count('\\section{'),
 'subsections_preserved':old.count('\\subsection{')==new.count('\\subsection{'),
 'abstract_word_count':len(re.findall(r"\b[\w]+(?:[-'][\w]+)*\b",re.search(r'\\begin\{abstract\}\s*(.*?)\\keywords',new,re.S)[1])),
 'new_experiments':False,'full_analysis_rerun':False}
tm=json.loads(read(R/'chinese/translation_map.json'))
checks['translation_numeric_math_refs']=all(nums(v['english'])==nums(v['chinese']) and re.findall(r'\$.*?\$',v['english'])==re.findall(r'\$.*?\$',v['chinese']) and re.findall(r'\\(?:cite|ref|label)\{[^}]+\}',v['english'])==re.findall(r'\\(?:cite|ref|label)\{[^}]+\}',v['chinese']) for v in tm.values())
# Check the retained abstract facts directly against existing summary CSVs.
prec=R.parent/'review-v3-budget-precision/analysis/precision_budget/summary_by_budget_precision.csv'
rows=list(csv.DictReader(prec.open(encoding='utf-8')))
ca=[r for r in rows if r['dataset']=='ca_grqc' and r['method']=='pagerank_4k']
checks['abstract_evidence']={
 'ca_default_80_gain_5_61':any(r['W']=='80' and r['solver']=='default' and round(float(r['loss_percent_mean']),2)==-5.61 for r in ca),
 'ca_default_1280_loss_5_07':any(r['W']=='1280' and r['solver']=='default' and round(float(r['loss_percent_mean']),2)==5.07 for r in ca),
 'ca_strict_no_mean_sign_reversal':all(float(r['loss_percent_mean'])<0 for r in ca if r['solver']=='strict'),
 'directed_strict_losses_persist':all(float(r['loss_percent_mean'])>0 for r in rows if r['dataset'] in ['college_msg','wiki_vote'] and r['method']=='pagerank_4k' and r['solver']=='strict')}
ap=R.parent/'review-v2/analysis/arm_path.csv'
ar=list(csv.DictReader(ap.open(encoding='utf-8')))
degree=[r for r in ar if r['W']=='1280' and r['method']=='degree_4k' and r['coupling']=='step']
checks['abstract_evidence']['degree_15_high_budget_trajectories']=len(degree)==15 and all(r['same_order']=='True' for r in degree)
checks['abstract_evidence_source_sha256']={str(prec):sha(prec),str(ap):sha(ap)}
# Infer the table's exact saved column names rather than reconstructing simulations.
checks['arm_path_columns']=list(ar[0]);checks['arm_path_rows']=len(ar)
refs=re.findall(r'\\cite\{([^}]+)\}',new)
bib=set(re.findall(r'\\bibitem\{([^}]+)\}',read(R/'manuscript/references.tex')))
checks['citation_keys_defined']=all(k in bib for g in refs for k in g.split(','))
checks['citation_sequence_unchanged']=refs==re.findall(r'\\cite\{([^}]+)\}',old)
logging.getLogger('pypdf').setLevel(logging.ERROR)
for tag,folder,stem in [('english',R/'manuscript','manuscript'),('chinese',R/'chinese/manuscript','manuscript_zh')]:
    p=folder/(stem+'.pdf');pdf=PdfReader(p);txt='\n'.join(page.extract_text() or '' for page in pdf.pages)
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
        contact=Image.new('RGB',(1080,1560),'white')
        for j,t in enumerate(tiles[start:start+4]):contact.paste(t,((j%2)*540,(j//2)*780))
        contact.save(render/f'contact-{start//4+1}.png')
    checks[tag]={'pages':len(pdf.pages),'sha256':sha(p),'compile_issues':issues,'unresolved':'??' in txt,'rendered_pages':len(pdf.pages)}
checks['status']='PASS' if all(v for v in checks.values() if isinstance(v,bool) and v not in [checks['new_experiments'],checks['full_analysis_rerun']]) and all(checks['unchanged_assets'].values()) and all(checks['abstract_evidence'].values()) and all(not checks[k]['compile_issues'] and not checks[k]['unresolved'] for k in ['english','chinese']) else 'FAIL'
# Explicit required checks prevent false values from being filtered as intentional non-execution.
required=['changed_lines_expected','methods_and_setup_unchanged','results_prose_and_numbers_unchanged','statements_unchanged','author_block_unchanged','inherited_analysis_unchanged','baseline_unchanged','subsections_preserved','translation_numeric_math_refs','citation_keys_defined','citation_sequence_unchanged']
if not all(checks[k] for k in required):checks['status']='FAIL'
(Q/'revision_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in checks.items() if k not in ['unchanged_assets','abstract_evidence_source_sha256']},ensure_ascii=False,indent=2))
