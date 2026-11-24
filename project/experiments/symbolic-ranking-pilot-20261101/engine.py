"""External-network adapter retaining the inherited exhaustive IC core.

The greedy, diffusion and hashed-world functions are imported byte-for-byte from
the prior frozen extension in ``legacy_engine.py``.  This module adds only
deterministic readers and topology/ranking metadata for the new source files.
"""
from __future__ import annotations

import gzip
import hashlib
import math
import statistics
import time
from collections import defaultdict
from pathlib import Path

import networkx as nx
import numpy as np

from legacy_engine import (  # noqa: F401
    csr,
    digest,
    evaluate,
    greedy,
    make_worlds,
    spread_one,
    uniform,
    warmup,
    world_ids,
)


RAW_FILENAMES = {
    "college_msg": "CollegeMsg.txt.gz",
    "ca_grqc": "ca-GrQc.txt.gz",
    "wiki_vote": "Wiki-Vote.txt.gz",
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _iter_pairs(path: Path):
    """Yield numeric-looking source/destination strings, skipping SNAP comments."""
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for row_index, line in enumerate(f):
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            fields = text.split()
            if len(fields) < 2:
                raise ValueError(f"Malformed edge row {row_index + 1} in {path.name}")
            yield fields[0], fields[1], row_index


def _read_college(path: Path):
    rows = []
    timestamps = set()
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for row_index, line in enumerate(f):
            fields = line.split()
            if len(fields) != 3:
                raise ValueError(f"Malformed CollegeMsg row {row_index + 1}")
            src, dst, ts_text = fields
            ts = int(ts_text)
            rows.append((ts, int(src), int(dst), row_index, str(src), str(dst)))
            timestamps.add(ts)
    groups = sorted(timestamps)
    cutoff_index = max(1, int(len(groups) * 0.65)) - 1
    cutoff = groups[cutoff_index]
    history = [r for r in rows if r[0] <= cutoff and r[4] != r[5]]
    adjacency = defaultdict(set)
    historical_events = defaultdict(int)
    nodes = set()
    for _, _, _, _, src, dst in history:
        adjacency[src].add(dst)
        historical_events[src] += 1
        nodes.add(src)
        nodes.add(dst)
    return {
        "nodes": sorted(nodes),
        "adjacency": {n: sorted(adjacency[n]) for n in nodes},
        "weighted_scores": dict(historical_events),
        "metadata": {
            "kind": "temporal private-message history; simulated diffusion only",
            "directed_input": True,
            "reciprocalized": False,
            "raw_event_rows": len(rows),
            "retained_event_rows": len(history),
            "timestamp_group_count": len(groups),
            "history_fraction_rule": "first 65% of complete timestamp groups; floor count with at least one group",
            "history_cutoff_unix_seconds": cutoff,
            "history_weight_meaning": "number of retained observed messages sent by a source",
        },
    }


def _read_static(path: Path, reciprocal: bool, kind: str):
    adjacency = defaultdict(set)
    nodes = set()
    raw_rows = 0
    self_loops = 0
    for src, dst, _ in _iter_pairs(path):
        raw_rows += 1
        if src == dst:
            self_loops += 1
            continue
        adjacency[src].add(dst)
        nodes.add(src)
        nodes.add(dst)
        if reciprocal:
            adjacency[dst].add(src)
    return {
        "nodes": sorted(nodes),
        "adjacency": {n: sorted(adjacency[n]) for n in nodes},
        "weighted_scores": None,
        "metadata": {
            "kind": kind,
            "directed_input": not reciprocal,
            "reciprocalized": reciprocal,
            "raw_edge_rows": raw_rows,
            "removed_self_loops": self_loops,
            "history_weight_meaning": None,
        },
    }


def _degree_summary(indptr: np.ndarray) -> dict:
    degrees = np.diff(indptr).astype(np.int64)
    return {
        "mean_out_degree": float(degrees.mean()) if len(degrees) else 0.0,
        "median_out_degree": float(np.median(degrees)) if len(degrees) else 0.0,
        "p95_out_degree": float(np.quantile(degrees, 0.95)) if len(degrees) else 0.0,
        "max_out_degree": int(degrees.max()) if len(degrees) else 0,
        "zero_out_degree_nodes": int(np.sum(degrees == 0)),
    }


def _component_summary(nodes, adjacency) -> dict:
    graph = nx.DiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from((u, v) for u in nodes for v in adjacency[u])
    n = len(nodes)
    weak = max((len(c) for c in nx.weakly_connected_components(graph)), default=0)
    strong = max((len(c) for c in nx.strongly_connected_components(graph)), default=0)
    return {
        "weak_component_count": int(nx.number_weakly_connected_components(graph)),
        "largest_weak_component_nodes": weak,
        "largest_weak_component_fraction": float(weak / n) if n else 0.0,
        "strong_component_count": int(nx.number_strongly_connected_components(graph)),
        "largest_strong_component_nodes": strong,
        "largest_strong_component_fraction": float(strong / n) if n else 0.0,
    }


def load_external_graph(raw_dir: Path, dataset: str) -> dict:
    """Load one preselected dataset without any diffusion outcome calculation."""
    started = time.perf_counter()
    raw_dir = Path(raw_dir)
    if dataset not in RAW_FILENAMES:
        raise ValueError(f"Unknown dataset: {dataset}")
    path = raw_dir / RAW_FILENAMES[dataset]
    if not path.exists():
        raise FileNotFoundError(path)
    if dataset == "college_msg":
        parsed = _read_college(path)
    elif dataset == "ca_grqc":
        parsed = _read_static(
            path,
            reciprocal=True,
            kind="static coauthorship topology; reciprocal arcs created for simulated diffusion only",
        )
    else:
        parsed = _read_static(
            path,
            reciprocal=False,
            kind="static administrator-voting topology; simulated diffusion only",
        )
    nodes = parsed["nodes"]
    adjacency = parsed["adjacency"]
    indptr, targets, sources = csr(nodes, adjacency)
    degree_scores = {n: len(adjacency[n]) for n in nodes}
    rankings = {}
    ranking_seconds = {}
    started_ranking = time.perf_counter()
    rankings["degree"] = np.asarray(
        sorted(range(len(nodes)), key=lambda i: (-float(degree_scores.get(nodes[i], 0)), nodes[i])),
        dtype=np.int64,
    )
    ranking_seconds["degree"] = time.perf_counter() - started_ranking
    started_ranking = time.perf_counter()
    page_scores = nx.pagerank(nx.DiGraph(adjacency), weight=None)
    rankings["pagerank"] = np.asarray(
        sorted(range(len(nodes)), key=lambda i: (-float(page_scores.get(nodes[i], 0)), nodes[i])),
        dtype=np.int64,
    )
    ranking_seconds["pagerank"] = time.perf_counter() - started_ranking
    if parsed["weighted_scores"] is not None:
        started_ranking = time.perf_counter()
        scores = parsed["weighted_scores"]
        rankings["history_weighted"] = np.asarray(
            sorted(range(len(nodes)), key=lambda i: (-float(scores.get(nodes[i], 0)), nodes[i])),
            dtype=np.int64,
        )
        ranking_seconds["history_weighted"] = time.perf_counter() - started_ranking
    metadata = dict(parsed["metadata"])
    metadata.update(
        {
            "dataset": dataset,
            "source_filename": path.name,
            "source_sha256": _sha256(path),
            "n": len(nodes),
            "m": len(targets),
            "density": float(len(targets) / (len(nodes) * (len(nodes) - 1))) if len(nodes) > 1 else 0.0,
            "graph_sha256": hashlib.sha256(
                indptr.tobytes() + targets.tobytes() + "|".join(nodes).encode("utf-8")
            ).hexdigest(),
            "available_rankings": sorted(rankings),
        }
    )
    metadata.update(_degree_summary(indptr))
    metadata.update(_component_summary(nodes, adjacency))
    return {
        "nodes": nodes,
        "indptr": indptr,
        "targets": targets,
        "sources": sources,
        "rankings": rankings,
        "metadata": metadata,
        "preparation_seconds": time.perf_counter() - started,
        "ranking_seconds": ranking_seconds,
    }
