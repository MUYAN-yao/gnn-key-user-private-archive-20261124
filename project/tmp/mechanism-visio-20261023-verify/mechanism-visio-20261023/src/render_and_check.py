"""Render every page using the available Python PDF renderer; inspect separately."""
from pathlib import Path
import re,json,hashlib
import fitz
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).resolve().parents[1];Q=R/'qa';Q.mkdir(exist_ok=True);M=R/'manuscript'
checks={};old=R.parents[1]/'computing-strengthening-20261015'
for stem in ['manuscript','Online_Resource_1']:
    path=M/(stem+'.pdf');doc=fitz.open(path);folder=Q/stem;folder.mkdir(exist_ok=True);thumbs=[];texts=[];outside=[];fonts=set()
    for i,page in enumerate(doc):
        pix=page.get_pixmap(matrix=fitz.Matrix(1.6,1.6),alpha=False);pix.save(folder/f'page-{i+1:02}.png');texts.append(page.get_text())
        for b in page.get_text('blocks'):
            if b[0]<0 or b[1]<0 or b[2]>page.rect.width+.1 or b[3]>page.rect.height+.1:outside.append([i+1,list(b[:4])])
        for f in page.get_fonts():fonts.add(tuple(f))
        img=Image.open(folder/f'page-{i+1:02}.png').convert('RGB');thumb=ImageOps.contain(img,(460,650));tile=Image.new('RGB',(480,690),'#eeeeee');tile.paste(thumb,((480-thumb.width)//2,8));ImageDraw.Draw(tile).text((15,665),f'{stem} page {i+1}',fill='black');thumbs.append(tile)
    for start in range(0,len(thumbs),4):
        sheet=Image.new('RGB',(960,1380),'white')
        for j,tile in enumerate(thumbs[start:start+4]):sheet.paste(tile,((j%2)*480,(j//2)*690))
        sheet.save(Q/f'{stem}-contact-{start//4+1}.png')
    text='\n'.join(texts);(Q/(stem+'-extracted.txt')).write_text(text,encoding='utf-8');log=(M/(stem+'.log')).read_text(errors='replace')
    issues=[line for line in log.splitlines() if any(s in line for s in ['Overfull','undefined','Float too large','Missing character','Rerun to get'])]
    checks[stem]={'pages':len(doc),'all_pages_rendered':True,'pdf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'issues':issues,'unresolved_markers':'??' in text,'outside_page_text_blocks':outside,'fonts':[list(f) for f in sorted(fonts)]}
src=(M/'manuscript.tex').read_text(encoding='utf-8');abstract=re.search(r'\\begin\{abstract\}(.*?)\\keywords',src,re.S).group(1);words=re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*",abstract)
citations={k.strip() for x in re.findall(r'\\cite\{([^}]+)\}',src) for k in x.split(',')};refs=set(re.findall(r'\\bibitem\{([^}]+)\}',(M/'references.tex').read_text(encoding='utf-8')))
checks['text']={'abstract_words':len(words),'keywords':src.split('\\keywords{')[1].split('}')[0].count('\\and')+1,'citation_keys':len(citations),'reference_entries':len(refs),'missing_citations':sorted(citations-refs),'uncited_entries':sorted(refs-citations),'class_unchanged':all((M/f).read_bytes()==(old/'manuscript'/f).read_bytes() for f in ['svjour3.cls','svglov3.clo'])}
figures={}
for f in (R/'analysis/figures').glob('*.pdf'):
    d=fitz.open(f);pg=d[0];figures[f.name]={'width_mm':pg.rect.width*25.4/72,'height_mm':pg.rect.height*25.4/72,'fonts':[list(x) for x in pg.get_fonts()]};assert abs(figures[f.name]['width_mm']-119)<.1
checks['figures']=figures
checks['status']='PASS' if 150<=len(words)<=250 and checks['manuscript']['pages']<=25 and not(citations-refs) and not(refs-citations) and all(not v['issues'] and not v['unresolved_markers'] and not v['outside_page_text_blocks'] for k,v in checks.items() if k in ['manuscript','Online_Resource_1']) else 'FAIL'
(Q/'render_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8');print(json.dumps({k:{kk:vv for kk,vv in v.items() if kk not in ['fonts','figures']} if isinstance(v,dict) else v for k,v in checks.items() if k!='figures'},indent=2));assert checks['status']=='PASS'
