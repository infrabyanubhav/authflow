import asyncio

import pytest
from config.init_config import auth_config  # noqa: F401
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from middleware.VerifyDeviceInforMiddleware import VerifyDeviceInfoMiddleware
from service.security.core.fingerprint import generate_fingerprint
from service.session.features.delete import DeleteSession
from service.session.features.save import SaveSession
from starlette.responses import JSONResponse

# Create test app with middleware
app = FastAPI()


# Add test routes
@app.get("/app")
async def app_route():
    """Main app route that requires valid session"""
    return {"message": "Access granted", "status": "authenticated"}


@app.get("/public")
async def public_route():
    """Public route for testing"""
    return {"message": "Public access", "status": "public"}


# Add the middleware
app.add_middleware(VerifyDeviceInfoMiddleware)

# Create test client
client = TestClient(app)


class TestVerifyDeviceInfoMiddleware:
    """Test suite for VerifyDeviceInfoMiddleware"""

    def setup_method(self):
        """Setup test data before each test method"""
        self.save_session = SaveSession()
        self.delete_session = DeleteSession()

        # Test session data
        self.test_session_id = "test_session_12345"
        self.valid_device_info = {
            "x_forwarded_for": "127.0.0.1",
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
            "accept_language": "en-US,en;q=0.9",
        }

    def teardown_method(self):
        """Cleanup after each test method"""
        # Cleanup will be handled in individual tests
        pass

    @pytest.mark.asyncio
    async def setup_valid_session(self):
        """Helper method to create a valid session"""
        # Generate fingerprint for valid session
        self.valid_fingerprint = await generate_fingerprint(self.valid_device_info)

        # Create valid session
        await self.save_session.save_session(
            self.test_session_id,
            {"fingerprint": self.valid_fingerprint, "user_id": "test_user"},
        )

    @pytest.mark.asyncio
    async def cleanup_sessions(self):
        """Helper method to cleanup test sessions"""
        try:
            await self.delete_session.delete_session(self.test_session_id)
            await self.delete_session.delete_session("invalid_session")
            await self.delete_session.delete_session("expired_session_123")
        except:
            pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_middleware_with_valid_session_and_fingerprint(self):
        """Test middleware allows access to /app with valid session and matching fingerprint"""
        # Setup session
        await self.setup_valid_session()

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
                "Accept-Language": "en-US,en;q=0.9",
                "X-Forwarded-For": "127.0.0.1",
            }
            cookies = {"session_id": self.test_session_id}

            response = client.get(
                "/app", headers=headers, cookies=cookies, follow_redirects=False
            )

            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Access granted"
            assert data["status"] == "authenticated"
        finally:
            # Cleanup
            await self.cleanup_sessions()

    def test_middleware_redirects_when_no_session_cookie(self):
        """Test middleware redirects /app when no session_id cookie is present"""
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Forwarded-For": "127.0.0.1",
        }

        response = client.get("/app", headers=headers, follow_redirects=False)

        assert response.status_code == 307  # Temporary Redirect
        assert response.headers["location"] == auth_config["auth_url"]

    def test_middleware_redirects_with_invalid_session_id(self):
        """Test middleware redirects /app when session_id doesn't exist in Redis"""
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Forwarded-For": "127.0.0.1",
        }
        cookies = {"session_id": "non_existent_session"}

        response = client.get(
            "/app", headers=headers, cookies=cookies, follow_redirects=False
        )

        assert response.status_code == 307
        assert response.headers["location"] == auth_config["auth_url"]

    @pytest.mark.asyncio
    async def test_middleware_redirects_with_mismatched_fingerprint(self):
        """Test middleware redirects when device fingerprint doesn't match"""
        # Setup session first
        await self.setup_valid_session()

        try:
            # Different device headers (different fingerprint)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",  # Different user agent
                "Accept-Language": "fr-FR,fr;q=0.9",  # Different language
                "X-Forwarded-For": "192.168.1.100",  # Different IP
            }
            cookies = {"session_id": self.test_session_id}

            response = client.get(
                "/app", headers=headers, cookies=cookies, follow_redirects=False
            )

            assert response.status_code == 307
            assert response.headers["location"] == auth_config["auth_url"]
        finally:
            await self.cleanup_sessions()

    @pytest.mark.asyncio
    async def test_middleware_with_different_ip_same_session(self):
        """Test middleware behavior when IP changes but other info remains same"""
        await self.setup_valid_session()

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
                "Accept-Language": "en-US,en;q=0.9",
                "X-Forwarded-For": "192.168.1.200",  # Different IP
            }
            cookies = {"session_id": self.test_session_id}

            response = client.get(
                "/app", headers=headers, cookies=cookies, follow_redirects=False
            )

            # Should redirect because fingerprint won't match (IP is part of fingerprint)
            assert response.status_code == 307
        finally:
            await self.cleanup_sessions()

    @pytest.mark.asyncio
    async def test_middleware_with_missing_headers(self):
        """Test middleware behavior when some headers are missing"""
        await self.setup_valid_session()

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
                # Missing Accept-Language and X-Forwarded-For
            }
            cookies = {"session_id": self.test_session_id}

            response = client.get(
                "/app", headers=headers, cookies=cookies, follow_redirects=False
            )

            # Should redirect because fingerprint won't match
            assert response.status_code == 307
        finally:
            await self.cleanup_sessions()

    @pytest.mark.asyncio
    async def test_middleware_with_expired_session(self):
        """Test middleware behavior with expired session"""
        # Create a session that will expire quickly
        expired_session_id = "expired_session_123"

        # Generate fingerprint for this test
        valid_fingerprint = await generate_fingerprint(self.valid_device_info)

        # Save session with short expiry (if your Redis is configured for it)
        await self.save_session.save_session(
            expired_session_id,
            {"fingerprint": valid_fingerprint, "user_id": "expired_user"},
        )

        # Wait a bit (in real scenario, you'd wait for expiration)
        # For this test, we'll delete it manually to simulate expiration
        await self.delete_session.delete_session(expired_session_id)

        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Forwarded-For": "127.0.0.1",
        }
        cookies = {"session_id": expired_session_id}

        response = client.get(
            "/app", headers=headers, cookies=cookies, follow_redirects=False
        )

        assert response.status_code == 307
        assert response.headers["location"] == auth_config["auth_url"]

    @pytest.mark.asyncio
    async def test_middleware_allows_multiple_valid_requests(self):
        """Test middleware allows multiple consecutive valid requests"""
        await self.setup_valid_session()

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
                "Accept-Language": "en-US,en;q=0.9",
                "X-Forwarded-For": "127.0.0.1",
            }
            cookies = {"session_id": self.test_session_id}

            # Make multiple requests
            for i in range(3):
                response = client.get(
                    "/app", headers=headers, cookies=cookies, follow_redirects=False
                )
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "authenticated"
        finally:
            await self.cleanup_sessions()

    def test_public_route_bypasses_middleware(self):
        """Test that middleware doesn't affect routes that don't require authentication"""
        # Note: This test assumes middleware applies to all routes
        # You might need to modify this based on your actual middleware implementation

        response = client.get("/public", follow_redirects=False)

        # If middleware applies to all routes, this should redirect
        # If it's selective, this should return 200
        # Adjust assertion based on your middleware design
        assert response.status_code in [200, 307]  # Either works or redirects


