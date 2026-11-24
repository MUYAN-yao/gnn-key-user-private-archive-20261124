from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import json, hashlib

source = Path(r'D:\校创\基于GNN的关键用户识别\manuscript\resolution_aware_candidate_truncation_submission_v0_1\manuscript_review_20260921 - 副本.docx')
work = Path(__file__).parent
ns = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
with ZipFile(source) as z:
    xml = etree.fromstring(z.read('word/document.xml'))
    relxml = etree.fromstring(z.read('word/_rels/document.xml.rels'))
    rels = {r.get('Id'):r.get('Target') for r in relxml}
    lines, blocks = [], []
    for i, element in enumerate(xml.find('w:body',ns)):
        kind = etree.QName(element).localname
        text = ''.join(element.xpath('.//w:t/text() | .//m:t/text()',namespaces=ns))
        style = element.xpath('w:pPr/w:pStyle/@w:val',namespaces=ns)
        images = element.xpath('.//a:blip/@r:embed',namespaces=ns)
        block = {'i':i,'type':kind,'style':style,'text':text,'images':[rels.get(r,r) for r in images]}
        if kind == 'tbl':
            block['rows'] = [[''.join(c.xpath('.//w:t/text() | .//m:t/text()',namespaces=ns)) for c in row.findall('w:tc',ns)] for row in element.findall('w:tr',ns)]
        blocks.append(block)
        lines.append(f'[{i:03d}] [{kind}] [{",".join(style)}] {text}')
        if images: lines.append('IMAGES '+repr(block['images']))
        if kind == 'tbl': lines.extend(' | '.join(r) for r in block['rows'])
    media=[]
    for name in z.namelist():
        if name.startswith('word/media/'):
            data=z.read(name)
            target=work/'docx-media'/Path(name).name
            target.parent.mkdir(exist_ok=True)
            target.write_bytes(data)
            media.append({'name':name,'size':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    report={'blocks':blocks,'media':media,'math_count':len(xml.xpath('//m:oMath',namespaces=ns)),'insertions':len(xml.xpath('//w:ins',namespaces=ns)),'deletions':len(xml.xpath('//w:del',namespaces=ns)),'comments':len(xml.xpath('//w:commentRangeStart',namespaces=ns))}
    (work/'word-structure.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (work/'word-text.txt').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('blocks','media')},ensure_ascii=False))
    print('Blocks',len(blocks),'images',len(media))
    print('\n'.join(lines[:24]))
