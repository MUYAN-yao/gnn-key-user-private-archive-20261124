from __future__ import annotations
import hashlib, json
from pathlib import Path
FILES=["config.json","protocol.md","requirements.txt","data_selection.md","data/source_manifest.json","snapshot/legacy_engine.py","snapshot/engine.py","snapshot/preflight.py","snapshot/write_data_manifest.py","snapshot/run_experiment.py","snapshot/freeze.py"]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    base=Path(__file__).resolve().parents[1]; out=base/"snapshot/source_manifest.json"
    if out.exists(): raise FileExistsError(out)
    report={"version":1,"files":{p:sha(base/p) for p in FILES}}
    with out.open("x",encoding="utf-8") as f: json.dump(report,f,indent=2,sort_keys=True); f.write("\n")
if __name__=="__main__": main()
