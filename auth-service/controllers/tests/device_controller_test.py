import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from controllers.device_controller import DeviceController
from database.models.device_info import DeviceInfo
from pydantic import ValidationError
from schema.device_schema import DeviceSchema


class TestDeviceController:  # pylint: disable=too-many-public-methods
    """Comprehensive unit test suite for DeviceController"""

    @pytest.fixture
    def sample_device_data(self):
        """Sample valid device data for testing"""
        return {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "accept_language": "en-US,en;q=0.9",
            "ip": "192.168.1.100",
            "user_id": 123,
        }

    @pytest.fixture
    def device_controller(self, sample_device_data):
        """Create a DeviceController instance with valid data"""
        return DeviceController(
            user_agent=sample_device_data["user_agent"],
            accept_language=sample_device_data["accept_language"],
            ip=sample_device_data["ip"],
            user_id=sample_device_data["user_id"],
        )

    def test_device_controller_initialization(
        self, device_controller, sample_device_data
    ):
        """Test DeviceController initialization with valid data"""
        assert device_controller.user_agent == sample_device_data["user_agent"]
        assert (
            device_controller.accept_language == sample_device_data["accept_language"]
        )
        assert device_controller.ip == sample_device_data["ip"]
        assert device_controller.user_id == sample_device_data["user_id"]
        assert hasattr(device_controller, "validate_device")
        assert hasattr(device_controller, "create_device")

    def test_validate_device_success(self, device_controller, sample_device_data):
        """Test successful device validation"""
        with patch("controllers.device_controller.DeviceSchema") as mock_schema:
            mock_device = MagicMock()
            mock_device.user_agent = sample_device_data["user_agent"]
            mock_device.accept_language = sample_device_data["accept_language"]
            mock_device.ip = sample_device_data["ip"]
            mock_device.user_id = sample_device_data["user_id"]
            mock_schema.return_value = mock_device

            result = device_controller.validate_device()

            assert result["success"] is True
            assert result["message"] == "Device validated successfully"
            assert "data" in result
            assert result["data"] == mock_device

    def test_validate_device_schema_none(self, device_controller):
        """Test device validation when schema returns None"""
        with patch("controllers.device_controller.DeviceSchema") as mock_schema:
            mock_schema.return_value = None

            result = device_controller.validate_device()

            assert result["success"] is False
            assert result["message"] == "Device is None"

    def test_validate_device_exception(self, device_controller):
        """Test device validation with exception"""
        with patch("controllers.device_controller.DeviceSchema") as mock_schema:
            mock_schema.side_effect = Exception("Validation error")

            result = device_controller.validate_device()

            assert result["success"] is False
            assert (
                result["message"] == "Error validating device! Please try again later."
            )

    def test_create_device_success(self, device_controller, sample_device_data):
        """Test successful device creation"""
        with patch.object(device_controller, "validate_device") as mock_validate, patch(
            "controllers.device_controller.DeviceInfo"
        ) as mock_device_info_model, patch(
            "controllers.device_controller.create_device_info"
        ) as mock_create_device_info:

            # Mock validate_device response
            mock_validated_device = MagicMock()
            mock_validated_device.user_agent = sample_device_data["user_agent"]
            mock_validated_device.accept_language = sample_device_data[
                "accept_language"
            ]
            mock_validated_device.ip = sample_device_data["ip"]
            mock_validated_device.user_id = sample_device_data["user_id"]

            mock_validate.return_value = {
                "success": True,
                "data": mock_validated_device,
            }

            # Mock DeviceInfo model
            mock_device_info_instance = MagicMock()
            mock_device_info_model.return_value = mock_device_info_instance

            # Mock create_device_info response
            mock_created_device = MagicMock()
            mock_create_device_info.return_value = mock_created_device

            result = device_controller.create_device()

            assert result["success"] is True
            assert result["message"] == "Device created successfully"
            assert "data" in result
            assert result["data"]["user_agent"] == sample_device_data["user_agent"]
            assert (
                result["data"]["accept_language"]
                == sample_device_data["accept_language"]
            )
            assert result["data"]["ip"] == sample_device_data["ip"]
            assert hasattr(device_controller, "device_data")

    def test_create_device_validation_failure(self, device_controller):
        """Test device creation when validation fails"""
        with patch.object(device_controller, "validate_device") as mock_validate:
            mock_validate.return_value = {
                "success": False,
                "message": "Validation failed",
            }

            result = device_controller.create_device()

            # When validation fails, create_device should return early with the validation error
            assert result["success"] is False
            assert result["message"] == "Validation failed"

    def test_create_device_db_failure(self, device_controller, sample_device_data):
        """Test device creation when database operation fails"""
        with patch.object(device_controller, "validate_device") as mock_validate, patch(
            "controllers.device_controller.DeviceInfo"
        ) as mock_device_info_model, patch(
            "controllers.device_controller.create_device_info"
        ) as mock_create_device_info:

            # Mock validate_device response
            mock_validated_device = MagicMock()
            mock_validated_device.user_agent = sample_device_data["user_agent"]
            mock_validated_device.accept_language = sample_device_data[
                "accept_language"
            ]
            mock_validated_device.ip = sample_device_data["ip"]
            mock_validated_device.user_id = sample_device_data["user_id"]

            mock_validate.return_value = {
                "success": True,
                "data": mock_validated_device,
            }

            # Mock DeviceInfo model
            mock_device_info_instance = MagicMock()
            mock_device_info_model.return_value = mock_device_info_instance

            # Mock create_device_info to return None (failure)
            mock_create_device_info.return_value = None

            result = device_controller.create_device()

            assert result["success"] is False
            assert result["message"] == "Error adding device"

    def test_create_device_exception(self, device_controller):
        """Test device creation with exception"""
        with patch.object(device_controller, "validate_device") as mock_validate:
            mock_validate.side_effect = Exception("Creation error")

            result = device_controller.create_device()

            assert result["success"] is False
            assert result["message"] == "Error creating device! Please try again later."


class TestDeviceControllerEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_device_controller_with_special_characters(self):
        """Test DeviceController with special characters in user agent"""
        special_user_agent = "Mozilla/5.0 (X11; Linux x86_64) 中文测试/1.0"
        device_controller = DeviceController(
            user_agent=special_user_agent,
            accept_language="zh-CN,zh;q=0.9,en;q=0.8",
            ip="192.168.1.1",
            user_id=456,
        )

        assert device_controller.user_agent == special_user_agent
        assert device_controller.accept_language == "zh-CN,zh;q=0.9,en;q=0.8"
        assert device_controller.ip == "192.168.1.1"
        assert device_controller.user_id == 456

    def test_device_controller_with_extreme_user_id_values(self):
        """Test DeviceController with extreme user ID values"""
        test_cases = [
            {"user_id": 1, "should_succeed": True},
            {"user_id": 999999, "should_succeed": True},
            {"user_id": -1, "should_succeed": True},  # Negative IDs might be valid
            {"user_id": 0, "should_succeed": True},
        ]

        for case in test_cases:
            device_controller = DeviceController(
                user_agent="TestAgent/1.0",
                accept_language="en-US",
                ip="10.0.0.1",
                user_id=case["user_id"],
            )

            assert device_controller.user_id == case["user_id"]

            if case["should_succeed"]:
                # Test that validation can handle this ID
                with patch("controllers.device_controller.DeviceSchema") as mock_schema:
                    mock_device = MagicMock()
                    mock_schema.return_value = mock_device

                    result = device_controller.validate_device()
                    assert result["success"] is True

    def test_device_controller_with_long_user_agent(self):
        """Test DeviceController with extremely long user agent"""
        long_user_agent = "A" * 1000
        device_controller = DeviceController(
            user_agent=long_user_agent,
            accept_language="en-US",
            ip="127.0.0.1",
            user_id=123,
        )

        assert len(device_controller.user_agent) == 1000
        assert device_controller.user_agent == long_user_agent

    def test_device_controller_with_malformed_ip(self):
        """Test DeviceController with malformed IP addresses"""
        malformed_ips = [
            "192.168.1",  # Incomplete
            "192.168.1.256",  # Invalid octet
            "invalid.ip.address",  # Non-numeric
            "",  # Empty
            "192.168.1.100.200",  # Too many octets
        ]

        for malformed_ip in malformed_ips:
            device_controller = DeviceController(
                user_agent="TestAgent/1.0",
                accept_language="en-US",
                ip=malformed_ip,
                user_id=123,
            )

            # The controller should accept any IP string - validation happens in DeviceSchema
            assert device_controller.ip == malformed_ip

    def test_device_controller_with_empty_strings(self):
        """Test DeviceController with empty string values"""
        device_controller = DeviceController(
            user_agent="", accept_language="", ip="", user_id=123
        )

        assert device_controller.user_agent == ""
        assert device_controller.accept_language == ""
        assert device_controller.ip == ""
        assert device_controller.user_id == 123


