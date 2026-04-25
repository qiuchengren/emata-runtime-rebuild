from fastapi.testclient import TestClient
import time

from app.main import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

    missing_benchmark = client.get("/api/v1/eval/benchmark")
    assert missing_benchmark.status_code == 404
    assert missing_benchmark.json()["error"]["code"] == "BENCHMARK_NOT_FOUND"


def test_upload_ask_eval_meta() -> None:
    up = client.post("/api/v1/knowledge/uploads", files={"file": ("doc.txt", b"Search relates to ranking.")})
    assert up.status_code == 200

    ask = client.post("/api/v1/ask", json={"message": "What is search?", "use_knowledge": True})
    assert ask.status_code == 200
    assert "answer" in ask.json()

    rep = client.get("/api/v1/eval/report")
    assert rep.status_code == 200
    assert rep.json()["sample_size"] >= 1

    tune = client.post("/api/v1/meta/tune")
    assert tune.status_code == 200
    assert "new_top_k" in tune.json()

    bad_upload = client.post("/api/v1/knowledge/uploads", files={"file": ("x.txt", b"")})
    assert bad_upload.status_code == 400
    assert bad_upload.json()["error"]["code"] == "EMPTY_FILE"


def test_async_ingestion_job() -> None:
    queued = client.post("/api/v1/knowledge/uploads/async", files={"file": ("job.txt", b"Async ingestion for runtime queue.")})
    assert queued.status_code == 200
    job_id = queued.json()["job_id"]

    status = {"status": "queued"}
    for _ in range(15):
        status_resp = client.get(f"/api/v1/jobs/{job_id}")
        assert status_resp.status_code == 200
        status = status_resp.json()
        if status["status"] in {"done", "failed"}:
            break
        time.sleep(0.05)

    assert status["status"] == "done"
    assert status["doc_id"] is not None
