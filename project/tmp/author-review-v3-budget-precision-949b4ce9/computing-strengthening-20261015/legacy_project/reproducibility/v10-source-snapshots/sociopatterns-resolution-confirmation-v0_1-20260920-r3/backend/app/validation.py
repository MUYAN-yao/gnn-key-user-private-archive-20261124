from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pandas as pd


class DatasetValidationError(ValueError):
    pass


@dataclass
class NetworkDataset:
    nodes: pd.DataFrame
    edges: pd.DataFrame
    cascades: pd.DataFrame
    warnings: list[str]


REQUIRED = {
    "nodes.csv": {"node_id"},
    "edges.csv": {"src", "dst", "timestamp"},
    "cascades.csv": {"cascade_id", "user_id", "parent_user_id", "event_time"},
}


def _read_csv(path: Path, required: set[str], dtype: dict[str, str] | None = None) -> pd.DataFrame:
    if not path.exists():
        raise DatasetValidationError(f"Missing required file: {path.name}")
    frame = pd.read_csv(path, dtype=dtype)
    missing = required - set(frame.columns)
    if missing:
        raise DatasetValidationError(f"{path.name} is missing columns: {', '.join(sorted(missing))}")
    return frame


def load_dataset(directory: str | Path) -> NetworkDataset:
    directory = Path(directory)
    nodes = _read_csv(directory / "nodes.csv", REQUIRED["nodes.csv"], {"node_id": "string"})
    edges = _read_csv(directory / "edges.csv", REQUIRED["edges.csv"], {"src": "string", "dst": "string"})
    cascades = _read_csv(
        directory / "cascades.csv", REQUIRED["cascades.csv"],
        {"user_id": "string", "parent_user_id": "string"},
    )
    # Preserve numeric-looking external identifiers exactly. Without this,
    # blank cascade parents can coerce an ID column to float (e.g. 17375.0).
    nodes["node_id"] = nodes.node_id.astype("string")
    edges["src"] = edges.src.astype("string")
    edges["dst"] = edges.dst.astype("string")
    cascades["user_id"] = cascades.user_id.astype("string")
    cascades["parent_user_id"] = cascades.parent_user_id.astype("string")
    warnings: list[str] = []

    if nodes.node_id.isna().any() or nodes.node_id.duplicated().any():
        raise DatasetValidationError("nodes.csv requires unique, non-empty node_id values")
    for field in ("src", "dst", "timestamp"):
        if edges[field].isna().any():
            raise DatasetValidationError(f"edges.csv contains null {field} values")
    if (edges.src == edges.dst).any():
        warnings.append("Self-loops retained; they are ignored by diffusion simulation.")
    edge_times = pd.to_datetime(edges.timestamp, errors="coerce", utc=True)
    cascade_times = pd.to_datetime(cascades.event_time, errors="coerce", utc=True)
    if edge_times.isna().any() or cascade_times.isna().any():
        raise DatasetValidationError("timestamp and event_time must be ISO-8601 parseable")
    edges = edges.assign(timestamp=edge_times).sort_values("timestamp").drop_duplicates(
        subset=["src", "dst", "timestamp"], keep="first"
    )
    cascades = cascades.assign(event_time=cascade_times).sort_values("event_time")
    known = set(nodes.node_id.dropna().astype(str))
    for field in ("src", "dst"):
        unknown = set(edges[field].astype(str)) - known
        if unknown:
            raise DatasetValidationError(f"edges.csv contains {len(unknown)} {field} IDs absent from nodes.csv")
    unknown_users = set(cascades.user_id.astype(str)) - known
    if unknown_users:
        raise DatasetValidationError(f"cascades.csv contains {len(unknown_users)} users absent from nodes.csv")
    invalid_parent = set(cascades.parent_user_id.dropna().astype(str)) - known
    if invalid_parent:
        raise DatasetValidationError("cascades.csv parent_user_id must be blank or present in nodes.csv")
    if cascades.duplicated(subset=["cascade_id", "user_id", "event_time"]).any():
        warnings.append("Duplicate cascade events were retained for audit; they are collapsed in feature building.")
    if edges.timestamp.nunique() < 3:
        warnings.append("Fewer than three distinct edge timestamps; temporal evaluation will be weak.")
    return NetworkDataset(nodes=nodes, edges=edges, cascades=cascades, warnings=warnings)
