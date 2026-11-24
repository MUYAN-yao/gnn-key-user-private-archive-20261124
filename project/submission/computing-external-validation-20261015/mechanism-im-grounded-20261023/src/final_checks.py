"""Gate delivery on computational audit, historical identity and document checks."""
from pathlib import Path
import json,hashlib,re,sys,platform,importlib.metadata as md,inspect
import numpy as np
import pandas as pd
import networkx as nx
R=Path(__file__).resolve().parents[1];B=R.parent;O=B.parent/'computing-strengthening-20261015';Q=R/'qa';Q.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
audit=json.loads((R/'audit/full_validation.json').read_text());assert audit['status']=='PASS' and audit['full_score_exhaustive_replay'] and audit['conditions']==54 and audit['arms']==468
precision_dir=R/'supplement-pr-precision';precision=json.loads((precision_dir/'run_status.json').read_text());assert precision['status']=='complete' and precision['conditions']==15 and precision['arms']==30
precision_hashes=json.loads((precision_dir/'source_manifest.json').read_text())
assert sha(precision_dir/'protocol.md')==precision_hashes['protocol.md'] and sha(R/'src/run_precision_control.py')==precision_hashes['src/run_precision_control.py']
assert sha(R/'audit/pagerank_precision_diagnostic.csv')==precision_hashes['audit/pagerank_precision_diagnostic.csv'] and sha(B/'snapshot/source_manifest.json')==precision_hashes['external_snapshot_manifest']
for rec in precision['completed']:
    js=precision_dir/'conditions'/(rec['key']+'.json');npz=js.with_suffix('.npz');assert sha(js)==rec['json_sha256'] and sha(npz)==rec['npz_sha256']
    a=json.loads(js.read_text());assert a['source_manifest_sha256']==sha(precision_dir/'source_manifest.json')
    original=B/'results/main/conditions'/f"resolution__{a['dataset']}__p{a['path']}__w1280__step.json";assert sha(original)==a['frozen_reference_json_sha256']
    with np.load(npz) as zz,np.load(original.with_suffix('.npz')) as oz:
        for method,v in a['arms'].items():
            vals=zz[method+'_evaluation'];assert vals.shape==(10000,) and vals.dtype.kind in 'iu' and vals.min()>=5
            totals=zz[method+'_round_totals'];pool=v['candidate_ids'];assert totals.shape==(5,len(pool)) and pool==sorted(pool)
            for q in range(5):assert pool[int(np.argmax(totals[q]))]==v['selected'][q]
            d=zz[method+'_evaluation']-oz['full_evaluation'];assert abs(d.mean()-v['delta_vs_full'])<1e-12
            assert abs(d.std(ddof=1)/100-v['mc_se_vs_full'])<1e-12
            assert abs((zz[method+'_evaluation']-oz[method+'_evaluation']).mean()-v['delta_vs_default'])<1e-12
cfg=json.loads((B/'config.json').read_text());assert sha(B/cfg['preflight']['file'])==cfg['preflight']['sha256']
oldmanifest=json.loads((O/'package_manifest.json').read_text());bad=[r for r,h in oldmanifest['files'].items() if not(O/r).is_file() or sha(O/r)!=h];assert not bad,bad
oldrecords={}
for path in (O/'results/conditions').glob('*.json'):
    a=json.loads(path.read_text());c=a['config']
    if c['stage']=='resolution' and c['W'] in [1280,5120] and not c['dataset'].startswith('synthetic'):
        oldrecords[(c['dataset'],c['path'],c['W'])]=(path,a)
changes=0;diffs=[];degree=0;pr=0
for (ds,path,W),(f,a) in oldrecords.items():
    if W!=5120:continue
    lo,b=oldrecords[(ds,path,1280)]
    changes+=set(a['arms']['full']['selected'])!=set(b['arms']['full']['selected'])
    with np.load(f.with_suffix('.npz')) as hi,np.load(lo.with_suffix('.npz')) as low:diffs.append(float((hi['full_evaluation']-low['full_evaluation']).mean()))
    degree+=a['arms']['degree_4k']['selected']==a['arms']['full']['selected'];pr+=a['arms']['pagerank_4k']['selected']==a['arms']['full']['selected']
