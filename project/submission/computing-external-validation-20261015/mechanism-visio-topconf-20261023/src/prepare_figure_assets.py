"""Convert Visio's own vector exports and audit the native drawing/evidence."""
from pathlib import Path
import ast
import csv
import hashlib
import json
import re
import shutil
import zipfile
import xml.etree.ElementTree as ET
import fitz

R=Path(__file__).resolve().parents[1]
B=R.parent/'submission-ready-draft-20261016'
F=R/'figures'
A=R/'audit/evidence_sources'
def read(name):
    with (A/name).open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))
pool=next(x for x in read('candidate_pool_precision_diagnostics.csv') if x['dataset']=='ca_grqc' and x['method']=='pagerank_4k')
assert set(ast.literal_eval(pool['strict_added_ids']))=={'17655','6610'}
assert set(ast.literal_eval(pool['strict_removed_ids']))=={'1488','19865'}
assert int(pool['default_vs_strict_overlap'])==18 and pool['strict_vs_tighter_same_pool']=='True'
rows=[x for x in read('summary_by_budget_precision.csv') if x['dataset']=='ca_grqc' and x['method']=='pagerank_4k' and int(x['W'])==1280]
means={x['solver']:float(x['delta_nodes_mean']) for x in rows}
assert abs(means['default']+.25082)<1e-10 and abs(means['strict']-.02608)<1e-10
t=next(x for x in read('tolerance_effects_summary.csv') if x['dataset']=='ca_grqc' and x['method']=='pagerank_4k' and int(x['W'])==1280)
assert int(t['same_set_count'])==0
native={}
ns={'v':'http://schemas.microsoft.com/office/visio/2012/main'}
with zipfile.ZipFile(F/'evaluation_mechanisms.vsdx') as z:
    media=[n for n in z.namelist() if n.startswith('visio/media/')]
    assert not media
    for n in z.namelist():
        if n.startswith('visio/pages/page') and n.endswith('.xml') and n!='visio/pages/pages.xml' and '/_rels/' not in n:
            root=ET.fromstring(z.read(n))
            shapes=root.findall('.//v:Shape',ns)
            native[n]={'shapes':len(shapes),'editable_text_shapes':sum(bool(''.join(s.itertext()).strip()) for s in root.findall('.//v:Text',ns))}
    assert len(native)==2 and all(x['shapes']>20 for x in native.values())
converted={}
for stem,target in [('mechanism_overview','Fig1_mechanism'),('coupling_counterexample','FigS2_mechanism')]:
    # MuPDF ignores Visio's stylesheet selectors. Materialize the existing
    # styles as presentation attributes; retain all exported coordinates/text.
    source_svg=(F/(stem+'.svg')).read_text(encoding='utf-8')
    css={name:dict(re.findall(r'([\w-]+)\s*:\s*([^;]+)',body)) for name,body in re.findall(r'\.(st\d+)\s*\{([^}]+)\}',source_svg)}
    root=ET.fromstring(source_svg)
    def materialize(element,parent_size=12):
        attrs={}
        for name in element.get('class','').split(): attrs.update(css.get(name,{}))
        attrs.update(dict(re.findall(r'([\w-]+)\s*:\s*([^;]+)',element.get('style',''))))
        size=attrs.get('font-size',str(parent_size))
        size=parent_size*float(size[:-2]) if size.endswith('em') else float(size.replace('px','').replace('pt',''))
        if 'font-size' in attrs:attrs['font-size']=str(size)
        if 'font-family' in attrs:attrs['font-family']='Helvetica'
        for key,value in attrs.items():element.set(key,value)
        element.attrib.pop('class',None)
        for child in element: materialize(child,size)
    materialize(root)
    normalized=F/(stem+'_portable.svg')
    normalized.write_bytes(ET.tostring(root,encoding='utf-8',xml_declaration=True))
    svg=fitz.open(normalized)
    data=svg.convert_to_pdf()
    pdf=fitz.open('pdf',data)
    # Scale the page to the journal's 119 mm column without rasterization.
    source=pdf[0]
    scale=(119/25.4*72)/source.rect.width
    final=fitz.open(); p=final.new_page(width=source.rect.width*scale,height=source.rect.height*scale)
    p.show_pdf_page(p.rect,pdf,0)
    final.save(F/(stem+'.pdf'),garbage=4,deflate=True)
    final[0].get_pixmap(dpi=240).save(F/(stem+'_preview.png'))
    assert not final[0].get_images(full=True), 'vector conversion must not rasterize'
    assert 'ca-GrQc' in final[0].get_text() if stem=='mechanism_overview' else 'submodularity' in final[0].get_text()
    converted[stem]={'width_mm':119,'height_mm':final[0].rect.height*25.4/72,'raster_images':0,'fonts':final[0].get_fonts(full=True)}
    shutil.copy2(F/(stem+'.pdf'),R/'manuscript'/(target+'.pdf'))
    final.close();pdf.close();svg.close()
# Numeric plot filenames match the new printed numbering.
for old,new in [('Fig1.pdf','Fig2_loss.pdf'),('Fig4.pdf','Fig3_precision.pdf'),('Fig2.pdf','Fig4_transitions.pdf'),('Fig3.pdf','Fig5_cost.pdf')]:
    source=B/'manuscript'/old
    if source.is_file():shutil.copy2(source,R/'manuscript'/new)
    else:assert (R/'manuscript'/new).is_file(), new
result={'status':'PASS','native_pages':native,'media_files':media,'vector_conversion':converted,'observed_ca_grqc':{'default_mean_delta':means['default'],'strict_mean_delta':means['strict'],'changed_sets':5,'pool_shared':18},'pdf_route':'Visio native SVG -> MuPDF vector PDF, resized to 119 mm; native Visio fixed-format exporter unavailable'}
(R/'qa/figure_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
