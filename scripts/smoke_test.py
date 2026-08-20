"""End-to-end smoke test against a running docker-compose stack.

Ingests a small sample document via POST /ingest, asks a question that should
be answerable from it via POST /query, and checks the response for a
non-empty answer plus at least one matching source.

Usage:
    docker compose up --build -d
    python scripts/smoke_test.py

Configure the backend location with the BACKEND_URL env var
(default: http://localhost:8000).
"""

import os
import sys

import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

SAMPLE_FILENAME = "smoke_test_sample.txt"
SAMPLE_CONTENT = (
    b"Smoke Test Policy\n\n"
    b"The company observes 12 public holidays per year, including New Year's "
    b"Day and Independence Day. Employees who work on a public holiday "
    b"receive a compensatory day off within the following month."
)
QUESTION = "How many public holidays does the company observe per year?"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def main() -> None:
    print(f"Running smoke test against {BACKEND_URL}")

    # 1. Ingest a small sample document.
    try:
        ingest_response = requests.post(
            f"{BACKEND_URL}/ingest",
            files={"file": (SAMPLE_FILENAME, SAMPLE_CONTENT, "text/plain")},
            timeout=60,
        )
    except requests.RequestException as exc:
        fail(f"Could not reach {BACKEND_URL}/ingest ({exc})")

    if ingest_response.status_code != 200:
        fail(f"POST /ingest returned {ingest_response.status_code}: {ingest_response.text}")

    ingest_data = ingest_response.json()
    if ingest_data.get("chunks_added", 0) < 1:
        fail(f"Ingest reported 0 chunks added: {ingest_data}")

    print(f"  Ingested '{ingest_data['filename']}' ({ingest_data['chunks_added']} chunks).")

    try:
        # 2. Ask a question answerable from the ingested document.
        # Generous timeout: the local LLM runs on CPU and the first call
        # may also need to pull the model, both of which can be slow.
        query_response = requests.post(
            f"{BACKEND_URL}/query", json={"question": QUESTION}, timeout=300
        )

        if query_response.status_code != 200:
            fail(f"POST /query returned {query_response.status_code}: {query_response.text}")

        query_data = query_response.json()
        answer = query_data.get("answer", "")
        sources = query_data.get("sources", [])

        if not answer.strip():
            fail("Query response contained an empty answer.")

        matching_sources = [s for s in sources if s.get("filename") == SAMPLE_FILENAME]
        if not matching_sources:
            fail(f"No source citing '{SAMPLE_FILENAME}' in response sources: {sources}")

        print(f"  Answer: {answer}")
        print(f"  Sources: {[s['filename'] for s in sources]}")
    finally:
        # 3. Clean up the sample document regardless of outcome.
        try:
            requests.delete(f"{BACKEND_URL}/documents/{SAMPLE_FILENAME}", timeout=30)
        except requests.RequestException:
            pass

    print("PASS: ingested a document and got a grounded, cited answer.")


if __name__ == "__main__":
    main()
