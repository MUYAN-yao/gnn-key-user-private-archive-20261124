"""Create a hash-verified local archive; never upload or publish anything."""
import sys,json,hashlib,zipfile
from pathlib import Path

base=Path(sys.argv[1]).resolve()
assert json.loads((base/'analysis/validation.json').read_text())['status']=='PASS'
assert json.loads((base/'qa/verification.json').read_text())['status']=='PASS'

def eligible(p):
    rel=p.relative_to(base)
    if '__pycache__' in rel.parts or p.suffix in ['.pyc','.nbc','.nbi','.zip']:return False
    if rel.name=='package_manifest.json':return False
    if rel.parts[0]=='qa' and p.suffix not in ['.json','.md','.jpg']:return False
    if rel.parts[0]=='manuscript' and p.suffix not in ['.tex','.pdf','.cls','.clo','.txt','.json']:return False
    if rel.parts[0]=='manuscript' and p.name.startswith('compile-'):return False
    return p.is_file()

paths=sorted(p for p in base.rglob('*') if eligible(p))
manifest={'status':'local author-review release; not publicly archived','hash':'sha256','files':{p.relative_to(base).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
mf=base/'package_manifest.json';mf.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
archive=base.parent/(base.name+'-reproducibility.zip')
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in paths+[mf]:z.write(p,arcname=base.name+'/'+p.relative_to(base).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for name,expected in manifest['files'].items():
        assert hashlib.sha256(z.read(base.name+'/'+name)).hexdigest()==expected,name
sources=base.parent/(base.name+'-manuscript-sources.zip')
with zipfile.ZipFile(sources,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for p in sorted((base/'manuscript').iterdir()):
        if p.suffix in ['.tex','.pdf','.cls','.clo']:z.write(p,p.name)
    for name in ['summary_for_editor.txt','cover_letter_draft.txt','author_checklist_zh.md']:
        z.write(base/name,name)
with zipfile.ZipFile(sources) as z:assert z.testzip() is None
print(json.dumps({'reproducibility':str(archive),'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files_verified':len(paths),'manuscript_sources':str(sources)},ensure_ascii=False))
