from fastapi.testclient import TestClient
from server.init_server import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200

    # Check that the response contains the expected fields
    data = response.json()
    assert data["status"] == "ok"
    assert "message" in data
    assert "version" in data
    assert "timestamp" in data
    assert data["message"] == "Auth service is running"
    assert data["version"] == "1.0.0"
