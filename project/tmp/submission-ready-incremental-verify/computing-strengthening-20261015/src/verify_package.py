"""Read-only SHA256 verification of delivered package files."""
import sys,json,hashlib
from pathlib import Path

base=Path(sys.argv[1]).resolve()
manifest=json.loads((base/'package_manifest.json').read_text(encoding='utf-8'))
for name,expected in manifest['files'].items():
    p=(base/name).resolve()
    assert p.is_relative_to(base),name
    assert p.is_file(),name
    assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,name
print(f'PASS: {len(manifest["files"])} delivered file hashes verified')
