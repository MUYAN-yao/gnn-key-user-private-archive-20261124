from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    dataset_id: str
    seed_count: int = Field(default=5, ge=1, le=100)
    horizon: int = Field(default=4, ge=1, le=100)
    risk_lambda: float = Field(default=0.35, ge=0, le=5)
    community_weight: float = Field(default=0.25, ge=0, le=5)
    diffusion_model: Literal["ic", "sir"] = "ic"
    random_seed: int = Field(default=42, ge=0)
    epochs: int = Field(default=80, ge=5, le=500)
    ants: int = Field(default=18, ge=2, le=100)
    iterations: int = Field(default=10, ge=1, le=100)
    simulations: int = Field(default=30, ge=5, le=1000)
    train_fraction: float = Field(default=0.70, ge=0.50, le=0.90)
    optimizer: Literal["robust_greedy", "aco"] = "robust_greedy"
    candidate_pool_size: int = Field(default=120, ge=2, le=5000)


class DatasetResponse(BaseModel):
    dataset_id: str
    nodes: int
    edges: int
    cascades: int
    warnings: list[str] = []


class AnalysisCreated(BaseModel):
    analysis_id: str
    status: str


class AnalysisStatus(BaseModel):
    analysis_id: str
    status: Literal["queued", "running", "completed", "failed"]
    error: str | None = None
