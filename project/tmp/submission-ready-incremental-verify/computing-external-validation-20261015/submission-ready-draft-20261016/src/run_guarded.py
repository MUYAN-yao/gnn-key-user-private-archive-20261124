"""Add fail-closed raw-input enforcement around the unchanged frozen runner."""
from pathlib import Path
import sys,json,hashlib,argparse,subprocess
BASE=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path);ap.add_argument('--verify-only',action='store_true');args=ap.parse_args()
sys.path.insert(0,str(BASE/'snapshot'));import run_experiment
run_experiment.verify(BASE)
for ds,m in json.loads((BASE/'data/source_manifest.json').read_text())['datasets'].items():
    p=BASE/'data/raw/snap'/m['source_filename'];assert hashlib.sha256(p.read_bytes()).hexdigest()==m['source_sha256'],ds+' input mismatch'
print('Frozen source and all raw hashes verified')
if not args.verify_only:
    if args.output.exists() and any(args.output.iterdir()):raise FileExistsError('Use a new empty output directory')
    subprocess.run([sys.executable,str(BASE/'snapshot/run_experiment.py'),'--base',str(BASE),'--output',str(args.output.resolve())],check=True)
