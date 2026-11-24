# Source-Data Archive License Access Audit

Date: 2026-07-29

## Scope

This is a read-only access audit for the terms needed before distributing any
raw or processed Higgs Twitter or Digg data in a public reproducibility
archive. It does not establish a license, grant redistribution permission, or
alter any experiment input or output.

## Local Preservation Boundary

- `data/README.md` already states that `data/raw/` contains publisher-downloaded
  files and must not be committed to a public code repository.
- The Digg processed data card identifies its parent links as inferred exposure
  proxies. This semantic qualification does not determine redistribution rights.
- Existing manuscript and reproducibility records therefore correctly keep a
  public archive pending rather than promising data release.

## Official-Source Access Attempts

| Source | URL attempted | Result | License conclusion |
| --- | --- | --- | --- |
| SNAP Higgs Twitter dataset page | `https://snap.stanford.edu/data/higgs-twitter.html` | The HTTP client returned no usable response object in this environment. | No terms or redistribution permission verified. |
| SNAP terms candidate | `https://snap.stanford.edu/terms.html` | HTTP 404. | Not a verified terms source. |
| Network Data Repository Digg page | `https://networkrepository.com/soc-digg.php` | The HTTP client returned no usable response object in this environment. | No terms or redistribution permission verified. |
| Network Data Repository terms candidate | `https://networkrepository.com/terms.php` | Connection closed before a response was returned. | Not a verified terms source. |

## Decision

Do not place raw Higgs/Digg files, derived `nodes.csv`/`edges.csv`/`cascades.csv`
files, or their archive copies in a public repository or archival upload.
Proceed only after obtaining and preserving a first-party source page or
license text that explicitly covers the intended research redistribution. A
code-and-metadata-only archive may be prepared later, but its data-acquisition
instructions must direct users to the original publishers and must not imply
that the data are included.
