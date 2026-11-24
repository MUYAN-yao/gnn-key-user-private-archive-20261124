from pilot import *
expected={'protocol.md':'BCBC6A6EF938511C977407AEE15C61ADBCC47EEE087A00CD673728E9B7C8660D','config.json':'2D98966252D1B2A7023CEC1FE6AE3E56948C80708CFAB0C27DC1B8F58CD63D8D','pilot.py':'2FE8F749C04390C8AE441DB34FABB524A79B899342D0712DE61CDAE239A5FE11','run.py':'F3D6C15D8AABB616D89780ECCB834D75157CA47AB8E96278979196F21E20EDC0'}
for name,sha in expected.items():assert hashlib.sha256((BASE/name).read_bytes()).hexdigest().upper()==sha,name
manifest=json.loads((BASE/'readonly-input-manifest.json').read_text(encoding='utf-8'))
for name,sha in manifest.items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==sha
required=['analysis-report.md','stats-appendix.md','figure-catalog.md','README.md','2026-11-01--symbolic-ranking--r1--round-review.md','figures/diagnostics.png','figures/models_utility.png']
for name in required:assert (BASE/name).stat().st_size>100
files=[p for p in BASE.rglob('*') if p.is_file() and not any(part in ['vendor','numba_cache','__pycache__'] for part in p.relative_to(BASE).parts) and p.name not in ['delivery-manifest.json','final_integrity.json']]
dump('delivery-manifest.json',{str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
dump('final_integrity.json',dict(status='PASS',frozen_protocol_config_code_unchanged=True,original_input_hashes_unchanged=True,required_artifacts_complete=True,deliverable_files=len(files)))
print('PASS final integrity',len(files),'files')
