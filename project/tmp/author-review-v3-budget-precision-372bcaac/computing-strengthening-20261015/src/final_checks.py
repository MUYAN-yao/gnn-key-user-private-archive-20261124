"""Final mechanical artifact checks after explicit visual review."""
import sys,re,json,hashlib,csv
from pathlib import Path
from pypdf import PdfReader

base=Path(sys.argv[1]).resolve();qa=base/'qa'
render=json.loads((qa/'render_checks.json').read_text())
visual=json.loads((qa/'visual_review.json').read_text())
assert visual['status']=='PASS'
meta=json.loads((base/'manuscript/metadata.json').read_text())
assert 150<=meta['abstract_words']<=250 and 4<=meta['keywords']<=6
main=(base/'manuscript/manuscript.tex').read_text(encoding='utf-8')
results=(base/'manuscript/results_generated.tex').read_text(encoding='utf-8')
source=main+'\n'+results
citations={key for group in re.findall(r'\\cite\{([^}]+)\}',source) for key in group.split(',')}
references=re.findall(r'\\bibitem\{([^}]+)\}',main)
assert len(references)==len(set(references))==19
assert citations==set(references),(citations,set(references))
assert r'\documentclass[smallextended]{svjour3}' in main
assert not re.search(r'\\(?:linespread|baselinestretch|fontsize|geometry)|\\usepackage(?:\[[^]]*\])?\{geometry\}',main)
assert len(re.findall(r'\\begin\{figure\}',results))==5
for name in ['svjour3.cls','svglov3.clo']:
    original=base/'legacy_project/c-users-36024-downloads-texlive2026-20260301/outputs/computing_latex'/name
    assert (base/'manuscript'/name).read_bytes()==original.read_bytes()

figures=[]
for i in range(1,6):
    pdf=PdfReader(base/f'analysis/figures/Fig{i}.pdf');page=pdf.pages[0]
    width=float(page.mediabox.width)/72*25.4;height=float(page.mediabox.height)/72*25.4
    assert abs(width-119)<.01 and height<=195
    fonts=[]
    for ref in page['/Resources']['/Font'].values():
        f=ref.get_object()
        descendants=f.get('/DescendantFonts')
        if descendants:f=descendants[0].get_object()
        desc=f['/FontDescriptor'].get_object()
        assert any(k in desc for k in ['/FontFile','/FontFile2','/FontFile3'])
        fonts.append(str(desc['/FontName']))
    figures.append({'name':f'Fig{i}','width_mm':width,'height_mm':height,'fonts_embedded':fonts})
rows=json.loads((base/'audit/data-rebuild-verification.json').read_text(encoding='utf-8-sig'))
assert len(rows)==16 and all(r['Match'] for r in rows)
snapshot=json.loads((base/'snapshot/source_manifest.json').read_text())
for name,h in snapshot['files'].items():assert hashlib.sha256((base/'snapshot'/name).read_bytes()).hexdigest()==h
analysis=json.loads((base/'analysis/validation.json').read_text());assert analysis['status']=='PASS'
report={'status':'PASS','scope':'author-review artifacts, not author approval or editorial acceptance','pdfs':render,'abstract_words':meta['abstract_words'],'keywords':meta['keywords'],'references_defined_and_cited':19,'figures':figures,'template_files_unchanged':True,'reconstructed_data_files_byte_identical':16,'visual_review':visual,'source_manifest_verified':True,'analysis_validation':analysis,'remaining_author_items':'author_checklist_zh.md'}
(qa/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'status':'PASS','main_pages':render['manuscript']['pages'],'supplement_pages':render['Online_Resource_1']['pages'],'references':19,'figures':5,'data_files_identical':16}))
