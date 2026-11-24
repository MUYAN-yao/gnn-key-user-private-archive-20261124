# Internal DOCX WPS Visual Preflight

Date: 2026-07-29

## Scope

This is a read-only visual preflight of
`manuscript/temporal_key_user_identification_internal_draft.docx`. It does
not certify the internal draft as a journal-template manuscript and does not
replace final Word or official-template rendering.

## Renderer

- Microsoft Word COM export was attempted first but made no PDF within two
  minutes and was terminated after it remained CPU-idle. No source DOCX was
  saved or changed.
- The source DOCX was then opened through the installed WPS Office desktop
  application. WPS displayed a 17-page document.

## Observed Pages

- Page 1: title, English title, Chinese abstract, keywords, and the opening
  of the introduction were visible without clipping or overlap.
- Page 17: Appendix C pseudo-code and its explanatory prose were visible
  without clipping or overlap.
- The document navigation pane exposed the expected manuscript sections,
  English abstract, and appendices.

## Render Limitation

WPS reported two missing fonts and substituted them:

| Missing font | WPS substitution shown | Consequence |
| --- | --- | --- |
| Courier | Courier New | Pseudo-code may reflow relative to its source rendering. |
| MS Mincho | Fangzheng YDL Gk Typewriting M | Any use of this font may reflow relative to its source rendering. |

Therefore this preflight establishes that the inspected first and final pages
are legible in the available WPS environment, but it is **not** a full
page-by-page, font-faithful render pass. The final delivery gate remains:
render the completed official-template DOCX with the required fonts present,
inspect every page, and record any repairs.

## OOXML Font Follow-up

A read-only inspection of the DOCX package found direct body font declarations
only for `Courier New`, `Times New Roman`, `SimSun`, and `SimHei`. The missing
`Courier` name occurs in `word/styles.xml`, while `MS Mincho` occurs only as
the Japanese theme fallback in `word/theme/theme1.xml`; neither was found as a
direct body-run font. Thus the WPS warning is not proof that the inspected
Chinese prose was reflowed. It still prevents claiming a font-faithful final
render until the official-template pass is performed.
