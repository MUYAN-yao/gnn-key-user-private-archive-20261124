"""Generate v3 numeric LaTex inserts and copy the raw-data-backed figure."""
from pathlib import Path
import shutil
import pandas as pd

R = Path(__file__).resolve().parents[1]
A = R / "analysis/precision_budget"
M = R / "manuscript"


def write_table(path: Path, caption: str, label: str, header: str, rows: list[list[str]], columns: str) -> None:
    body = "\n".join(" & ".join(row) + r" \\" for row in rows)
    path.write_text(
        "\\begin{table}[htbp]\n\\caption{" + caption + "}\\label{" + label + "}\n"
        "\\begin{tabular}{" + columns + "}\n\\toprule\n" + header + r" \\" + "\n\\midrule\n"
        + body + "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n",
        encoding="utf-8",
    )


def triplet(frame: pd.DataFrame, dataset: str, method: str, solver: str) -> str:
    values = frame[(frame.dataset == dataset) & (frame.method == method) & (frame.solver == solver)].sort_values("W")
    return " / ".join(f"{value:.2f}" for value in values.loss_percent_mean)


def main() -> None:
    summary = pd.read_csv(A / "summary_by_budget_precision.csv")
    pool = pd.read_csv(A / "candidate_pool_precision_diagnostics.csv")
    names = {"ca_grqc": "ca-GrQc", "college_msg": "CollegeMsg", "wiki_vote": "wiki-Vote"}
    rows = []
    for dataset in ("ca_grqc", "college_msg", "wiki_vote"):
        for method, label in (("pagerank_4k", "4k"), ("pagerank_5pct", r"5\%")):
            diag = pool[(pool.dataset == dataset) & (pool.method == method)].iloc[0]
            rows.append([names[dataset], label, triplet(summary, dataset, method, "default"), triplet(summary, dataset, method, "strict"), f"{diag.default_vs_strict_jaccard:.3f}"])
    write_table(
        M / "precision_budget_table.tex",
        "Post-hoc PageRank loss across budgets. Each entry is the mean incremental-loss percentage across five original paths at $W=80/320/1280$. Default uses NetworkX tolerance $10^{-6}$; strict uses $10^{-12}$, whose pool is unchanged at $10^{-14}$. Pool Jaccard compares default and strict candidates. This is a numerical sensitivity analysis, not a new primary test family.",
        "tab:precision-budget",
        "Graph & Pool & Default loss (\\%) & Strict loss (\\%) & Pool Jaccard",
        rows,
        "llrrr",
    )
    (M / "related_work_table.tex").write_text(r'''\begin{table}[htbp]
\caption{Source-scoped comparison of stated evaluation focus. ``Not the stated focus'' does not assert that a feature was absent from every implementation or supplement.}\label{tab:related-scope}
\begin{tabularx}{\linewidth}{p{.19\linewidth}p{.31\linewidth}X}
\toprule
Study & Stated object and role of eligibility & Evaluation dimensions relevant here \\
\midrule
Kempe et al. (2003); CELF/IMM & Expected-spread objective and faster seed selection; fixed full eligibility in the standard formulation & Candidate restriction, held-out utility, cross-budget reference changes, ranking precision and coverage are not the stated comparative object. \\
StaticGreedy (2013) & Reused static realizations for scalable influence maximization & Fixed-world construction is central; this paper does not treat its solver result as evidence about the present restricted-pool evaluation chain. \\
Arora et al. (2017) & Comparative benchmarking of influence-maximization methods & Quality and running-time comparability are relevant; the stated benchmark focus differs from cross-budget evaluation of a fixed truncated ranking. \\
Rui et al. (2020) & Neighbour-scale candidate approach & Candidate restriction and influence outcomes are central; numerical ranking precision and sequence/set-versus-held-out-utility separation are not its stated focus. \\
Ko et al. (2025) & Learned inductive influence estimation/maximization & It changes the estimator and evaluates held-out networks; this differs from preserving a simulator while diagnosing a fixed ranking truncation. \\
This study & Fixed candidate restrictions against finite-world full references & Reports coverage, budget, ranking tolerance, sequence/set agreement, disjoint utility, coupling and scoped costs jointly. \\
\bottomrule
\end{tabularx}
\end{table}
''', encoding="utf-8")
    source = A / "figures/precision_budget_loss.pdf"
    shutil.copy2(source, M / "Fig4.pdf")
    shutil.copy2(A / "figures/precision_budget_loss.svg", M / "Fig4.svg")
    (M / "precision_budget_figure_source.csv").write_bytes((A / "precision_budget_loss_figure_source.csv").read_bytes())
    print("v3 numeric insert and Fig4 generated")


if __name__ == "__main__":
    main()
