"""Create presentation-only, low-saturation derivatives of frozen PNG figures."""
from pathlib import Path
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "manuscript" / "figures_v44"
SOURCES = {
    "fig-01-frozen-comparison": ROOT / "analysis/frozen-main-comparison-v1/figures/figure-01-paired-objective-improvement.png",
    "fig-02-v1-future-auc": ROOT / "analysis/higgs-edge-prediction-audit-v2/figures/figure-01-future-auc-by-seed.png",
    "fig-03-t0-outer-auc": ROOT / "analysis/edge-prediction-v2-t0-gate-v2/figures/figure-01-t0-outer-auc.png",
    "fig-04-t0b-comparison": ROOT / "analysis/v2-t0b-strict-paired-v1/figures/figure-01-paired-objective-improvement.png",
    "fig-05-t0b-seed-differences": ROOT / "analysis/v2-t0b-strict-paired-v1/figures/figure-02-seed-level-paired-differences.png",
    "fig-06-t0d-null-matrix": ROOT / "analysis/v2-t0d-common-world-objective-ablation-v2-null-matrix/figures/figure-01-exact-null-matrix.png",
}

# Mapping preserves method identity while reducing saturation for print.
SRC = np.array([[91, 135, 180], [121, 177, 58], [233, 181, 33], [221, 114, 33]], dtype=float)
DST = np.array([[158, 183, 190], [127, 169, 162], [198, 177, 132], [200, 166, 162]], dtype=float)


def recolor(path, stem):
    image = Image.open(path).convert("RGB")
    arr = np.asarray(image).astype(float)
    out = arr.copy()
    flat = arr.reshape(-1, 3)
    flat_out = out.reshape(-1, 3)
    dist = ((flat[:, None, :] - SRC[None, :, :]) ** 2).sum(axis=2)
    idx = dist.argmin(axis=1)
    near = dist.min(axis=1) < 55 ** 2
    flat_out[near] = DST[idx[near]]
    rgb = Image.fromarray(np.uint8(np.clip(out, 0, 255)), mode="RGB")
    OUT.mkdir(parents=True, exist_ok=True)
    rgb.save(OUT / f"{stem}.png")
    rgb.save(OUT / f"{stem}.tif", compression="tiff_lzw")
    rgb.convert("CMYK").save(OUT / f"{stem}-cmyk.tif", compression="tiff_lzw")


if __name__ == "__main__":
    for stem, source in SOURCES.items():
        if source.exists():
            recolor(source, stem)
