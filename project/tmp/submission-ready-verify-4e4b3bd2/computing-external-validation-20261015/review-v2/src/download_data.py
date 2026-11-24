"""Fetch public SNAP originals into local data/raw/snap; refuse unknown hashes."""
from pathlib import Path
import urllib.request,hashlib,json,os
BASE=Path(__file__).resolve().parents[2]
data=json.loads((BASE/'data/source_manifest.json').read_text())['datasets']
urls={'college_msg':'https://snap.stanford.edu/data/CollegeMsg.txt.gz','ca_grqc':'https://snap.stanford.edu/data/ca-GrQc.txt.gz','wiki_vote':'https://snap.stanford.edu/data/wiki-Vote.txt.gz'}
folder=BASE/'data/raw/snap';folder.mkdir(parents=True,exist_ok=True)
for name,record in data.items():
    path=folder/record['source_filename'];expected=record['source_sha256']
    if path.exists():
        assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,'Existing input mismatch: '+str(path)
        print('verified existing',name);continue
    temp=path.with_suffix(path.suffix+'.download')
    if temp.exists():raise FileExistsError('Inspect prior partial download first: '+str(temp))
    req=urllib.request.Request(urls[name],headers={'User-Agent':'LocalResearchReproduction/1.0'})
    with urllib.request.urlopen(req,timeout=120) as response: content=response.read()
    temp.write_bytes(content)
    assert hashlib.sha256(content).hexdigest()==expected,'Downloaded input changed; preserved for inspection: '+str(temp)
    os.replace(temp,path);print('downloaded and verified',name)
