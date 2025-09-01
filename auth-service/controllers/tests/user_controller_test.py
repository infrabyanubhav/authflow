import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from controllers.user_controller import UserController
from database.models.user import User
from pydantic import ValidationError
from schema.user_schema import UserSchema


class TestUserController:
    """Comprehensive unit test suite for UserController"""

    @pytest.fixture
    def user_controller(self):
        """Create a UserController instance"""
        return UserController()

    @pytest.fixture
    def sample_user_data(self):
        """Sample valid user data for testing"""
        return {
            "user_name": "John Doe",
            "user_email": "john.doe@example.com",
            "user_avatar": "https://example.com/avatar.jpg",
            "user_uuid": str(uuid.uuid4()),
        }

    def test_user_controller_initialization(self, user_controller):
        """Test UserController initialization"""
        assert user_controller is not None
        assert hasattr(user_controller, "validate_user")
        assert hasattr(user_controller, "create_user")
        assert hasattr(user_controller, "get_user")

    @pytest.mark.asyncio
    async def test_validate_user_success(self, user_controller, sample_user_data):
        """Test successful user validation"""
        with patch("controllers.user_controller.UserSchema") as mock_schema:
            mock_validated_data = MagicMock()
            mock_validated_data.user_name = sample_user_data["user_name"]
            mock_validated_data.user_email = sample_user_data["user_email"]
            mock_validated_data.validate_all.return_value = mock_validated_data

            mock_schema.return_value = mock_validated_data

            result = await user_controller.validate_user(
                sample_user_data["user_name"], sample_user_data["user_email"]
            )

            assert result["success"] is True
            assert result["message"] == "User validation successful"
            assert "data" in result
            assert result["data"] == mock_validated_data

    @pytest.mark.asyncio
    async def test_validate_user_validation_failure(self, user_controller):
        """Test user validation when schema validation fails"""
        with patch("controllers.user_controller.UserSchema") as mock_schema:
            mock_validated_data = MagicMock()
            mock_validated_data.validate_all.return_value = None

            mock_schema.return_value = mock_validated_data

            result = await user_controller.validate_user("John Doe", "john@example.com")

            assert result["success"] is False
            assert (
                result["message"] == "User validation failed! Please try again later."
            )

    @pytest.mark.asyncio
    async def test_validate_user_exception(self, user_controller):
        """Test user validation with exception"""
        with patch("controllers.user_controller.UserSchema") as mock_schema:
            mock_schema.side_effect = Exception("Validation error")

            result = await user_controller.validate_user("John Doe", "john@example.com")

            assert result["success"] is False
            assert result["message"] == "Error validating user! Please try again later."

    @pytest.mark.asyncio
    async def test_create_user_success_new_user(
        self, user_controller, sample_user_data
    ):
        """Test successful user creation for new user"""
        with patch.object(user_controller, "validate_user") as mock_validate, patch(
            "controllers.user_controller.get_user"
        ) as mock_get_user, patch(
            "controllers.user_controller.User"
        ) as mock_user_model, patch(
            "controllers.user_controller.create_user"
        ) as mock_create_user_db:

            # Mock validate_user response
            mock_validated_data = MagicMock()
            mock_validated_data.user_name = sample_user_data["user_name"]
            mock_validated_data.user_email = sample_user_data["user_email"]

            mock_validate.return_value = {"success": True, "data": mock_validated_data}

            # Mock get_user to return None (user doesn't exist)
            mock_get_user.return_value = None

            # Mock User model
            mock_user_instance = MagicMock()
            mock_user_model.return_value = mock_user_instance

            # Mock create_user database function
            mock_created_user = MagicMock()
            mock_create_user_db.return_value = mock_created_user

            result = await user_controller.create_user(
                sample_user_data["user_name"],
                sample_user_data["user_email"],
                sample_user_data["user_avatar"],
                sample_user_data["user_uuid"],
            )

            assert result["success"] is True
            assert result["message"] == "User created successfully"
            assert result["data"] == mock_created_user

    @pytest.mark.asyncio
    async def test_create_user_existing_user(self, user_controller, sample_user_data):
        """Test user creation when user already exists"""
        with patch.object(user_controller, "validate_user") as mock_validate, patch(
            "controllers.user_controller.get_user"
        ) as mock_get_user:

            # Mock validate_user response
            mock_validated_data = MagicMock()
            mock_validated_data.user_name = sample_user_data["user_name"]
            mock_validated_data.user_email = sample_user_data["user_email"]

            mock_validate.return_value = {"success": True, "data": mock_validated_data}

            # Mock get_user to return existing user
            existing_user_data = {
                "id": 1,
                "user_name": sample_user_data["user_name"],
                "user_email": sample_user_data["user_email"],
                "user_uuid": sample_user_data["user_uuid"],
            }
            mock_get_user.return_value = existing_user_data

            result = await user_controller.create_user(
                sample_user_data["user_name"], sample_user_data["user_email"]
            )

            assert result["success"] is True
            assert result["message"] == "User already exists"
            assert result["data"] == existing_user_data

    @pytest.mark.asyncio
    async def test_create_user_validation_failure(self, user_controller):
        """Test user creation when validation fails"""
        with patch.object(user_controller, "validate_user") as mock_validate:
            mock_validate.return_value = {
                "success": False,
                "message": "Validation failed",
            }

            result = await user_controller.create_user("John Doe", "john@example.com")

            assert result["success"] is False
            assert result["message"] == "Validation failed"

    @pytest.mark.asyncio
    async def test_create_user_exception(self, user_controller, sample_user_data):
        """Test user creation with exception"""
        with patch.object(user_controller, "validate_user") as mock_validate:
            mock_validate.side_effect = Exception("Creation error")

            result = await user_controller.create_user(
                sample_user_data["user_name"], sample_user_data["user_email"]
            )

            assert result["success"] is False
            assert result["message"] == "Error creating user! Please try again later."

    @pytest.mark.asyncio
    async def test_get_user_success(self, user_controller):
        """Test successful user retrieval"""
        user_id = "test@example.com"
        expected_user_data = {
            "id": 1,
            "user_name": "John Doe",
            "user_email": user_id,
            "user_uuid": str(uuid.uuid4()),
        }

        with patch("controllers.user_controller.get_user") as mock_get_user:
            mock_get_user.return_value = expected_user_data

            result = await user_controller.get_user(user_id)

            assert result["success"] is True
            assert result["message"] == "User retrieved successfully"
            assert result["data"] == expected_user_data
            mock_get_user.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, user_controller):
        """Test user retrieval when user doesn't exist"""
        user_id = "nonexistent@example.com"

        with patch("controllers.user_controller.get_user") as mock_get_user:
            mock_get_user.return_value = None

            result = await user_controller.get_user(user_id)

            assert result["success"] is False
            assert result["message"] == "User not found"

    @pytest.mark.asyncio
    async def test_get_user_exception(self, user_controller):
        """Test user retrieval with exception"""
        user_id = "test@example.com"

        with patch("controllers.user_controller.get_user") as mock_get_user:
            mock_get_user.side_effect = Exception("Database error")

            result = await user_controller.get_user(user_id)

            # Now correctly returns success=False on error
            assert result["success"] is False
            assert result["message"] == "Error getting user! Please try again later."


