from fastapi.testclient import TestClient
from api.app import app


def test_root_status() -> None:
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Meeting Knowledge Hub"}
