# API Contract (v1)

Base path: `/api/v1`

## Error Schema
All structured business errors return:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message"
  }
}
```

### Error Codes
- `EMPTY_FILE`: upload payload has no content.
- `JOB_NOT_FOUND`: async ingestion job id does not exist.
- `BENCHMARK_NOT_FOUND`: benchmark report file is missing.

## Endpoints

### Health
- `GET /health`
- Response:
```json
{"status": "ok"}
```

### Sync Knowledge Upload
- `POST /knowledge/uploads` (multipart file)
- Response:
```json
{"doc_id":"...","chunks":3,"status":"indexed"}
```

### Async Knowledge Upload
- `POST /knowledge/uploads/async` (multipart file)
- Response:
```json
{"job_id":"...","status":"queued"}
```

### Job Status
- `GET /jobs/{job_id}`

### Ask Runtime
- `POST /ask`
- Request:
```json
{"message":"What is EMATA?","session_id":null,"use_knowledge":true}
```
- Response includes `answer`, `sources`, `confidence`, `eval_summary`.

### Eval Summary
- `GET /eval/report`

### Benchmark Report
- `GET /eval/benchmark`

### Meta Tune
- `POST /meta/tune`