class TestUserControllerEdgeCases:
    """Test edge cases and boundary conditions"""

    @pytest.fixture
    def user_controller(self):
        return UserController()

    @pytest.mark.asyncio
    async def test_create_user_with_special_characters(self, user_controller):
        """Test user creation with special characters in name and email"""
        special_name = "José María O'Connor-Smith"
        special_email = "user+tag@example-domain.co.uk"

        with patch.object(user_controller, "validate_user") as mock_validate, patch(
            "controllers.user_controller.get_user"
        ) as mock_get_user, patch(
            "controllers.user_controller.User"
        ) as mock_user_model, patch(
            "controllers.user_controller.create_user"
        ) as mock_create_user_db:

            mock_validated_data = MagicMock()
            mock_validated_data.user_name = special_name
            mock_validated_data.user_email = special_email

            mock_validate.return_value = {"success": True, "data": mock_validated_data}
            mock_get_user.return_value = None
            mock_user_model.return_value = MagicMock()
            mock_create_user_db.return_value = MagicMock()

            result = await user_controller.create_user(special_name, special_email)

            assert result["success"] is True
            assert result["message"] == "User created successfully"

    @pytest.mark.asyncio
    async def test_create_user_with_extreme_values(self, user_controller):
        """Test user creation with extreme but valid values"""
        # Very long name
        long_name = "A" * 200
        # Very long email
        long_email = "a" * 180 + "@example.com"

        with patch.object(user_controller, "validate_user") as mock_validate, patch(
            "controllers.user_controller.get_user"
        ) as mock_get_user, patch(
            "controllers.user_controller.User"
        ) as mock_user_model, patch(
            "controllers.user_controller.create_user"
        ) as mock_create_user_db:

            mock_validated_data = MagicMock()
            mock_validated_data.user_name = long_name
            mock_validated_data.user_email = long_email

            mock_validate.return_value = {"success": True, "data": mock_validated_data}
            mock_get_user.return_value = None
            mock_user_model.return_value = MagicMock()
            mock_create_user_db.return_value = MagicMock()

            result = await user_controller.create_user(long_name, long_email)

            assert result["success"] is True
            assert result["message"] == "User created successfully"

    @pytest.mark.asyncio
    async def test_create_user_with_empty_optional_fields(self, user_controller):
        """Test user creation with empty optional fields"""
        with patch.object(user_controller, "validate_user") as mock_validate, patch(
            "controllers.user_controller.get_user"
        ) as mock_get_user, patch(
            "controllers.user_controller.User"
        ) as mock_user_model, patch(
            "controllers.user_controller.create_user"
        ) as mock_create_user_db:

            mock_validated_data = MagicMock()
            mock_validated_data.user_name = "John Doe"
            mock_validated_data.user_email = "john@example.com"

            mock_validate.return_value = {"success": True, "data": mock_validated_data}
            mock_get_user.return_value = None
            mock_user_model.return_value = MagicMock()
            mock_create_user_db.return_value = MagicMock()

            result = await user_controller.create_user(
                "John Doe", "john@example.com", None, None  # No avatar  # No UUID
            )

            assert result["success"] is True
            assert result["message"] == "User created successfully"

    @pytest.mark.asyncio
    async def test_validate_user_with_empty_strings(self, user_controller):
        """Test user validation with empty strings"""
        with patch("controllers.user_controller.UserSchema") as mock_schema:
            mock_validated_data = MagicMock()
            mock_validated_data.validate_all.return_value = mock_validated_data
            mock_schema.return_value = mock_validated_data

            result = await user_controller.validate_user("", "")

            assert result["success"] is True
            assert result["message"] == "User validation successful"


