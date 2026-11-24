"""Serial execution controller; never changes the frozen v5 experiment code."""
from __future__ import annotations

import argparse
import ctypes
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / 'reproducibility/v5-source-snapshots/candidate-reduction-v5-20260917-r2'
PREFLIGHT = ROOT / 'audits/candidate-reduction-v5-cost-preflight'
FORMAL = ROOT / 'results/candidate-reduction-v5-formal-r2'
ANALYSIS = ROOT / 'analysis/candidate-reduction-v5-formal-r2'
DATA = {'higgs': 'data/processed/higgs-twitter/pilot-50000',
        'digg': 'data/processed/digg/pilot-20000'}


def read_json_report(path: Path) -> dict:
    """Read validator JSON emitted under either UTF-8 or Windows GB18030."""
    payload = path.read_bytes()
    for encoding in ('utf-8', 'gb18030'):
        try:
            value = json.loads(payload.decode(encoding))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if isinstance(value, dict):
            return value
    raise ValueError(f'{path}: validator output is not a decodable JSON object')


def joint_gate(reports: dict) -> dict:
    if set(reports) != set(DATA):
        raise ValueError('Both dataset preflights are required')
    seconds = {}
    for dataset, report in reports.items():
        if (report.get('status') != 'PASS' or report.get('mode') != 'preflight'
                or report.get('dataset_id') != dataset
                or report.get('validated_run_count') != 1):
            raise ValueError(f'{dataset}: preflight integrity gate failed')
        gate = report.get('cost_gate') or {}
        value = float(gate.get('full_candidate_seconds', math.nan))
        if not math.isfinite(value) or value < 0 or value > 14400 or gate.get('passed') is not True:
            raise ValueError(f'{dataset}: preflight cost gate failed')
        seconds[dataset] = value
    projected = sum(seconds.values()) * 10
    if projected > 72 * 3600:
        raise ValueError('Joint 20-block projection exceeds 72 hours')
    return {'passed': True, 'full_arm_seconds': seconds,
            'joint_projection_hours': projected / 3600}


def wait_for_windows_process(pid: int) -> None:
    # Wait on an OS handle, not a reused PID; no polling of experiment outcomes.
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    kernel.WaitForSingleObject.restype = ctypes.c_uint32
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = kernel.OpenProcess(0x00100000, 0, pid)
    if not handle:
        # An exited process is acceptable only if the later artifact validation passes.
        if ctypes.get_last_error() == 87:
            return
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        if kernel.WaitForSingleObject(handle, 0xFFFFFFFF) != 0:
            raise RuntimeError('Failed to wait for attached preflight process')
    finally:
        kernel.CloseHandle(handle)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--higgs-preflight-pid', type=int, required=True)
    parser.add_argument('--control-dir', type=Path, required=True)
    args = parser.parse_args()
    control = args.control_dir.resolve()
    control.relative_to(PREFLIGHT.resolve())
    control.mkdir(parents=True, exist_ok=True)
    # Persistent exclusive ownership: re-running cannot launch a duplicate batch.
    with (PREFLIGHT / 'controller.lock').open('x', encoding='utf-8') as handle:
        handle.write(str(control))

    def record(stage: str, **details) -> None:
        entry = {'utc': datetime.now(timezone.utc).isoformat(), 'stage': stage, **details}
        with (control / 'events.jsonl').open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(entry) + '\n')
        temporary = control / 'status.tmp'
        temporary.write_text(json.dumps(entry, indent=2) + '\n', encoding='utf-8')
        temporary.replace(control / 'status.json')
        print(json.dumps(entry), flush=True)

    def execute(label: str, script: str, arguments: list[str], report: bool = False):
        command = [sys.executable, '-u', str(SNAPSHOT / 'experiments' / script), *arguments]
        record(label, command=command)
        environment = os.environ.copy()
        environment['PYTHONIOENCODING'] = 'utf-8'
        with (control / f'{label}.stdout.log').open('x', encoding='utf-8') as stdout, \
                (control / f'{label}.stderr.log').open('x', encoding='utf-8') as stderr:
            completed = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=stderr, env=environment)
        if completed.returncode:
            raise RuntimeError(f'{label}: exit {completed.returncode}; see logs')
        if report:
            value = read_json_report(control / f'{label}.stdout.log')
            if value.get('status') != 'PASS':
                raise RuntimeError(f'{label}: validation failed')
            return value

    def validate(dataset: str, mode: str):
        directory = (PREFLIGHT if mode == 'preflight' else FORMAL) / dataset
        return execute(f'{dataset}-{mode}-validation', 'validate_v5_candidate_reduction.py',
                       ['--study-dir', str(directory), '--mode', mode], report=True)

    def run(dataset: str, mode: str) -> None:
        directory = (PREFLIGHT if mode == 'preflight' else FORMAL) / dataset
        execute(f'{dataset}-{mode}', 'run_v5_candidate_reduction.py',
                ['--dataset-name', dataset, '--dataset', str(ROOT / DATA[dataset]),
                 '--output-dir', str(directory), '--source-snapshot', str(SNAPSHOT),
                 '--mode', mode])

    try:
        record('waiting-for-higgs-preflight', attached_pid=args.higgs_preflight_pid)
        wait_for_windows_process(args.higgs_preflight_pid)
        reports = {'higgs': validate('higgs', 'preflight')}
        if reports['higgs'].get('cost_gate', {}).get('passed') is not True:
            raise RuntimeError('Higgs resource gate failed; no further experiments started')
        run('digg', 'preflight')
        reports['digg'] = validate('digg', 'preflight')
        decision = joint_gate(reports)
        (control / 'joint_resource_gate.json').write_text(
            json.dumps(decision, indent=2) + '\n', encoding='utf-8')
        record('joint-resource-gate-passed', **decision)
        for dataset in DATA:
            run(dataset, 'formal')
            validate(dataset, 'formal')
        execute('paired-analysis', 'analyze_v5_candidate_reduction.py',
                ['--study-root', str(FORMAL), '--output-dir', str(ANALYSIS)], report=True)
        record('complete', analysis_directory=str(ANALYSIS),
               manuscript_integration='pending review of accepted formal evidence')
    except Exception as exc:
        record('stopped', reason=str(exc), formal_evidence_admitted=False)
        raise


if __name__ == '__main__':
    main()
