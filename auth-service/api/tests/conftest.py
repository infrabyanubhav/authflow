"""
Test configuration and fixtures for API tests
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def test_app():
    """Create a minimal FastAPI app for testing without database dependencies"""
    app = FastAPI(title="Test AuthFlow API")

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    @app.get("/api/v1/auth/github")
    async def github_auth():
        return {"status": "ok"}

    @app.get("/api/v1/github_auth/github")
    async def github_auth_redirect():
        return {"url": "/api/v1/github_auth/callback"}

    @app.get("/welcome")
    async def welcome():
        return {"message": "Welcome to AuthFlow"}

    return app


@pytest.fixture
def client(test_app):
    """Create a test client for the test app"""
    return TestClient(test_app)
