from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

root = Path(__file__).resolve().parent.parent
source = root / 'outputs' / 'computing_latex' / 'manuscript_大纲修订版.pdf'
target = root / 'outputs' / 'computing_latex' / 'manuscript_紧凑阅读版_非投稿.pdf'

reader = PdfReader(source)
writer = PdfWriter()
writer.clone_document_from_reader(reader)

# The journal template typesets a 337 pt wide column on A4, with a wide
# unprinted area at the right.  All visible content lies within this fixed
# rectangle on every page.  Crop page boxes only; leave text and figures intact.
box = RectangleObject([21, 160, 460, 826])  # 439 x 666 pt
for page in writer.pages:
    page.mediabox = RectangleObject(box)
    page.cropbox = RectangleObject(box)
    page.trimbox = RectangleObject(box)
    page.bleedbox = RectangleObject(box)
    page.artbox = RectangleObject(box)

writer.add_metadata({
    '/Title': 'Selection Resolution Changes Candidate-Truncation Conclusions in Simulated Influence Maximization - Reading Edition',
    '/Subject': 'Cropped reading copy only; use the original smallextended PDF and LaTeX source for Computing submission.',
})
with target.open('wb') as stream:
    writer.write(stream)

print(target)
