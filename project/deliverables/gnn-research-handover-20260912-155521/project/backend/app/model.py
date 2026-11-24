from __future__ import annotations

import os
import numpy as np
import torch
from torch import nn

try:
    from torch_geometric.nn import GATv2Conv
    HAS_PYG = True
except ImportError:  # pragma: no cover - validated by fallback test
    HAS_PYG = False


class TemporalEdgeGAT(nn.Module):
    """GATv2 encoder with a deterministic PyTorch fallback for lightweight runs."""

    def __init__(self, in_channels: int, hidden_channels: int = 32):
        super().__init__()
        self.has_pyg = HAS_PYG
        if HAS_PYG:
            self.encoder = GATv2Conv(in_channels, hidden_channels, heads=2, concat=False, edge_dim=1, add_self_loops=True)
        else:
            self.self_linear = nn.Linear(in_channels, hidden_channels)
            self.neighbor_linear = nn.Linear(in_channels, hidden_channels)
        self.edge_head = nn.Sequential(nn.Linear(hidden_channels * 2 + 1, hidden_channels), nn.ReLU(), nn.Linear(hidden_channels, 1))

    def encode(self, x: torch.Tensor, edge_index: torch.Tensor, edge_attr: torch.Tensor) -> torch.Tensor:
        if self.has_pyg:
            return torch.relu(self.encoder(x, edge_index, edge_attr))
        aggregate = torch.zeros_like(x)
        counts = torch.zeros((x.size(0), 1), device=x.device)
        if edge_index.numel():
            src, dst = edge_index
            aggregate.index_add_(0, dst, x[src] * edge_attr)
            counts.index_add_(0, dst, edge_attr)
        return torch.relu(self.self_linear(x) + self.neighbor_linear(aggregate / counts.clamp(min=1.0)))

    def edge_logits(self, z: torch.Tensor, pairs: torch.Tensor, edge_weight: torch.Tensor) -> torch.Tensor:
        return self.edge_head(torch.cat([z[pairs[0]], z[pairs[1]], edge_weight], dim=1)).squeeze(1)


def train_edge_model(features: np.ndarray, edges: list[tuple[int, int, float]], epochs: int, seed: int) -> tuple[TemporalEdgeGAT, torch.Tensor, bool]:
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    requested_device = os.environ.get("RIL_DEVICE", "auto").lower()
    device = torch.device("cpu" if requested_device == "cpu" else "cuda" if torch.cuda.is_available() else "cpu")
    n_nodes = len(features)
    x = torch.tensor(features, dtype=torch.float32, device=device)
    edge_index = torch.tensor([[u for u, _, _ in edges], [v for _, v, _ in edges]], dtype=torch.long, device=device)
    edge_attr = torch.tensor([[w] for _, _, w in edges], dtype=torch.float32, device=device)
    model = TemporalEdgeGAT(x.size(1)).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=1e-4)
    positives = edge_index
    existing = {(u, v) for u, v, _ in edges}
    rng = np.random.default_rng(seed)
    negatives: list[tuple[int, int]] = []
    while len(negatives) < len(edges):
        pair = (int(rng.integers(n_nodes)), int(rng.integers(n_nodes)))
        if pair[0] != pair[1] and pair not in existing:
            negatives.append(pair)
    negative_pairs = torch.tensor(negatives, dtype=torch.long, device=device).T
    pairs = torch.cat([positives, negative_pairs], dim=1)
    # Interaction strength informs message passing only. It must not leak the
    # positive label directly through the edge classifier.
    weights = torch.zeros((pairs.size(1), 1), dtype=torch.float32, device=device)
    labels = torch.cat([torch.ones(len(edges), device=device), torch.zeros(len(negatives), device=device)])
    for _ in range(epochs):
        optimizer.zero_grad()
        z = model.encode(x, edge_index, edge_attr)
        loss = nn.functional.binary_cross_entropy_with_logits(model.edge_logits(z, pairs, weights), labels)
        loss.backward()
        optimizer.step()
    model.eval()
    with torch.no_grad():
        z = model.encode(x, edge_index, edge_attr)
    return model, z.detach(), model.has_pyg


def predict_edge_probabilities(model: TemporalEdgeGAT, embeddings: torch.Tensor, pairs: list[tuple[int, int]]) -> np.ndarray:
    """Score arbitrary candidate edges without exposing future edge weight."""
    if not pairs:
        return np.array([], dtype=np.float32)
    device = embeddings.device
    tensor_pairs = torch.tensor(pairs, dtype=torch.long, device=device).T
    with torch.no_grad():
        weights = torch.zeros((len(pairs), 1), dtype=torch.float32, device=device)
        return torch.sigmoid(model.edge_logits(embeddings, tensor_pairs, weights)).cpu().numpy()
