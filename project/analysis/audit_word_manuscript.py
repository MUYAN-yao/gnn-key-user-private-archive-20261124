from pathlib import Path
import json,re,statistics
R=Path(__file__).resolve().parents[1]
P=R/'manuscript/resolution_aware_candidate_truncation_submission_v0_1'
run=R/'audits/sociopatterns-resolution-confirmation-v0_1/snapshot-r3-confirmation-run-20260920'
m=json.loads((run/'manifest.json').read_text(encoding='utf-8'))
assert m['status']=='COMPLETE'
rows=[json.loads((run/r['path']).read_text(encoding='utf-8')) for r in m['runs']]
assert len(rows)==42
assert len({(r['dataset'],r['k'],r['world_path'],r['selection_world_count']) for r in rows})==42
summary=json.loads((R/'analysis/sociopatterns-resolution-confirmation-v0_2/summary.json').read_text())
checks=[]
for w in [20,80,320]:
    rr=[r for r in rows if r['selection_world_count']==w]
    assert sum(r['k'] for r in rr)==160
    for name in ['degree_2k','degree_4k','degree_8k']:
        arms=[r['arms'][name] for r in rr]
        matches=sum(a['selection']['top_k']==r['arms']['full']['selection']['top_k'] for a,r in zip(arms,rr))
        saturated=sum(a['candidate_count']==r['graph']['historical_nodes'] for a,r in zip(arms,rr))
        med=statistics.median(1-a['decision_seconds']/r['arms']['full']['decision_seconds'] for a,r in zip(arms,rr))
        s=summary['candidate_profiles'][f'{name}@W{w}']
        assert matches==s['same_ordered_top_k_count']
        assert abs(med-s['median_decision_time_saving_fraction'])<1e-6
        checks.append(dict(W=w,pool=name,matches=matches,saturated=saturated,restricted_matches=matches-saturated,restricted_conditions=14-saturated))
text=(P/'manuscript.md').read_text(encoding='utf-8')
assert re.findall(r'\*\*Fig\. (\d+)\*\*',text)==list(map(str,range(1,9)))
assert re.findall(r'\*\*Table (\d+)\.',text)==list(map(str,range(1,5)))
for file in re.findall(r'!\[[^]]*\]\(([^)]+)\)',text): assert (P/file).is_file()
cited=set()
for val in re.findall(r'\[([\d,\s–-]+)\]',text.split('## References')[0]):
    for piece in val.split(','):
        nums=[int(v) for v in re.split('[–-]',piece.strip())]
        cited.update(range(nums[0],nums[-1]+1))
assert cited==set(range(1,17))
assert not re.search('鈥|�|190 greedy|/190',text)
result=dict(status='PASS',conditions=len(rows),rounds_per_budget=160,table4=checks,figures=8,tables=4,cited_references=16)
(P/'word_review_numeric_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
