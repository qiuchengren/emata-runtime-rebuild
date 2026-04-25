# EMATA Runtime Rebuild (Replica + Beyond)

This project rebuilds the core runtime capabilities of `EMATA-Runtime-main` and extends it with production-friendly modularity and innovation features.

## Source Project
- Source analyzed from: `C:/Users/17738/Desktop/other/EMATA-Runtime-main`
- Use case: learning-oriented replica and secondary innovation.
- License note: original repository currently does not include a license file; publish this rebuild with explicit attribution and your own licensing decision after confirming reuse boundaries.

## Step 1: Original stack analysis (summary)
- Backend: FastAPI + Pydantic + SQLAlchemy style architecture.
- Frontend: Next.js + React app-router based console.
- Infra in source: Postgres, Redis, Temporal, Milvus, MinIO.
- Core capability: Ask runtime + knowledge ingestion + retrieval + tools/skills.

## Step 2: Stack alignment and beyond
| Area | Source | This Rebuild |
|---|---|---|
| Backend | FastAPI + Python | FastAPI (latest stable pins) + Python 3.11 |
| Frontend | Next.js + React | Next.js 16 + React 19 |
| Storage | Multi infra with optional fallback | In-memory MVP runtime, container-ready extension points |
| Retrieval | Embedding + rerank flow | Hybrid retrieval baseline + adaptive top-k tuning |
| Evaluation | Runtime traces/observability oriented | Built-in auto eval report API + UI dashboard |

### How this version goes beyond
1. **Innovation A - Auto Evaluation Engine**  
   Collects recall/confidence/latency signals for each ask turn and serves aggregated metrics via `/api/v1/eval/report`.
2. **Innovation B - Meta Tuner**  
   Learns from recent low-recall ratio and automatically adjusts retrieval `top_k` via `/api/v1/meta/tune`.

## Step 3: Project structure
```text
2026/emata/
├── backend/
├── frontend/
├── scripts/
├── docs/
├── tests/
├── docker-compose.yml
├── README.md
└── .gitignore
```

## Step 4: Core features replicated
- Knowledge upload and chunk ingestion (`/api/v1/knowledge/uploads`)
- Ask runtime grounded response (`/api/v1/ask`)
- Source chunk return and confidence estimation
- Runtime metrics accumulation and reporting

## Step 5: Innovation details
- Auto eval endpoint: `/api/v1/eval/report`
- Meta tune endpoint: `/api/v1/meta/tune`
- Frontend dashboard page: `/eval`
- Async ingestion queue (Temporal-style skeleton):
  - enqueue: `POST /api/v1/knowledge/uploads/async`
  - status: `GET /api/v1/jobs/{job_id}`
- API error contract with structured codes:
  - Example: `EMPTY_FILE`, `JOB_NOT_FOUND`, `BENCHMARK_NOT_FOUND`

## Step 6: Run guide

### Local backend
```bash
cd backend
python -m venv .venv
# activate venv
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Local frontend
```bash
cd frontend
npm install
npm run dev
```

### Docker fullstack
```bash
cp .env.example .env
docker compose up --build
```

## Configuration
Use `.env.example` as baseline:
- `EMBEDDING_DIM`
- `AUTO_EVAL_ENABLED`
- `META_TUNER_ENABLED`

## Testing
```bash
cd backend
pytest ../tests/test_api.py ../tests/test_benchmark_endpoint.py -q
```

## Benchmark Compare
After starting backend:
```bash
python scripts/benchmark_compare.py
```
Outputs:
- `docs/BENCHMARK_REPORT.json`
- `docs/BENCHMARK_REPORT.md`

The frontend `/eval` page can load benchmark JSON via `GET /api/v1/eval/benchmark`.

## Utility Scripts
- Reset local SQLite state:
  - `python scripts/init_db.py`
- Seed demo knowledge data:
  - `python scripts/seed_demo.py`

## Step 7: Delivery verification
- Health endpoint responds: `GET /api/v1/health`
- Upload + ask + eval + tune chain works
- Checklist available in `CHECKLIST.md`
