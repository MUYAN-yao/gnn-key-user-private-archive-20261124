"""Convert the public SNAP Higgs Twitter activity file to the platform contract.

Raw format: actor_id target_id epoch_seconds action_type.  The actor performs
the activity on the target.  For influence modelling, the exported graph is
target -> actor: the target is the potential information source and the actor
is the observed responder.  `cascades.csv` therefore records *observed
transmission events*, not complete topic-level cascades.
"""
from __future__ import annotations

import argparse
import gzip
from pathlib import Path
import zipfile

import pandas as pd


RAW_COLUMNS = ["actor_id", "target_id", "epoch_seconds", "event_type"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/higgs-twitter/higgs-activity_time.txt.gz")
    parser.add_argument("--output", default="data/processed/higgs-twitter")
    parser.add_argument("--max-events", type=int, default=None, help="Use the earliest N events for a controlled pilot run")
    args = parser.parse_args()
    source, output = Path(args.input), Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(source, sep=r"\s+", names=RAW_COLUMNS, compression="gzip")
    if args.max_events is not None:
        raw = raw.head(args.max_events).copy()
    raw["timestamp"] = pd.to_datetime(raw.epoch_seconds, unit="s", utc=True)
    raw["actor_id"] = raw.actor_id.astype(str)
    raw["target_id"] = raw.target_id.astype(str)
    raw["event_type"] = raw.event_type.str.lower()

    # The target authored/was the source of the activity; model propagation
    # from target to the responding actor.  Multiplicity remains as separate,
    # timestamped interactions and weight is one event per row.
    edges = pd.DataFrame({
        "src": raw.target_id,
        "dst": raw.actor_id,
        "timestamp": raw.timestamp.dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "event_type": raw.event_type,
        "weight": 1.0,
    }).sort_values("timestamp")
    nodes = pd.DataFrame({"node_id": sorted(set(raw.actor_id) | set(raw.target_id))})

    # The raw release does not expose an original-post/topic identifier.  A
    # cascade ID groups events by source and UTC hour only for UI traceability;
    # experimental labels are derived from the temporal edge split, never from
    # this proxy grouping.
    cascades = pd.DataFrame({
        "cascade_id": "higgs_" + raw.target_id + "_" + raw.timestamp.dt.strftime("%Y%m%d%H"),
        "user_id": raw.actor_id,
        "parent_user_id": raw.target_id,
        "event_time": raw.timestamp.dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }).sort_values("event_time")

    nodes.to_csv(output / "nodes.csv", index=False)
    edges.to_csv(output / "edges.csv", index=False)
    cascades.to_csv(output / "cascades.csv", index=False)
    with zipfile.ZipFile(output / "higgs-twitter-platform.zip", "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name in ("nodes.csv", "edges.csv", "cascades.csv"):
            bundle.write(output / name, name)
    print({"nodes": len(nodes), "edges": len(edges), "events": len(cascades), "output": str(output)})


if __name__ == "__main__":
    main()
