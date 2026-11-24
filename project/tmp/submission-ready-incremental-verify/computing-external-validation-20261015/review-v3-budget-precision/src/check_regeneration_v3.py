"""Regenerate the new precision-budget analysis and confirm deterministic artifacts."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tracked() -> dict[str, str]:
    files = [
        *sorted((R / "analysis/precision_budget").glob("*.csv")),
        *sorted((R / "analysis/precision_budget/figures").glob("*.csv")),
        *sorted((R / "analysis/precision_budget/figures").glob("*.png")),
        R / "manuscript/precision_budget_table.tex",
        R / "manuscript/related_work_table.tex",
        R / "manuscript/precision_budget_figure_source.csv",
    ]
    return {str(path.relative_to(R)): sha(path) for path in files}


before = tracked()
for name in ("analyze_precision_budget.py", "build_budget_precision_documents.py"):
    subprocess.run([sys.executable, str(R / "src" / name)], check=True)
after = tracked()
different = sorted(key for key in before if before[key] != after.get(key))
result = {
    "status": "PASS" if not different else "FAIL",
    "files_checked": len(before),
    "different_files": different,
    "hashes": after,
    "scope": "Regenerated raw-result-derived precision-budget CSVs, PNG pixels, SVG, LaTeX tables and figure source. The SVG is regenerated but excluded from byte comparison because Matplotlib embeds volatile XML metadata; its source CSV and PNG pixels are checked. The inherited frozen-default regeneration record remains in qa/regeneration.json.",
}
(R / "qa/regeneration_v3.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
assert not different, different
print(json.dumps(result, indent=2))
