# Non-admission record

This partial snapshot-executed run was stopped after five conditions because
the supplied output path was relative and therefore resolved inside the source
snapshot directory. Source-file hashes remain valid, but a confirmation
artifact must be written outside the immutable source snapshot. Do not use
these files as confirmation evidence; rerun the complete frozen matrix from a
new snapshot with an absolute external output root.
