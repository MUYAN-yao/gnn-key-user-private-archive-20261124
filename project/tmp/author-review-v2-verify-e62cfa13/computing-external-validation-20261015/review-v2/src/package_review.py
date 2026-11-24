"""Create a local combined archive, actually extract it, verify every member."""
from pathlib import Path
import json,hashlib,zipfile,uuid
R=Path(__file__).resolve().parents[1];B=R.parent;S=B.parent;O=S/'computing-strengthening-20261015'
assert json.loads((R/'qa/final_checks.json').read_text())['status']=='PASS'
dest=S/'computing-author-review-20261015-v2.zip'
if dest.exists():raise FileExistsError('Preserve existing release; choose a new version')
files=[];excluded=[]
for base in [B,O]:
    for p in sorted(base.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(base)
        if '__pycache__' in rel.parts or p.suffix in ['.pyc','.nbc','.nbi','.download'] or rel.parts[:2]==('data','raw'):
            excluded.append(str(p.relative_to(S)));continue
        files.append(p)
manifest={'status':'local author-review package; no submission/publication','algorithm':'sha256','files':{p.relative_to(S).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'excluded':excluded,'raw_data_policy':'Third-party raw data omitted; downloader and expected hashes included. No redistribution permission asserted.'}
with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,p.relative_to(S).as_posix())
    z.writestr('package_manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
unpack=S.parent/'tmp'/('author-review-v2-verify-'+uuid.uuid4().hex[:8]);unpack.mkdir(parents=True)
with zipfile.ZipFile(dest) as z:
    assert z.testzip() is None
    for info in z.infolist():
        target=(unpack/info.filename).resolve();assert target.is_relative_to(unpack.resolve()),'unsafe archive path'
    z.extractall(unpack)
extracted=json.loads((unpack/'package_manifest.json').read_text(encoding='utf-8'))
bad=[name for name,h in extracted['files'].items() if hashlib.sha256((unpack/name).read_bytes()).hexdigest()!=h];assert not bad
assert not any('/data/raw/' in name for name in extracted['files'])
result={'status':'PASS','archive':str(dest),'archive_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'archive_bytes':dest.stat().st_size,'files_verified_after_extraction':len(extracted['files']),'extraction_directory':str(unpack),'hash_mismatches':bad,'zip_crc_check':True,'third_party_raw_data_excluded':True}
dest.with_suffix('.verification.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
dest.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
