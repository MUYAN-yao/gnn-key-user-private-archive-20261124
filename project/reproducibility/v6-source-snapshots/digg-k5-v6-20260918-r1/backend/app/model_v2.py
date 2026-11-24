"""Versioned configurable temporal edge model for the v2 preregistered pilot.

This module intentionally does not alter model.py, which remains the frozen
v1 implementation used by the completed studies.
"""
from __future__ import annotations

import os
import numpy as np
import torch
from torch import nn

try:
    from torch_geometric.nn import GATv2Conv
    HAS_PYG = True
except ImportError:  # pragma: no cover
    HAS_PYG = False


class TemporalEdgeGATV2(nn.Module):
    def __init__(self, in_channels: int, hidden_channels: int, layers: int, decoder: str):
        super().__init__()
        self.has_pyg = HAS_PYG
        self.decoder_name = decoder
        if layers not in (1, 2):
            raise ValueError("layers must be 1 or 2")
        if decoder not in ("concat_mlp", "bilinear"):
            raise ValueError("decoder must be concat_mlp or bilinear")
        if HAS_PYG:
            dimensions = [in_channels] + [hidden_channels] * layers
            self.convs = nn.ModuleList(
                GATv2Conv(dimensions[index], dimensions[index + 1], heads=2, concat=False, edge_dim=1, add_self_loops=True)
                for index in range(layers)
            )
        else:
            dimensions = [in_channels] + [hidden_channels] * layers
            self.self_linears = nn.ModuleList(nn.Linear(dimensions[index], dimensions[index + 1]) for index in range(layers))
            self.neighbor_linears = nn.ModuleList(nn.Linear(dimensions[index], dimensions[index + 1]) for index in range(layers))
        self.concat_head = nn.Sequential(
            nn.Linear(hidden_channels * 2 + 1, hidden_channels), nn.ReLU(), nn.Linear(hidden_channels, 1)
        ) if decoder == "concat_mlp" else None
        self.bilinear_head = nn.Bilinear(hidden_channels, hidden_channels, 1) if decoder == "bilinear" else None

    def encode(self, x: torch.Tensor, edge_index: torch.Tensor, edge_attr: torch.Tensor) -> torch.Tensor:
        state = x
        if self.has_pyg:
            for conv in self.convs:
                state = torch.relu(conv(state, edge_index, edge_attr))
            return state
        for self_linear, neighbor_linear in zip(self.self_linears, self.neighbor_linears):
            aggregate = torch.zeros_like(state)
            counts = torch.zeros((state.size(0), 1), device=state.device)
            if edge_index.numel():
                source, target = edge_index
                aggregate.index_add_(0, target, state[source] * edge_attr)
                counts.index_add_(0, target, edge_attr)
            state = torch.relu(self_linear(state) + neighbor_linear(aggregate / counts.clamp(min=1.0)))
        return state

    def edge_logits(self, z: torch.Tensor, pairs: torch.Tensor, edge_weight: torch.Tensor) -> torch.Tensor:
        if self.concat_head is not None:
            return self.concat_head(torch.cat([z[pairs[0]], z[pairs[1]], edge_weight], dim=1)).squeeze(1)
        return self.bilinear_head(z[pairs[0]], z[pairs[1]]).squeeze(1)


def _device() -> torch.device:
    requested = os.environ.get("RIL_DEVICE", "auto").lower()
    return torch.device("cpu" if requested == "cpu" else "cuda" if torch.cuda.is_available() else "cpu")


def train_edge_model_v2(
    features: np.ndarray,
    edges: list[tuple[int, int, float]],
    *,
    epochs: int,
    seed: int,
    hidden_channels: int,
    layers: int,
    learning_rate: float,
    decoder: str,
    supervised_positive_pairs: list[tuple[int, int]] | None = None,
) -> tuple[TemporalEdgeGATV2, torch.Tensor, bool]:
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    device = _device()
    x = torch.tensor(features, dtype=torch.float32, device=device)
    edge_index = torch.tensor([[source for source, _, _ in edges], [target for _, target, _ in edges]], dtype=torch.long, device=device)
    edge_attr = torch.tensor([[weight] for _, _, weight in edges], dtype=torch.float32, device=device)
    model = TemporalEdgeGATV2(x.size(1), hidden_channels, layers, decoder).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    existing = {(source, target) for source, target, _ in edges}
    positive_pair_list = supervised_positive_pairs or [(source, target) for source, target, _ in edges]
    if not positive_pair_list:
        raise ValueError("At least one supervised positive edge is required")
    existing.update(positive_pair_list)
    rng = np.random.default_rng(seed)
    negatives: list[tuple[int, int]] = []
    while len(negatives) < len(positive_pair_list):
        pair = (int(rng.integers(len(features))), int(rng.integers(len(features))))
        if pair[0] != pair[1] and pair not in existing:
            negatives.append(pair)
    positive_pairs = torch.tensor(positive_pair_list, dtype=torch.long, device=device).T
    negative_pairs = torch.tensor(negatives, dtype=torch.long, device=device).T
    pairs = torch.cat([positive_pairs, negative_pairs], dim=1)
    labels = torch.cat([torch.ones(len(positive_pair_list), device=device), torch.zeros(len(negatives), device=device)])
    weights = torch.zeros((pairs.size(1), 1), dtype=torch.float32, device=device)
    for _ in range(epochs):
        optimizer.zero_grad()
        embeddings = model.encode(x, edge_index, edge_attr)
        loss = nn.functional.binary_cross_entropy_with_logits(model.edge_logits(embeddings, pairs, weights), labels)
        loss.backward()
        optimizer.step()
    model.eval()
    with torch.no_grad():
        embeddings = model.encode(x, edge_index, edge_attr)
    return model, embeddings.detach(), model.has_pyg


def predict_edge_probabilities_v2(model: TemporalEdgeGATV2, embeddings: torch.Tensor, pairs: list[tuple[int, int]]) -> np.ndarray:
    if not pairs:
        return np.array([], dtype=np.float32)
    tensor_pairs = torch.tensor(pairs, dtype=torch.long, device=embeddings.device).T
    with torch.no_grad():
        weights = torch.zeros((len(pairs), 1), dtype=torch.float32, device=embeddings.device)
        return torch.sigmoid(model.edge_logits(embeddings, tensor_pairs, weights)).cpu().numpy()
