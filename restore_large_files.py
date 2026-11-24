"""Restore chunked files to project/ and verify every archived file."""
import hashlib,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent
if os.name=='nt' and not str(ROOT).startswith('\\\\?\\'):
    ROOT=Path('\\\\?\\'+str(ROOT))
for item in json.loads((ROOT/'large-files.json').read_text(encoding='utf-8')):
    target=ROOT/'project'/item['path'];target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        if hashlib.sha256(target.read_bytes()).hexdigest()!=item['sha256']:
            raise RuntimeError(f'Refusing to overwrite changed file: {target}')
        continue
    temp=target.with_name(target.name+'.restoring')
    with temp.open('wb') as out:
        for part in item['storage']:out.write((ROOT/part).read_bytes())
    assert hashlib.sha256(temp.read_bytes()).hexdigest()==item['sha256'],str(target)
    temp.replace(target)
for item in json.loads((ROOT/'inventory.json').read_text(encoding='utf-8')):
    p=ROOT/'project'/item['path']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],str(p)
print('All archived files verified.')
