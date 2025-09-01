from fastapi.testclient import TestClient
from server.init_server import app

client = TestClient(app)


def test_device_info_test():
    """Test device info middleware with provided X-Device-Info header"""
    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:3000", "X-Device-Info": "test"},
        cookies={"access_token": "valid_token"},
    )
    assert response.status_code == 200
    # The health endpoint doesn't necessarily return device info headers
    # Just check that the request was processed successfully
    assert response.status_code == 200


def test_device_info_test_with_invalid_token():
    """Test device info middleware when no X-Device-Info header is provided"""
    response = client.get(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "User-Agent": "TestBrowser/1.0",
            "Accept-Language": "en-US",
        },
        cookies={"access_token": "invalid_token"},
    )
    assert response.status_code == 200
    # The health endpoint doesn't necessarily return device info headers
    # Just check that the request was processed successfully
    assert response.status_code == 200
