import requests

BASE = 'http://localhost:8000'

SAMPLES = [
    ('runtime_basics.txt', 'Ask runtime handles sessions and turns with grounded retrieval.'),
    ('ingestion_queue.txt', 'Async ingestion uses queue workers and reports job status for observability.'),
    ('meta_eval.txt', 'Meta tuner adapts top_k using recent recall signals to balance latency and quality.'),
]


def main() -> None:
    for name, text in SAMPLES:
        r = requests.post(f'{BASE}/api/v1/knowledge/uploads', files={'file': (name, text.encode('utf-8'))}, timeout=30)
        r.raise_for_status()
        print(r.json())


if __name__ == '__main__':
    main()
