# Archive extraction portability

The first local archive attempt (computing-author-review-20261015-v2.zip) passed
ZIP CRC reading but extraction stopped at a deeply nested historical protocol
path because the unprefixed Windows target exceeded the effective path limit.
This is a packaging portability issue, not an experimental result failure.
The first ZIP and partial extraction are preserved and are not the final delivery.

The delivery archive is computing-author-review-20261015-v3.zip. The verification
script preserves historical paths and uses Windows extended-length paths for
actual extraction and file reads. All members must still pass SHA256 verification.
On Windows, use a short extraction destination or a long-path-aware extraction
tool; a deep destination with an older extractor may reproduce the original error.
See the final adjacent .verification.json for the actual completed extraction.
