"""Check metadata integration without altering the frozen experimental evidence."""
from pathlib import Path
import hashlib
import json

import pandas as pd

R = Path(__file__).resolve().parents[1]
BASE = R.parent / "review-v3-budget-precision"
Q = R / "qa"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


for relative in [
    Path("supplement-pr-precision"),
    Path("supplement-pr-budget-precision"),
    Path("audit/precision_budget_validation.json"),
    Path("audit/full_validation.json"),
    Path("analysis/precision_budget/summary_by_budget_precision.csv"),
    Path("analysis/precision_budget/path_metrics.csv"),
]:
    source = BASE / relative
    target = R / relative
    if source.is_dir():
        for path in source.rglob("*"):
            if path.is_file():
                match = target / path.relative_to(source)
                assert match.is_file() and sha(path) == sha(match), path
    else:
        assert sha(source) == sha(target), relative

main = (R / "manuscript/manuscript.tex").read_text(encoding="utf-8")
supp = (R / "manuscript/Online_Resource_1.tex").read_text(encoding="utf-8")
cover = (R / "cover_letter_draft.txt").read_text(encoding="utf-8")
editor = (R / "summary_for_editor.txt").read_text(encoding="utf-8")
metadata = (R / "submission_metadata_audit.md").read_text(encoding="utf-8")
required_main = [
    "The authors declare that they have no competing interests.",
    "All authors read and approved the final manuscript and agreed to its submission to",
    "OpenAI Codex was used to assist code development",
    "This work was supported by a provincial undergraduate innovation and entrepreneurship training project.",
]
for fragment in required_main:
    assert fragment in main, fragment
for text in (main, supp, cover, editor):
    assert "Pending author confirmation" not in text
    assert "await author verification" not in text
    assert "AUTHOR-REVIEW DRAFT" not in text
assert "No public\narchive URL is asserted." in supp
assert "All authors have read and approved the manuscript" in cover
assert "No value to enter" in metadata and "No verified value located" in metadata

old_gate = json.loads((BASE / "qa/final_checks_v3.json").read_text())
assert old_gate["status"] == "PASS"
validation = json.loads((R / "audit/precision_budget_validation.json").read_text())
assert validation["status"] == "PASS" and validation["conditions"] == 30 and validation["arms"] == 60
precision = pd.read_csv(R / "analysis/precision_budget/summary_by_budget_precision.csv")
row = precision[(precision.dataset == "ca_grqc") & (precision.method == "pagerank_4k") & (precision.solver == "strict") & (precision.W == 1280)]
assert len(row) == 1 and abs(float(row.iloc[0].loss_percent_mean) + 0.544437) < 1e-6
render = json.loads((Q / "render_checks_submission.json").read_text())
assert render["status"] == "PASS"
assert render["manuscript"]["pages"] <= 25 and render["text"]["abstract_words"] == 234
assert render["text"]["keywords"] == 5 and not render["text"]["missing_citations"]
assert (R / "audit/submission_guidelines_checked_20261016.md").is_file()
visual = (Q / "visual_review_submission.md").read_text(encoding="utf-8")
assert "19/19" in visual and "11/11" in visual

result = {
    "status": "PASS",
    "frozen_experimental_assets_match_v3": True,
    "metadata_declarations_integrated": True,
    "placeholder_language_absent_from_submission_materials": True,
    "strict_precision_value_verified": float(row.iloc[0].loss_percent_mean),
    "main_pages": render["manuscript"]["pages"],
    "supplement_pages": render["Online_Resource_1"]["pages"],
    "abstract_words": render["text"]["abstract_words"],
    "keywords": render["text"]["keywords"],
    "missing_public_identifiers_not_invented": True,
    "all_pages_visually_reviewed": True,
    "manual_steps_remaining": [
        "corresponding-author web-form declarations and file upload",
        "enter a real grant identifier, ORCID, public URL, DOI or licence only if the journal system requires one and the author has it",
    ],
}
(Q / "submission_ready_checks.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
