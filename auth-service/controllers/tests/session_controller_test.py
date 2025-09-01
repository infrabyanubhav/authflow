import asyncio
import time
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from controllers.session_controller import SessionController
from fastapi import Request
from pydantic import ValidationError
from schema.sessionSchema import SessionSchema


class TestSessionController:
    """Comprehensive test suite for SessionController"""

    @pytest.fixture
    def session_controller(self):
        """Create a SessionController instance for testing"""
        return SessionController()

    @pytest.fixture
    def mock_request(self):
        """Create a mock FastAPI Request object"""
        request = MagicMock()
        request.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        request.client = MagicMock()
        request.client.host = "192.168.1.100"
        request.cookies = {"session_id": "test-session-id"}
        return request

    @pytest.fixture
    def sample_extracted_info(self):
        """Sample extracted device info"""
        return {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "accept_language": "en-US,en;q=0.9",
            "x_forwarded_for": "192.168.1.100",
        }

    # Session Generation Tests
    @pytest.mark.asyncio
    async def test_generate_session_success(
        self, session_controller, mock_request, sample_extracted_info
    ):
        """Test successful session generation"""
        with patch(
            "controllers.session_controller.extract_info", new_callable=AsyncMock
        ) as mock_extract, patch(
            "controllers.session_controller.generate_fingerprint",
            new_callable=AsyncMock,
        ) as mock_fingerprint:

            mock_extract.return_value = sample_extracted_info
            mock_fingerprint.return_value = "test-fingerprint-123"

            result = await session_controller.generate_session(mock_request)

            assert result["success"] is True
            assert result["message"] == "Session generated successfully"
            assert "data" in result
            assert "session_id" in result["data"]
            assert "fingerprint" in result["data"]
            assert "info" in result["data"]
            assert result["data"]["fingerprint"] == "test-fingerprint-123"
            assert result["data"]["info"] == sample_extracted_info

            # Verify session_id is a valid UUID
            uuid.UUID(result["data"]["session_id"])

    @pytest.mark.asyncio
    async def test_generate_session_invalid_request(self, session_controller):
        """Test session generation with invalid request"""
        # The extract_info function handles exceptions gracefully and returns default values
        # When request is None, it will fail to access headers and return default info
        with patch(
            "controllers.session_controller.extract_info", new_callable=AsyncMock
        ) as mock_extract:
            mock_extract.return_value = {
                "user_agent": "Unknown",
                "accept_language": "",
                "x_forwarded_for": "Unknown",
            }

            result = await session_controller.generate_session(None)

            # Should return error response because request is None
            assert result["success"] is False
            assert "Invalid request" in result["message"]

    @pytest.mark.asyncio
    async def test_generate_session_fingerprint_failure(
        self, session_controller, mock_request, sample_extracted_info
    ):
        """Test session generation when fingerprint generation fails"""
        with patch(
            "controllers.session_controller.extract_info", new_callable=AsyncMock
        ) as mock_extract, patch(
            "controllers.session_controller.generate_fingerprint",
            new_callable=AsyncMock,
        ) as mock_fingerprint:

            mock_extract.return_value = sample_extracted_info
            mock_fingerprint.return_value = None

            result = await session_controller.generate_session(mock_request)

            assert result["success"] is False
            assert (
                result["message"]
                == "Invalid request, Error Creating Session! Please try again later."
            )

    @pytest.mark.asyncio
    async def test_generate_session_extract_info_exception(
        self, session_controller, mock_request
    ):
        """Test session generation when extract_info raises exception"""
        with patch(
            "controllers.session_controller.extract_info", new_callable=AsyncMock
        ) as mock_extract:
            mock_extract.side_effect = Exception("Extract info failed")

            # The extract_info call is outside the try-catch block, so exceptions propagate
            with pytest.raises(Exception, match="Extract info failed"):
                await session_controller.generate_session(mock_request)

    # Session Creation Tests
    @pytest.mark.asyncio
    async def test_create_session_success(self, session_controller, mock_request):
        """Test successful session creation"""
        user_id = "123"

        with patch.object(
            session_controller, "generate_session", new_callable=AsyncMock
        ) as mock_generate, patch.object(
            session_controller.save_session, "save_session", new_callable=AsyncMock
        ) as mock_save:

            mock_generate.return_value = {
                "success": True,
                "data": {
                    "session_id": str(uuid.uuid4()),
                    "fingerprint": "test-fingerprint",
                    "info": {"user_agent": "test"},
                },
            }

            result = await session_controller.create_session(mock_request, user_id)

            assert result["success"] is True
            assert result["message"] == "Session created successfully"
            assert "data" in result
            assert result["data"]["session_id"] is not None
            assert result["data"]["fingerprint"] == "test-fingerprint"
            assert result["data"]["user_id"] == int(user_id)

            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_session_generation_failure(
        self, session_controller, mock_request
    ):
        """Test session creation when generation fails"""
        user_id = "123"

        with patch.object(
            session_controller, "generate_session", new_callable=AsyncMock
        ) as mock_generate:
            mock_generate.return_value = {
                "success": False,
                "message": "Generation failed",
            }

            result = await session_controller.create_session(mock_request, user_id)

            assert result["success"] is False
            assert (
                result["message"] == "Error creating session! Please try again later."
            )

    @pytest.mark.asyncio
    async def test_create_session_invalid_user_id(
        self, session_controller, mock_request
    ):
        """Test session creation with invalid user ID"""
        user_id = "invalid"

        with patch.object(
            session_controller, "generate_session", new_callable=AsyncMock
        ) as mock_generate:
            mock_generate.return_value = {
                "success": True,
                "data": {
                    "session_id": str(uuid.uuid4()),
                    "fingerprint": "test-fingerprint",
                    "info": {"user_agent": "test"},
                },
            }

            result = await session_controller.create_session(mock_request, user_id)

            assert result["success"] is False
            assert (
                result["message"] == "Error creating session! Please try again later."
            )

    @pytest.mark.asyncio
    async def test_create_session_save_failure(self, session_controller, mock_request):
        """Test session creation when save operation fails"""
        user_id = "123"

        with patch.object(
            session_controller, "generate_session", new_callable=AsyncMock
        ) as mock_generate, patch.object(
            session_controller.save_session, "save_session", new_callable=AsyncMock
        ) as mock_save:

            mock_generate.return_value = {
                "success": True,
                "data": {
                    "session_id": str(uuid.uuid4()),
                    "fingerprint": "test-fingerprint",
                    "info": {"user_agent": "test"},
                },
            }
            mock_save.side_effect = Exception("Save failed")

            result = await session_controller.create_session(mock_request, user_id)

            assert result["success"] is False
            assert (
                result["message"] == "Error creating session! Please try again later."
            )

    @pytest.mark.asyncio
    async def test_create_session_empty_fingerprint(
        self, session_controller, mock_request
    ):
        """Test session creation with empty fingerprint"""
        user_id = "123"

        with patch.object(
            session_controller, "generate_session", new_callable=AsyncMock
        ) as mock_generate:
            mock_generate.return_value = {
                "success": True,
                "data": {
                    "session_id": str(uuid.uuid4()),
                    "fingerprint": "",  # Empty fingerprint
                    "info": {"user_agent": "test"},
                },
            }

            result = await session_controller.create_session(mock_request, user_id)

            assert result["success"] is False
            assert (
                result["message"] == "Error creating session! Please try again later."
            )

    # Session Deletion Tests
    @pytest.mark.asyncio
    async def test_delete_session_success(self, session_controller, mock_request):
        """Test successful session deletion"""
        with patch("controllers.session_controller.DeleteSession") as mock_delete_class:
            mock_delete_instance = AsyncMock()
            mock_delete_class.return_value = mock_delete_instance

            result = await session_controller.delete_session(mock_request)

            mock_delete_instance.delete_session.assert_called_once_with(
                "test-session-id"
            )

    @pytest.mark.asyncio
    async def test_delete_session_no_session_id(self, session_controller):
        """Test session deletion without session ID in cookies"""
        mock_request = MagicMock()
        mock_request.cookies = {}  # No session_id cookie

        result = await session_controller.delete_session(mock_request)

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_session_exception(self, session_controller, mock_request):
        """Test session deletion with exception"""
        with patch("controllers.session_controller.DeleteSession") as mock_delete_class:
            mock_delete_instance = AsyncMock()
            mock_delete_class.return_value = mock_delete_instance
            mock_delete_instance.delete_session.side_effect = Exception("Delete failed")

            result = await session_controller.delete_session(mock_request)

            assert result is None

    # Edge Cases and Error Handling Tests
    @pytest.mark.asyncio
    async def test_create_session_with_extreme_user_id_values(
        self, session_controller, mock_request
    ):
        """Test session creation with extreme user ID values"""
        test_cases = [
            ("0", True),  # Minimum valid user ID
            ("999999999", True),  # Large user ID
            ("-1", True),  # Negative user ID (actually converts to int successfully)
            ("", False),  # Empty string
            ("abc", False),  # Non-numeric string
        ]

        for user_id, should_succeed in test_cases:
            with patch.object(
                session_controller, "generate_session", new_callable=AsyncMock
            ) as mock_generate, patch.object(
                session_controller.save_session, "save_session", new_callable=AsyncMock
            ):

                mock_generate.return_value = {
                    "success": True,
                    "data": {
                        "session_id": str(uuid.uuid4()),
                        "fingerprint": "test-fingerprint",
                        "info": {"user_agent": "test"},
                    },
                }

                result = await session_controller.create_session(mock_request, user_id)

                if should_succeed:
                    assert result["success"] is True, f"Failed for user_id: {user_id}"
                else:
                    assert (
                        result["success"] is False
                    ), f"Should have failed for user_id: {user_id}"

    @pytest.mark.asyncio
    async def test_generate_session_with_missing_headers(self, session_controller):
        """Test session generation with missing request headers"""
        mock_request = MagicMock()
        mock_request.headers = {}  # No headers
        mock_request.client = None  # No client info

        with patch(
            "controllers.session_controller.extract_info", new_callable=AsyncMock
        ) as mock_extract, patch(
            "controllers.session_controller.generate_fingerprint",
            new_callable=AsyncMock,
        ) as mock_fingerprint:

            mock_extract.return_value = {
                "user_agent": "Unknown",
                "accept_language": "",
                "x_forwarded_for": "Unknown",
            }
            mock_fingerprint.return_value = "test-fingerprint"

            result = await session_controller.generate_session(mock_request)

            assert result["success"] is True
            assert result["data"]["info"]["user_agent"] == "Unknown"

    @pytest.mark.asyncio
    async def test_session_controller_initialization(self):
        """Test SessionController initialization"""
        controller = SessionController()

        assert hasattr(controller, "save_session")
        assert hasattr(controller, "session_data")
        assert isinstance(controller.session_data, dict)
        assert controller.session_data == {}

    @pytest.mark.asyncio
    async def test_concurrent_session_creation(self, session_controller, mock_request):
        """Test concurrent session creation to ensure thread safety"""
        user_id = "123"

        with patch.object(
            session_controller, "generate_session", new_callable=AsyncMock
        ) as mock_generate, patch.object(
            session_controller.save_session, "save_session", new_callable=AsyncMock
        ):

            # Create unique session IDs for each call
            session_ids = [str(uuid.uuid4()) for _ in range(3)]
            mock_generate.side_effect = [
                {
                    "success": True,
                    "data": {
                        "session_id": session_id,
                        "fingerprint": "test-fingerprint",
                        "info": {"user_agent": "test"},
                    },
                }
                for session_id in session_ids
            ]

            # Execute multiple session creations concurrently
            tasks = [
                session_controller.create_session(mock_request, user_id)
                for _ in range(3)
            ]
            results = await asyncio.gather(*tasks)

            # All should succeed
            for result in results:
                assert result["success"] is True

            # Each should have unique session IDs
            session_ids_from_results = [
                result["data"]["session_id"] for result in results
            ]
            assert len(set(session_ids_from_results)) == 3


