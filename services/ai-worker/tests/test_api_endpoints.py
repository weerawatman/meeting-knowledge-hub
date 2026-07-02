import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from api.app import app


def test_root_status() -> None:
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Meeting Knowledge Hub"}


def test_ingest_endpoint_queues_existing_file() -> None:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(b"RIFF")
        tmp_path = f.name
    with TestClient(app) as client:
        response = client.post(
            "/meetings/ingest",
            json={"source_path": tmp_path, "metadata": {"title": "Daily sync"}},
        )
    assert response.status_code == 200
    assert response.json()["status"] == "queued"


def test_ingest_endpoint_rejects_missing_file() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/meetings/ingest",
            json={"source_path": "/nonexistent/path/meeting.wav"},
        )
    assert response.status_code == 400


def test_get_meeting_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/meetings/meeting-1")
    assert response.status_code == 200
    assert response.json()["meeting_id"] == "meeting-1"


def test_search_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/search", params={"q": "meeting"}, headers={"X-API-Key": "viewer-token"}
        )
    assert response.status_code == 200
    assert response.json()["query"] == "meeting"


def test_search_requires_api_key() -> None:
    with TestClient(app) as client:
        response = client.get("/search", params={"q": "meeting"})
    assert response.status_code == 401
