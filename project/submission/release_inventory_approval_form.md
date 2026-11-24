# Public Release Inventory Approval

This form authorizes a hash inventory only; it does not create an archive and
does not redistribute raw or processed Higgs/Digg data.

## Proposed Include Set

Approve or remove each path before running `build_public_release_inventory.py`:

- [ ] `backend/`
- [ ] `experiments/` (source and statistical scripts only; exclude local logs)
- [ ] `protocols/`
- [ ] `reproducibility/` (manifests and environment records only)
- [ ] `manuscript/` (source, appendices, bibliography, and terminology ledger)
- [ ] `audits/` (approved audit reports only)
- [ ] `analysis/` (accepted derived analysis reports and figures only)
- [ ] `pyproject.toml`
- [ ] `requirements.txt`

## Required Exclusions

The inventory must exclude `data/raw/`, `data/processed/`, `results/`,
`logs/`, `tmp/`, private credentials, author contact details, and any file
whose licence or redistribution status is not confirmed.

## Approval

- Approved include paths (final explicit list):
- Archive platform:
- Archive URL or DOI (if already created):
- Raw-data redistribution status: approved / not approved / unknown
- Code/config/statistics inventory approved: yes / no
- Approver and date:
