from __future__ import annotations

from dataclasses import dataclass
import networkx as nx
import numpy as np
import pandas as pd

from .validation import NetworkDataset


@dataclass
class GraphSnapshot:
    graph: nx.DiGraph
    node_ids: list[str]
    features: np.ndarray
    communities: dict[str, int]
    cutoff: str


def time_split(edges: pd.DataFrame, fraction: float = 0.70) -> tuple[pd.DataFrame, pd.DataFrame]:
    point = max(1, min(len(edges) - 1, int(len(edges) * fraction)))
    return edges.iloc[:point].copy(), edges.iloc[point:].copy()


def build_snapshot(dataset: NetworkDataset, edges: pd.DataFrame) -> GraphSnapshot:
    graph = nx.DiGraph()
    node_ids = sorted(dataset.nodes.node_id.astype(str).tolist())
    graph.add_nodes_from(node_ids)
    if edges.empty:
        raise ValueError("Training edge window is empty")
    max_time = edges.timestamp.max()
    age_days = (max_time - edges.timestamp).dt.total_seconds().clip(lower=0) / 86400.0
    decay = np.exp(-age_days / max(age_days.quantile(0.75), 1.0))
    for (_, row), value in zip(edges.iterrows(), decay):
        src, dst = str(row.src), str(row.dst)
        existing = graph.get_edge_data(src, dst, default={})
        graph.add_edge(src, dst, weight=float(existing.get("weight", 0.0)) + float(value), events=int(existing.get("events", 0)) + 1)
    undirected = graph.to_undirected()
    communities_raw = list(nx.algorithms.community.greedy_modularity_communities(undirected, weight="weight"))
    communities = {str(node): idx for idx, group in enumerate(communities_raw) for node in group}
    for node in node_ids:
        communities.setdefault(node, len(communities))
    in_degree = np.array([graph.in_degree(n, weight="weight") for n in node_ids], dtype=np.float32)
    out_degree = np.array([graph.out_degree(n, weight="weight") for n in node_ids], dtype=np.float32)
    pagerank = nx.pagerank(graph, weight="weight") if graph.number_of_edges() else {n: 0 for n in node_ids}
    cascade_counts = dataset.cascades[dataset.cascades.event_time <= max_time].groupby(dataset.cascades.user_id.astype(str)).size()
    activity = np.array([float(cascade_counts.get(n, 0)) for n in node_ids], dtype=np.float32)
    feature = np.column_stack([np.log1p(in_degree), np.log1p(out_degree), activity, [pagerank[n] for n in node_ids]]).astype(np.float32)
    feature = (feature - feature.mean(axis=0)) / (feature.std(axis=0) + 1e-6)
    return GraphSnapshot(graph=graph, node_ids=node_ids, features=feature, communities=communities, cutoff=max_time.isoformat())
