# Progress — budget–precision sensitivity

## 2026-10-16

- Began independent `review-v3-budget-precision`; copied the prior author-review
  package without modifying it.
- Checked the frozen adapter and W=1280 precision-control interface. The added
  experiment can reuse full-reference outputs and independent evaluation worlds;
  it does not require any full-greedy rerun.
- Froze the W80/W320 strict-PageRank protocol before reading its new utilities,
  then completed all 30 conditions and 60 restricted arms. The raw-output
  validator checked hashes, score maxima, serialized means and Monte Carlo SEs.
- Recomputed the combined 45-condition/90-arm post-hoc precision sensitivity
  study from arrays and selected the contribution framing that distinguishes
  finite-reference budget from numerical ranking precision.
- Rewrote the manuscript and supplement, compiled a 19-page main article and
  11-page online resource, and visually inspected every page. The final
  regeneration, delivery gate and independent archive extraction check remain.
- Regenerated the new analysis from raw arrays without value changes, passed the
  V3 delivery gate, and created/extracted a SHA-256-verified local review archive.
- Final archive: `submission/computing-author-review-20261016-budget-precision-v3.zip`;
  1,794 extracted members passed CRC and SHA-256 verification. Third-party raw
  source files remain excluded, with download and hash records retained.
