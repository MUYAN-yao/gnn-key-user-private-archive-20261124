"""One-time editorial block move; preserve every result paragraph and asset."""
from pathlib import Path
import json, hashlib
root=Path(__file__).resolve().parents[1]
p=root/'manuscript/manuscript.tex'
s=p.read_text(encoding='utf-8')
before,rest=s.split('\\section{Results}\n',1)
body,after=rest.split('\\section{Discussion}',1)
blocks=['\\subsection{'+part for part in body.split('\\subsection{')[1:]]
assert len(blocks)==5
assert blocks[0].startswith('\\subsection{External topology changes the ranking comparison}')
scope=blocks[0].split('\n',1)[1]
coverage_heading,coverage=blocks[2].split('\n',1)
reordered=blocks[1]+blocks[3]+coverage_heading+'\n'+scope+coverage+blocks[4]
p.write_text(before+'\\section{Results}\n'+reordered+'\\section{Discussion}'+after,encoding='utf-8')
(root/'qa/result_order_change.json').write_text(json.dumps({
    'action':'Reorder unchanged result blocks and merge external comparison with coverage section',
    'old_order':['external','precision','coverage','transitions','cost'],
    'new_order':['precision','transitions','external and coverage','cost'],
    'block_hashes_before_move':[hashlib.sha256(b.encode()).hexdigest() for b in blocks],
    'experimental_inputs_changed':False
},indent=2),encoding='utf-8')
