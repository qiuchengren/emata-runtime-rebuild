import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from uuid import uuid4


@dataclass
class Document:
    id: str
    filename: str
    content: str
    chunks: list[str]
    vectors: list[list[float]]


class InMemoryDB:
    def __init__(self) -> None:
        self._lock = Lock()
        self._db_path = Path(__file__).resolve().parents[2] / "emata.db"
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self.documents: dict[str, Document] = {}
        self.sessions: dict[str, list[str]] = {}
        self.metrics: list[dict] = []
        self.runtime_config = {"top_k": 3}
        self._bootstrap()

    def _bootstrap(self) -> None:
        with self._conn:
            self._conn.execute(
                "CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, filename TEXT, content TEXT, chunks TEXT, vectors TEXT)"
            )
            self._conn.execute(
                "CREATE TABLE IF NOT EXISTS sessions (session_id TEXT, message TEXT)"
            )
            self._conn.execute(
                "CREATE TABLE IF NOT EXISTS metrics (recall REAL, confidence REAL, latency_ms REAL)"
            )
            self._conn.execute(
                "CREATE TABLE IF NOT EXISTS runtime_config (key TEXT PRIMARY KEY, value TEXT)"
            )
            self._conn.execute(
                "INSERT OR IGNORE INTO runtime_config (key, value) VALUES ('top_k', '3')"
            )
        self._reload_from_db()

    def _reload_from_db(self) -> None:
        self.documents.clear()
        self.sessions.clear()
        self.metrics.clear()
        docs = self._conn.execute("SELECT * FROM documents").fetchall()
        for row in docs:
            self.documents[row["id"]] = Document(
                id=row["id"],
                filename=row["filename"],
                content=row["content"],
                chunks=json.loads(row["chunks"]),
                vectors=json.loads(row["vectors"]),
            )
        turns = self._conn.execute("SELECT session_id, message FROM sessions").fetchall()
        for row in turns:
            self.sessions.setdefault(row["session_id"], []).append(row["message"])
        metrics = self._conn.execute("SELECT recall, confidence, latency_ms FROM metrics").fetchall()
        for row in metrics:
            self.metrics.append(
                {"recall": float(row["recall"]), "confidence": float(row["confidence"]), "latency_ms": float(row["latency_ms"])}
            )
        top_k_row = self._conn.execute("SELECT value FROM runtime_config WHERE key='top_k'").fetchone()
        if top_k_row:
            self.runtime_config["top_k"] = int(top_k_row["value"])

    def create_doc(self, filename: str, content: str, chunks: list[str], vectors: list[list[float]]) -> str:
        doc_id = str(uuid4())
        with self._lock:
            self.documents[doc_id] = Document(doc_id, filename, content, chunks, vectors)
            with self._conn:
                self._conn.execute(
                    "INSERT INTO documents (id, filename, content, chunks, vectors) VALUES (?, ?, ?, ?, ?)",
                    (doc_id, filename, content, json.dumps(chunks), json.dumps(vectors)),
                )
        return doc_id

    def append_turn(self, session_id: str, message: str) -> None:
        with self._lock:
            self.sessions.setdefault(session_id, []).append(message)
            with self._conn:
                self._conn.execute(
                    "INSERT INTO sessions (session_id, message) VALUES (?, ?)",
                    (session_id, message),
                )

    def add_metric(self, recall: float, confidence: float, latency_ms: float) -> None:
        with self._lock:
            rec = {"recall": recall, "confidence": confidence, "latency_ms": latency_ms}
            self.metrics.append(rec)
            with self._conn:
                self._conn.execute(
                    "INSERT INTO metrics (recall, confidence, latency_ms) VALUES (?, ?, ?)",
                    (recall, confidence, latency_ms),
                )

    def set_top_k(self, value: int) -> None:
        with self._lock:
            self.runtime_config["top_k"] = value
            with self._conn:
                self._conn.execute(
                    "UPDATE runtime_config SET value=? WHERE key='top_k'",
                    (str(value),),
                )


db = InMemoryDB()
