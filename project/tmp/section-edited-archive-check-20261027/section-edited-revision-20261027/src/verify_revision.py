"""Check the editorial revision against its preserved source; render every page."""
from pathlib import Path
import argparse, csv, hashlib, json, re, subprocess, shutil, logging
from pypdf import PdfReader
from PIL import Image, ImageOps, ImageDraw

R = Path(__file__).resolve().parents[1]
M = R / 'manuscript'
Q = R / 'qa'
BASE = R.parent / 'mechanism-im-grounded-20261023'
parser = argparse.ArgumentParser()
parser.add_argument('--sort-references', action='store_true')
parser.add_argument('--render', action='store_true')
args = parser.parse_args()
source = (M / 'manuscript.tex').read_text(encoding='utf-8')
old_source = (BASE / 'manuscript/manuscript.tex').read_text(encoding='utf-8')

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def abstract(s): return re.search(r'\\begin\{abstract\}(.*?)\\keywords', s, re.S).group(1)
def word_count(s):
    s = re.sub(r'\\[A-Za-z]+', ' ', s)
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", s))
def references(s):
    return {m.group(1): m.group(0).strip() for m in re.finditer(
        r'\\bibitem\{([^}]+)\}.*?(?=\\bibitem|\\end\{thebibliography\})', s, re.S)}

refs_path = M / 'references.tex'
refs = references(refs_path.read_text(encoding='utf-8'))
old_refs = references((BASE / 'manuscript/references.tex').read_text(encoding='utf-8'))
order = list(dict.fromkeys(k.strip() for group in re.findall(r'\\cite\{([^}]+)\}', source) for k in group.split(',')))
assert set(order) == set(refs), (set(order)-set(refs), set(refs)-set(order))
assert refs == old_refs, 'Citation metadata changed'
if args.sort_references:
    refs_path.write_text('\\begin{thebibliography}{99}\n' + '\n\n'.join(refs[k] for k in order)
                        + '\n\\end{thebibliography}\n', encoding='utf-8')
    print('Reordered existing bibliography by first citation; metadata unchanged.')
    raise SystemExit(0)

Q.mkdir(exist_ok=True)
handler=logging.FileHandler(Q/'pdf_parser_warnings.log',mode='w',encoding='utf-8')
logging.getLogger('pypdf').addHandler(handler)
logging.getLogger('pypdf').propagate=False
checks = {'source_package': str(BASE), 'date': '2026-10-27'}
checks['abstract_words'] = {'old': word_count(abstract(old_source)), 'new': word_count(abstract(source))}
checks['source_word_tokens'] = {'old': word_count(old_source), 'new': word_count(source)}
checks['main_figures'] = {'old': old_source.count('\\begin{figure}'), 'new': source.count('\\begin{figure}')}
checks['template_identical'] = all(sha(M / n) == sha(BASE / 'manuscript' / n) for n in ['svjour3.cls','svglov3.clo'])
checks['mechanism_pdf_sha256'] = sha(M / 'FigEvaluationMechanism.pdf')
checks['mechanism_pdf_identical'] = sha(M / 'FigEvaluationMechanism.pdf') == sha(BASE / 'manuscript/FigEvaluationMechanism.pdf')
checks['mechanism_vsdx_sha256'] = sha(BASE / 'figures/im_evaluation_mechanism_v2.vsdx')
checks['bibliography_content_identical'] = refs == old_refs
checks['bibliography_first_citation_order'] = list(refs) == order
checks['author_block_identical'] = source.split('\\author{')[1].split('\\date{}')[0] == old_source.split('\\author{')[1].split('\\date{}')[0]
checks['removed_algorithm_denials'] = all(x not in source for x in ['not a new influence-maximization algorithm', 'We do not claim a new optimization algorithm'])
checks['ai_disclosure_occurrences'] = source.count('OpenAI Codex')
checks['no_ai_subsection'] = '\\subsection{AI' not in source
checks['plot_assets_identical'] = {n:sha(M/n)==sha(BASE/'manuscript'/n) for n in ['Fig1.pdf','Fig2.pdf','Fig3.pdf','Fig4.pdf','FigS1.pdf','FigDirectionMechanism.pdf']}
checks['unchanged_numeric_tables'] = {}
for n in ['primary_table.tex','cost_table.tex','precision_budget_table.tex','transition_table.tex','numbers.tex','supp_tables.tex']:
    a=(M/n).read_text(encoding='utf-8'); b=(BASE/'manuscript'/n).read_text(encoding='utf-8')
    if '\\midrule' in a:
        a='\n'.join(re.findall(r'\\midrule(.*?)\\bottomrule',a,re.S))
        b='\n'.join(re.findall(r'\\midrule(.*?)\\bottomrule',b,re.S))
    checks['unchanged_numeric_tables'][n] = re.findall(r'-?\d+(?:\.\d+)?',a)==re.findall(r'-?\d+(?:\.\d+)?',b)

