from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


@dataclass(frozen=True)
class AnalysisConfig:
    seed_count: int = 5
    horizon: int = 4
    risk_lambda: float = 0.35
    community_weight: float = 0.25
    diffusion_model: Literal["ic", "sir"] = "ic"
    random_seed: int = 42
    epochs: int = 80
    ants: int = 18
    iterations: int = 10
    simulations: int = 30
    train_fraction: float = 0.70
    optimizer: Literal["robust_greedy", "aco"] = "robust_greedy"
    candidate_pool_size: int = 120

    def to_dict(self) -> dict:
        return asdict(self)
