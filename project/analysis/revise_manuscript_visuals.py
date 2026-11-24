"""Integrate verified literature and explicitly post-hoc diagnostics."""
from pathlib import Path
import re,json,zipfile,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
P=R/'manuscript/resolution_aware_candidate_truncation_submission_v0_1'
f=P/'manuscript.md'
s=f.read_text(encoding='utf-8')
backup=P/'manuscript_before_visio_expansion_20260920.md'
if not backup.exists(): backup.write_text(s,encoding='utf-8')
else: s=backup.read_text(encoding='utf-8')
s=s.replace('Larger candidate pools reproduced more reference sequences overall, but none reproduced them in every condition.','Larger nominal pools matched more reference sequences, partly because some covered the full graph; genuinely restricted pools did not match consistently.')
s=s.replace('figures/Fig1-evaluation-mechanism.png','figures/Fig1-mechanism-editable.png')
s=s.replace('Arrows indicate computational information flow, not an experimentally established causal mechanism for trace instability.','The network motifs, world tiles, and seed tokens are schematic, not measured data; tile counts are not proportional to simulation budgets. Muted nodes remain in the propagation graph but are ineligible as seeds. Arrows indicate computational information flow, not an experimentally established causal mechanism for trace instability. An editable native Visio master accompanies the figure.')
related='''### 1.1 Related work and the scope of the present contribution

Influence-maximization research addresses several distinct sources of computational difficulty. The classical formulation connects seed selection to the expected reach of a stochastic diffusion process [1]. The algorithmic survey by Li et al. organizes diffusion models and optimization methods, illustrating why a result for one simulator and implementation need not describe the entire problem family [9]. Efficient optimization may reduce repeated marginal-gain calculations, change how influence is sampled, or restrict the eligible seeds. These interventions affect different parts of the computation and require different evidence of accuracy.

The cost-effective lazy-forward approach developed in outbreak detection exploits previously computed information to avoid unnecessary objective evaluations [7]. StaticGreedy instead emphasizes consistent reuse of sampled diffusion realizations during optimization [8]. The latter is particularly relevant here: a fixed collection of worlds defines a reproducible empirical objective, but reproducibility within that collection is a different question from stability when the collection is enlarged. Our shared, nested worlds expose this second question. We do not claim that fixed-world optimization or simulation reuse is new. Nor do we infer that a change in the finite-world greedy sequence invalidates approximation results that apply under their own assumptions.

Sampling-based methods such as IMM pursue efficient influence maximization with algorithm-specific statistical guarantees [2]. Their sampling procedures and stopping conditions differ from the small, enumerated world prefixes examined here. Consequently, the present results cannot be read as a comparison with IMM or as evidence against its guarantees. Our full-search arm exhausts eligible nodes at each greedy round, rather than exhaustively enumerating all seed sets or calculating an exact expected-influence optimum. Naming this comparator precisely is necessary when interpreting either speed improvements or agreement counts.

Candidate-selection research also includes structural heuristics and population-based optimization. In Computing, Rui et al. study a fixed-neighbour-scale approach [12], while Fan et al. develop discrete Harris hawks optimization for influence maximization [13]. These articles establish relevant algorithmic context for the journal, but their reported performance does not validate our degree pools. We deliberately retain a simple historical weighted-degree ranking so that changing the candidate set does not simultaneously change a learned representation. This isolates an evaluation issue; it does not establish a competitive new solver.

Learning-based combinatorial optimization offers another route, reviewed by Li et al. [10]. A recent example combines lightweight reinforcement learning with prior knowledge for imbalanced heterogeneous networks [14]. Learned selection can introduce additional variability from training, representations, and tuning. None of those sources is tested by the present confirmation matrix. Its findings therefore support neither a GNN advantage nor the broader conclusion that learned selectors are unnecessary. A learning claim would require matched historical-information baselines, controlled training choices, and independent evaluation beyond this study.

Two further distinctions concern realism and benchmarking. Temporal-network influence maximization explicitly considers evolving interactions [11], whereas our timestamp split supplies an aggregated historical topology. Empirically motivated influence models can change seed-selection conclusions [15]; contact observations alone do not identify such a model. Benchmarking itself has an established literature, including the study by Arora et al. [16]. We cite that work as evaluation context, without adopting its broader algorithm rankings. The narrower contribution here is a fully exposed comparison of reference resolution, actual candidate coverage, seed-set changes, conditional utility uncertainty, and measured cost on one frozen matrix. This contribution is descriptive and reproducible, rather than a new approximation theorem or a claim of general algorithmic superiority.

'''
s=s.replace('## 2 Resolution-aware evaluation',related+'## 2 Resolution-aware evaluation')
s=s.replace('## 3 Experimental design','''The distinction between the eligible seed set and the propagation graph is essential. Restriction changes which node can be added at a greedy round; it does not delete ineligible nodes or their incident edges from diffusion. Otherwise, a comparison would confound search-space reduction with a different spread model. Similarly, when the nominal pool size reaches the number of vertices, the pool is the full search space. Such an arm is a useful implementation consistency check but supplies no evidence that truncation preserved a solution.

## 3 Experimental design''')
table='''**Table 2. Historical graph instances used by the frozen confirmation run. Edge counts include both directions of each aggregated contact link. Conditions count world-path and selection-budget combinations, not independent datasets.**

| Dataset | Nodes | Directed edges | Seed budgets | Conditions |
| --- | ---: | ---: | --- | ---: |
| invs2013 | 91 | 1,238 | 5, 20 | 12 |
| invs2015 | 212 | 6,938 | 5, 20 | 12 |
| kenya2012 | 75 | 1,044 | 5, 20 | 12 |
| sfhh2009 | 402 | 11,856 | 5 | 6 |

These are sizes after historical preprocessing, rather than headline sizes of the complete provider datasets. The instances permit exhaustive per-round candidate enumeration at the chosen budgets. They do not constitute a large-scale scalability benchmark. Their different sizes also mean that a fixed multiple of the seed budget represents different fractions of the graph.

'''
s=s.replace('### 3.2 Candidate pools and comparison matrix',table+'### 3.2 Candidate pools and comparison matrix')
s=s.replace('These observations establish sensitivity of the reference sequence in this matrix; they do not determine how many final unordered sets changed or whether the higher-budget sequences are uniformly better.','These observations establish sensitivity of the ordered reference in this matrix. Section 4.4 separately examines final unordered sets; neither analysis establishes that higher-budget sequences are uniformly better.')
s=s.replace('(Table 2)','(Table 3)').replace('**Table 2. Exact ordered','**Table 3. Exact ordered')
s=s.replace('The smallest pool delivered', '''Actual candidate coverage qualifies these nominal-pool totals. At \\(k=20\\), the \\(4k\\) pool covers all 75 Kenya nodes, while the \\(8k\\) pool covers all nodes in Kenya and invs2013. Thus, six of the 12 matches for \\(4k\\), and 12 of the 18 matches for \\(8k\\), arise without any restriction. Among genuinely restricted conditions, the match counts are 0/42, 6/36, and 6/30 for \\(2k\\), \\(4k\\), and \\(8k\\). These denominators differ because saturation depends on network size and seed budget; they are not paired estimates of a general success rate. All full-pool arms matched their reference, providing a consistency check on shared-world selection.

The smallest pool delivered''')
s=s.replace('This is a trade-off between computation and reference reproduction.','The nominal comparison mixes genuinely restricted and saturated pools, so the increased match count cannot be attributed entirely to successful truncation.')
s=s.replace('An equals sign indicates an identical ordered trace, and a cross indicates a different trace.','An equals sign indicates an identical ordered trace with a genuinely restricted pool, a cross indicates a different trace, and V identifies a pool containing every graph node. All V cells match by full-pool consistency; they are not successful truncations.')
methods=r'''#### Post-hoc diagnostics

After inspecting the confirmation summaries, we computed additional diagnostics from the stored outputs, without repeating selection or modifying outcomes. Final-set similarity is the Jaccard index \(J(A,B)=|A\cap B|/|A\cup B|\). The first divergence is the one-based greedy round at which adjacent-budget sequences first differ; division by \(k\) expresses its location within a trace. These analyses distinguish changed ordering from changed membership. We also classify each arm by whether its actual candidate count equals the graph's node count, separating full-pool controls from genuine restrictions.

For conditional evaluation uncertainty, let \(d_i\) be candidate-minus-full spread in shared evaluation world \(i\). We estimate the Monte Carlo standard error as \(s_d/\sqrt{2000}\) and display the normal-approximation interval \(\bar d\pm1.96s_d/\sqrt{2000}\). This calculation preserves pairing rather than treating the two arm means as independent. It is conditional on the selected sets and simulator, and assumes the evaluation worlds are independent draws. It does not include selection-path variability, model uncertainty, or sampling of networks. The intervals are unadjusted descriptive intervals, not simultaneous tests or evidence of equivalence. Figure 6 displays the largest tested selection budget; the accompanying CSV retains all 126 comparisons.

'''
s=s.replace('## 4 Results',methods+'## 4 Results')
results=r'''### 4.4 Do changed traces also change final sets?

The post-hoc set analysis shows that the reference changes are not merely reorderings. All 14 final full-greedy sets changed from 20 to 80 worlds, and all 14 changed again from 80 to 320. Jaccard overlap ranged from 0.111 to 0.481 at the first transition and from 0 to 0.667 at the second. The descriptive means were 0.267 and 0.352, respectively. The higher mean at the second transition does not establish monotonic convergence: individual blocks can become less similar, and no tested block has identical final membership across either adjacent transition.

![Final-set stability and trace divergence](figures/Fig5-set-stability.png)

**Fig. 5** Post-hoc seed-set diagnostics from frozen full-greedy outputs. (a) Final-set Jaccard similarity for both adjacent budget transitions within each of the 14 blocks. Grey segments connect the two transitions of the same block; overlapping symbols are retained. (b) The first differing greedy round divided by the seed budget. Smaller values indicate earlier divergence, not a larger utility penalty. Path identifiers 301 and 302 denote the two random-world realizations. These diagnostics were added after confirmation and are not new independent replications.

Within candidate-versus-full comparisons, unordered-set agreement equals ordered agreement for every stored condition. Thus, the discrepancy between those criteria is conceptually important but does not change the match totals in this matrix. The larger concern for interpreting the totals is pool saturation, identified in Section 4.2. Separating actual coverage from nominal pool labels prevents full-search controls from being mistaken for evidence that a reduced search space is sufficient.

![Conditional paired evaluation uncertainty](figures/Fig6-evaluation-uncertainty.png)

**Fig. 6** Post-hoc conditional evaluation uncertainty at 320 selection worlds. Points show candidate-minus-full spread on 2,000 shared, disjoint evaluation worlds; horizontal segments show paired normal-approximation 95% Monte Carlo intervals. The vertical dashed line marks zero. Identical sets have zero paired differences in every world and therefore zero-width intervals. Such points include full-pool controls but are not limited to them. Intervals quantify evaluation sampling uncertainty conditional on the selected sets and fixed simulator; they do not quantify uncertainty across networks or establish practical equivalence.

The forest display distinguishes identical-set zeros, estimates near zero, and visibly negative differences. It complements the computation–utility scatter rather than replacing it: uncertainty and timing answer different questions. A zero-width interval for an identical set is an algebraic consequence of paired evaluation, not exceptional evidence of precision about a broader population. Conversely, an interval crossing zero is insufficient to declare utility preservation without a prespecified equivalence margin. No such margin was fixed for this study.

'''
s=s.replace('## 5 Implications and limits',results+'## 5 Implications and limits')
old='The distinction between an ordered trace and a final seed set also limits the primary stability result. A changed order may leave the final set unchanged; different sets may have similar utility. Our ordered-agreement counts describe procedural reproduction and must be interpreted alongside held-out spread.'
s=s.replace(old,'The post-hoc analysis rules out pure reordering as the explanation of reference changes in this matrix: every adjacent transition also changes final membership. This does not identify the cause of the change or establish a utility penalty. Likewise, separating saturated pools reduces the apparent evidence for successful truncation: many nominal large-pool matches are full-search controls. Both qualifications strengthen interpretation while narrowing the supported claim.')
s=s.replace('## 6 Conclusion','''For reuse, a candidate-pool claim should record the actual candidate fraction alongside its nominal multiplier. A match at full coverage verifies consistency, while a match below full coverage establishes reproduction only for the specified empirical objective. If practical utility preservation is the goal, an acceptable spread-loss margin should be chosen before confirmatory evaluation. Additional evaluation worlds can then reduce conditional Monte Carlo uncertainty, whereas additional selection paths address a different source of variation. Simply increasing one of these budgets does not substitute for the other.

This separation also guides future experiments. Testing another transmission probability or diffusion horizon would probe the scope of the observed sensitivity. Testing larger graphs would probe whether comparable actual candidate fractions remain useful. A learned selector would require a separate comparison against simple historical rankings under matched information and tuning budgets. These are distinct extensions, and the current observations do not predict their outcomes. The frozen study remains valuable as a transparent diagnostic case, but its modest network scale and lack of a new algorithmic guarantee should remain explicit in assessing its contribution.

## 6 Conclusion''')
refs='''
7. Leskovec J, Krause A, Guestrin C, Faloutsos C, VanBriesen J, Glance N (2007) Cost-effective outbreak detection in networks. In: KDD, pp 420–429. https://doi.org/10.1145/1281192.1281239
8. Cheng S, Shen H, Huang J, Zhang G, Cheng X (2013) StaticGreedy: solving the scalability-accuracy dilemma in influence maximization. In: CIKM, pp 509–518. https://doi.org/10.1145/2505515.2505541
9. Li Y, Fan J, Wang Y, Tan K-L (2018) Influence maximization on social graphs: a survey. IEEE Transactions on Knowledge and Data Engineering 30:1852–1872. https://doi.org/10.1109/TKDE.2018.2807843
10. Li Y, Gao H, Gao Y, Guo J, Wu W (2023) A survey on influence maximization: from an ML-based combinatorial optimization. ACM Transactions on Knowledge Discovery from Data 17(9):1–50. https://doi.org/10.1145/3604559
11. Yanchenko E, Murata T, Holme P (2024) Influence maximization on temporal networks: a review. Applied Network Science 9:16. https://doi.org/10.1007/s41109-024-00625-3
12. Rui X, Yang X, Fan J, Wang Z (2020) A neighbour scale fixed approach for influence maximization in social networks. Computing 102:427–449. https://doi.org/10.1007/s00607-019-00778-5
13. Fan C, Wang Z, Zhang J, Zhao J, Rui X (2024) Influence maximization in social networks based on discrete harris hawks optimization algorithm. Computing 106:327–351. https://doi.org/10.1007/s00607-023-01207-4
14. You K, Liu S, Bai Y (2025) Influence maximization under imbalanced heterogeneous networks via lightweight reinforcement learning with prior knowledge. Complex & Intelligent Systems 11:40. https://doi.org/10.1007/s40747-024-01666-y
15. Aral S, Dhillon PS (2018) Social influence maximization under empirical influence models. Nature Human Behaviour 2:375–382. https://doi.org/10.1038/s41562-018-0346-z
16. Arora A, Galhotra S, Ranu S (2017) Debunking the myths of influence maximization: an in-depth benchmarking study. In: SIGMOD, pp 651–666. https://doi.org/10.1145/3035918.3035924
'''
s+=refs
f.write_text(s,encoding='utf-8')
def words(t): return len(re.findall(r"\b[A-Za-z]+(?:[-'][A-Za-z]+)*\b",t.split('## 1 Introduction')[1].split('## Statements and Declarations')[0]))
with zipfile.ZipFile(P/'figures/Fig1-mechanism-editable.vsdx') as z:
    pages=[ET.fromstring(z.read(n)) for n in z.namelist() if re.fullmatch(r'visio/pages/page\d+\.xml',n)]
    shapes=[el for p in pages for el in p.iter() if el.tag.endswith('}Shape')]
    groups=sum(el.attrib.get('Type')=='Group' for el in shapes)
    media=[n for n in z.namelist() if n.startswith('visio/media/')]
assert len(shapes)>100 and groups>=4 and not media
links=re.findall(r'!\[[^]]*\]\(([^)]+)\)',s)
assert len(links)==6 and all((P/l).exists() for l in links)
audit=dict(body_words_before=words(backup.read_text(encoding='utf-8')),body_words_after=words(s),
           figures=len(links),tables=len(re.findall(r'\*\*Table \d',s)),references=16,
           visio_native_shapes=len(shapes),visio_groups=groups,visio_embedded_media=media)
(P/'visual_expansion_audit_20260920.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print(json.dumps(audit,indent=2))