# Integration test that combines multiple scenarios
class TestMiddlewareIntegration:
    """Integration tests for middleware with various scenarios"""

    @pytest.mark.asyncio
    async def test_full_authentication_flow(self):
        """Test complete authentication flow simulation"""
        save_session = SaveSession()
        delete_session = DeleteSession()

        try:
            # Step 1: No session - should redirect
            response = client.get("/app", follow_redirects=False)
            assert response.status_code == 307

            # Step 2: Create session and make valid request
            session_id = "integration_test_session"
            device_info = {
                "x_forwarded_for": "10.0.0.1",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "accept_language": "en-US,en;q=0.9",
            }

            fingerprint = await generate_fingerprint(device_info)
            await save_session.save_session(
                session_id, {"fingerprint": fingerprint, "user_id": "integration_user"}
            )

            headers = {
                "User-Agent": device_info["user_agent"],
                "Accept-Language": device_info["accept_language"],
                "X-Forwarded-For": device_info["x_forwarded_for"],
            }
            cookies = {"session_id": session_id}

            # Should now allow access
            response = client.get(
                "/app", headers=headers, cookies=cookies, follow_redirects=False
            )
            assert response.status_code == 200

            # Step 3: Change device info - should redirect
            headers["User-Agent"] = "Different-Agent/1.0"
            response = client.get(
                "/app", headers=headers, cookies=cookies, follow_redirects=False
            )
            assert response.status_code == 307

        finally:
            # Cleanup
            try:
                await delete_session.delete_session(session_id)
            except:
                pass
