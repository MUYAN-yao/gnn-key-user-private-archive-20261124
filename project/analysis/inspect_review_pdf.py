from pathlib import Path
import json
import pypdfium2 as pdfium
from pypdf import PdfReader
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).resolve().parents[1]
OUT=R/'manuscript/resolution_aware_candidate_truncation_submission_v0_1/word_qa'
path=OUT/'manuscript_review_20260921.pdf'
pdf=pdfium.PdfDocument(str(path));reader=PdfReader(path)
summaries=[];thumbs=[]
for i,page in enumerate(pdf):
    im=page.render(scale=1.7).to_pil().convert('RGB')
    im.save(OUT/f'page-{i+1}.png')
    thumb=im.copy();thumb.thumbnail((340,440))
    tile=Image.new('RGB',(360,470),'#dddddd');tile.paste(thumb,((360-thumb.width)//2,20))
    ImageDraw.Draw(tile).text((10,450),f'Page {i+1}',fill='black');thumbs.append(tile)
    text=reader.pages[i].extract_text() or ''
    summaries.append({'page':i+1,'characters':len(text),'start':text[:110],'end':text[-150:]})
    page.close()
for start in range(0,len(thumbs),8):
    canvas=Image.new('RGB',(360*4,470*2),'white')
    for n,tile in enumerate(thumbs[start:start+8]):canvas.paste(tile,((n%4)*360,(n//4)*470))
    canvas.save(OUT/f'overview-{start//8+1}.png')
(OUT/'pagination.json').write_text(json.dumps(summaries,indent=2,ensure_ascii=True),encoding='utf-8')
print(json.dumps(summaries,indent=2,ensure_ascii=True))
