import json
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile

from app.errors import AppError
from app.eval import answer_confidence, summarize_eval, timed_call
from app.jobs import job_queue
from app.meta import adaptive_tune
from app.models import (
    AskRequest,
    AskResponse,
    EvalReport,
    IngestionJobResponse,
    JobStatusResponse,
    KnowledgeUploadResponse,
    MetaTuneResponse,
    Source,
)
from app.rag import chunk_text, embed, search
from app.storage import db

router = APIRouter(prefix="/api/v1")


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/knowledge/uploads", response_model=KnowledgeUploadResponse)
async def upload(file: UploadFile = File(...)) -> KnowledgeUploadResponse:
    raw = await file.read()
    if not raw:
        raise AppError("EMPTY_FILE", "Uploaded file is empty.", 400)
    content = raw.decode("utf-8", errors="ignore")
    chunks = chunk_text(content)
    vectors = [embed(c) for c in chunks]
    doc_id = db.create_doc(file.filename, content, chunks, vectors)
    return KnowledgeUploadResponse(doc_id=doc_id, chunks=len(chunks), status="indexed")


@router.post("/knowledge/uploads/async", response_model=IngestionJobResponse)
async def upload_async(file: UploadFile = File(...)) -> IngestionJobResponse:
    raw = await file.read()
    if not raw:
        raise AppError("EMPTY_FILE", "Uploaded file is empty.", 400)
    content = raw.decode("utf-8", errors="ignore")
    job_id = await job_queue.enqueue(file.filename, content)
    return IngestionJobResponse(job_id=job_id, status="queued")


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job(job_id: str) -> JobStatusResponse:
    state = job_queue.jobs.get(job_id)
    if state is None:
        raise AppError("JOB_NOT_FOUND", "Ingestion job was not found.", 404)
    return JobStatusResponse(job_id=job_id, status=state["status"], doc_id=state["doc_id"], error=state["error"])


@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest) -> AskResponse:
    session_id = payload.session_id or str(uuid4())
    top_k = db.runtime_config["top_k"]

    def _run():
        hits = search(payload.message, top_k=top_k) if payload.use_knowledge else []
        context = "\n".join(h[1] for h in hits)
        answer = (
            f"EMATA answer: {payload.message}\n\n"
            f"Grounded context:\n{context[:900] if context else 'No knowledge context used.'}"
        )
        return answer, hits, context

    (answer, hits, context), latency_ms = timed_call(_run)
    confidence = answer_confidence(answer, context)
    recall = 0.0 if not hits else min(1.0, len(hits) / max(1, top_k))
    db.add_metric(recall, confidence, latency_ms)
    db.append_turn(session_id, payload.message)

    return AskResponse(
        session_id=session_id,
        answer=answer,
        sources=[Source(doc_id=h[0], chunk=h[1], score=h[2]) for h in hits],
        confidence=confidence,
        eval_summary={"recall": round(recall, 3), "latency_ms": round(latency_ms, 2), "top_k": top_k},
    )


@router.get("/eval/report", response_model=EvalReport)
def report() -> EvalReport:
    return EvalReport(**summarize_eval(db.metrics))


@router.get("/eval/benchmark")
def benchmark_report() -> dict:
    path = Path(__file__).resolve().parents[2] / "docs" / "BENCHMARK_REPORT.json"
    if not path.exists():
        raise AppError("BENCHMARK_NOT_FOUND", "Run scripts/benchmark_compare.py first.", 404)
    return json.loads(path.read_text(encoding="utf-8"))


@router.post("/meta/tune", response_model=MetaTuneResponse)
def tune() -> MetaTuneResponse:
    return MetaTuneResponse(**adaptive_tune())