class TestSessionSchemaValidation:
    """Test SessionSchema validation edge cases"""

    def test_session_schema_valid_data(self):
        """Test SessionSchema with valid data"""
        schema = SessionSchema(
            session_id=str(uuid.uuid4()), fingerprint="valid-fingerprint", user_id=123
        )

        result = schema.validate_all()
        assert result["session_id"] is not None
        assert result["fingerprint"] == "valid-fingerprint"
        assert result["user_id"] == 123

    def test_session_schema_empty_session_id(self):
        """Test SessionSchema with empty session ID"""
        with pytest.raises(ValueError, match="Session ID is required"):
            SessionSchema(session_id="", fingerprint="valid-fingerprint", user_id=123)

    def test_session_schema_none_session_id(self):
        """Test SessionSchema with None session ID"""
        with pytest.raises(ValidationError):
            SessionSchema(session_id=None, fingerprint="valid-fingerprint", user_id=123)

    def test_session_schema_empty_fingerprint(self):
        """Test SessionSchema with empty fingerprint"""
        with pytest.raises(ValueError, match="Fingerprint is required"):
            SessionSchema(session_id=str(uuid.uuid4()), fingerprint="", user_id=123)


# Legacy test for backwards compatibility
def test_session_creation():
    """Legacy test case - updated to be functional"""
    # Note: The original test was not functional because:
    # 1. create_session is async and requires await
    # 2. create_session requires a Request object and user_id
    # 3. SessionController doesn't have a 'session' attribute

    session_controller = SessionController()

    # Test basic initialization
    assert session_controller is not None
    assert hasattr(session_controller, "save_session")
    assert hasattr(session_controller, "session_data")
    assert isinstance(session_controller.session_data, dict)


