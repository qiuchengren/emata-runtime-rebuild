import json
from statistics import mean
from time import perf_counter

import requests

BASE = "http://localhost:8000"


def run_round(label: str, questions: list[str]) -> dict:
    latencies = []
    confidences = []
    recalls = []
    for q in questions:
        t0 = perf_counter()
        r = requests.post(f"{BASE}/api/v1/ask", json={"message": q, "use_knowledge": True}, timeout=30)
        latencies.append((perf_counter() - t0) * 1000)
        r.raise_for_status()
        body = r.json()
        confidences.append(float(body.get("confidence", 0.0)))
        recalls.append(float(body.get("eval_summary", {}).get("recall", 0.0)))
    return {
        "label": label,
        "avg_latency_ms": round(mean(latencies), 2),
        "avg_confidence": round(mean(confidences), 3),
        "avg_recall": round(mean(recalls), 3),
    }


def main() -> None:
    questions = [
        "What is retrieval runtime?",
        "How does confidence work in EMATA?",
        "Explain ingestion and queue behavior.",
    ]
    baseline = run_round("before_tune", questions)
    tune = requests.post(f"{BASE}/api/v1/meta/tune", timeout=30).json()
    after = run_round("after_tune", questions)
    result = {"baseline": baseline, "after": after, "tune": tune}
    with open("docs/BENCHMARK_REPORT.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    with open("docs/BENCHMARK_REPORT.md", "w", encoding="utf-8") as f:
        f.write("# Benchmark Compare\n\n")
        f.write(f"- Baseline latency: {baseline['avg_latency_ms']} ms\n")
        f.write(f"- After-tune latency: {after['avg_latency_ms']} ms\n")
        f.write(f"- Baseline recall: {baseline['avg_recall']}\n")
        f.write(f"- After-tune recall: {after['avg_recall']}\n")
        f.write(f"- Tuning decision: {tune}\n")


if __name__ == "__main__":
    main()