class TestDeviceControllerIntegration:
    """Integration tests using real components"""

    @pytest.fixture
    def real_device_controller(self):
        """Create a DeviceController with realistic data"""
        return DeviceController(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            accept_language="en-US,en;q=0.9",
            ip="203.0.113.1",
            user_id=999,
        )

    def test_real_device_validation_success(self, real_device_controller):
        """Test device validation with real DeviceSchema"""
        result = real_device_controller.validate_device()

        assert result["success"] is True
        assert result["message"] == "Device validated successfully"
        assert "data" in result

        # Verify the validated device data
        device_data = result["data"]
        assert (
            device_data.user_agent
            == "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        assert device_data.accept_language == "en-US,en;q=0.9"
        assert device_data.ip == "203.0.113.1"
        assert device_data.user_id == 999

    def test_real_device_validation_invalid_ip(self):
        """Test device validation with invalid IP using real schema"""
        device_controller = DeviceController(
            user_agent="TestAgent/1.0",
            accept_language="en-US",
            ip="invalid.ip.address",
            user_id=123,
        )

        result = device_controller.validate_device()

        # Should fail due to invalid IP format
        assert result["success"] is False
        assert "Error validating device" in result["message"]

    def test_real_device_creation_flow(self, real_device_controller):
        """Test complete device creation flow with minimal mocking"""
        with patch(
            "controllers.device_controller.create_device_info"
        ) as mock_create_device_info:
            # Mock successful database operation
            mock_created_device = MagicMock()
            mock_create_device_info.return_value = mock_created_device

            result = real_device_controller.create_device()

            assert result["success"] is True
            assert result["message"] == "Device created successfully"
            assert "data" in result
            assert (
                result["data"]["user_agent"]
                == "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            )
            assert result["data"]["accept_language"] == "en-US,en;q=0.9"
            assert result["data"]["ip"] == "203.0.113.1"

            # Verify create_device_info was called with correct DeviceInfo object
            mock_create_device_info.assert_called_once()
            call_args = mock_create_device_info.call_args
            device_info_arg = call_args[0][0]  # First argument (device_info)

            assert isinstance(device_info_arg, DeviceInfo)
            assert (
                device_info_arg.user_agent
                == "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            )
            assert device_info_arg.accept_language == "en-US,en;q=0.9"
            assert device_info_arg.ip == "203.0.113.1"
            assert device_info_arg.user_id == 999


class TestDeviceControllerRealistic:
    """Tests that simulate real-world scenarios"""

    def test_concurrent_device_creation(self):
        """Test concurrent device creation"""
        import asyncio

        async def create_device_async(device_data):
            controller = DeviceController(**device_data)
            with patch(
                "controllers.device_controller.create_device_info"
            ) as mock_create:
                mock_create.return_value = MagicMock()
                return controller.create_device()

        device_configs = [
            {
                "user_agent": f"Browser-{i}/1.0",
                "accept_language": "en-US",
                "ip": f"192.168.1.{i}",
                "user_id": i + 100,
            }
            for i in range(5)
        ]

        async def run_concurrent():
            tasks = [create_device_async(config) for config in device_configs]
            results = await asyncio.gather(*tasks)
            return results

        results = asyncio.run(run_concurrent())

        # Verify all succeeded
        for result in results:
            assert result["success"] is True
            assert result["message"] == "Device created successfully"

    def test_device_controller_resilience(self):
        """Test how DeviceController handles real-world edge cases"""
        edge_cases = [
            # Extremely long user agent
            {
                "user_agent": "A" * 500,
                "accept_language": "en-US",
                "ip": "127.0.0.1",
                "user_id": 123,
                "should_validate": True,
            },
            # Special characters in user agent
            {
                "user_agent": "Mozilla/5.0 (X11; Linux x86_64) 中文测试/1.0",
                "accept_language": "zh-CN,zh;q=0.9,en;q=0.8",
                "ip": "192.168.1.1",
                "user_id": 456,
                "should_validate": True,
            },
            # Malformed accept-language
            {
                "user_agent": "TestBot/1.0",
                "accept_language": "invalid-language-format!!!",
                "ip": "10.0.0.1",
                "user_id": 789,
                "should_validate": True,
            },
            # IPv6-like format (should fail validation)
            {
                "user_agent": "TestAgent/1.0",
                "accept_language": "en-US",
                "ip": "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
                "user_id": 101,
                "should_validate": False,
            },
        ]

        for case in edge_cases:
            device_controller = DeviceController(
                **{k: v for k, v in case.items() if k != "should_validate"}
            )

            result = device_controller.validate_device()

            if case["should_validate"]:
                assert (
                    result["success"] is True
                ), f"Failed for case: {case['user_agent'][:50]}..."
            else:
                assert (
                    result["success"] is False
                ), f"Should have failed for case: {case['ip']}"

    def test_device_controller_with_realistic_browser_data(self):
        """Test with realistic browser user agents"""
        realistic_browsers = [
            {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "accept_language": "en-US,en;q=0.9",
                "ip": "192.168.1.100",
                "user_id": 123,
            },
            {
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
                "accept_language": "en-US,en;q=0.9",
                "ip": "192.168.1.101",
                "user_id": 456,
            },
            {
                "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
                "accept_language": "en-US,en;q=0.9",
                "ip": "192.168.1.102",
                "user_id": 789,
            },
        ]

        for browser_data in realistic_browsers:
            device_controller = DeviceController(**browser_data)

            result = device_controller.validate_device()

            assert result["success"] is True
            assert result["data"].user_agent == browser_data["user_agent"]
            assert result["data"].accept_language == browser_data["accept_language"]
            assert result["data"].ip == browser_data["ip"]
            assert result["data"].user_id == browser_data["user_id"]


class TestDeviceSchemaValidation:
    """Test DeviceSchema validation independently"""

    def test_device_schema_valid_data(self):
        """Test DeviceSchema with valid data"""
        device = DeviceSchema(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            accept_language="en-US,en;q=0.9",
            ip="192.168.1.100",
            user_id=123,
        )

        assert device.user_agent == "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        assert device.accept_language == "en-US,en;q=0.9"
        assert device.ip == "192.168.1.100"
        assert device.user_id == 123

        # Test validate_all method
        validated = device.validate_all()
        assert validated == device

    def test_device_schema_invalid_ip_formats(self):
        """Test DeviceSchema with various invalid IP formats"""
        invalid_ips = [
            "192.168.1",  # Incomplete - only 3 octets
            "192.168.1.256",  # Invalid octet - 256 > 255
            "192.168.1.100.200",  # Too many octets - 5 instead of 4
            "invalid.ip.address",  # Non-numeric
            "",  # Empty string
        ]

        for invalid_ip in invalid_ips:
            with pytest.raises(ValidationError):
                DeviceSchema(
                    user_agent="TestAgent/1.0",
                    accept_language="en-US",
                    ip=invalid_ip,
                    user_id=123,
                )

    def test_device_schema_valid_ip_with_leading_zero(self):
        """Test that IP with leading zeros is actually valid"""
        # This should NOT raise an exception
        device = DeviceSchema(
            user_agent="TestAgent/1.0",
            accept_language="en-US",
            ip="192.168.1.01",  # Leading zero is fine, converts to 1
            user_id=123,
        )

        assert device.ip == "192.168.1.01"

    def test_device_schema_none_user_id(self):
        """Test DeviceSchema with None user_id"""
        with pytest.raises(ValidationError):
            DeviceSchema(
                user_agent="TestAgent/1.0",
                accept_language="en-US",
                ip="192.168.1.100",
                user_id=None,
            )

    def test_device_schema_empty_strings(self):
        """Test DeviceSchema with empty strings"""
        # Empty strings should be accepted for user_agent and accept_language
        device = DeviceSchema(
            user_agent="", accept_language="", ip="192.168.1.100", user_id=123
        )

        assert device.user_agent == ""
        assert device.accept_language == ""
        assert device.ip == "192.168.1.100"
        assert device.user_id == 123

    def test_device_schema_extreme_values(self):
        """Test DeviceSchema with extreme but valid values"""
        # Very long user agent
        long_user_agent = "A" * 2000
        device = DeviceSchema(
            user_agent=long_user_agent,
            accept_language="en-US",
            ip="127.0.0.1",
            user_id=999999,
        )

        assert len(device.user_agent) == 2000
        assert device.user_id == 999999

        # Negative user_id (should be accepted)
        device_neg = DeviceSchema(
            user_agent="TestAgent/1.0",
            accept_language="en-US",
            ip="127.0.0.1",
            user_id=-1,
        )

        assert device_neg.user_id == -1


class TestDeviceControllerPerformance:
    """Performance-focused tests"""

    @pytest.fixture
    def device_controller(self):
        return DeviceController(
            user_agent="LoadTest/1.0",
            accept_language="en-US",
            ip="127.0.0.1",
            user_id=123,
        )

    def test_device_creation_performance(self, device_controller):
        """Test device creation performance with multiple operations"""
        import time

        with patch(
            "controllers.device_controller.create_device_info"
        ) as mock_create_device_info:
            mock_create_device_info.return_value = MagicMock()

            start_time = time.time()

            # Create 100 devices
            results = []
            for i in range(100):
                result = device_controller.create_device()
                results.append(result)

            end_time = time.time()
            execution_time = end_time - start_time

            # Verify all succeeded
            for result in results:
                assert result["success"] is True

            # Performance assertion
            assert (
                execution_time < 1.0
            ), f"Device creation took too long: {execution_time}s"

            # Should be very fast since we're mocking I/O
            avg_time_per_device = execution_time / 100
            assert (
                avg_time_per_device < 0.01
            ), f"Average device creation too slow: {avg_time_per_device}s"

    def test_concurrent_device_validation(self):
        """Test concurrent device validation performance"""
        import asyncio

        async def validate_device_async():
            controller = DeviceController(
                user_agent="ConcurrentTest/1.0",
                accept_language="en-US",
                ip="127.0.0.1",
                user_id=123,
            )
            return controller.validate_device()

        async def run_concurrent_validation():
            tasks = [validate_device_async() for _ in range(50)]
            results = await asyncio.gather(*tasks)
            return results

        import time

        start_time = time.time()

        results = asyncio.run(run_concurrent_validation())

        end_time = time.time()
        execution_time = end_time - start_time

        # Verify all succeeded
        for result in results:
            assert result["success"] is True

        # Should complete 50 validations quickly
        assert (
            execution_time < 0.5
        ), f"Concurrent validation took too long: {execution_time}s"
