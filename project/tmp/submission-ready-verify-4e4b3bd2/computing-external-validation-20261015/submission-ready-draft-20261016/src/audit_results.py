"""Read-only audit of frozen v1; outputs only under review-v2/audit.
Run with --replay to exhaustively regenerate every full-candidate score matrix.
"""
from pathlib import Path
import argparse, gzip, hashlib, json, sys, time
from collections import defaultdict, Counter
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'review-v2'/'audit'; OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'snapshot'))
import engine, run_experiment as runner
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name,obj): (OUT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def check(ok, text):
    if not ok: raise AssertionError(text)
def independent_graph(ds):
    rows=[]
    with gzip.open(ROOT/'data/raw/snap'/engine.RAW_FILENAMES[ds],'rt') as f:
        for line in f:
            if line.strip() and not line.startswith('#'): rows.append(line.split())
    allnodes={n for r in rows for n in r[:2]}
    if ds=='college_msg':
        times=sorted({int(r[2]) for r in rows}); cut=times[int(.65*len(times))-1]
        rows=[r for r in rows if int(r[2])<=cut]
    edges={(r[0],r[1]) for r in rows if r[0]!=r[1]}
    if ds=='ca_grqc': edges |= {(v,u) for u,v in list(edges)}
    nodes=sorted({n for e in edges for n in e}); ix={n:i for i,n in enumerate(nodes)}
    ad=[[] for n in nodes]
    for u,v in edges: ad[ix[u]].append(ix[v])
    ad=[sorted(a) for a in ad]
    indptr=np.array([0]+list(np.cumsum([len(a) for a in ad])),dtype=np.int64)
    targets=np.array([v for a in ad for v in a],dtype=np.int64)
    return nodes,indptr,targets,sorted(allnodes-set(nodes))
def ids(ds,path,family,n,namespace):
    return np.array([int(hashlib.sha256(f'{namespace}|{ds}|{path}|{family}|{i}'.encode()).hexdigest()[:16],16)&((1<<63)-1) for i in range(n)],dtype=np.uint64)
def oracle(g,world,seeds,h,p,edge):
    mask=(1<<64)-1
    def open_edge(t,u,v):
        x=((int(world)+0x9E3779B97F4A7C15)&mask)^(((t+1)*0xBF58476D1CE6E5B9)&mask)^(((u+1)*0x94D049BB133111EB)&mask)^(((v+1)*0xBF58476D1CE6E93)&mask)
        x=((x^(x>>30))*0xBF58476D1CE6E5B9)&mask
        x=((x^(x>>27))*0x94D049BB133111EB)&mask
        x=x^(x>>31)
        return (x>>11)/(1<<53)<p
    active=set(map(int,seeds)); frontier=set(active)
    for t in range(h):
        newly=set()
        for u in frontier:
            for v0 in g['targets'][g['indptr'][u]:g['indptr'][u+1]]:
                v=int(v0)
                if v not in active and open_edge(0 if edge else t,u,v): newly.add(v)
        active |= newly; frontier=newly
    return len(active)
def main(replay):
    start=time.perf_counter(); cfg=json.loads((ROOT/'config.json').read_text()); manifest=json.loads((ROOT/'data/source_manifest.json').read_text())
    frozen=runner.verify(ROOT); status=json.loads((ROOT/'results/main/run_status.json').read_text()); check(status['status']=='complete','run status')
    matrix=list(runner.condition_matrix(cfg)); check(len(matrix)==54,'matrix count')
    records={r['key']:r for r in status['completed']}; check(set(records)=={runner.key(c) for c in matrix},'run status matrix')
    folder=ROOT/'results/main/conditions'; check(len(list(folder.glob('*.json')))==54 and len(list(folder.glob('*.npz')))==54,'file counts')
    graphs={}; allids=set(); diagnostics={}; armcount=0; evalcount=0; oraclecount=0; scorecount=0; peaks=[]; timingcount=0; checked=[]; cache={}
    for ds in cfg['datasets']:
        g=engine.load_external_graph(ROOT/'data/raw/snap',ds); graphs[ds]=g
        nodes,ip,tt,dropped=independent_graph(ds)
        check(nodes==g['nodes'] and np.array_equal(ip,g['indptr']) and np.array_equal(tt,g['targets']),'independent graph '+ds)
        expected=manifest['datasets'][ds]
        check(g['metadata']==expected,'manifest graph '+ds)
        diagnostics[ds]={'source_nodes_missing_from_processed':dropped,'graph':expected}
        for path in cfg['resolution']['paths']:
            for family,n in [('selection',max(cfg['resolution']['selection_worlds'])),('evaluation',cfg['evaluation_worlds'])]:
                vals=ids(ds,path,family,n,cfg['namespace']); check(np.array_equal(vals,engine.world_ids(ds,path,family,n,cfg['namespace'])),'independent IDs')
                ss=set(map(int,vals)); check(len(ss)==n and not(ss&allids),'world collision'); allids |= ss
    for c in matrix:
        stem=runner.key(c); js=folder/(stem+'.json'); npz=folder/(stem+'.npz'); r=json.loads(js.read_text()); g=graphs[c['dataset']]; ix={n:i for i,n in enumerate(g['nodes'])}
        check(sha(js)==records[stem]['json_sha256'] and sha(npz)==records[stem]['npz_sha256']==r['array_sha256'],'result hashes '+stem)
        check(r['config']==c and r['source_manifest_sha256']==frozen and r['graph']==g['metadata'],'provenance '+stem)
        sid=ids(c['dataset'],c['path'],'selection',c['W'],cfg['namespace']); eid=ids(c['dataset'],c['path'],'evaluation',cfg['evaluation_worlds'],cfg['namespace'])
        check(sha_bytes(sid)==r['selection_world_sha256'] and sha_bytes(eid)==r['evaluation_world_sha256'],'world hashes')
        candidates=runner.arms_for(g,c,cfg); check(set(candidates)==set(r['arms']),'arm matrix')
        with np.load(npz,allow_pickle=False) as z:
            check(set(z.files)=={a+s for a in candidates for s in ['_evaluation','_round_totals']},'array keys')
            sw=engine.make_worlds(sid,g['sources'],g['targets'],c['p'],c['h'],c['coupling']=='edge')
            unique={}
            for method,a in r['arms'].items():
                armcount+=1; vals=z[method+'_evaluation']; totals=z[method+'_round_totals']; pool=sorted(int(i) for i in candidates[method]); seeds=np.array([ix[n] for n in a['selected']],dtype=np.int64)
                check(a['candidate_ids']==[g['nodes'][i] for i in pool],'candidate identity')
                check(a['candidate_count']==len(pool) and a['coverage']==len(pool)/len(g['nodes']),'coverage')
                check(len(set(seeds))==c['k'] and set(seeds)<=set(pool),'eligible distinct seeds')
                check(vals.dtype.kind in 'iu' and vals.shape==(cfg['evaluation_worlds'],) and vals.min()>=c['k'] and vals.max()<=len(g['nodes']),'eval range')
                check(totals.shape==(c['k'],len(pool)) and totals.dtype.kind in 'iu','score shape')
                for q in range(c['k']):
                    used=set(seeds[:q]); check(all((totals[q,j]==-1)==(node in used) for j,node in enumerate(pool)),'used score sentinel')
                    win=int(np.argmax(totals[q])); check(pool[win]==seeds[q],'integer argmax lexical tie')
                    tr=a['trace'][q]; valid=totals[q][totals[q]>=0]
                    check(valid.min()>=(q+1)*c['W'] and valid.max()<=len(g['nodes'])*c['W'],'score bounds')
                    check(tr['winner']==a['selected'][q] and tr['total']==int(valid.max()) and tr['ties']==int(np.sum(valid==valid.max())),'trace')
                    check(abs(tr['margin']-(np.sort(valid)[-1]-np.sort(valid)[-2])/c['W'])<1e-12,'margin')
                    # Regenerate the chosen node total at every round and every arm.
                    check(int(engine.evaluate(g['indptr'],g['targets'],sw,seeds[:q+1],c['h']).sum())==tr['total'],'winner total replay')
                scorecount+=totals.size
                diff=vals-z['full_evaluation']; metrics={'mean_spread':vals.mean(),'incremental_spread':vals.mean()-c['k'],'delta':diff.mean(),'mc_se':diff.std(ddof=1)/np.sqrt(len(diff))}
                check(all(abs(a[k]-v)<1e-12 for k,v in metrics.items()),'recorded numeric metrics')
                check(a['same_order']==(a['selected']==r['arms']['full']['selected']) and a['same_set']==(set(a['selected'])==set(r['arms']['full']['selected'])),'agreement')
                sk=tuple(sorted(seeds)); check(sk not in unique or np.array_equal(vals,unique[sk][1]),'same-set world identity'); unique[sk]=(seeds,vals.copy())
                # Scalar reference does not import frozen simulation/hash code.
                if (c['dataset'],c['path'],c['coupling'],tuple(seeds)) not in cache:
                    for i in range(16): check(oracle(g,eid[i],seeds,c['h'],c['p'],c['coupling']=='edge')==vals[i],'independent scalar oracle')
                    oraclecount+=16; cache[(c['dataset'],c['path'],c['coupling'],tuple(seeds))]=True
                evalcount+=len(vals)
            for offset in range(0,len(eid),256):
                ew=engine.make_worlds(eid[offset:offset+256],g['sources'],g['targets'],c['p'],c['h'],c['coupling']=='edge')
                for seeds,vals in unique.values(): check(np.array_equal(engine.evaluate(g['indptr'],g['targets'],ew,seeds,c['h']),vals[offset:offset+256]),'complete evaluation replay')
            if replay:
                selected,totals=engine.greedy(g['indptr'],g['targets'],sw,np.arange(len(g['nodes']),dtype=np.int64),c['k'],c['h'])
                check([g['nodes'][i] for i in selected]==r['arms']['full']['selected'] and np.array_equal(totals,z['full_round_totals']),'exhaustive full score replay')
            if c['stage']=='resolution' and c['path']==1101 and c['W']==320:
                check(len(r['timing_repeats'])==5*len(candidates),'repeat count')
                check(Counter(x['method'] for x in r['timing_repeats'])==Counter({a:5 for a in candidates}),'repeat matrix')
            else: check(len(r['timing_repeats'])==0,'unexpected repeats')
            timingcount+=len(r['timing_repeats']); peaks.append(r['peak_working_set_bytes']); check(peaks[-1]>0,'positive saved psutil memory')
        checked.append(stem); write('audit_progress.json',{'status':'running','conditions':len(checked),'exhaustive_replay':replay,'elapsed_seconds':time.perf_counter()-start}); print(f'checked {len(checked)}/54 {stem}',flush=True)
    result={'status':'PASS','conditions':len(checked),'arms':armcount,'evaluation_values':evalcount,'stored_integer_scores_checked':scorecount,'independent_scalar_world_checks':oraclecount,'unique_world_ids':len(allids),'timing_repeats':timingcount,'source_manifest_sha256':frozen,'full_score_exhaustive_replay':replay,'all_evaluation_arrays_replayed':True,'peak_working_set_bytes_min':min(peaks),'peak_working_set_bytes_max':max(peaks),'elapsed_seconds':time.perf_counter()-start,'graphs':diagnostics,'limits':['Scalar independent oracle checks first 16 worlds per distinct ordered sequence; complete replay uses frozen core.','Stored timing durations cannot be reconstructed; supplementary independent measurements are separately labelled.','Saved peak working set is process-lifetime peak, not per-condition allocation.']}
    write('full_validation.json',result); write('audit_progress.json',{'status':'complete','conditions':54}); print(json.dumps({k:v for k,v in result.items() if k!='graphs'},indent=2))
def sha_bytes(x): return hashlib.sha256(x.tobytes()).hexdigest()
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--replay',action='store_true');args=ap.parse_args()
    try: main(args.replay)
    except Exception as exc: write('audit_failure.json',{'error':repr(exc)});raise
