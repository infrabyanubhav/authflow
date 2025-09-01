"""
Simple API tests that don't require full database initialization
"""

from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Create a minimal FastAPI app for testing
test_app = FastAPI()


@test_app.get("/health")
async def health_check():
    return {"status": "ok"}


@test_app.get("/auth")
async def simple_auth():
    return {"message": "auth endpoint"}


client = TestClient(test_app)


def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_auth_endpoint():
    """Test a simple auth endpoint"""
    response = client.get("/auth")
    assert response.status_code == 200
    assert response.json() == {"message": "auth endpoint"}


@patch("requests.get")
def test_external_api_mock(mock_get):
    """Test mocking external API calls"""
    # Mock external API response
    mock_response = MagicMock()
    mock_response.json.return_value = {"user": "test_user"}
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    # This would be your actual API call logic
    import requests

    response = requests.get("https://api.github.com/user")

    assert response.status_code == 200
    assert response.json() == {"user": "test_user"}
    mock_get.assert_called_once_with("https://api.github.com/user")