assert len(diffs)==40 and changes==16 and degree==39 and pr==40 and abs(np.mean(diffs)-.01111)<1e-12
df=pd.read_csv(R/'analysis/arm_path.csv');sm=pd.read_csv(R/'analysis/summary_by_method.csv');primary=sm[(sm.stage=='resolution')&(sm.W==1280)]
for ds,target in [('ca_grqc',-.25082),('college_msg',-.9078),('wiki_vote',-40.69334)]:
    a=primary[(primary.dataset==ds)&(primary.method=='pagerank_4k')].iloc[0];assert abs(a.delta_mean-target)<1e-12
    a=primary[(primary.dataset==ds)&(primary.method=='degree_4k')].iloc[0];assert a.same_order_mean==1 and a.delta_mean==0
for ds,loss in [('ca_grqc',0.),('college_msg',4.277062605476086),('wiki_vote',24.275215551531184)]:
    a=primary[(primary.dataset==ds)&(primary.method=='pagerank_5pct')].iloc[0];assert abs(a.loss_percent_mean-loss)<.0001
direction=pd.read_csv(R/'analysis/direction_diagnostics.csv')
for method,outdeg,indeg,coverage in [('pagerank_4k',56.2,249.75,0.),('degree_4k',489.25,70.3,1.)]:
    a=direction[(direction.dataset=='wiki_vote')&(direction.method==method)].iloc[0];assert a.mean_outdegree==outdeg and a.mean_indegree==indeg and a.full_seed_coverage_mean==coverage
tests=pd.read_csv(R/'analysis/primary_tests.csv');assert len(tests)==9 and tests.p_holm.min()==.1875
tr=pd.read_csv(R/'analysis/full_reference_transitions.csv');adj=tr[tr.low==320];assert len(adj)==15 and adj.changed.sum()==6 and (adj.mc_lo>0).sum()==4
assert (df.full_incremental_spread>0).all()
render=json.loads((Q/'render_checks.json').read_text());assert render['status']=='PASS'
for stem in ['manuscript','Online_Resource_1']:assert sha(R/'manuscript'/(stem+'.pdf'))==render[stem]['pdf_sha256']
regen=json.loads((Q/'regeneration.json').read_text());assert regen['status']=='PASS'
refs=json.loads((R/'audit/reference_metadata.json').read_text(encoding='utf-8'));assert not any(v['status']=='retrieval-failed' for v in refs.values())
review=(Q/'visual-review.md').read_text(encoding='utf-8')
for stem in ['manuscript','Online_Resource_1']:
    n=render[stem]['pages'];assert f'{n}/{n}' in review
env={'python':sys.version,'platform':platform.platform(),'packages':{n:md.version(n) for n in ['numpy','pandas','scipy','networkx','matplotlib','psutil','numba','llvmlite','pymupdf','pillow']},'pagerank_signature':str(inspect.signature(nx.pagerank)),'pagerank_source_sha256':hashlib.sha256(inspect.getsource(nx.pagerank).encode()).hexdigest(),'pdf_renderer':'PyMuPDF; Poppler not found in inspected TeX binary path','threads':'frozen single worker; OMP/OPENBLAS constrained to1 in review commands'}
(Q/'environment.json').write_text(json.dumps(env,indent=2),encoding='utf-8')
lines=['# Original output index','','SHA256 values are from actual files; the frozen run status is preserved.','','| Condition | JSON SHA256 | NPZ SHA256 |','| --- | --- | --- |']
for js in sorted((B/'results/main/conditions').glob('*.json')):lines.append(f'| {js.stem} | {sha(js)} | {sha(js.with_suffix(".npz"))} |')
(R/'raw-output-index.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
result={'status':'PASS','external_conditions':54,'external_arms':468,'posthoc_precision_conditions':15,'posthoc_precision_arms':30,'precision_hash_and_numeric_checks':True,'external_evaluation_values':audit['evaluation_values'],'historical_manifest_files_checked':len(oldmanifest['files']),'historical_1280_to_5120':{'pairs':len(diffs),'changed_sets':changes,'mean_gain':float(np.mean(diffs)),'degree_order_matches':degree,'pagerank_order_matches':pr},'preflight_hash_match':True,'external_primary_numbers_match':True,'sign_test_family_match':True,'transition_numbers_match':True,'all_doi_metadata_retrieved':True,'abstract_words':render['text']['abstract_words'],'main_pages':render['manuscript']['pages'],'supplement_pages':render['Online_Resource_1']['pages'],'all_pages_visually_reviewed':True,'unresolved_author_declarations':True,'scope':'Ready for final author scientific review, not approved for submission.'}
(Q/'final_checks.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
