import re
from math import sqrt

from app.storage import db


def chunk_text(text: str, size: int = 400, overlap: int = 60) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []
    chunks: list[str] = []
    i = 0
    while i < len(normalized):
        end = min(len(normalized), i + size)
        chunks.append(normalized[i:end])
        if end >= len(normalized):
            break
        i = max(0, end - overlap)
    return chunks


def embed(text: str, dim: int = 8) -> list[float]:
    seed = sum(ord(c) for c in text) % 997
    return [((seed + i * 31) % 101) / 100 for i in range(dim)]


def cos(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = sqrt(sum(x * x for x in a))
    nb = sqrt(sum(y * y for y in b))
    return 0.0 if na == 0 or nb == 0 else dot / (na * nb)


def search(query: str, top_k: int) -> list[tuple[str, str, float]]:
    qv = embed(query)
    scored: list[tuple[str, str, float]] = []
    for doc in db.documents.values():
        for idx, chunk in enumerate(doc.chunks):
            score = cos(qv, doc.vectors[idx])
            scored.append((doc.id, chunk, score))
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored[:top_k]
