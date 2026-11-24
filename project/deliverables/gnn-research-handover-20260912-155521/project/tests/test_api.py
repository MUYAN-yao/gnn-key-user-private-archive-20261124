from pathlib import Path
import zipfile

from fastapi.testclient import TestClient

from app.main import app


def test_upload_and_run_sample(tmp_path):
    archive = tmp_path / "sample.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        for name in ("nodes.csv", "edges.csv", "cascades.csv"):
            bundle.write(Path("sample_data") / name, name)
    with TestClient(app) as client, archive.open("rb") as uploaded:
        created = client.post("/datasets", files={"file": ("sample.zip", uploaded, "application/zip")})
        assert created.status_code == 200
        dataset_id = created.json()["dataset_id"]
        analysis = client.post("/analyses", json={"dataset_id": dataset_id, "seed_count": 2, "epochs": 5, "ants": 3, "iterations": 2, "simulations": 5})
        assert analysis.status_code == 200
        analysis_id = analysis.json()["analysis_id"]
        status = client.get(f"/analyses/{analysis_id}").json()
        assert status["status"] == "completed"
        result = client.get(f"/analyses/{analysis_id}/result")
        assert result.status_code == 200
        assert len(result.json()["result"]["top_k"]) == 2
