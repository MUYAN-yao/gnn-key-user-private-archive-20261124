import json

import pytest

from experiments.build_public_release_inventory import collect, relative_path

from experiments.audit_submission_package import (
    V3_ENVIRONMENT_HASH_FILES,
    audit_claim_boundaries,
    audit_citations,
    audit_metadata,
    audit_v3_environment,
)


def test_submission_audit_accepts_consecutive_citations(tmp_path):
    source = tmp_path / "draft.md"
    references = tmp_path / "references.bib"
    source.write_text("Use [1].\n\n[1] First.\n[2] Second.\n", encoding="utf-8")
    references.write_text("@article{first, title={First}}\n@article{second, title={Second}}\n", encoding="utf-8")
    assert audit_citations(source, references)[0]


def test_submission_audit_requires_claim_boundaries(tmp_path):
    source = tmp_path / "draft.md"
    abstract = tmp_path / "abstract.md"
    ledger = tmp_path / "ledger.md"
    source.write_text("GNN Top-K and Holm are reported.\n", encoding="utf-8")
    abstract.write_text("A protected lower-bound audit is not an independent efficacy comparison.\n", encoding="utf-8")
    ledger.write_text(
        "algorithmic lower-bound audit\nall three comparisons with RIS\n"
        "exactly zero\nnot independent social networks\n",
        encoding="utf-8",
    )
    assert audit_claim_boundaries(source, abstract, ledger)[0]


def test_submission_metadata_rejects_blank_value_marked_confirmed(tmp_path):
    metadata = tmp_path / "metadata.md"
    metadata.write_text(
        "| Field | Verified value | Source or confirmation | Status |\n"
        "| --- | --- | --- | --- |\n"
        "| Author order |  | Written confirmation | confirmed |\n",
        encoding="utf-8",
    )
    passed, detail = audit_metadata(metadata)
    assert not passed
    assert "verified value" in detail


def test_submission_metadata_accepts_explicitly_confirmed_or_not_applicable_rows(tmp_path):
    metadata = tmp_path / "metadata.md"
    metadata.write_text(
        "| Field | Verified value | Source or confirmation | Status |\n"
        "| --- | --- | --- | --- |\n"
        "| Author order | A; B | Signed author confirmation | confirmed |\n"
        "| Ethics statement | not applicable | Signed author confirmation | not applicable |\n",
        encoding="utf-8",
    )
    assert audit_metadata(metadata)[0]


def test_v3_environment_reconciliation_requires_matching_manifest_hashes(tmp_path, monkeypatch):
    environment = tmp_path / "environment.md"
    study = tmp_path / "study"
    study.mkdir()
    hashes = {path: f"{index:064x}" for index, path in enumerate(sorted(V3_ENVIRONMENT_HASH_FILES), start=1)}
    lines = ["| File | SHA-256 |", "| --- | --- |"]
    lines.extend(f"| `{path}` | `{value}` |" for path, value in hashes.items())
    environment.write_text("\n".join(lines), encoding="utf-8")
    manifest = {
        "protocol": {"influence_v3_fairness_sensitivity_preregistration.md": hashes["protocols/influence_v3_fairness_sensitivity_preregistration.md"]},
        "source": {
            "run_v3_fairness_sensitivity.py": hashes["experiments/run_v3_fairness_sensitivity.py"],
            "pipeline_v2_t0.py": hashes["backend/app/pipeline_v2_t0.py"],
            "pipeline_v2_t0b.py": hashes["backend/app/pipeline_v2_t0b.py"],
            "model_v2.py": hashes["backend/app/model_v2.py"],
        },
    }
    (study / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr("experiments.audit_submission_package.validate_v3", lambda _study: None)
    assert audit_v3_environment(environment, study)[0]
    manifest["source"]["model_v2.py"] = "f" * 64
    (study / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    passed, detail = audit_v3_environment(environment, study)
    assert not passed
    assert "hashes differ" in detail


def test_public_release_inventory_rejects_result_paths():
    with pytest.raises(ValueError, match="Forbidden release path"):
        collect([relative_path("results/large-robust-greedy-higgs-50000-v1")])


def test_public_release_inventory_rejects_parent_traversal():
    with pytest.raises(ValueError, match="workspace-relative"):
        relative_path("../outside-workspace")
