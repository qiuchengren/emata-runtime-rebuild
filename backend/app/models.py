from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    message: str
    session_id: str | None = None
    use_knowledge: bool = True


class Source(BaseModel):
    doc_id: str
    chunk: str
    score: float


class AskResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[Source] = Field(default_factory=list)
    confidence: float = 0.0
    eval_summary: dict = Field(default_factory=dict)


class KnowledgeUploadResponse(BaseModel):
    doc_id: str
    chunks: int
    status: str


class IngestionJobResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    doc_id: str | None = None
    error: str | None = None


class EvalReport(BaseModel):
    sample_size: int
    avg_recall: float
    avg_confidence: float
    avg_latency_ms: float


class MetaTuneResponse(BaseModel):
    previous_top_k: int
    new_top_k: int
    reason: str
