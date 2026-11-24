"""Copy only the historical evidence required by the reproducibility audit."""
import sys,shutil
from pathlib import Path

project=Path(sys.argv[1]).resolve();base=Path(sys.argv[2]).resolve()
target=base/'legacy_project'
paths=[
 'reproducibility/v10-source-snapshots/sociopatterns-resolution-confirmation-v0_1-20260920-r3',
 'audits/sociopatterns-resolution-confirmation-v0_1/snapshot-r3-confirmation-run-20260920',
 'analysis/sociopatterns-resolution-confirmation-v0_1-validation.json']
for name in ['manuscript.tex','svjour3.cls','svglov3.clo']:
    paths.append('c-users-36024-downloads-texlive2026-20260301/outputs/computing_latex/'+name)
for relative in paths:
    source=project/relative;dest=target/relative
    assert source.exists(),source
    if source.is_dir():
        shutil.copytree(source,dest,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    else:
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
print('Copied historical source, output ledger and manuscript template assets')