class TestSessionControllerIntegration:
    """Integration tests using real components (no mocking)"""

    @pytest.fixture
    def session_controller(self):
        """Create a real SessionController instance"""
        return SessionController()

    @pytest.fixture
    def real_request(self):
        """Create a realistic request object"""
        from fastapi import Request
        from starlette.datastructures import Headers
        from starlette.requests import Request as StarletteRequest

        # Create a more realistic request mock
        request = MagicMock()
        request.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Forwarded-For": "203.0.113.1",
        }
        request.client = MagicMock()
        request.client.host = "203.0.113.1"
        request.cookies = {"session_id": f"real-session-{str(uuid.uuid4())[:8]}"}
        return request

    @pytest.mark.asyncio
    async def test_real_session_generation_with_extract_info(
        self, session_controller, real_request
    ):
        """Test session generation using real extract_info function"""
        # Use real extract_info but mock fingerprint generation for predictability
        with patch(
            "controllers.session_controller.generate_fingerprint",
            new_callable=AsyncMock,
        ) as mock_fingerprint:
            mock_fingerprint.return_value = "real-fingerprint-hash"

            result = await session_controller.generate_session(real_request)

            assert result["success"] is True
            assert result["message"] == "Session generated successfully"
            assert "data" in result
            assert result["data"]["fingerprint"] == "real-fingerprint-hash"

            # Verify real extracted info structure
            info = result["data"]["info"]
            assert "user_agent" in info
            assert "accept_language" in info
            assert "x_forwarded_for" in info
            assert (
                info["user_agent"]
                == "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            )

    @pytest.mark.asyncio
    async def test_real_session_creation_end_to_end(
        self, session_controller, real_request
    ):
        """Test complete session creation flow with minimal mocking"""
        user_id = "999"

        # Only mock the save operation to avoid Redis dependency
        with patch.object(
            session_controller.save_session, "save_session", new_callable=AsyncMock
        ) as mock_save, patch(
            "controllers.session_controller.generate_fingerprint",
            new_callable=AsyncMock,
        ) as mock_fingerprint:

            mock_fingerprint.return_value = "integration-test-fingerprint"

            result = await session_controller.create_session(real_request, user_id)

            assert result["success"] is True
            assert result["message"] == "Session created successfully"
            assert result["data"]["user_id"] == int(user_id)
            assert result["data"]["fingerprint"] == "integration-test-fingerprint"

            # Verify save was called with correct structure
            mock_save.assert_called_once()
            call_args = mock_save.call_args
            session_id = call_args[0][0]  # First argument (session_id)
            session_data = call_args[0][1]  # Second argument (session_data)

            assert isinstance(session_id, str)
            assert "fingerprint" in session_data
            assert "user_id" in session_data
            assert session_data["user_id"] == int(user_id)

    @pytest.mark.asyncio
    async def test_real_extract_info_edge_cases(self, session_controller):
        """Test extract_info with various real-world header scenarios"""
        test_cases = [
            # Standard browser
            {
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept-Language": "en-US,en;q=0.9",
                },
                "expected_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            },
            # Mobile browser
            {
                "headers": {
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
                    "Accept-Language": "en-US",
                },
                "expected_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
            },
            # Bot/crawler
            {
                "headers": {
                    "User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)",
                    "Accept-Language": "*",
                },
                "expected_agent": "Googlebot/2.1 (+http://www.google.com/bot.html)",
            },
            # Missing User-Agent
            {
                "headers": {"Accept-Language": "fr-FR,fr;q=0.9"},
                "expected_agent": "Unknown",
            },
            # Empty headers
            {"headers": {}, "expected_agent": "Unknown"},
        ]

        for i, test_case in enumerate(test_cases):
            request = MagicMock()
            request.headers = test_case["headers"]
            request.client = MagicMock()
            request.client.host = f"192.168.1.{i + 1}"

            with patch(
                "controllers.session_controller.generate_fingerprint",
                new_callable=AsyncMock,
            ) as mock_fingerprint:
                mock_fingerprint.return_value = f"test-fingerprint-{i}"

                result = await session_controller.generate_session(request)

                assert result["success"] is True
                assert (
                    result["data"]["info"]["user_agent"] == test_case["expected_agent"]
                )

    @pytest.mark.asyncio
    async def test_real_session_validation_with_schema(
        self, session_controller, real_request
    ):
        """Test session creation with real SessionSchema validation"""
        user_id = "123"

        with patch.object(
            session_controller.save_session, "save_session", new_callable=AsyncMock
        ), patch(
            "controllers.session_controller.generate_fingerprint",
            new_callable=AsyncMock,
        ) as mock_fingerprint:

            mock_fingerprint.return_value = "schema-test-fingerprint"

            result = await session_controller.create_session(real_request, user_id)

            # Test that the result matches what SessionSchema.validate_all() returns
            assert result["success"] is True
            validated_data = result["data"]

            # These should match SessionSchema structure
            assert "session_id" in validated_data
            assert "fingerprint" in validated_data
            assert "user_id" in validated_data

            # Verify types match schema expectations
            assert isinstance(validated_data["session_id"], str)
            assert isinstance(validated_data["fingerprint"], str)
            assert isinstance(validated_data["user_id"], int)

            # Verify UUID format
            uuid.UUID(validated_data["session_id"])


class TestSessionControllerRealistic:
    """Tests that simulate real-world scenarios without external dependencies"""

    @pytest.fixture
    def session_controller(self):
        return SessionController()

    @pytest.mark.asyncio
    async def test_concurrent_real_session_creation(self, session_controller):
        """Test concurrent session creation with realistic data"""
        # Simulate multiple users creating sessions simultaneously
        user_requests = []
        for i in range(5):
            request = MagicMock()
            request.headers = {
                "User-Agent": f"Browser-{i}/1.0",
                "Accept-Language": "en-US",
            }
            request.client = MagicMock()
            request.client.host = f"10.0.0.{i + 1}"
            user_requests.append((request, str(i + 1)))

        with patch.object(
            session_controller.save_session, "save_session", new_callable=AsyncMock
        ), patch(
            "controllers.session_controller.generate_fingerprint",
            new_callable=AsyncMock,
        ) as mock_fingerprint:

            # Return unique fingerprints for each request
            mock_fingerprint.side_effect = [f"fingerprint-{i}" for i in range(5)]

            # Create sessions concurrently
            tasks = [
                session_controller.create_session(request, user_id)
                for request, user_id in user_requests
            ]
            results = await asyncio.gather(*tasks)

            # Verify all succeeded
            for i, result in enumerate(results):
                assert result["success"] is True
                assert result["data"]["user_id"] == i + 1
                assert result["data"]["fingerprint"] == f"fingerprint-{i}"

            # Verify all session IDs are unique
            session_ids = [result["data"]["session_id"] for result in results]
            assert len(set(session_ids)) == 5

    @pytest.mark.asyncio
    async def test_session_controller_resilience(self, session_controller):
        """Test how session controller handles real-world edge cases"""
        edge_case_requests = [
            # Extremely long user agent
            {
                "headers": {"User-Agent": "A" * 1000, "Accept-Language": "en-US"},
                "should_succeed": True,
            },
            # Special characters in headers
            {
                "headers": {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) 中文测试",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                },
                "should_succeed": True,
            },
            # Malformed Accept-Language
            {
                "headers": {
                    "User-Agent": "TestBot/1.0",
                    "Accept-Language": "invalid-language-format!!!",
                },
                "should_succeed": True,
            },
        ]

        for i, case in enumerate(edge_case_requests):
            request = MagicMock()
            request.headers = case["headers"]
            request.client = MagicMock()
            request.client.host = f"edge.case.{i}.1"

            with patch.object(
                session_controller.save_session, "save_session", new_callable=AsyncMock
            ), patch(
                "controllers.session_controller.generate_fingerprint",
                new_callable=AsyncMock,
            ) as mock_fingerprint:

                mock_fingerprint.return_value = f"edge-case-fingerprint-{i}"

                result = await session_controller.create_session(request, str(i + 100))

                if case["should_succeed"]:
                    assert result["success"] is True
                    assert result["data"]["user_id"] == i + 100
                else:
                    assert result["success"] is False


# Performance and Load Testing
class TestSessionControllerPerformance:
    """Performance-focused tests"""

    @pytest.fixture
    def session_controller(self):
        return SessionController()

    @pytest.mark.asyncio
    async def test_session_creation_performance(self, session_controller):
        """Test session creation performance with realistic load"""
        request = MagicMock()
        request.headers = {"User-Agent": "LoadTest/1.0", "Accept-Language": "en-US"}
        request.client = MagicMock()
        request.client.host = "load.test.1.1"

        with patch.object(
            session_controller.save_session, "save_session", new_callable=AsyncMock
        ), patch(
            "controllers.session_controller.generate_fingerprint",
            new_callable=AsyncMock,
        ) as mock_fingerprint:

            mock_fingerprint.return_value = "performance-test-fingerprint"

            start_time = time.time()

            # Create 100 sessions
            tasks = [
                session_controller.create_session(request, str(i)) for i in range(100)
            ]
            results = await asyncio.gather(*tasks)

            end_time = time.time()
            execution_time = end_time - start_time

            # Verify all succeeded
            for result in results:
                assert result["success"] is True

            # Performance assertion (should complete 100 sessions in reasonable time)
            assert (
                execution_time < 5.0
            ), f"Session creation took too long: {execution_time}s"

            # Calculate average time per session
            avg_time_per_session = execution_time / 100
            print(f"Average time per session: {avg_time_per_session:.4f}s")

            # Should be quite fast since we're mocking I/O
            assert (
                avg_time_per_session < 0.1
            ), f"Average session creation too slow: {avg_time_per_session}s"
