from statistics import mean
from time import perf_counter


def answer_confidence(answer: str, evidence: str) -> float:
    a_tokens = set(answer.lower().split())
    e_tokens = set(evidence.lower().split())
    if not a_tokens:
        return 0.0
    overlap = len(a_tokens & e_tokens) / max(1, len(a_tokens))
    return max(0.1, min(0.99, overlap + 0.2))


def summarize_eval(records: list[dict]) -> dict:
    if not records:
        return {"sample_size": 0, "avg_recall": 0.0, "avg_confidence": 0.0, "avg_latency_ms": 0.0}
    return {
        "sample_size": len(records),
        "avg_recall": round(mean(x["recall"] for x in records), 3),
        "avg_confidence": round(mean(x["confidence"] for x in records), 3),
        "avg_latency_ms": round(mean(x["latency_ms"] for x in records), 2),
    }


def timed_call(fn):
    start = perf_counter()
    result = fn()
    latency_ms = (perf_counter() - start) * 1000
    return result, latency_ms