class TestUserControllerIntegration:
    """Integration tests using real components"""

    @pytest.fixture
    def user_controller(self):
        return UserController()

    @pytest.mark.asyncio
    async def test_real_user_validation_success(self, user_controller):
        """Test user validation with real UserSchema"""
        result = await user_controller.validate_user("John Doe", "john.doe@example.com")

        assert result["success"] is True
        assert result["message"] == "User validation successful"
        assert "data" in result

        # Verify the validated data
        user_data = result["data"]
        assert user_data.user_name == "John Doe"
        assert user_data.user_email == "john.doe@example.com"

    @pytest.mark.asyncio
    async def test_real_user_creation_flow(self, user_controller):
        """Test complete user creation flow with minimal mocking"""
        user_name = "Integration Test User"
        user_email = f"integration-{str(uuid.uuid4())[:8]}@test.com"

        with patch("controllers.user_controller.create_user") as mock_create_user_db:
            # Mock successful database operation
            mock_created_user = MagicMock()
            mock_created_user.id = 999
            mock_created_user.user_name = user_name
            mock_created_user.user_email = user_email
            mock_create_user_db.return_value = mock_created_user

            result = await user_controller.create_user(user_name, user_email)

            assert result["success"] is True
            assert result["message"] == "User created successfully"
            assert result["data"] == mock_created_user

            # Verify create_user was called with correct User model
            mock_create_user_db.assert_called_once()
            call_args = mock_create_user_db.call_args
            user_model_arg = call_args[0][0]  # First argument (user model)

            assert isinstance(user_model_arg, User)
            assert user_model_arg.user_name == user_name
            assert user_model_arg.user_email == user_email


