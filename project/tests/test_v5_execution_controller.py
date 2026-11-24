import json

import pytest

from experiments.continue_v5_candidate_reduction import joint_gate, read_json_report


def reports(higgs=10000, digg=10000):
    return {name: {'status': 'PASS', 'mode': 'preflight', 'dataset_id': name,
                   'validated_run_count': 1,
                   'cost_gate': {'passed': True, 'full_candidate_seconds': value}}
            for name, value in [('higgs', higgs), ('digg', digg)]}


def test_accepts_joint_boundary():
    assert joint_gate(reports(12960, 12960))['joint_projection_hours'] == 72


def test_rejects_joint_overrun_even_when_individual_gates_pass():
    with pytest.raises(ValueError, match='72 hours'):
        joint_gate(reports(14000, 14000))


@pytest.mark.parametrize('seconds', [float('nan'), float('inf'), -1, 14401])
def test_rejects_invalid_or_excessive_cost(seconds):
    with pytest.raises(ValueError):
        joint_gate(reports(seconds, 1))


def test_rejects_incomplete_or_wrong_mode_evidence():
    values = reports()
    with pytest.raises(ValueError):
        joint_gate({'higgs': values['higgs']})
    values['higgs']['mode'] = 'smoke'
    with pytest.raises(ValueError):
        joint_gate(values)


@pytest.mark.parametrize('encoding', ['utf-8', 'gb18030'])
def test_reads_validator_json_under_windows_or_utf8_output(tmp_path, encoding):
    path = tmp_path / 'report.json'
    expected = {'status': 'PASS', 'study_dir': 'E:\\大学\\校创'}
    path.write_bytes(json.dumps(expected, ensure_ascii=False).encode(encoding))
    assert read_json_report(path) == expected
