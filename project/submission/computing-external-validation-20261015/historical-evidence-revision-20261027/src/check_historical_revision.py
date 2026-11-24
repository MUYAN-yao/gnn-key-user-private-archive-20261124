"""Check this revision and optionally regenerate saved-result summaries only."""
from pathlib import Path
import argparse, ast, hashlib, json, subprocess, sys, re, platform
import numpy as np
import pandas as pd
import matplotlib
from PIL import Image
from pypdf import PdfReader

R=Path(__file__).resolve().parents[1]; E=R.parent; H=R.parents[2]/'submission/computing-strengthening-20261015'
P=E/'narrative-revision-20261027'; Q=R/'qa'
pa=argparse.ArgumentParser();pa.add_argument('--regenerate',action='store_true');args=pa.parse_args()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def pixel(p):
    with Image.open(p) as im:return hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()
script=R/'src/integrate_historical.py'
tree=ast.parse(script.read_text(encoding='utf-8'))
imports=[]
for node in ast.walk(tree):
    if isinstance(node,ast.Import):imports.extend(a.name for a in node.names)
    if isinstance(node,ast.ImportFrom):imports.append(node.module)
allowed={'pathlib','argparse','hashlib','json','shutil','numpy','pandas','matplotlib','matplotlib.pyplot','matplotlib.lines'}
assert set(imports)<=allowed
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in {'eval','exec','compile','__import__'} for n in ast.walk(tree))
generated=list((R/'analysis').rglob('*.csv'))+list((R/'manuscript').glob('history_*_table.tex'))+[R/'analysis/historical_key_facts.json']
pngs=list((R/'analysis/figures').glob('*.png'))
if args.regenerate:
    before={str(p.relative_to(R)):sha(p) for p in generated};pixels={p.name:pixel(p) for p in pngs}
    proc=subprocess.run([sys.executable,str(script)],capture_output=True,text=True,encoding='utf-8',check=True)
    (Q/'regeneration-console.txt').write_text(proc.stdout,encoding='utf-8')
    after={str(p.relative_to(R)):sha(p) for p in generated};afterpixels={p.name:pixel(p) for p in pngs}
    assert before==after and pixels==afterpixels
    dump(Q/'historical_regeneration.json',{'status':'PASS','new_experiments':False,'csv_tex_json_files':len(generated),
          'content_hashes':after,'png_pixel_hashes':afterpixels,'excluded_binary_equality':'PDF/SVG metadata contains export timestamps.'})

v=read(Q/'historical_integration_validation.json');assert v['status']=='PASS'
f=read(R/'analysis/historical_key_facts.json')
assert f['step']['changed_sets']==16 and abs(f['step']['mean_delta']-.01111)<1e-12
assert f['edge']['changed_sets']==29 and abs(f['edge']['mean_delta']-.061845)<1e-12
assert f['parameters']['degree_4k']['order_matches']==117 and f['parameters']['pagerank_4k']['order_matches']==132
assert f['parameters']['weighted_4k']['negative_delta']==117 and f['parameters']['weighted_4k']['positive_delta']==43
sg=pd.read_csv(R/'analysis/historical_group_summary.csv');pl=pd.read_csv(R/'analysis/historical_path_metrics.csv')
assert len(sg)==378 and len(pl)==3640 and (pl.full_incremental>0).all()
assert ((pl.coverage>0)&(pl.coverage<=1)).all()
for m,n in [('degree_4k',38),('pagerank_4k',40),('weighted_4k',5)]:
    assert sg[(sg.stage=='coupling')&(sg.W==1280)&(sg.method==m)].order_matches.sum()==n
