"""Rebuild normalized study data from user-obtained original provider archives.

No automatic external uploads or downloads. Validate the original raw archive
hashes from the supplied cards before reproducing the original preprocessing.
"""
import argparse,importlib.util,json,hashlib
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--raw-dir',type=Path,required=True);ap.add_argument('--project-root',type=Path,required=True);a=ap.parse_args()
    here=Path(__file__).resolve().parent
    legacy=here/'prepare_sociopatterns_confirmation.py'
    spec=importlib.util.spec_from_file_location('legacy_prepare',legacy);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    mod.RAW=a.raw_dir.resolve()
    for name in ['invs2013','invs2015','kenya2012','sfhh2009']:
        card=json.loads((here.parent/'data_cards'/name/'data_card.json').read_text())
        raw=a.raw_dir/card['source_file']
        assert raw.is_file(),f'Obtain {card["source_file"]} from {card["source_page"]}'
        assert hashlib.sha256(raw.read_bytes()).hexdigest()==card['source_sha256'],'raw archive differs: '+name
        mod.normalize(name,a.project_root/'data/processed/sociopatterns-confirmation-v0_1')
        print('Prepared',name)

if __name__=='__main__':main()
