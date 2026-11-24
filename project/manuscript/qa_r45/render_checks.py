"""Read-only document/data verification; render QA images in this folder."""
import csv
import json
from pathlib import Path

import pymupdf
from docx import Document
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIGURES = HERE.parent / "figures_snam_r45"
report = {"figures": {}, "document": {}}
for name in ("fig-02-method-mechanism", "fig-06-v1-future-auc", "fig-07-t0-outer-auc"):
    with pymupdf.open(FIGURES / f"{name}.pdf") as pdf:
        width_mm = pdf[0].rect.width / 72 * 25.4
        assert abs(width_mm - 183) < .01
        assert len(pdf[0].get_text().strip()) > 80, "Missing editable vector text"
        pdf[0].get_pixmap(dpi=150).save(HERE / f"{name}-pdf-render.png")
    with Image.open(FIGURES / f"{name}.png") as image:
        assert min(image.info["dpi"]) >= 599
        report["figures"][name] = {"width_mm": width_mm, "pixels": list(image.size), "dpi": list(image.info["dpi"])}

for name, source, seed_key, metric_key in (
    ("fig-06-v1-future-auc", "audits/higgs-edge-prediction-v1/audit_report.json", "random_seed", "future_edge_prediction"),
    ("fig-07-t0-outer-auc", "audits/edge-prediction-v2-t0-outer-test-v1/report.json", "seed", "metrics"),
):
    raw = json.loads((ROOT / source).read_text(encoding="utf-8"))["runs"]
    expected = {(float(r["train_fraction"]), int(r[seed_key])): r[metric_key]["auc"] for r in raw}
    with (FIGURES / f"{name}-source-data.csv").open(encoding="utf-8", newline="") as handle:
        actual = {(float(r["train_fraction"]), int(r["seed"])): float(r["auc"]) for r in csv.DictReader(handle)}
    assert actual == expected and len(actual) == 30
    report["figures"][name]["exact_source_value_match"] = True

doc = Document(HERE.parent / "temporal_key_user_identification_snam_r45_figure_revision.docx")
assert len(doc.inline_shapes) == 10
text = "\n".join(p.text for p in doc.paragraphs)
assert "[Missing figure" not in text
report["document"]["inline_figures"] = len(doc.inline_shapes)
with pymupdf.open(HERE / "word-render.pdf") as pdf:
    report["document"]["pages"] = len(pdf)
    report["document"]["figure_pages"] = {}
    for number, page in enumerate(pdf, 1):
        page.get_pixmap(dpi=105).save(HERE / f"page-{number:02d}.png")
        text = page.get_text()
        for figure in (2, 6, 7):
            if f"图 {figure}：" in text:
                report["document"]["figure_pages"][str(figure)] = number
(HERE / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
