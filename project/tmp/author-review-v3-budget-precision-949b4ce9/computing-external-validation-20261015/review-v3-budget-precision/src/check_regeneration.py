"""Recreate analysis/figures/tables using saved setup data and compare content."""
from pathlib import Path
import hashlib,subprocess,sys,json
R=Path(__file__).resolve().parents[1]
def tracked():
    files=list((R/'analysis').glob('*.csv'))+list((R/'analysis/figures').glob('*.csv'))+list((R/'analysis/figures').glob('*.png'))+[R/'manuscript'/f for f in ['numbers.tex','primary_table.tex','cost_table.tex','transition_table.tex','supp_tables.tex','precision_table.tex']]
    return {str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
before=tracked()
for name in ['analyze.py','make_figures.py','build_documents.py']:subprocess.run([sys.executable,str(R/'src'/name)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
after=tracked();differences=[k for k in before if before[k]!=after.get(k)]
(R/'qa/regeneration.json').write_text(json.dumps({'status':'PASS' if not differences else 'FAIL','files_checked':len(before),'different_files':differences,'hashes':after,'scope':'All CSVs, figure PNG pixels and generated LaTeX tables/macros; timing measurements retained, not remeasured. PDF/SVG creation metadata not compared.'},indent=2),encoding='utf-8');assert not differences,differences;print('regeneration PASS',len(before))
