"""Audit the gates required for a release-ready Journal of Software package.

The audit is intentionally conservative. It never edits a manuscript, creates
an archive, or writes inside an experiment study. Its report distinguishes
verified evidence from author-controlled and manual submission requirements.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).parent))
from build_v3_fairness_sensitivity_analysis import validate as validate_v3
from audit_v3_manuscript_consistency import audit as audit_v3_text


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_V3_ENVIRONMENT = "reproducibility/environment-record-v3-fairness-sensitivity-2026-08-15.md"
V3_ENVIRONMENT_HASH_FILES = {
    "protocols/influence_v3_fairness_sensitivity_preregistration.md",
    "experiments/run_v3_fairness_sensitivity.py",
    "backend/app/pipeline_v2_t0.py",
    "backend/app/pipeline_v2_t0b.py",
    "backend/app/model_v2.py",
}


def check_file(path: Path, label: str) -> tuple[bool, str]:
    if not path.is_file():
        return False, f"Missing required {label}: {path.as_posix()}"
    return True, f"Present: {path.as_posix()}"


def audit_citations(source: Path, references: Path) -> tuple[bool, str]:
    source_text = source.read_text(encoding="utf-8")
    reference_text = references.read_text(encoding="utf-8")
    declared = [int(value) for value in re.findall(r"^\[(\d+)\]", source_text, flags=re.MULTILINE)]
    cited = {int(value) for value in re.findall(r"\[(\d+)\]", source_text)}
    expected = list(range(1, len(declared) + 1))
    if declared != expected:
        return False, "Reference list numbering is not consecutive from 1."
    unknown = sorted(cited - set(declared))
    if unknown:
        return False, f"Manuscript cites undeclared references: {unknown}"
    entries = len(re.findall(r"(?m)^@\w+\s*\{", reference_text))
    if entries != len(declared):
        return False, f"Reference count differs between draft ({len(declared)}) and BibTeX ({entries})."
    return True, f"Citation numbering and bibliography count agree ({entries} entries)."


def audit_claim_boundaries(source: Path, abstract: Path, ledger: Path) -> tuple[bool, str]:
    source_text = source.read_text(encoding="utf-8")
    abstract_text = abstract.read_text(encoding="utf-8")
    ledger_text = ledger.read_text(encoding="utf-8")
    required = {
        "RIS non-significance boundary": "all three comparisons with RIS",
        "exact-null ablation boundary": "exactly zero",
        "paired-repeat boundary": "not independent social networks",
    }
    missing = [name for name, token in required.items() if token not in ledger_text]
    if not any(token in ledger_text for token in ("algorithmic lower-bound audit", "protected-lower-bound audit")):
        missing.append("protected GNN lower-bound boundary")
    if "GNN Top-K" not in source_text or "Holm" not in source_text:
        missing.append("Chinese manuscript GNN/Holm evidence markers")
    if "protected lower-bound audit" not in abstract_text or "independent efficacy comparison" not in abstract_text:
        missing.append("English abstract protected-baseline boundary")
    if missing:
        return False, "Missing claim-boundary evidence: " + "; ".join(missing)
    return True, "Manuscript, abstract, and claim ledger retain the protected-baseline, RIS, null-ablation, and paired-repeat boundaries."


def audit_metadata(path: Path) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8")
    rows: list[tuple[str, str, str, str]] = []
    for line in text.splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 4 and cells[0] != "Field":
            rows.append((cells[0], cells[1], cells[2], cells[3].lower()))
    if not rows:
        return False, "Author-controlled metadata table is missing or malformed."
    pending = [field for field, _, _, status in rows if status == "pending"]
    if pending:
        return False, f"Author-controlled metadata has {len(pending)} pending fields."
    invalid_status = [field for field, _, _, status in rows if status not in {"confirmed", "not applicable"}]
    if invalid_status:
        return False, "Metadata rows require status `confirmed` or `not applicable`: " + ", ".join(invalid_status)
    missing_value = [field for field, value, _, _ in rows if not value]
    if missing_value:
        return False, "Metadata rows lack a verified value or explicit `not applicable`: " + ", ".join(missing_value)
    missing_source = [field for field, _, source, _ in rows if not source]
    if missing_source:
        return False, "Metadata rows lack a confirmation source: " + ", ".join(missing_source)
    return True, f"All {len(rows)} author-controlled metadata fields are confirmed or explicitly not applicable."


def audit_v3(study: Path, analysis: Path | None) -> tuple[bool, str]:
    if analysis is None:
        return False, "No strict v3 analysis directory was supplied."
    try:
        validate_v3(study)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return False, f"v3 study is not accepted: {exc}"
    required = {
        "analysis-report.md", "stats-appendix.md", "figure-catalog.md",
        "paired_comparisons.json", "sensitivity_descriptives.csv",
        "sensitivity-descriptives.md",
    }
    missing = sorted(name for name in required if not (analysis / name).is_file())
    if missing:
        return False, "Strict v3 analysis is incomplete: " + ", ".join(missing)
    return True, "Completed v3 study and strict analysis bundle passed their required artifacts check."


def audit_v3_environment(path: Path, study: Path) -> tuple[bool, str]:
    """Require a frozen runtime sidecar that agrees with the accepted manifest."""
    ok, detail = check_file(path, "v3 runtime environment record")
    if not ok:
        return ok, detail
    try:
        validate_v3(study)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return False, f"v3 environment record cannot be reconciled until v3 is accepted: {exc}"
    record = path.read_text(encoding="utf-8")
    hashes = {
        name: value.lower()
        for name, value in re.findall(r"\| `([^`]+)` \| `([0-9A-Fa-f]{64})` \|", record)
    }
    missing = sorted(V3_ENVIRONMENT_HASH_FILES - set(hashes))
    if missing:
        return False, "v3 environment record lacks required hash entries: " + ", ".join(missing)
    manifest = json.loads((study / "manifest.json").read_text(encoding="utf-8"))
    manifest_hashes = {**manifest.get("protocol", {}), **manifest.get("source", {})}
    expected = {
        "protocols/influence_v3_fairness_sensitivity_preregistration.md": manifest_hashes.get("influence_v3_fairness_sensitivity_preregistration.md"),
        "experiments/run_v3_fairness_sensitivity.py": manifest_hashes.get("run_v3_fairness_sensitivity.py"),
        "backend/app/pipeline_v2_t0.py": manifest_hashes.get("pipeline_v2_t0.py"),
        "backend/app/pipeline_v2_t0b.py": manifest_hashes.get("pipeline_v2_t0b.py"),
        "backend/app/model_v2.py": manifest_hashes.get("model_v2.py"),
    }
    absent = sorted(name for name, value in expected.items() if not isinstance(value, str))
    if absent:
        return False, "v3 manifest lacks required protocol/source hashes: " + ", ".join(absent)
    mismatched = sorted(name for name, value in expected.items() if hashes[name] != value.lower())
    if mismatched:
        return False, "v3 environment and final-manifest hashes differ: " + ", ".join(mismatched)
    return True, "v3 runtime environment record and final manifest agree on protocol and source hashes."


def audit_v3_manuscript(analysis: Path | None, source: Path, abstract: Path, ledger: Path) -> tuple[bool, str]:
    if analysis is None:
        return False, "No strict v3 analysis directory was supplied for manuscript consistency."
    try:
        issues = audit_v3_text(analysis, source, abstract, ledger)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return False, f"v3 manuscript consistency audit failed: {exc}"
    if issues:
        return False, "v3 manuscript consistency issues: " + "; ".join(issues)
    return True, "Accepted v3 family counts and null-result wording agree with the manuscript, abstract, and claim ledger."


def audit_release_inventory(path: Path | None) -> tuple[bool, str]:
    if path is None:
        return False, "No author-approved public release inventory was supplied."
    ok, detail = check_file(path, "release inventory")
    if not ok:
        return ok, detail
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"Release inventory is not valid JSON: {exc}"
    if data.get("release_scope") != "code-and-metadata inventory only; no archive is created":
        return False, "Release inventory scope is not the approved code-and-metadata inventory scope."
    return True, f"Author-approved release inventory lists {data.get('file_count', 0)} files."


def audit_manual_artifact(path: Path | None, label: str) -> tuple[bool, str]:
    if path is None:
        return False, f"No {label} was supplied."
    return check_file(path, label)


def render_report(checks: list[dict[str, str | bool]]) -> str:
    lines = [
        "# Final Submission-Package Audit",
        "",
        "This is a gate audit, not evidence of acceptance or an online submission.",
        "",
        "| Gate | Status | Evidence |",
        "| --- | --- | --- |",
    ]
    for check in checks:
        status = "pass" if check["passed"] else "open"
        lines.append(f"| {check['gate']} | {status} | {check['detail']} |")
    open_gates = [check["gate"] for check in checks if not check["passed"]]
    lines.extend(["", "## Disposition", ""])
    if open_gates:
        lines.append("Not ready for official-template conversion or submission. Open gates: " + ", ".join(open_gates) + ".")
    else:
        lines.append("All audited gates pass. Perform the final human upload review before submitting.")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="manuscript/draft_zh_v0_1.md")
    parser.add_argument("--abstract", default="manuscript/abstract_en_v0_1.md")
    parser.add_argument("--claim-ledger", default="manuscript/claim_ledger.md")
    parser.add_argument("--references", default="manuscript/references.bib")
    parser.add_argument("--metadata", default="manuscript/submission_metadata_intake.md")
    parser.add_argument("--v3-study", default="results/large-robust-greedy-higgs-50000-v3-fairness-sensitivity")
    parser.add_argument("--v3-analysis")
    parser.add_argument("--v3-environment", default=DEFAULT_V3_ENVIRONMENT)
    parser.add_argument("--release-inventory")
    parser.add_argument("--template-verification")
    parser.add_argument("--final-docx")
    parser.add_argument("--visual-qa")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()

    output = Path(args.output_dir)
    if output.exists() and any(output.iterdir()):
        parser.error(f"Refusing to overwrite a non-empty audit directory: {output}")
    source = Path(args.source)
    abstract = Path(args.abstract)
    ledger = Path(args.claim_ledger)
    references = Path(args.references)
    metadata = Path(args.metadata)
    required = [(source, "Chinese manuscript source"), (abstract, "English abstract"), (ledger, "claim ledger"), (references, "BibTeX bibliography"), (metadata, "submission metadata intake")]
    missing = [(path, label) for path, label in required if not path.is_file()]
    if missing:
        parser.error("; ".join(f"Missing {label}: {path}" for path, label in missing))

    citation_ok, citation_detail = audit_citations(source, references)
    claim_ok, claim_detail = audit_claim_boundaries(source, abstract, ledger)
    metadata_ok, metadata_detail = audit_metadata(metadata)
    v3_ok, v3_detail = audit_v3(Path(args.v3_study), Path(args.v3_analysis) if args.v3_analysis else None)
    environment_ok, environment_detail = audit_v3_environment(Path(args.v3_environment), Path(args.v3_study))
    v3_text_ok, v3_text_detail = audit_v3_manuscript(Path(args.v3_analysis) if args.v3_analysis else None, source, abstract, ledger)
    release_ok, release_detail = audit_release_inventory(Path(args.release_inventory) if args.release_inventory else None)
    template_ok, template_detail = audit_manual_artifact(Path(args.template_verification) if args.template_verification else None, "fresh official-template verification")
    docx_ok, docx_detail = audit_manual_artifact(Path(args.final_docx) if args.final_docx else None, "final official-template DOCX")
    visual_ok, visual_detail = audit_manual_artifact(Path(args.visual_qa) if args.visual_qa else None, "page-by-page official-template visual QA")
    checks = [
        {"gate": "citation consistency", "passed": citation_ok, "detail": citation_detail},
        {"gate": "claim-boundary consistency", "passed": claim_ok, "detail": claim_detail},
        {"gate": "completed v3 evidence", "passed": v3_ok, "detail": v3_detail},
        {"gate": "v3 environment reconciliation", "passed": environment_ok, "detail": environment_detail},
        {"gate": "v3 manuscript consistency", "passed": v3_text_ok, "detail": v3_text_detail},
        {"gate": "author metadata", "passed": metadata_ok, "detail": metadata_detail},
        {"gate": "public release inventory", "passed": release_ok, "detail": release_detail},
        {"gate": "fresh official template", "passed": template_ok, "detail": template_detail},
        {"gate": "official-template DOCX", "passed": docx_ok, "detail": docx_detail},
        {"gate": "official-template visual QA", "passed": visual_ok, "detail": visual_detail},
    ]
    output.mkdir(parents=True, exist_ok=False)
    (output / "submission-package-audit.md").write_text(render_report(checks), encoding="utf-8")
    (output / "submission-package-audit.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.require_ready and not all(bool(check["passed"]) for check in checks):
        print(f"Wrote open-gate submission audit to {output}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Wrote submission audit to {output}")


if __name__ == "__main__":
    main()