class TestUserControllerRealistic:
    """Tests that simulate real-world scenarios"""

    @pytest.fixture
    def user_controller(self):
        return UserController()

    @pytest.mark.asyncio
    async def test_concurrent_user_creation(self, user_controller):
        """Test concurrent user creation"""
        import asyncio

        async def create_user_async(user_data):
            controller = UserController()
            with patch.object(controller, "validate_user") as mock_validate, patch(
                "controllers.user_controller.get_user"
            ) as mock_get_user, patch(
                "controllers.user_controller.User"
            ) as mock_user_model, patch(
                "controllers.user_controller.create_user"
            ) as mock_create_user_db:

                mock_validated_data = MagicMock()
                mock_validated_data.user_name = user_data["name"]
                mock_validated_data.user_email = user_data["email"]

                mock_validate.return_value = {
                    "success": True,
                    "data": mock_validated_data,
                }
                mock_get_user.return_value = None
                mock_user_model.return_value = MagicMock()
                mock_create_user_db.return_value = MagicMock()

                return await controller.create_user(
                    user_data["name"], user_data["email"]
                )

        user_configs = [
            {"name": f"User-{i}", "email": f"user{i}@example.com"} for i in range(5)
        ]

        async def run_concurrent():
            tasks = [create_user_async(config) for config in user_configs]
            results = await asyncio.gather(*tasks)
            return results

        results = await run_concurrent()

        # Verify all succeeded
        for result in results:
            assert result["success"] is True
            assert result["message"] == "User created successfully"

    @pytest.mark.asyncio
    async def test_user_controller_with_realistic_data(self, user_controller):
        """Test with realistic user data"""
        realistic_users = [
            {"name": "Alice Johnson", "email": "alice.johnson@gmail.com"},
            {"name": "Bob Smith", "email": "bob.smith+work@company.co.uk"},
            {"name": "Maria García", "email": "maria.garcia@university.edu"},
            {"name": "李小明", "email": "xiaoming.li@tech.cn"},
        ]

        for user_data in realistic_users:
            result = await user_controller.validate_user(
                user_data["name"], user_data["email"]
            )

            assert result["success"] is True
            assert result["data"].user_name == user_data["name"]
            assert result["data"].user_email == user_data["email"]

    @pytest.mark.asyncio
    async def test_user_operations_resilience(self, user_controller):
        """Test user operations with various edge cases"""
        edge_cases = [
            # Very short names
            {"name": "A", "email": "a@test.com", "should_validate": True},
            # Names with numbers
            {"name": "User123", "email": "user123@test.com", "should_validate": True},
            # Emails with subdomains
            {
                "name": "Test User",
                "email": "test@sub.domain.com",
                "should_validate": True,
            },
            # Names with apostrophes
            {"name": "O'Connor", "email": "oconnor@test.com", "should_validate": True},
        ]

        for case in edge_cases:
            result = await user_controller.validate_user(case["name"], case["email"])

            if case["should_validate"]:
                assert result["success"] is True, f"Failed for case: {case['name']}"
            else:
                assert (
                    result["success"] is False
                ), f"Should have failed for case: {case['name']}"


