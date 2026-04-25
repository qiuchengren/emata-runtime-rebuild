from pathlib import Path
import json
import time

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_benchmark_endpoint_when_file_exists() -> None:
    docs_dir = Path(__file__).resolve().parents[1] / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    report_path = docs_dir / "BENCHMARK_REPORT.json"
    payload = {"baseline": {"avg_latency_ms": 10}, "after": {"avg_latency_ms": 9}, "tune": {"new_top_k": 4}}
    report_path.write_text(json.dumps(payload), encoding="utf-8")

    resp = client.get("/api/v1/eval/benchmark")
    assert resp.status_code == 200
    assert resp.json()["tune"]["new_top_k"] == 4


def test_ask_latency_threshold_soft_guard() -> None:
    client.post("/api/v1/knowledge/uploads", files={"file": ("perf.txt", b"retrieval and ranking data")})
    start = time.perf_counter()
    resp = client.post("/api/v1/ask", json={"message": "Explain retrieval", "use_knowledge": True})
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert resp.status_code == 200
    assert elapsed_ms < 800
