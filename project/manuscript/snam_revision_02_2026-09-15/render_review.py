"""Render the read-only Word PDF export for page-by-page inspection."""
from pathlib import Path
import json
import pymupdf

HERE = Path(__file__).resolve().parent
QA = HERE / 'qa'
report = {'renderer': 'Word PDF export + PyMuPDF at 110 dpi', 'pages': []}
with pymupdf.open(QA / 'word-render.pdf') as pdf:
    for number, page in enumerate(pdf, 1):
        page.get_pixmap(dpi=110).save(QA / f'page-{number:02d}.png')
        spans = [s for b in page.get_text('dict')['blocks'] if b['type'] == 0
                 for line in b['lines'] for s in line['spans']]
        outside = [s['text'] for s in spans if not page.rect.contains(pymupdf.Rect(s['bbox']))]
        text = page.get_text()
        report['pages'].append({'page': number, 'text_chars': len(text),
            'out_of_page_spans': outside,
            'section_markers': [line for line in text.splitlines() if
                                line.startswith(('6.7', '7.', '8 ', '图 ', 'Abstract'))]})
    report['page_count'] = len(pdf)
(QA / 'page_checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
