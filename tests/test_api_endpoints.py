from fastapi.testclient import TestClient

from api.app import app


def test_root_status() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Meeting Knowledge Hub"}


def test_ingest_endpoint() -> None:
    client = TestClient(app)
    response = client.post("/meetings/ingest", json={"source_path": "meeting-1", "metadata": {"title": "Daily sync"}})
    assert response.status_code == 200
    assert response.json()["status"] == "ingested"


def test_get_meeting_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/meetings/meeting-1")
    assert response.status_code == 200
    assert response.json()["meeting_id"] == "meeting-1"


def test_search_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/search", params={"q": "meeting"}, headers={"X-API-Key": "viewer-token"})
    assert response.status_code == 200
    assert response.json()["query"] == "meeting"


def test_search_requires_api_key() -> None:
    client = TestClient(app)
    response = client.get("/search", params={"q": "meeting"})
    assert response.status_code == 401
