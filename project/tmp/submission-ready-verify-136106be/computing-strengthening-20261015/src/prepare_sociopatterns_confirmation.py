"""Normalize explicitly licensed SocioPatterns contact data for IM diagnostics.

The source contacts are undirected proximity events.  This preparation writes
both directed orientations at each observed time solely to define a symmetric
IC topology; it does not convert contacts into observed information cascades.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from io import TextIOWrapper
from pathlib import Path
from zipfile import ZipFile

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "sociopatterns"
DATASETS = {
    "invs2013": {"file": "workplace_InVS_tij.dat.zip", "kind": "zip_tij", "member": "tij_InVS.dat", "license": "CC0", "source_page": "https://sociopatterns.org/datasets/contacts-in-a-workplace/"},
    "invs2015": {"file": "workplace_InVS15_tij.dat.gz", "kind": "gzip_tij", "license": "CC0", "source_page": "https://sociopatterns.org/datasets/test/"},
    "sfhh2009": {"file": "SFHH_tij.dat.gz", "kind": "gzip_tij", "license": "CC0", "source_page": "https://sociopatterns.org/datasets/sfhh-conference-data-set/"},
    "kenya2012": {"file": "scc2034_household_contact_dataset.zip", "kind": "zip_kenya", "license": "CC0", "source_page": "https://sociopatterns.org/datasets/kenyan-households-contact-network/"},
    "hospital2010": {"file": "hospital_lyon_contacts.dat.gz", "kind": "gzip_tij", "license": "CC-BY-NC-SA", "source_page": "https://sociopatterns.org/datasets/hospital-ward-dynamic-contact-network/"},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_tij(lines: list[str]) -> list[tuple[int, str, str]]:
    events = []
    for line in lines:
        fields = line.split()
        if len(fields) < 3:
            continue
        timestamp, left, right = fields[:3]
        events.append((int(timestamp), str(left), str(right)))
    if not events:
        raise ValueError("no valid tij events")
    return events


def parse_kenya(rows: list[dict[str, str]]) -> list[tuple[int, str, str]]:
    events = []
    for row in rows:
        left = f"{row['h1']}-{row['m1']}"
        right = f"{row['h2']}-{row['m2']}"
        timestamp = (int(row["day"]) - 1) * 24 * 3600 + int(row["hour"]) * 3600
        events.append((timestamp, left, right))
    if not events:
        raise ValueError("no valid Kenya contacts")
    return events


def load_events(config: dict) -> list[tuple[int, str, str]]:
    path = RAW / config["file"]
    kind = config["kind"]
    if kind == "gzip_tij":
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            return parse_tij(stream.read().splitlines())
    if kind == "zip_tij":
        with ZipFile(path) as archive:
            text = archive.read(config["member"]).decode("utf-8")
        return parse_tij(text.splitlines())
    if kind == "zip_kenya":
        rows = []
        with ZipFile(path) as archive:
            for member in archive.namelist():
                if member.endswith(".csv") and not member.startswith("__MACOSX/"):
                    with archive.open(member) as binary:
                        rows.extend(csv.DictReader(TextIOWrapper(binary, encoding="latin-1")))
        return parse_kenya(rows)
    raise ValueError(f"unknown source kind: {kind}")


def normalize(dataset_id: str, output_root: Path) -> dict:
    config = DATASETS[dataset_id]
    source = RAW / config["file"]
    events = load_events(config)
    origin = pd.Timestamp("2000-01-01T00:00:00Z")
    rows = []
    for timestamp, left, right in events:
        if left == right:
            continue
        instant = (origin + pd.Timedelta(seconds=timestamp)).isoformat()
        rows.extend(((left, right, instant), (right, left, instant)))
    edges = pd.DataFrame(rows, columns=["src", "dst", "timestamp"]).drop_duplicates().sort_values(["timestamp", "src", "dst"], kind="mergesort")
    nodes = pd.DataFrame({"node_id": sorted(set(edges.src) | set(edges.dst))})
    destination = output_root / dataset_id
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite {destination}")
    destination.mkdir(parents=True)
    nodes.to_csv(destination / "nodes.csv", index=False)
    edges.to_csv(destination / "edges.csv", index=False)
    pd.DataFrame(columns=["cascade_id", "user_id", "parent_user_id", "event_time"]).to_csv(destination / "cascades.csv", index=False)
    card = {
        "schema": "sociopatterns-confirmation-data-card-0.1",
        "dataset": dataset_id,
        "source_file": config["file"],
        "source_sha256": sha256(source),
        "source_page": config["source_page"],
        "license": config["license"],
        "downloaded_on": "2026-09-20",
        "raw_contact_semantics": "undirected, timestamped proximity contact",
        "edge_transformation": "each undirected contact emitted as two directed events at the original timestamp",
        "cascade_semantics": "not observed; cascades.csv is schema-only and must not be used for propagation claims",
        "node_count": int(len(nodes)),
        "directed_event_count": int(len(edges)),
        "timestamp_group_count": int(edges.timestamp.nunique()),
    }
    (destination / "data_card.json").write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return card


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=sorted(DATASETS), required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(normalize(args.dataset, args.output_root), ensure_ascii=False))


if __name__ == "__main__":
    main()
