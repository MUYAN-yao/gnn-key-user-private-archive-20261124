# 附录 C　GNN 引导鲁棒贪心的可复核伪代码

本附录是 `backend/app/optimizer.py` 中 `gnn_guided_robust_greedy` 的文字化伪代码，仅说明冻结 v1 所用优化逻辑。它不改变候选池、扩散模型或任何运行工件。

**输入：** 决策快照图 $G$，边概率 $p$，GNN 节点先验 $q$，社区映射 $c$，种子预算 $k$，传播时域 $H$，风险系数 $\lambda$，社区权重 $\eta$，扩散模拟数 $M$，运行随机种子 $r$，候选池大小 $L$。

```text
ROBUST-GREEDY(G, p, q, c, k, H, lambda, eta, M, r, L)
  A <- nodes sorted by decreasing q, then node identifier
  A <- first min(max(k, L), |A|) nodes of A
  R <- M integer streams drawn once from a generator seeded by r
  S <- empty set

  repeat min(k, |A|) times:
      for each v in A not already in S:
          T_v <- EVALUATE(G, p, c, S union {v}, H, lambda, eta, R)
      S <- seed set in the T_v with largest robust objective
      (an exact tie retains the first node in the stable candidate order)

  G_result <- EVALUATE(G, p, c, S, H, lambda, eta, R)
  Q_result <- EVALUATE(G, p, c, first min(k, |A|) nodes of A, H, lambda, eta, R)
  if objective(G_result) > objective(Q_result): return G_result
  otherwise: return Q_result
```

```text
EVALUATE(G, p, c, S, H, lambda, eta, R)
  x_i <- independent-cascade spread from S in G for each fixed stream r_i in R
  mu <- mean(x_i)
  s <- population standard deviation of x_i
  coverage <- number of distinct c(v) for v in S
  return (S, mu, s, mu - lambda*s + eta*coverage, coverage)
```

The same stream list $R$ is passed to every candidate evaluation and every
baseline evaluation in a paired run. The final comparison against GNN Top-K is
intentional: the variance penalty can make the objective non-monotone, so a
pure greedy candidate is retained only when it strictly improves the same
robust objective under the same streams. This is a protocol-level selection
rule, not a guarantee of a global optimum over all nodes.
