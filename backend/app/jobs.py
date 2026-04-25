from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from app.rag import chunk_text, embed
from app.storage import db


@dataclass
class IngestionJob:
    job_id: str
    filename: str
    content: str


class JobQueue:
    def __init__(self) -> None:
        self.queue: asyncio.Queue[IngestionJob] = asyncio.Queue()
        self.jobs: dict[str, dict[str, Any]] = {}
        self._worker_task: asyncio.Task | None = None

    async def start(self) -> None:
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._worker(), name="ingestion-worker")

    async def stop(self) -> None:
        if self._worker_task is not None:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
            self._worker_task = None

    async def enqueue(self, filename: str, content: str) -> str:
        job_id = str(uuid4())
        self.jobs[job_id] = {"status": "queued", "doc_id": None, "error": None}
        job = IngestionJob(job_id=job_id, filename=filename, content=content)
        if self._worker_task is None:
            # Fallback for environments where startup hooks are not active.
            await self._process_job(job)
            return job_id
        await self.queue.put(job)
        return job_id

    async def _worker(self) -> None:
        while True:
            job = await self.queue.get()
            await self._process_job(job)
            self.queue.task_done()

    async def _process_job(self, job: IngestionJob) -> None:
        self.jobs[job.job_id]["status"] = "processing"
        try:
            chunks = chunk_text(job.content)
            vectors = [embed(c) for c in chunks]
            doc_id = db.create_doc(job.filename, job.content, chunks, vectors)
            self.jobs[job.job_id].update({"status": "done", "doc_id": doc_id})
        except Exception as exc:  # noqa: BLE001
            self.jobs[job.job_id].update({"status": "failed", "error": str(exc)})
        finally:
            pass


job_queue = JobQueue()
