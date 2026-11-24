"""Render every PDF page for human visual QA; do not infer visual approval."""
import sys,json,re
from pathlib import Path
import pypdfium2 as pdfium
from pypdf import PdfReader
from PIL import Image,ImageOps,ImageDraw

base=Path(sys.argv[1]).resolve();out=base/'qa';out.mkdir(exist_ok=True)
info={}
for stem in ['manuscript','Online_Resource_1']:
    path=base/'manuscript'/(stem+'.pdf');pdf=pdfium.PdfDocument(path);reader=PdfReader(path)
    pages=out/stem;pages.mkdir(exist_ok=True);thumbs=[]
    for i in range(len(pdf)):
        page=pdf[i];pil=page.render(scale=1.5).to_pil().convert('RGB')
        pil.save(pages/f'page-{i+1:02}.png')
        thumb=ImageOps.contain(pil,(340,460));tile=Image.new('RGB',(360,495),'#dedede')
        tile.paste(thumb,((360-thumb.width)//2,15));ImageDraw.Draw(tile).text((15,477),f'{stem} p{i+1}',fill='black');thumbs.append(tile)
    for start in range(0,len(thumbs),6):
        sheet=Image.new('RGB',(1080,990),'white')
        for j,t in enumerate(thumbs[start:start+6]):sheet.paste(t,((j%3)*360,(j//3)*495))
        sheet.save(out/f'{stem}-contact-{start//6+1}.jpg',quality=90)
    text='\n'.join(p.extract_text() or '' for p in reader.pages)
    (out/(stem+'-extracted.txt')).write_text(text,encoding='utf-8')
    log=(base/'manuscript'/(stem+'.log')).read_text(errors='replace')
    warnings=[line for line in log.splitlines() if any(token in line for token in ['Overfull','Float too large','undefined','Missing character','Rerun to get'])]
    info[stem]={'pages':len(pdf),'text_characters':len(text),'unresolved_markers':'??' in text,'compile_warnings':warnings,'all_pages_rendered':True}
assert info['manuscript']['pages']<=25
assert not any(x['unresolved_markers'] or x['compile_warnings'] for x in info.values()),info
(out/'render_checks.json').write_text(json.dumps(info,indent=2))
print(json.dumps(info))
