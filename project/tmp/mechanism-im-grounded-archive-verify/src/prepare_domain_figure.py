"""Build the manuscript-ready vector PDF from the native Visio export."""
from __future__ import annotations

from pathlib import Path
import csv
import json
import re
import xml.etree.ElementTree as ET
import zipfile
import fitz

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
SOURCE = FIG / "wiki_vote_candidate_coverage_mechanism_v2.svg"
VSDX = FIG / "wiki_vote_candidate_coverage_mechanism_v2.vsdx"
OUT = ROOT / "manuscript" / "FigDirectionMechanism.pdf"
AUDIT = ROOT / "audit" / "direction_figure_validation.json"


def load_wiki_rows() -> dict[str, dict[str, str]]:
    path = ROOT.parent / "review-v3-budget-precision" / "analysis" / "summary_by_method.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    keep = [row for row in rows if row["dataset"] == "wiki_vote" and row["stage"] == "resolution"
            and int(row["W"]) == 1280 and row["method"] in {"full", "pagerank_4k"}]
    return {row["method"]: row for row in keep}


def materialize_visio_css(source: str) -> bytes:
    css = {name: dict(re.findall(r"([\w-]+)\s*:\s*([^;]+)", body))
           for name, body in re.findall(r"\.(st\d+)\s*\{([^}]+)\}", source)}
    root = ET.fromstring(source)

    def visit(node: ET.Element, parent_size: float = 12.0) -> None:
        attrs: dict[str, str] = {}
        for name in node.get("class", "").split():
            attrs.update(css.get(name, {}))
        attrs.update(dict(re.findall(r"([\w-]+)\s*:\s*([^;]+)", node.get("style", ""))))
        size = attrs.get("font-size", str(parent_size))
        try:
            numeric = parent_size * float(size[:-2]) if size.endswith("em") else float(size.replace("px", "").replace("pt", ""))
        except ValueError:
            numeric = parent_size
        if "font-size" in attrs:
            attrs["font-size"] = str(numeric)
        if "font-family" in attrs:
            attrs["font-family"] = "Helvetica"
        for key, value in attrs.items():
            node.set(key, value)
        node.attrib.pop("class", None)
        for child in node:
            visit(child, numeric)

    visit(root)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def main() -> None:
    rows = load_wiki_rows()
    full, pr = rows["full"], rows["pagerank_4k"]
    assert abs(float(full["incremental_spread_mean"]) - 55.73602) < 1e-8
    assert abs(float(pr["incremental_spread_mean"]) - 15.04268) < 1e-8
    assert abs(float(pr["delta_mean"]) + 40.69334) < 1e-8
    assert abs(float(pr["loss_percent_mean"]) - 73.01069737882713) < 1e-10

    native_ns = {"v": "http://schemas.microsoft.com/office/visio/2012/main"}
    with zipfile.ZipFile(VSDX) as package:
        media = [name for name in package.namelist() if name.startswith("visio/media/")]
        pages = [name for name in package.namelist() if name.startswith("visio/pages/page")
                 and name.endswith(".xml") and name != "visio/pages/pages.xml" and "/_rels/" not in name]
        assert not media
        assert len(pages) == 1
        shapes = ET.fromstring(package.read(pages[0])).findall(".//v:Shape", native_ns)
        assert len(shapes) > 50

    portable = FIG / "wiki_vote_candidate_coverage_mechanism_portable.svg"
    portable.write_bytes(materialize_visio_css(SOURCE.read_text(encoding="utf-8")))
    svg = fitz.open(portable)
    incoming = fitz.open("pdf", svg.convert_to_pdf())
    page = incoming[0]
    target_width = 119 / 25.4 * 72
    scale = target_width / page.rect.width
    final = fitz.open()
    target = final.new_page(width=page.rect.width * scale, height=page.rect.height * scale)
    target.show_pdf_page(target.rect, incoming, 0)
    final.save(OUT, garbage=4, deflate=True)
    preview = FIG / "wiki_vote_candidate_coverage_mechanism_preview.png"
    final[0].get_pixmap(dpi=240, alpha=False).save(preview)
    assert not final[0].get_images(full=True)
    text = final[0].get_text()
    for required in ("Candidate coverage", "55.74", "15.04", "73.01%"):
        assert required in text, required
    report = {
        "status": "PASS",
        "native_visio": {"path": str(VSDX.relative_to(ROOT)), "shape_count": len(shapes), "embedded_media": media},
        "vector_pdf": {"path": str(OUT.relative_to(ROOT)), "raster_images": 0, "width_mm": 119,
                       "height_mm": final[0].rect.height * 25.4 / 72},
        "numeric_sources": {"full_incremental_spread_mean": float(full["incremental_spread_mean"]),
                            "pagerank_incremental_spread_mean": float(pr["incremental_spread_mean"]),
                            "pagerank_delta_mean": float(pr["delta_mean"]),
                            "pagerank_loss_percent_mean": float(pr["loss_percent_mean"])},
    }
    AUDIT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    final.close(); incoming.close(); svg.close()


if __name__ == "__main__":
    main()
