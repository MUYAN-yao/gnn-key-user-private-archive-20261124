"""Run v6 only from a verified source snapshot; v5 outputs are never touched."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments import run_v5_candidate_reduction as base
from experiments.v6_digg_snapshot import MANIFEST, sha256, verify

STUDY = 'v6-digg-k5-candidate-reduction'
SCHEMA = 'v6-digg-k5-1'
PROTOCOL = 'influence_v6_digg_k5_preregistration.md'
PREFLIGHT_SEED = 73
FORMAL_SEEDS = tuple(range(74, 84))


def snapshot_metadata(snapshot: Path) -> dict:
    manifest = verify(snapshot)
    expected_runner = (snapshot / 'experiments' / 'run_v6_digg_k5.py').resolve()
    if Path(__file__).resolve() != expected_runner or ROOT.resolve() != snapshot.resolve():
        raise ValueError('v6 runner must execute from the verified v6 snapshot')
    expected_base = (snapshot / 'experiments' / 'run_v5_candidate_reduction.py').resolve()
    if Path(base.__file__).resolve() != expected_base:
        raise ValueError('v6 runner imported computation code outside its snapshot')
    return {'snapshot_dir': str(snapshot.resolve()), 'snapshot_id': manifest['snapshot_id'],
            'manifest_name': MANIFEST, 'manifest_sha256': sha256(snapshot / MANIFEST),
            'file_count': len(manifest['files'])}


def metric_rows(identifier: str, artifact: dict) -> list[dict]:
    return base.metric_rows(identifier, artifact)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--source-snapshot', required=True)
    parser.add_argument('--mode', choices=('preflight', 'formal'), required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    snapshot = Path(args.source_snapshot)
    provenance = snapshot_metadata(snapshot)
    dataset = Path(args.dataset).resolve()
    inputs = base.input_hashes('digg', dataset)
    seeds = (PREFLIGHT_SEED,) if args.mode == 'preflight' else FORMAL_SEEDS
    output = Path(args.output_dir)
    if 'candidate-reduction-v6' not in str(output).lower():
        parser.error('Output must identify the separately versioned v6 study')
    if args.dry_run:
        print(json.dumps({'status': 'dry-run passed', 'study_version': STUDY,
                          'mode': args.mode, 'seeds': seeds, 'writes_nothing': True}, indent=2))
        return
    if output.exists() and any(output.iterdir()):
        parser.error(f'Refusing non-empty output directory: {output}')
    output.mkdir(parents=True)
    protocol_source = ROOT / 'protocols' / PROTOCOL
    shutil.copy2(protocol_source, output / PROTOCOL)
    run_hashes, rows = {}, []
    stopped = False
    for seed in seeds:
        artifact = base.run_one(dataset, 'digg', seed, args.mode, None)
        exceeded = args.mode == 'formal' and artifact['block_elapsed_seconds'] > 18_000
        artifact.update({'study_version': STUDY, 'artifact_schema': SCHEMA,
                         'execution_mode': args.mode, 'formal_batch': args.mode == 'formal' and not exceeded,
                         'not_eligible_for_inference': args.mode != 'formal' or exceeded,
                         'v6_scope_limit': 'Digg inferred exposure proxies; conditional simulated selection only.'})
        artifact['integrity'] = {'status': 'failed_block_time_limit' if exceeded else 'passed',
                                 'block_time_limit_exceeded': exceeded,
                                 'formal_block_time_limit_seconds': 18_000,
                                 'world_families_disjoint': True}
        artifact['artifact_manifest'] = {'inputs': inputs, 'source_snapshot': provenance}
        name = f'seed-{seed}.json'
        path = output / name
        path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2, default=base.json_default) + '\n', encoding='utf-8')
        run_hashes[name] = sha256(path)
        rows.extend(metric_rows(f'seed-{seed}', artifact))
        if exceeded:
            stopped = True
            break
    with (output / 'method_metrics.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    manifest = {'study_version': STUDY, 'artifact_schema': SCHEMA, 'dataset_id': 'digg',
                'execution_mode': args.mode, 'formal_batch': args.mode == 'formal' and not stopped and len(run_hashes) == len(seeds),
                'not_eligible_for_inference': args.mode != 'formal' or stopped or len(run_hashes) != len(seeds),
                'protocol': {PROTOCOL: sha256(protocol_source)}, 'inputs': inputs,
                'source_snapshot': provenance, 'expected_run_ids': [f'seed-{seed}' for seed in seeds],
                'runs': run_hashes, 'run_parameters': {'fraction': 0.65, 'seeds': seeds, 'seed_count': 5,
                'selection_world_count': 20, 'primary_evaluation_world_count': 100,
                'stability_evaluation_world_count': 100, 'arms': list(base.ARMS)}}
    (output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(output)
    if stopped:
        raise RuntimeError('A formal v6 block exceeded 18,000 seconds; batch stopped')


if __name__ == '__main__':
    main()
