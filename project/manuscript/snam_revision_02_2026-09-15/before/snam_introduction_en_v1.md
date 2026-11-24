# Introduction — SNAM working draft

Selecting key users in a social network requires identifying a small set of seeds that can influence subsequent diffusion. Classical influence maximization targets expected spread [1,8]. In a temporal network, however, seed selection is also constrained by what is observable at the decision time: future interactions are unavailable, and historical connections and activity provide inputs to prediction and selection [19,25,26]. A pipeline's score on a historical graph must therefore be interpreted alongside its prediction task, selection rule, and evaluation conditions.

Learning-based pipelines introduce several potential sources of change, including graph representations, candidate screening, and combinatorial search [6,21,31]. A higher final objective relative to degree ranking or a spread-oriented baseline does not isolate which of these components is responsible. Risk-aware and community-oriented formulations add further decision preferences beyond expected spread [11,12,17,20]. Including these preferences in an objective specifies a selection rule; whether they change the selected users or improve utility under a common reporting objective remains an empirical question.

We address three questions. First, which baseline comparisons support a conditional advantage when decision information is restricted by a temporal protocol? Second, do GNN candidate screening, risk penalties, and community rewards change selected sets or utility when the probability graph, reporting objective, and diffusion conditions are controlled? Third, what can be learned separately from future-edge prediction and computational cost? Our community term counts communities represented by selected seeds. It neither measures communities reached by the resulting diffusion nor imposes a group-fairness constraint.

The evaluated pipeline uses GATv2 [2] to obtain edge-probability estimates and a node prior, then searches a restricted candidate set using a mean-spread objective with a standard-deviation penalty and a seed-community reward. We retain frozen Digg 20k and Higgs 50k comparisons and report three separately versioned Higgs studies: a strict timestamp-grouped baseline comparison, a common-world objective ablation, and a candidate-screening and sensitivity study with separate selection and evaluation worlds. Future-edge prediction is evaluated through a separate external test. The same learned probability graph is supplied to both routes in the screening comparison, so that comparison tests the node-screening step rather than removal of the entire GNN model.

The study makes three contributions:

1. An auditable evaluation structure connects future-edge prediction, baseline comparisons under a common objective, and matched-objective component tests to distinct evidence records, with hashes linking inputs, runs, and reported statistics.
2. The strict Higgs results delimit the observed utility gains. Several baseline comparisons survive Holm correction, but none of the RIS comparisons does. All nine common-world objective-ablation contrasts are exactly zero, and the subsequent screening, candidate-pool, and weight families provide no Holm-supported utility difference.
3. Selected-set agreement and local computational cost are reported together. Across thirty paired Higgs runs, screening to 120 candidates produces the same selected sets as full-candidate robust greedy, with lower recorded search-and-final-scoring times. These timings exclude model training and preprocessing, and do not establish an advantage over other candidate-screening rules.

These findings concern a two-seed budget and the documented temporal protocols. Ten stochastic repetitions per split do not constitute ten independent social networks, and overlapping temporal prefixes do not provide independent network samples. The practical contribution is to distinguish a pipeline-level score improvement, an independently supported component effect, and a reduction in the cost of a specific computational stage. This distinction supports a more precise interpretation of learned seed-selection procedures without attributing gains to components solely because they appear in the pipeline.

---

Editorial note: citation numbers refer to the existing bibliography in
`draft_zh_v0_1.md`; no new reference is introduced here. This is the English
introduction draft, not a complete English manuscript or a formatted submission.