class TestUserSchemaValidation:
    """Test UserSchema validation independently"""

    def test_user_schema_valid_data(self):
        """Test UserSchema with valid data"""
        user = UserSchema(user_name="John Doe", user_email="john.doe@example.com")

        assert user.user_name == "John Doe"
        assert user.user_email == "john.doe@example.com"

        # Test validate_all method
        validated = user.validate_all()
        assert validated == user

    def test_user_schema_empty_strings(self):
        """Test UserSchema with empty strings (should be valid)"""
        user = UserSchema(user_name="", user_email="")

        assert user.user_name == ""
        assert user.user_email == ""

        # Empty strings are valid according to current schema
        validated = user.validate_all()
        assert validated == user

    def test_user_schema_special_characters(self):
        """Test UserSchema with special characters"""
        test_cases = [
            {"name": "José María O'Connor-Smith", "email": "jose.maria@domain.co.uk"},
            {"name": "李小明", "email": "xiaoming.li@tech.cn"},
            {"name": "Test@User#123", "email": "test+tag@example-domain.com"},
        ]

        for case in test_cases:
            user = UserSchema(user_name=case["name"], user_email=case["email"])

            assert user.user_name == case["name"]
            assert user.user_email == case["email"]

            validated = user.validate_all()
            assert validated == user

    def test_user_schema_extreme_values(self):
        """Test UserSchema with extreme but valid values"""
        # Very long strings
        long_name = "A" * 1000
        long_email = "a" * 500 + "@example.com"

        user = UserSchema(user_name=long_name, user_email=long_email)

        assert len(user.user_name) == 1000
        assert len(user.user_email) == len(long_email)

        validated = user.validate_all()
        assert validated == user


class TestUserControllerPerformance:
    """Performance-focused tests"""

    @pytest.fixture
    def user_controller(self):
        return UserController()

    @pytest.mark.asyncio
    async def test_user_creation_performance(self, user_controller):
        """Test user creation performance with multiple operations"""
        import time

        with patch.object(user_controller, "validate_user") as mock_validate, patch(
            "controllers.user_controller.get_user"
        ) as mock_get_user, patch(
            "controllers.user_controller.User"
        ) as mock_user_model, patch(
            "controllers.user_controller.create_user"
        ) as mock_create_user_db:

            mock_validate.return_value = {"success": True, "data": MagicMock()}
            mock_get_user.return_value = None
            mock_user_model.return_value = MagicMock()
            mock_create_user_db.return_value = MagicMock()

            start_time = time.time()

            # Create 100 users
            results = []
            for i in range(100):
                result = await user_controller.create_user(
                    f"User{i}", f"user{i}@test.com"
                )
                results.append(result)

            end_time = time.time()
            execution_time = end_time - start_time

            # Verify all succeeded
            for result in results:
                assert result["success"] is True

            # Performance assertion
            assert (
                execution_time < 2.0
            ), f"User creation took too long: {execution_time}s"

            # Should be very fast since we're mocking I/O
            avg_time_per_user = execution_time / 100
            assert avg_time_per_user < 0.01, ".4f"

    @pytest.mark.asyncio
    async def test_concurrent_user_validation(self, user_controller):
        """Test concurrent user validation performance"""
        import asyncio

        async def validate_user_async():
            return await user_controller.validate_user("Test User", "test@example.com")

        async def run_concurrent_validation():
            tasks = [validate_user_async() for _ in range(50)]
            results = await asyncio.gather(*tasks)
            return results

        import time

        start_time = time.time()

        results = await run_concurrent_validation()

        end_time = time.time()
        execution_time = end_time - start_time

        # Verify all succeeded
        for result in results:
            assert result["success"] is True

        # Should complete 50 validations quickly
        assert execution_time < 1.0, ".4f"
