"""Audit that the completed v3 statistical bundle is reflected conservatively in the manuscript."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def audit(analysis: Path, manuscript: Path, abstract: Path, ledger: Path) -> list[str]:
    rows = json.loads((analysis / "paired_comparisons.json").read_text(encoding="utf-8"))
    primary = [row for row in rows if row["family"] == "primary_fairness"]
    pools = [row for row in rows if row["family"] == "candidate_pool_sensitivity"]
    weights = [row for row in rows if row["family"] == "objective_weight_sensitivity"]
    issues: list[str] = []
    if len(primary) != 3 or any(row["mean_difference"] != 0.0 or row["ties"] != 10 or row["holm_adjusted_p"] != 1.0 for row in primary):
        issues.append("Primary fairness rows do not match the accepted exact-null result.")
    if len(pools) != 9 or any(row["mean_difference"] != 0.0 or row["ties"] != 10 or row["holm_adjusted_p"] != 1.0 for row in pools):
        issues.append("Candidate-pool rows do not match the accepted exact-null result.")
    nonzero_weights = [row for row in weights if row["mean_difference"] != 0.0]
    if len(weights) != 24 or len(nonzero_weights) != 3 or any(row["holm_adjusted_p"] != 1.0 for row in weights):
        issues.append("Weight-sensitivity family does not match the accepted 23-zero/3-nonzero Holm-null result.")
    manuscript_text = manuscript.read_text(encoding="utf-8")
    abstract_text = abstract.read_text(encoding="utf-8")
    ledger_text = ledger.read_text(encoding="utf-8")
    required_source = ("6.5 v3", "10 次平局", "10.751", "Holm $p=1.000$")
    for token in required_source:
        if token not in manuscript_text:
            issues.append(f"Chinese manuscript is missing v3 evidence token: {token}")
    for token in ("v3", "null", "Holm-supported utility difference"):
        if token not in abstract_text:
            issues.append(f"English abstract is missing v3 boundary token: {token}")
    for token in ("completed confirmatory null result", "exactly zero", "protocol-conditional negative findings"):
        if token not in ledger_text:
            issues.append(f"Claim ledger is missing v3 boundary token: {token}")
    forbidden = ("v3 improves", "v3 superiority", "universal equivalence")
    for token in forbidden:
        if token.lower() in (manuscript_text + abstract_text).lower():
            issues.append(f"Forbidden over-claim token appears in manuscript text: {token}")
    return issues


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis", default="analysis/v3-fairness-sensitivity-strict-paired-v1")
    parser.add_argument("--manuscript", default="manuscript/draft_zh_v0_1.md")
    parser.add_argument("--abstract", default="manuscript/abstract_en_v0_1.md")
    parser.add_argument("--ledger", default="manuscript/claim_ledger.md")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    issues = audit(Path(args.analysis), Path(args.manuscript), Path(args.abstract), Path(args.ledger))
    report = ["# v3 Manuscript Consistency Audit", "", f"Status: {'PASS' if not issues else 'FAIL'}", ""]
    report.append("No v3-to-manuscript inconsistencies were found." if not issues else "\n".join(f"- {issue}" for issue in issues))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(report) + "\n", encoding="utf-8")
    if issues:
        raise SystemExit(1)
    print(f"Wrote v3 manuscript consistency audit to {output}")


if __name__ == "__main__":
    main()
