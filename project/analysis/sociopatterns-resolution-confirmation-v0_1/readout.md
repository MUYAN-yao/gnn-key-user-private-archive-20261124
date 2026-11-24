# Confirmed resolution-sensitive candidate truncation: readout

## Admission and scope

The source snapshot and all **42/42** conditions passed the frozen-matrix
validator (`status: PASS`). This is a descriptive simulation study: standard
independent-cascade influence maximization with `p=0.01` and horizon 3 on four
SocioPatterns contact-derived bidirectional topologies. It does not estimate a
population parameter, observe information diffusion, establish causal
influence, or compare a GNN with degree screening.

## Main result

Across all 14 nested `(dataset, path, k)` blocks, the ordered full-greedy seed
sequence changed from W=20 to W=80 (**0/14**
unchanged) and again from W=80 to W=320 (**0/14**
unchanged). Exact best-score ties in the full selection trace fell from
**80** at W=20 to **46** at W=80 and **21** at
W=320, out of 190, 190, and 190 greedy rounds respectively. Thus a candidate
pool must be assessed against a named, finite-W full reference; it cannot be
presented as an unconditional approximation to a single stable full search.

## Same-W candidate-pool profile

| Candidate pool | W | Exact ordered match | Mean independent-evaluation difference, range | Positive/zero/negative conditions | Median decision-time saving |
| --- | ---: | ---: | ---: | ---: | ---: |
| Degree 2k | 20 | 0/14 | +0.053 [-0.755, +1.270] | 8/0/6 | 67.2% |
| Degree 2k | 80 | 0/14 | -0.225 [-0.848, +0.156] | 3/0/11 | 83.8% |
| Degree 2k | 320 | 0/14 | -0.356 [-0.831, +0.019] | 1/0/13 | 87.4% |
| Degree 4k | 20 | 4/14 | +0.090 [-0.512, +0.669] | 8/4/2 | 55.9% |
| Degree 4k | 80 | 4/14 | +0.028 [-0.739, +0.905] | 7/4/3 | 66.2% |
| Degree 4k | 320 | 4/14 | -0.158 [-0.671, +0.030] | 1/4/9 | 72.4% |
| Degree 8k | 20 | 6/14 | +0.007 [-1.112, +0.752] | 6/6/2 | 32.8% |
| Degree 8k | 80 | 5/14 | -0.040 [-0.635, +0.470] | 5/5/4 | 41.2% |
| Degree 8k | 320 | 7/14 | -0.124 [-0.610, +0.000] | 0/7/7 | 45.6% |

Evaluation differences have both signs. The sign is therefore not evidence
that a degree pool improves influence; it reflects finite selection and
evaluation variation under the stated protocol. Degree 2k never reproduced the
same-W full sequence; 4k and 8k did so only in a subset of conditions. The
cost reductions are descriptive benefits with an explicit reproduction risk.

## Publication decision

The evidence supports a **methods-and-reproducibility paper**, not an algorithm
paper: *candidate-truncation claims in simulation-based influence maximization
must report selection resolution, nested-world stability, independent
evaluation and computation together*. The article can make a constructive,
bounded contribution by giving a transparent protocol and documenting both the
cost benefit and the failure boundary. It must not claim that any fixed pool is
universally equivalent to full greedy, or that degree screening or a GNN is
superior.

## Figure

`figures/figure-01-resolution-confirmation.png` and `.pdf` are the primary
confirmation figure. It should be accompanied by the frozen protocol,
validator report, source snapshot manifest and condition-level CSV.
