"""Convert the public Digg relation-and-vote release to the platform contract.

The release contains directed user relations (user A follows/observes user B)
and timestamped user-to-story votes.  A vote by B on a story can expose that
story to A only after the A->B relation exists.  For each vote, this converter
selects the most recent earlier vote by such a source as an *inferred proxy
parent*.  These are not ground-truth reshare links and must be reported as a
structural exposure proxy in any experiment using this data.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import zipfile

import pandas as pd


EDGE_COLUMNS = ["src", "dst", "epoch_seconds"]
TYPE_COLUMNS = ["node_id", "node_type"]


def iso_timestamp(value: int) -> str:
    return pd.Timestamp(value, unit="s", tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="data/raw/digg/unpacked")
    parser.add_argument("--output", default="data/processed/digg/pilot-5000")
    parser.add_argument("--max-events", type=int, default=5000, help="Use the earliest N timestamped votes after filtering.")
    parser.add_argument("--start", help="Optional UTC timestamp, e.g. 2009-06-01T00:00:00Z")
    parser.add_argument("--end", help="Optional exclusive UTC timestamp.")
    args = parser.parse_args()
    if args.max_events < 10:
        parser.error("--max-events must be at least 10")

    input_dir, output = Path(args.input_dir), Path(args.output)
    node_types = pd.read_csv(input_dir / "digg.types", names=TYPE_COLUMNS, dtype={"node_id": "int64", "node_type": "int8"})
    user_ids = set(node_types.loc[node_types.node_type == 1, "node_id"])
    raw_edges = pd.read_csv(
        input_dir / "digg.edges", names=EDGE_COLUMNS,
        dtype={"src": "int64", "dst": "int64", "epoch_seconds": "int64"},
    )
    raw_edges = raw_edges[raw_edges.epoch_seconds > 0].copy()
    is_user_src = raw_edges.src.isin(user_ids)
    is_user_dst = raw_edges.dst.isin(user_ids)
    relations = raw_edges[is_user_src & is_user_dst].copy()
    votes = raw_edges[is_user_src & ~is_user_dst].copy()
    votes["timestamp"] = pd.to_datetime(votes.epoch_seconds, unit="s", utc=True)
    if args.start:
        votes = votes[votes.timestamp >= pd.Timestamp(args.start)]
    if args.end:
        votes = votes[votes.timestamp < pd.Timestamp(args.end)]
    votes = votes.sort_values(["epoch_seconds", "src", "dst"]).head(args.max_events).reset_index(drop=True)
    if len(votes) < 10:
        raise ValueError("The selected vote window has fewer than 10 events")

    # In the source format, A->B is interpreted as A observing B.  Propagation
    # therefore flows B->A once the relation timestamp has passed.
    relation_start: dict[int, dict[int, int]] = defaultdict(dict)
    for row in relations[relations.epoch_seconds <= votes.epoch_seconds.max()].itertuples(index=False):
        observer, source, created = int(row.src), int(row.dst), int(row.epoch_seconds)
        prior = relation_start[observer].get(source)
        if prior is None or created < prior:
            relation_start[observer][source] = created

    previous_votes: dict[int, list[tuple[int, int]]] = defaultdict(list)
    edge_rows: list[dict] = []
    cascade_rows: list[dict] = []
    linked_votes = 0
    for row in votes.itertuples(index=False):
        voter, story, event_time = int(row.src), int(row.dst), int(row.epoch_seconds)
        parent: int | None = None
        observable_sources = relation_start.get(voter, {})
        for source, source_time in reversed(previous_votes[story]):
            if observable_sources.get(source, event_time + 1) <= event_time:
                parent = source
                break
        cascade_rows.append({
            "cascade_id": f"digg_story_{story}",
            "user_id": str(voter),
            "parent_user_id": "" if parent is None else str(parent),
            "event_time": iso_timestamp(event_time),
        })
        if parent is not None:
            linked_votes += 1
            edge_rows.append({
                "src": str(parent),
                "dst": str(voter),
                "timestamp": iso_timestamp(event_time),
                "event_type": "inferred_vote_exposure",
                "weight": 1.0,
            })
        previous_votes[story].append((voter, event_time))
    if not edge_rows:
        raise ValueError("No temporally valid proxy parents were found; choose another vote window or reject this dataset")

    selected_users = sorted({str(value) for value in votes.src} | {row["src"] for row in edge_rows})
    nodes = pd.DataFrame({"node_id": selected_users})
    edges = pd.DataFrame(edge_rows).sort_values("timestamp")
    cascades = pd.DataFrame(cascade_rows).sort_values("event_time")
    output.mkdir(parents=True, exist_ok=True)
    nodes.to_csv(output / "nodes.csv", index=False)
    edges.to_csv(output / "edges.csv", index=False)
    cascades.to_csv(output / "cascades.csv", index=False)
    metadata = {
        "source": "Network Data Repository Digg release (2009 Digg relation-and-vote data)",
        "raw_files": ["digg.edges", "digg.types"],
        "node_semantics": "type-1 nodes only (Digg users)",
        "edge_semantics": "proxy information flow from a previous voter to a later voter on the same story when a prior directed relation permits exposure",
        "proxy_limitation": "parent links are inferred from temporal co-voting and directed relations, not observed reshare causality",
        "orientation_assumption": "raw relation A->B means A observes B, so potential propagation is B->A",
        "selected_vote_events": int(len(votes)),
        "proxy_linked_events": linked_votes,
        "proxy_link_rate": round(linked_votes / len(votes), 6),
        "time_range": [iso_timestamp(int(votes.epoch_seconds.min())), iso_timestamp(int(votes.epoch_seconds.max()))],
    }
    (output / "data-card.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    with zipfile.ZipFile(output / "digg-platform.zip", "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name in ("nodes.csv", "edges.csv", "cascades.csv", "data-card.json"):
            bundle.write(output / name, name)
    print(metadata | {"nodes": len(nodes), "edges": len(edges), "output": str(output)})


if __name__ == "__main__":
    main()
