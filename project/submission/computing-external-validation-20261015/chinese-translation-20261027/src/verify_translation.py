"""Compile-independent translation checks and full PDF rendering; no experiments."""
from pathlib import Path
import json,re,hashlib,subprocess,logging
from pypdf import PdfReader
from PIL import Image,ImageOps,ImageDraw
from translation_text import MAIN
R=Path(__file__).resolve().parents[1];B=R.parent/'structural-language-revision-20261027'
Q=R/'qa';P=R/'manuscript/manuscript_zh.pdf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
logging.getLogger('pypdf').setLevel(logging.ERROR)
reader=PdfReader(P);text='\n'.join(p.extract_text() or '' for p in reader.pages)
(Q/'manuscript_zh_text.txt').write_text(text,encoding='utf-8')
source=(B/'manuscript/manuscript.tex').read_text(encoding='utf-8').splitlines()
untranslated=[]
for n,line in enumerate(source,1):
    if n<25 or n in MAIN or not line.strip():continue
    # Data rows, pure math and structural LaTeX are retained verbatim.
    if re.match(r'[A-Za-z]',line) and '&' not in line:untranslated.append({'line':n,'text':line})
mapping=json.loads((R/'source_map.json').read_text(encoding='utf-8'))
md=(R/'paper.md').read_text(encoding='utf-8')
assets=re.findall(r'!\[[^]]*\]\(([^)]+)\)',md)
pres=json.loads((Q/'translation_preservation.json').read_text(encoding='utf-8'))
log=(R/'manuscript/manuscript_zh.log').read_text(encoding='utf-8',errors='replace')
issues=[s for s in log.splitlines() if re.search(r'Overfull|Missing character|undefined|Float too large|Fatal error|Rerun to get',s)]
folder=Q/'render';folder.mkdir(exist_ok=True)
subprocess.run(['pdftoppm','-png','-r','115',str(P),str(folder/'page')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
tiles=[];files=[]
for i in range(1,len(reader.pages)+1):
    p=folder/f'page-{i:02}.png';files.append(p)
    im=ImageOps.contain(Image.open(p).convert('RGB'),(520,740))
    tile=Image.new('RGB',(540,780),'#eeeeee');tile.paste(im,((540-im.width)//2,5));ImageDraw.Draw(tile).text((15,755),f'Chinese manuscript page {i}',fill='black');tiles.append(tile)
for start in range(0,len(tiles),4):
    out=Image.new('RGB',(1080,1560),'white')
    for j,tile in enumerate(tiles[start:start+4]):out.paste(tile,((j%2)*540,(j//2)*780))
    out.save(folder/f'contact-{start//4+1}.png')
sourcehash=sha(B/'manuscript/manuscript.pdf')
checks={'pdf_pages':len(reader.pages),'pdf_sha256':sha(P),'source_english_pdf_unchanged':sourcehash==mapping['paper']['source_pdf_sha256'],
 'source_pdf_sha256':sourcehash,'untranslated_body_lines':untranslated,'preservation_checks_pass':pres['all_numeric_math_citation_ref_checks'],
 'main_figure_hashes_unchanged':{x:sha(R/'manuscript'/x)==sha(B/'manuscript'/x) for x in ['FigEvaluationMechanism.pdf','Fig4.pdf','Fig2.pdf']},
 'references_unchanged':sha(R/'manuscript/references.tex')==sha(B/'manuscript/references.tex'),
 'bilingual_pair_counts':[md.count('**Original:**'),md.count('**中文:**')],
 'source_blocks':len(mapping['blocks']),'figure_table_cards':len(mapping['figures']),
 'all_asset_links_exist':all(Path(x).is_file() for x in assets),
 'compile_issues':issues,'unresolved_reference_markers':'??' in text,'rendered_pages':len(files),'new_experiments':False}
checks['status']='PASS' if not(untranslated or issues or checks['unresolved_reference_markers']) and checks['preservation_checks_pass'] and checks['source_english_pdf_unchanged'] and checks['all_asset_links_exist'] and all(checks['main_figure_hashes_unchanged'].values()) else 'FAIL'
(Q/'translation_checks.json').write_text(json.dumps(checks,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(checks,indent=2,ensure_ascii=False))
