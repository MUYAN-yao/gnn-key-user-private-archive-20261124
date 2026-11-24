# Findings — budget–precision sensitivity

## Verified starting state

- `review-v2` passed its final gate: 54 frozen main conditions, 468 arms and
  4,680,000 evaluation values; 1,191 historical-manifest files were unchanged.
- Its separate W=1280 precision control comprises 15 conditions and 30 PageRank
  arms. Tightening tolerance changes ca-GrQc PageRank-4k from -0.25082 to
  +0.02608 mean paired nodes, leaves CollegeMsg unchanged, and retains large
  wiki-Vote losses.
- The new work must distinguish candidate-only tolerance diagnostics from new
  utility outputs. No W=80/W=320 strict-tolerance utility result has been read
  while this protocol was being prepared.