with (BASE/'analysis/precision_budget/summary_by_budget_precision.csv').open(encoding='utf-8-sig',newline='') as f:
    rows=list(csv.DictReader(f))
checks['precision_values']={}
for graph in ['ca_grqc','college_msg','wiki_vote']:
    for solver in ['default','strict']:
        vals=[r for r in rows if r['dataset']==graph and r['solver']==solver and r['method']=='pagerank_4k']
        checks['precision_values'][graph+'_'+solver]=[{'W':int(r['W']),'loss_percent':round(float(r['loss_percent_mean']),2),'delta_nodes':round(float(r['delta_nodes_mean']),5)} for r in vals]

render_exe = shutil.which('pdftoppm')
if args.render and not render_exe:
    raise RuntimeError('pdftoppm not available')
for stem in ['manuscript','Online_Resource_1']:
    pdf=M/(stem+'.pdf'); reader=PdfReader(pdf)
    text='\n'.join(p.extract_text() or '' for p in reader.pages)
    (Q/(stem+'-text.txt')).write_text(text,encoding='utf-8')
    log=(M/(stem+'.log')).read_text(errors='replace')
    issues=[l for l in log.splitlines() if re.search(r'Overfull|undefined|Float too large|Missing character|Rerun to get|Fatal error',l)]
    checks[stem]={'pages':len(reader.pages),'sha256':sha(pdf),'unresolved': '??' in text, 'compile_issues':issues}
    if args.render:
        render_root=Q/'render-final'
        folder=render_root/stem;folder.mkdir(parents=True,exist_ok=True)
        subprocess.run([render_exe,'-png','-r','115',str(pdf),str(folder/'page')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        files=[folder/f'page-{i:0{len(str(len(reader.pages)))}d}.png' for i in range(1,len(reader.pages)+1)]
        assert len(files)==len(reader.pages)
        thumbs=[]
        for i,file in enumerate(files):
            im=Image.open(file).convert('RGB');thumb=ImageOps.contain(im,(520,740))
            tile=Image.new('RGB',(540,780),'#eeeeee');tile.paste(thumb,((540-thumb.width)//2,5))
            ImageDraw.Draw(tile).text((15,755),f'{stem} page {i+1}',fill='black');thumbs.append(tile)
        for start in range(0,len(thumbs),4):
            contact=Image.new('RGB',(1080,1560),'white')
            for j,tile in enumerate(thumbs[start:start+4]):contact.paste(tile,((j%2)*540,(j//2)*780))
            contact.save(render_root/f'{stem}-contact-{start//4+1}.png')
        checks[stem]['rendered_pages']=len(files)
checks['status']='PASS' if (150<=checks['abstract_words']['new']<=250 and checks['manuscript']['pages']<=25
    and checks['mechanism_pdf_identical'] and checks['template_identical'] and checks['author_block_identical']
    and checks['bibliography_first_citation_order'] and all(checks['unchanged_numeric_tables'].values())
    and all(checks['plot_assets_identical'].values()) and all(not checks[s]['compile_issues'] and not checks[s]['unresolved'] for s in ['manuscript','Online_Resource_1'])) else 'FAIL'
(Q/'revision_checks.json').write_text(json.dumps(checks,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:v for k,v in checks.items() if k!='precision_values'},indent=2,ensure_ascii=False))
if checks['status']!='PASS':raise SystemExit(1)
