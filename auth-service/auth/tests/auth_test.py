from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from auth.simple_auth import SimpleAuth
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.requests import Scope


class TestSimpleAuth:
    """Test class for SimpleAuth functionality"""

    @pytest.fixture
    def mock_request(self):
        """Fixture for mock request"""
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Host": "localhost:8000",
        }
        mock_request.client.host = "127.0.0.1"
        return mock_request

    @pytest.fixture
    def mock_auth_response_success(self):
        """Mock successful auth response from Supabase"""
        mock_user = MagicMock()
        mock_user.id = "test-user-123"
        mock_user.user_metadata = {"email": "test@test.com", "name": "Test User"}

        mock_data = MagicMock()
        mock_data.user = mock_user

        return {"success": True, "data": mock_data}

    @pytest.fixture
    def mock_auth_response_failure(self):
        """Mock failed auth response from Supabase"""
        return {"success": False, "message": "Invalid credentials"}

    @pytest.mark.asyncio
    @patch("auth.simple_auth.SimpleAuthController")
    @patch("auth.simple_auth.UserController")
    @patch("auth.simple_auth.SessionController")
    @patch("auth.simple_auth.DeviceController")
    async def test_sign_up_success(
        self,
        mock_device_controller,
        mock_session_controller,
        mock_user_controller,
        mock_auth_controller,
        mock_request,
        mock_auth_response_success,
    ):
        """Test successful user sign up"""
        # Setup mocks
        mock_auth_controller.return_value.sign_up.return_value = (
            mock_auth_response_success
        )

        # Mock UserController to return structured response
        mock_user_controller.return_value.create_user = AsyncMock(
            return_value={"success": True, "data": MagicMock(id=1)}
        )

        # Mock DeviceController to return structured response
        mock_device_instance = MagicMock()
        mock_device_instance.create_device.return_value = {
            "success": True,
            "data": {"device_id": "device-123"},
        }
        mock_device_controller.return_value = mock_device_instance

        # Mock SessionController to return structured response
        mock_session_controller.return_value.create_session = AsyncMock(
            return_value={
                "success": True,
                "data": {"session_id": "session-123", "token": "jwt-token"},
            }
        )

        # Test sign up
        simple_auth = SimpleAuth(request=mock_request)
        response = await simple_auth.sign_up(
            email="test@test.com", password="password123"
        )

        # Assertions - Updated to match actual response structure
        assert response is not None
        assert response["success"] is True
        assert response["message"] == "Sign in successful"
        assert response["data"] is not None
        # The sign_up_process returns a message about email verification
        assert "message" in response["data"]
        assert "Sign up successful" in response["data"]["message"]

        # Verify controller calls
        mock_auth_controller.return_value.sign_up.assert_called_once_with(
            "test@test.com", "password123"
        )

    @pytest.mark.asyncio
    @patch("auth.simple_auth.SimpleAuthController")
    async def test_sign_up_auth_failure(self, mock_auth_controller, mock_request):
        """Test sign up when auth controller returns None"""
        # Setup mock to return None (auth failure)
        mock_auth_controller.return_value.sign_up.return_value = None

        # Test sign up
        simple_auth = SimpleAuth(request=mock_request)
        response = await simple_auth.sign_up(
            email="test@test.com", password="wrongpassword"
        )

        # Assertions - now returns proper error response instead of None
        assert response is not None
        assert response["success"] is False
        assert "Failed to sign up" in response["message"]

    @pytest.mark.asyncio
    @patch("auth.simple_auth.SimpleAuthController")
    @patch("auth.simple_auth.UserController")
    @patch("auth.simple_auth.SessionController")
    @patch("auth.simple_auth.DeviceController")
    async def test_sign_in_success(
        self,
        mock_device_controller,
        mock_session_controller,
        mock_user_controller,
        mock_auth_controller,
        mock_request,
        mock_auth_response_success,
    ):
        """Test successful user sign in"""
        # Setup mocks
        mock_auth_controller.return_value.sign_in.return_value = (
            mock_auth_response_success
        )

        # Mock UserController to return structured response
        mock_user_controller.return_value.create_user = AsyncMock(
            return_value={"success": True, "data": MagicMock(id=1)}
        )

        # Mock DeviceController to return structured response
        mock_device_instance = MagicMock()
        mock_device_instance.create_device.return_value = {
            "success": True,
            "data": {"device_id": "device-123"},
        }
        mock_device_controller.return_value = mock_device_instance

        # Mock SessionController to return structured response
        mock_session_controller.return_value.create_session = AsyncMock(
            return_value={
                "success": True,
                "data": {"session_id": "session-123", "token": "jwt-token"},
            }
        )

        # Test sign in
        simple_auth = SimpleAuth(request=mock_request)
        response = await simple_auth.sign_in(
            email="test@test.com", password="password123"
        )

        # Assertions
        assert response is not None
        assert response["success"] is True
        assert response["message"] == "Sign in successful"
        assert response["data"] is not None
        assert "session" in response["data"]

        # Verify controller calls
        mock_auth_controller.return_value.sign_in.assert_called_once_with(
            "test@test.com", "password123"
        )

    @pytest.mark.asyncio
    @patch("auth.simple_auth.SimpleAuthController")
    async def test_sign_in_auth_failure(
        self, mock_auth_controller, mock_request, mock_auth_response_failure
    ):
        """Test sign in when auth controller returns failure"""
        # Setup mock to return failure response
        mock_auth_controller.return_value.sign_in.return_value = (
            mock_auth_response_failure
        )

        # Test sign in
        simple_auth = SimpleAuth(request=mock_request)
        response = await simple_auth.sign_in(
            email="test@test.com", password="wrongpassword"
        )

        # Assertions - now returns proper error response instead of None
        assert response is not None
        assert response["success"] is False
        assert "Failed to sign in" in response["message"]

    @pytest.mark.asyncio
    @patch("auth.simple_auth.SimpleAuthController")
    async def test_sign_up_exception_handling(self, mock_auth_controller, mock_request):
        """Test sign up exception handling"""
        # Setup mock to raise an exception
        mock_auth_controller.return_value.sign_up.side_effect = Exception(
            "Database connection error"
        )

        # Test sign up
        simple_auth = SimpleAuth(request=mock_request)
        response = await simple_auth.sign_up(
            email="test@test.com", password="password123"
        )

        # Assertions
        assert response is not None
        assert response["success"] is False
        assert "Failed to sign up" in response["message"]

    @pytest.mark.asyncio
    @patch("auth.simple_auth.SimpleAuthController")
    async def test_sign_in_exception_handling(self, mock_auth_controller, mock_request):
        """Test sign in exception handling"""
        # Setup mock to raise an exception
        mock_auth_controller.return_value.sign_in.side_effect = Exception(
            "Network error"
        )

        # Test sign in
        simple_auth = SimpleAuth(request=mock_request)
        response = await simple_auth.sign_in(
            email="test@test.com", password="password123"
        )

        # Assertions
        assert response is not None
        assert response["success"] is False
        assert "Failed to sign in" in response["message"]

    @pytest.mark.asyncio
    @patch("auth.simple_auth.SimpleAuthController")
    @patch("auth.simple_auth.UserController")
    async def test_user_creation_failure(
        self,
        mock_user_controller,
        mock_auth_controller,
        mock_request,
        mock_auth_response_success,
    ):
        """Test behavior when user creation fails"""
        # Setup mocks
        mock_auth_controller.return_value.sign_up.return_value = (
            mock_auth_response_success
        )
        mock_user_controller.return_value.create_user = AsyncMock(
            return_value={"success": False, "data": None}
        )

        # Test sign up
        simple_auth = SimpleAuth(request=mock_request)
        response = await simple_auth.sign_up(
            email="test@test.com", password="password123"
        )

        # Assertions - should return failure response due to user creation failure
        assert response is not None
        assert response["success"] is False
        # The actual error message comes from auth_process method which catches the exception
        assert "Failed to sign" in response["message"]

    @pytest.mark.asyncio
    @patch("auth.simple_auth.SimpleAuthController")
    @patch("auth.simple_auth.UserController")
    @patch("auth.simple_auth.SessionController")
    @patch("auth.simple_auth.DeviceController")
    async def test_session_creation_failure(
        self,
        mock_device_controller,
        mock_session_controller,
        mock_user_controller,
        mock_auth_controller,
        mock_request,
        mock_auth_response_success,
    ):
        """Test behavior when session creation fails"""
        # Setup mocks
        mock_auth_controller.return_value.sign_up.return_value = (
            mock_auth_response_success
        )
        # Mock UserController to return structured response
        mock_user_controller.return_value.create_user = AsyncMock(
            return_value={"success": True, "data": MagicMock(id=1)}
        )

        # Mock DeviceController to return failure
        mock_device_instance = MagicMock()
        mock_device_instance.create_device.return_value = {
            "success": False,
            "data": None,
        }
        mock_device_controller.return_value = mock_device_instance

        # Test sign up
        simple_auth = SimpleAuth(request=mock_request)
        response = await simple_auth.sign_up(
            email="test@test.com", password="password123"
        )

        # Assertions - should return failure response due to session creation failure
        assert response is not None
        assert response["success"] is False
        assert "Failed to sign" in response["message"]
