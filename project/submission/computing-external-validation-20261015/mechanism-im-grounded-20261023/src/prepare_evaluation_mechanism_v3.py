"""Convert the editable Visio mechanism figure to a manuscript-ready vector PDF."""
from __future__ import annotations

from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET
import zipfile

import fitz

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
SOURCE = FIG / "im_evaluation_mechanism_v3.svg"
VSDX = FIG / "im_evaluation_mechanism_v3.vsdx"
PORTABLE = FIG / "im_evaluation_mechanism_v3_portable.svg"
OUT = ROOT / "manuscript" / "FigEvaluationMechanism.pdf"
PREVIEW = FIG / "im_evaluation_mechanism_v3_manuscript_preview.png"
AUDIT = ROOT / "audit" / "evaluation_mechanism_validation_v3.json"


def materialize_visio_css(source: str) -> bytes:
    css = {
        name: dict(re.findall(r"([\w-]+)\s*:\s*([^;]+)", body))
        for name, body in re.findall(r"\.(st\d+)\s*\{([^}]+)\}", source)
    }
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
    ns = {"v": "http://schemas.microsoft.com/office/visio/2012/main"}
    with zipfile.ZipFile(VSDX) as package:
        media = [name for name in package.namelist() if name.startswith("visio/media/")]
        pages = [
            name for name in package.namelist()
            if name.startswith("visio/pages/page") and name.endswith(".xml")
            and name != "visio/pages/pages.xml" and "/_rels/" not in name
        ]
        assert not media
        assert len(pages) == 1
        shapes = ET.fromstring(package.read(pages[0])).findall(".//v:Shape", ns)
        assert len(shapes) > 150

    PORTABLE.write_bytes(materialize_visio_css(SOURCE.read_text(encoding="utf-8")))
    svg = fitz.open(PORTABLE)
    incoming = fitz.open("pdf", svg.convert_to_pdf())
    source_page = incoming[0]
    target_width = 119 / 25.4 * 72
    scale = target_width / source_page.rect.width
    final = fitz.open()
    target = final.new_page(width=source_page.rect.width * scale, height=source_page.rect.height * scale)
    target.show_pdf_page(target.rect, incoming, 0)
    final.save(OUT, garbage=4, deflate=True)
    final[0].get_pixmap(dpi=260, alpha=False).save(PREVIEW)
    assert not final[0].get_images(full=True)
    text = re.sub(r"\s+", " ", final[0].get_text())
    for required in ("Observed topology", "Paired greedy selection", "Paired evaluation", "selection time"):
        assert required in text, required

    report = {
        "status": "PASS",
        "native_visio": {
            "path": str(VSDX.relative_to(ROOT)),
            "shape_count": len(shapes),
            "embedded_media": media,
        },
        "vector_pdf": {
            "path": str(OUT.relative_to(ROOT)),
            "raster_images": 0,
            "width_mm": 119,
            "height_mm": final[0].rect.height * 25.4 / 72,
        },
        "scope": "evaluation design; not a new influence-maximization algorithm",
    }
    AUDIT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    final.close(); incoming.close(); svg.close()


if __name__ == "__main__":
    main()
