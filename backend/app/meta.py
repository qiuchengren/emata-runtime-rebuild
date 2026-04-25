from app.storage import db


def adaptive_tune() -> dict:
    previous = db.runtime_config["top_k"]
    recent = db.metrics[-20:]
    if not recent:
        return {"previous_top_k": previous, "new_top_k": previous, "reason": "No metrics yet."}

    low_recall_ratio = sum(1 for m in recent if m["recall"] < 0.4) / len(recent)
    if low_recall_ratio > 0.4 and previous < 6:
        db.set_top_k(previous + 1)
        reason = "Raised top_k due to frequent low recall."
    elif low_recall_ratio < 0.1 and previous > 2:
        db.set_top_k(previous - 1)
        reason = "Lowered top_k to reduce latency with stable recall."
    else:
        reason = "No top_k change needed."

    return {"previous_top_k": previous, "new_top_k": db.runtime_config["top_k"], "reason": reason}
