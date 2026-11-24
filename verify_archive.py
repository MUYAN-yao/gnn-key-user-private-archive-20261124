"""Verify archive contents without restoring large files."""
import hashlib,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent
if os.name=='nt' and not str(ROOT).startswith('\\\\?\\'):ROOT=Path('\\\\?\\'+str(ROOT))
items=json.loads((ROOT/'inventory.json').read_text(encoding='utf-8'))
for item in items:
    files=item['storage'] if isinstance(item['storage'],list) else [item['storage']]
    h=hashlib.sha256();size=0
    for file in files:
        with (ROOT/file).open('rb') as f:
            while data:=f.read(4*1024**2):h.update(data);size+=len(data)
    assert h.hexdigest()==item['sha256'] and size==item['size'],item['path']
print(f'PASS: {len(items)} files, {sum(i["size"] for i in items)} bytes; all SHA-256 checks match.')