assert np.all(pl[(pl.stage=='seed_budget')&(pl.dataset=='kenya2012')&pl.method.str.endswith('_4k')].coverage==1)
assert not ((pl.stage=='seed_budget')&(pl.dataset=='sfhh2009')).any()
pc=E/'review-v3-budget-precision/analysis/precision_budget'
precision={}
for n in ['summary_by_budget_precision.csv','path_metrics.csv','budget_transitions_by_path.csv','budget_transitions_summary.csv','candidate_pool_precision_diagnostics.csv']:
    d=pd.read_csv(pc/n);precision[n]={'rows':len(d),'sha256':sha(pc/n),'columns':list(d.columns)}
ps=pd.read_csv(pc/'summary_by_budget_precision.csv')
c=ps[(ps.dataset=='ca_grqc')&(ps.method=='pagerank_4k')].sort_values('W')
assert (c[c.solver=='strict'].loss_percent_mean<0).all()
de=c[c.solver=='default'].loss_percent_mean.tolist();assert de[0]<0 and de[-1]>0
assets={}
for p in (P/'manuscript').iterdir():
    if p.is_file() and p.suffix.lower() in {'.pdf','.png','.svg','.jpg','.cls','.clo'} and p.stem not in {'manuscript','Online_Resource_1'}:
        q=R/'manuscript'/p.name;assert q.exists() and sha(p)==sha(q),p.name
        assets[p.name]=sha(p)
for n in ['primary_table.tex','cost_table.tex','precision_budget_table.tex','transition_table.tex','numbers.tex','supp_tables.tex','references.tex']:
    assert sha(P/'manuscript'/n)==sha(R/'manuscript'/n),n
src=(R/'manuscript/manuscript.tex').read_text(encoding='utf-8');old=(P/'manuscript/manuscript.tex').read_text(encoding='utf-8')
assert src.split(r'\begin{abstract}')[1].split(r'\end{abstract}')[0]==old.split(r'\begin{abstract}')[1].split(r'\end{abstract}')[0]
assert src.split(r'\section*{Statements and Declarations}')[1]==old.split(r'\section*{Statements and Declarations}')[1]
input_records={}
for base,paths in [(H,['protocol.md','snapshot/config.json','snapshot/source_manifest.json','analysis/validation.json','analysis/group_summary.csv','analysis/path_level_metrics.csv','analysis/reference_transitions.csv','analysis/network_metadata.json','analysis/figure_catalog.tsv','analysis/figures/Fig4.pdf','analysis/figures/Fig4.png','analysis/figures/Fig4.svg','results/manifest.json']),
                   (P,['README.md','manuscript/manuscript.tex','manuscript/Online_Resource_1.tex','qa/revision_checks.json']),
                   (E,['config.json','protocol.md','snapshot/legacy_engine.py'])]:
    for n in paths: input_records[str((base/n).relative_to(R.parents[2]))]=sha(base/n)
dump(Q/'provenance_input_hashes.json',input_records)
figs={}
for name in ['HistoryParameters','HistoryEdgeTransitions']:
    pdf=PdfReader(R/'analysis/figures'/f'{name}.pdf');pg=pdf.pages[0]
    width=float(pg.mediabox.width)*25.4/72
    assert abs(width-119)<.01
    figs[name]={'width_mm':width,'pdf_sha256':sha(R/'manuscript'/f'{name}.pdf'),'png_pixel_sha256':pixel(R/'analysis/figures'/f'{name}.png')}
report={'status':'PASS','new_experiments_executed':False,'new_simulation_replays_executed':False,'safe_analysis_imports':imports,
    'historical_checks':v,'external_precision_sources_read':precision,'protected_assets_identical':assets,
    'abstract_unchanged':True,'declarations_unchanged':True,'external_numeric_tables_unchanged':True,
    'figures':figs,'environment':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'matplotlib':matplotlib.__version__},
    'not_executed':['experiment runners','training','seed search','diffusion simulation','timing experiment','new bootstrap or significance tests','external full rerun','cross-platform replication']}
dump(Q/'historical_revision_checks.json',report)
print(json.dumps({'status':'PASS','new_experiments':False,'protected_assets':len(assets),'external_precision_files':len(precision)},indent=2))
