from __future__ import annotations

import asyncio
from dataclasses import asdict
from pathlib import Path
import shutil
import uuid
import zipfile

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .contracts import AnalysisConfig
from .pipeline import run_analysis
from .schemas import AnalysisCreated, AnalysisRequest, AnalysisStatus, DatasetResponse
from .validation import DatasetValidationError, load_dataset

ROOT = Path(__import__("os").environ.get("RIL_DATA_DIR", "runtime-data"))
DATASETS, ANALYSES = ROOT / "datasets", ROOT / "analyses"
DATASETS.mkdir(parents=True, exist_ok=True)
ANALYSES.mkdir(parents=True, exist_ok=True)
STATE: dict[str, dict] = {}

app = FastAPI(title="Robust Influence Lab", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://localhost:8080"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/datasets", response_model=DatasetResponse)
async def upload_dataset(file: UploadFile = File(...)) -> DatasetResponse:
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(400, "Upload one ZIP containing nodes.csv, edges.csv, and cascades.csv.")
    dataset_id = uuid.uuid4().hex
    target = DATASETS / dataset_id
    target.mkdir()
    archive = target / "upload.zip"
    archive.write_bytes(await file.read())
    try:
        with zipfile.ZipFile(archive) as source:
            for member in source.infolist():
                name = Path(member.filename)
                if name.is_absolute() or ".." in name.parts:
                    raise HTTPException(400, "Archive contains an unsafe path.")
            source.extractall(target)
        for expected in ("nodes.csv", "edges.csv", "cascades.csv"):
            nested = list(target.rglob(expected))
            if nested and not (target / expected).exists():
                shutil.copy2(nested[0], target / expected)
        dataset = load_dataset(target)
    except (zipfile.BadZipFile, DatasetValidationError) as exc:
        shutil.rmtree(target, ignore_errors=True)
        raise HTTPException(422, str(exc)) from exc
    return DatasetResponse(dataset_id=dataset_id, nodes=len(dataset.nodes), edges=len(dataset.edges), cascades=len(dataset.cascades), warnings=dataset.warnings)


def _work(analysis_id: str, request: AnalysisRequest) -> None:
    STATE[analysis_id]["status"] = "running"
    try:
        dataset = load_dataset(DATASETS / request.dataset_id)
        config = AnalysisConfig(**request.model_dump(exclude={"dataset_id"}))
        STATE[analysis_id]["result"] = run_analysis(dataset, config)
        STATE[analysis_id]["status"] = "completed"
    except Exception as exc:  # retained in task state for client-safe reporting
        STATE[analysis_id].update(status="failed", error=str(exc))


@app.post("/analyses", response_model=AnalysisCreated)
def create_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks) -> AnalysisCreated:
    if not (DATASETS / request.dataset_id).exists():
        raise HTTPException(404, "Unknown dataset_id")
    analysis_id = uuid.uuid4().hex
    STATE[analysis_id] = {"status": "queued"}
    background_tasks.add_task(_work, analysis_id, request)
    return AnalysisCreated(analysis_id=analysis_id, status="queued")


@app.get("/analyses/{analysis_id}", response_model=AnalysisStatus)
def analysis_status(analysis_id: str) -> AnalysisStatus:
    state = STATE.get(analysis_id)
    if state is None:
        raise HTTPException(404, "Unknown analysis_id")
    return AnalysisStatus(analysis_id=analysis_id, status=state["status"], error=state.get("error"))


@app.get("/analyses/{analysis_id}/result")
def analysis_result(analysis_id: str) -> dict:
    state = STATE.get(analysis_id)
    if state is None:
        raise HTTPException(404, "Unknown analysis_id")
    if state["status"] == "failed":
        raise HTTPException(422, state["error"])
    if state["status"] != "completed":
        raise HTTPException(409, "Analysis is not complete")
    return state["result"]
