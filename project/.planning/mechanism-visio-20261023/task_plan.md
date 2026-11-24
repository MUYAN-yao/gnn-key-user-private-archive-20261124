# Visio mechanism figures and conference-style integration

1. Inspect manuscript, evidence and primary illustration sources — complete.
2. Draw native Visio overview and coupling mechanism — complete.
3. Export, inspect and integrate figures; refine intro/method/captions — complete.
4. Compile and verify figures, manuscript and portable local deliverables — complete.

## Next Step
Deliver the editable Visio, standalone figures, revised PDFs and verified archive.

## Scope
Use Visio as explicitly requested; its native schematic route overrides the
Python/R plotting preference gate. No new quantitative experiment or causal
claim is introduced. Preserve all prior versions.

## Errors and resolutions

- Visio rejected the literal color `none`: set FillPattern/LinePattern explicitly.
- Visio fixed-format PDF export failed: used native SVG export and materialized
  styles plus native line-shape arrowheads before vector PDF conversion.
- MuPDF's initial CSS/marker handling produced invalid visual output: rejected
  and corrected it; inspected both direct Visio PNG and final PDF previews.
- The first supplement build used the wrong working directory: rebuilt twice
  from the flat manuscript folder.
- PDF serialization metadata differed during regeneration: compare portable SVG
  bytes and PNG pixels, with exact values/geometry checked separately.
- Explicit UTF-8 fixed a Windows default-encoding read in the delivery checker.
