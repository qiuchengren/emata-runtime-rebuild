import requests

BASE = "http://localhost:8000"


def main() -> None:
    requests.post(
        f"{BASE}/api/v1/knowledge/uploads",
        files={"file": ("sample.txt", b"Retrieval relates to ranking and answering.")},
        timeout=30,
    ).raise_for_status()

    requests.post(
        f"{BASE}/api/v1/ask",
        json={"message": "Explain retrieval", "use_knowledge": True},
        timeout=30,
    ).raise_for_status()

    report = requests.get(f"{BASE}/api/v1/eval/report", timeout=30).json()
    print(report)


if __name__ == "__main__":
    main()
