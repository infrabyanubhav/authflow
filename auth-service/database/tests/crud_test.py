from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
import sqlalchemy
from database.core.atomic import atomic_transaction
from database.core.engine import Session
from database.crud.device_info import create_device_info, get_device_info
from database.crud.user import create_user, get_user
from database.models.device_info import DeviceInfo
from database.models.user import User


class TestUserCRUD:
    """Comprehensive test suite for User CRUD operations"""

    def test_create_user_success(self):
        """Test successful user creation with valid data"""
        # Arrange
        user_name = "john_doe"
        user_email = f"john+{str(uuid4())[:8]}@example.com"
        user_avatar = "https://example.com/avatar.jpg"
        user_uuid = str(uuid4())

        user = User(
            user_name=user_name,
            user_email=user_email,
            user_avatar=user_avatar,
            user_uuid=user_uuid,
        )

        # Act
        created_user = create_user(user)

        # Assert
        assert created_user is not None
        # Note: create_user returns the User object, not a dict
        # We can access properties immediately since session is still active within the function

    def test_create_user_minimal_data(self):
        """Test user creation with minimal required data (no avatar)"""
        # Arrange
        user_name = "jane_doe"
        user_email = f"jane+{str(uuid4())[:8]}@example.com"
        user_uuid = str(uuid4())

        user = User(
            user_name=user_name,
            user_email=user_email,
            user_avatar=None,  # Optional field
            user_uuid=user_uuid,
        )

        # Act
        created_user = create_user(user)

        # Assert
        assert created_user is not None

    def test_get_user_success(self):
        """Test successful user retrieval by email"""
        # Arrange - First create a user
        user_name = "alice_smith"
        user_email = f"alice+{str(uuid4())[:8]}@example.com"
        user_avatar = "https://example.com/alice.jpg"
        user_uuid = str(uuid4())

        user = User(
            user_name=user_name,
            user_email=user_email,
            user_avatar=user_avatar,
            user_uuid=user_uuid,
        )

        create_user(user)

        # Act
        retrieved_user = get_user(user_email)

        # Assert
        assert retrieved_user is not None
        assert retrieved_user["id"] is not None
        assert retrieved_user["user_name"] == user_name
        assert retrieved_user["user_email"] == user_email
        assert retrieved_user["user_avatar"] == user_avatar
        assert retrieved_user["user_uuid"] == user_uuid

    def test_get_user_not_found(self):
        """Test retrieval of non-existent user"""
        # Arrange
        non_existent_email = f"nonexistent+{str(uuid4())[:8]}@example.com"

        # Act
        result = get_user(non_existent_email)

        # Assert
        assert result is None

    def test_create_and_retrieve_user_workflow(self):
        """Test complete workflow: create user and then retrieve it"""
        # Arrange
        user_name = "bob_wilson"
        user_email = f"bob+{str(uuid4())[:8]}@example.com"
        user_avatar = "https://example.com/bob.jpg"
        user_uuid = str(uuid4())

        user = User(
            user_name=user_name,
            user_email=user_email,
            user_avatar=user_avatar,
            user_uuid=user_uuid,
        )

        # Act
        created_user = create_user(user)
        retrieved_user = get_user(user_email)

        # Assert
        assert created_user is not None
        assert retrieved_user is not None
        assert retrieved_user["user_name"] == user_name
        assert retrieved_user["user_email"] == user_email
        assert retrieved_user["user_avatar"] == user_avatar
        assert retrieved_user["user_uuid"] == user_uuid

    def test_create_user_with_special_characters(self):
        """Test user creation with special characters in name"""
        # Arrange
        user_name = "José María O'Connor"
        user_email = f"jose+{str(uuid4())[:8]}@example.com"
        user_uuid = str(uuid4())

        user = User(
            user_name=user_name,
            user_email=user_email,
            user_avatar=None,
            user_uuid=user_uuid,
        )

        # Act
        created_user = create_user(user)
        retrieved_user = get_user(user_email)

        # Assert
        assert created_user is not None
        assert retrieved_user is not None
        assert retrieved_user["user_name"] == user_name

    def test_create_user_with_long_strings(self):
        """Test user creation with longer string values"""
        # Arrange
        user_name = "a" * 50  # Long name
        user_email = (
            f"very_long_email_address_{str(uuid4())[:8]}@verylongdomainname.com"
        )
        user_avatar = "https://example.com/very/long/path/to/avatar/image.jpg"
        user_uuid = str(uuid4())

        user = User(
            user_name=user_name,
            user_email=user_email,
            user_avatar=user_avatar,
            user_uuid=user_uuid,
        )

        # Act
        created_user = create_user(user)
        retrieved_user = get_user(user_email)

        # Assert
        assert created_user is not None
        assert retrieved_user is not None
        assert retrieved_user["user_name"] == user_name
        assert retrieved_user["user_email"] == user_email

    def test_uuid_string_conversion(self):
        """Test that UUID is properly converted to string"""
        # Arrange
        user_name = "uuid_test_user"
        user_email = f"uuid_test+{str(uuid4())[:8]}@example.com"
        user_uuid = str(uuid4())  # Ensure it's a string

        user = User(
            user_name=user_name,
            user_email=user_email,
            user_avatar=None,
            user_uuid=user_uuid,
        )

        # Act
        created_user = create_user(user)
        retrieved_user = get_user(user_email)

        # Assert
        assert created_user is not None
        assert retrieved_user is not None
        assert isinstance(retrieved_user["user_uuid"], str)
        assert retrieved_user["user_uuid"] == user_uuid

    def test_multiple_users_creation(self):
        """Test creating multiple users with different data"""
        # Arrange
        users_data = [
            {
                "name": "user1",
                "email": f"user1+{str(uuid4())[:8]}@example.com",
                "avatar": "https://example.com/user1.jpg",
            },
            {
                "name": "user2",
                "email": f"user2+{str(uuid4())[:8]}@example.com",
                "avatar": None,
            },
            {
                "name": "user3",
                "email": f"user3+{str(uuid4())[:8]}@example.com",
                "avatar": "https://example.com/user3.jpg",
            },
        ]

        created_users = []

        # Act
        for user_data in users_data:
            user = User(
                user_name=user_data["name"],
                user_email=user_data["email"],
                user_avatar=user_data["avatar"],
                user_uuid=str(uuid4()),
            )
            created_user = create_user(user)
            created_users.append((created_user, user_data))

        # Assert
        for created_user, original_data in created_users:
            assert created_user is not None

            # Verify by retrieving
            retrieved_user = get_user(original_data["email"])
            assert retrieved_user is not None
            assert retrieved_user["user_name"] == original_data["name"]
            assert retrieved_user["user_email"] == original_data["email"]
            assert retrieved_user["user_avatar"] == original_data["avatar"]

    def test_user_avatar_optional(self):
        """Test that user_avatar field is properly handled when None"""
        # Arrange
        user_name = "no_avatar_user"
        user_email = f"no_avatar+{str(uuid4())[:8]}@example.com"
        user_uuid = str(uuid4())

        user = User(
            user_name=user_name,
            user_email=user_email,
            user_avatar=None,
            user_uuid=user_uuid,
        )

        # Act
        created_user = create_user(user)
        retrieved_user = get_user(user_email)

        # Assert
        assert created_user is not None
        assert retrieved_user is not None
        assert retrieved_user["user_avatar"] is None

    def test_empty_string_values(self):
        """Test behavior with empty string values"""
        # Arrange
        user_name = ""  # Empty name
        user_email = f"empty_name+{str(uuid4())[:8]}@example.com"
        user_avatar = ""  # Empty avatar URL
        user_uuid = str(uuid4())

        user = User(
            user_name=user_name,
            user_email=user_email,
            user_avatar=user_avatar,
            user_uuid=user_uuid,
        )

        # Act
        created_user = create_user(user)
        retrieved_user = get_user(user_email)

        # Assert
        assert created_user is not None
        assert retrieved_user is not None
        assert retrieved_user["user_name"] == ""
        assert retrieved_user["user_avatar"] == ""


class TestTransactionRollback:
    """Test suite for transaction rollback functionality"""

    def test_create_user_rollback_on_database_error(self):
        """Test that transaction is rolled back when database error occurs"""
        # Arrange
        user_name = "rollback_test_user"
        user_email = f"rollback+{str(uuid4())[:8]}@example.com"
        user_uuid = str(uuid4())

        user = User(
            user_name=user_name,
            user_email=user_email,
            user_avatar=None,
            user_uuid=user_uuid,
        )

        # Mock the database session to raise an exception during flush
        with patch("database.core.atomic.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session

            # Configure mock to raise exception on flush
            mock_session.flush.side_effect = sqlalchemy.exc.IntegrityError(
                "Mock integrity error", None, None
            )

            # Act & Assert
            with pytest.raises(sqlalchemy.exc.IntegrityError):
                create_user(user)

            # Verify rollback was called
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()

    def test_create_user_rollback_on_commit_failure(self):
        """Test rollback when commit operation fails"""
        # Arrange
        user_name = "commit_fail_user"
        user_email = f"commit_fail+{str(uuid4())[:8]}@example.com"
        user_uuid = str(uuid4())

        user = User(
            user_name=user_name,
            user_email=user_email,
            user_avatar=None,
            user_uuid=user_uuid,
        )

        # Mock the database session to raise an exception during commit
        with patch("database.core.atomic.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session

            # Configure mock to raise exception on commit
            mock_session.commit.side_effect = sqlalchemy.exc.DatabaseError(
                "Mock database error", None, None
            )

            # Act & Assert
            with pytest.raises(sqlalchemy.exc.DatabaseError):
                create_user(user)

            # Verify rollback was called
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()

    def test_duplicate_uuid_constraint_violation(self):
        """Test rollback when trying to create user with duplicate UUID"""
        # Arrange
        duplicate_uuid = str(uuid4())

        # Create first user successfully
        user1 = User(
            user_name="first_user",
            user_email=f"first+{str(uuid4())[:8]}@example.com",
            user_avatar=None,
            user_uuid=duplicate_uuid,
        )
        created_user1 = create_user(user1)
        assert created_user1 is not None

        # Try to create second user with same UUID
        user2 = User(
            user_name="second_user",
            user_email=f"second+{str(uuid4())[:8]}@example.com",
            user_avatar=None,
            user_uuid=duplicate_uuid,  # Same UUID as first user
        )

        # Act & Assert
        with pytest.raises(Exception):  # Should raise constraint violation
            create_user(user2)

        # Verify second user was not created
        retrieved_user2 = get_user(user2.user_email)
        assert retrieved_user2 is None

    def test_atomic_transaction_decorator_functionality(self):
        """Test the atomic_transaction decorator behavior directly"""

        @atomic_transaction
        def failing_function(db):
            """A function that will fail after doing some database work"""
            # Create a user
            user = User(
                user_name="temp_user",
                user_email=f"temp+{str(uuid4())[:8]}@example.com",
                user_uuid=str(uuid4()),
            )
            db.add(user)
            db.flush()  # This will assign an ID

            # Now raise an exception to trigger rollback
            raise ValueError("Intentional test failure")

        # Arrange
        initial_user_count = self._count_users_in_db()

        # Act & Assert
        with pytest.raises(ValueError, match="Intentional test failure"):
            failing_function()

        # Verify no users were actually committed due to rollback
        final_user_count = self._count_users_in_db()
        assert final_user_count == initial_user_count

    def test_successful_transaction_commits(self):
        """Test that successful transactions properly commit"""

        @atomic_transaction
        def successful_function(db):
            """A function that will succeed"""
            user = User(
                user_name="success_user",
                user_email=f"success+{str(uuid4())[:8]}@example.com",
                user_uuid=str(uuid4()),
            )
            db.add(user)
            db.flush()
            return user

        # Arrange
        initial_user_count = self._count_users_in_db()

        # Act
        result = successful_function()

        # Assert
        assert result is not None
        final_user_count = self._count_users_in_db()
        assert final_user_count == initial_user_count + 1

    def test_nested_transaction_rollback(self):
        """Test rollback behavior when exception occurs after partial work"""

        @atomic_transaction
        def complex_failing_function(db):
            """Function that does multiple operations then fails"""
            # Add multiple users
            users = []
            for i in range(3):
                user = User(
                    user_name=f"batch_user_{i}",
                    user_email=f"batch_{i}+{str(uuid4())[:8]}@example.com",
                    user_uuid=str(uuid4()),
                )
                db.add(user)
                users.append(user)

            db.flush()  # Flush to get IDs

            # Verify users have IDs (meaning they would be committed)
            for user in users:
                assert user.id is not None

            # Now fail - this should rollback all the users
            raise RuntimeError("Batch operation failed")

        # Arrange
        initial_user_count = self._count_users_in_db()

        # Act & Assert
        with pytest.raises(RuntimeError, match="Batch operation failed"):
            complex_failing_function()

        # Verify none of the users were committed
        final_user_count = self._count_users_in_db()
        assert final_user_count == initial_user_count

    def _count_users_in_db(self):
        """Helper method to count total users in database"""
        db = Session()
        try:
            count = db.query(User).count()
            return count
        finally:
            db.close()


# Legacy test for backwards compatibility
def test_user():
    """Legacy test case - kept for backwards compatibility"""
    # Store values to avoid DetachedInstanceError later
    # Use unique email for each test run to avoid conflicts
    user_name = "anubhav"
    user_email = f"test+{str(uuid4())[:8]}@test.com"
    user_avatar = "https://eorix.io/avatar.png"
    user_uuid = str(uuid4())

    user = User(
        user_name=user_name,
        user_email=user_email,
        user_avatar=user_avatar,
        user_uuid=user_uuid,
    )

    created_user_data = create_user(user)
    got_user = get_user(user_email)

    # Now perform assertions using the returned data
    assert got_user is not None
    assert got_user["id"] is not None
    assert got_user["user_name"] == user_name
    assert got_user["user_email"] == user_email
    assert got_user["user_avatar"] == user_avatar
    assert got_user["user_uuid"] == user_uuid


class TestDeviceInfoCRUD:
    """Comprehensive test suite for DeviceInfo CRUD operations"""

    def test_create_device_info_success(self):
        """Test successful device info creation with valid data"""
        # Arrange
        ip = "192.168.1.100"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        accept_language = "en-US,en;q=0.9"
        user_id = 1

        device_info = DeviceInfo(
            ip=ip,
            user_agent=user_agent,
            accept_language=accept_language,
            user_id=user_id,
        )

        # Act
        created_device = create_device_info(device_info)

        # Assert
        assert created_device is not None

    def test_create_device_info_minimal_data(self):
        """Test device info creation with minimal required data"""
        # Arrange
        ip = "10.0.0.1"
        user_agent = "minimal-agent"
        accept_language = "en"
        user_id = 2

        device_info = DeviceInfo(
            ip=ip,
            user_agent=user_agent,
            accept_language=accept_language,
            user_id=user_id,
        )

        # Act
        created_device = create_device_info(device_info)

        # Assert
        assert created_device is not None

    def test_get_device_info_success(self):
        """Test successful device info retrieval by IP"""
        # Arrange - First create a device info
        ip = "172.16.0.1"
        user_agent = "Chrome/91.0.4472.124"
        accept_language = "fr-FR,fr;q=0.9"
        user_id = 3

        device_info = DeviceInfo(
            ip=ip,
            user_agent=user_agent,
            accept_language=accept_language,
            user_id=user_id,
        )

        create_device_info(device_info)

        # Act
        retrieved_device = get_device_info(ip)

        # Assert
        assert retrieved_device is not None
        assert retrieved_device["id"] is not None
        assert retrieved_device["ip"] == ip
        assert retrieved_device["user_agent"] == user_agent
        assert retrieved_device["accept_language"] == accept_language
        assert retrieved_device["user_id"] == user_id
        assert retrieved_device["created_at"] is not None
        assert retrieved_device["updated_at"] is not None

    def test_get_device_info_not_found(self):
        """Test retrieval of non-existent device info"""
        # Arrange
        non_existent_ip = f"255.255.255.{str(uuid4())[:3]}"

        # Act
        result = get_device_info(non_existent_ip)

        # Assert
        assert result is None

    def test_create_and_retrieve_device_workflow(self):
        """Test complete workflow: create device info and then retrieve it"""
        # Arrange
        ip = "203.0.113.1"  # TEST-NET-3 address
        user_agent = "Safari/537.36"
        accept_language = "es-ES,es;q=0.8"
        user_id = 4

        device_info = DeviceInfo(
            ip=ip,
            user_agent=user_agent,
            accept_language=accept_language,
            user_id=user_id,
        )

        # Act
        created_device = create_device_info(device_info)
        retrieved_device = get_device_info(ip)

        # Assert
        assert created_device is not None
        assert retrieved_device is not None
        assert retrieved_device["ip"] == ip
        assert retrieved_device["user_agent"] == user_agent
        assert retrieved_device["accept_language"] == accept_language
        assert retrieved_device["user_id"] == user_id

    def test_create_device_with_special_user_agent(self):
        """Test device creation with complex user agent string"""
        # Arrange
        ip = "198.51.100.1"  # TEST-NET-2 address
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
        accept_language = "zh-CN,zh;q=0.9,en;q=0.8"
        user_id = 5

        device_info = DeviceInfo(
            ip=ip,
            user_agent=user_agent,
            accept_language=accept_language,
            user_id=user_id,
        )

        # Act
        created_device = create_device_info(device_info)
        retrieved_device = get_device_info(ip)

        # Assert
        assert created_device is not None
        assert retrieved_device is not None
        assert retrieved_device["user_agent"] == user_agent

    def test_create_multiple_devices_for_same_user(self):
        """Test creating multiple device info records for the same user"""
        # Arrange
        user_id = 6
        devices_data = [
            {
                "ip": "192.168.1.10",
                "user_agent": "Chrome Mobile",
                "accept_language": "en-US",
            },
            {
                "ip": "192.168.1.11",
                "user_agent": "Firefox Desktop",
                "accept_language": "en-GB",
            },
            {
                "ip": "192.168.1.12",
                "user_agent": "Safari iPad",
                "accept_language": "en-AU",
            },
        ]

        created_devices = []

        # Act
        for device_data in devices_data:
            device_info = DeviceInfo(
                ip=device_data["ip"],
                user_agent=device_data["user_agent"],
                accept_language=device_data["accept_language"],
                user_id=user_id,
            )
            created_device = create_device_info(device_info)
            created_devices.append((created_device, device_data))

        # Assert
        for created_device, original_data in created_devices:
            assert created_device is not None

            # Verify by retrieving
            retrieved_device = get_device_info(original_data["ip"])
            assert retrieved_device is not None
            assert retrieved_device["ip"] == original_data["ip"]
            assert retrieved_device["user_agent"] == original_data["user_agent"]
            assert (
                retrieved_device["accept_language"] == original_data["accept_language"]
            )
            assert retrieved_device["user_id"] == user_id

    def test_device_timestamps_are_set(self):
        """Test that created_at and updated_at timestamps are properly set"""
        # Arrange
        ip = f"10.1.1.{str(uuid4())[:3]}"  # Use unique IP to avoid conflicts
        user_agent = "timestamp-test-agent"
        accept_language = "de-DE"
        user_id = 7

        device_info = DeviceInfo(
            ip=ip,
            user_agent=user_agent,
            accept_language=accept_language,
            user_id=user_id,
        )

        # Act
        create_device_info(device_info)
        retrieved_device = get_device_info(ip)

        # Assert
        assert retrieved_device is not None
        assert retrieved_device["created_at"] is not None
        assert retrieved_device["updated_at"] is not None
        # Both timestamps should be recent (within last few seconds)
        from datetime import datetime, timedelta

        now = datetime.now()
        created_at = retrieved_device["created_at"]
        updated_at = retrieved_device["updated_at"]

        assert isinstance(created_at, datetime)
        assert isinstance(updated_at, datetime)
        assert (now - created_at) < timedelta(seconds=10)
        assert (now - updated_at) < timedelta(seconds=10)


class TestDeviceInfoRollback:
    """Test suite for DeviceInfo transaction rollback functionality"""

    def test_create_device_rollback_on_database_error(self):
        """Test that transaction is rolled back when database error occurs"""
        # Arrange
        ip = "rollback.test.ip"
        user_agent = "rollback-test-agent"
        accept_language = "en-US"
        user_id = 999

        device_info = DeviceInfo(
            ip=ip,
            user_agent=user_agent,
            accept_language=accept_language,
            user_id=user_id,
        )

        # Mock the database session to raise an exception during flush
        with patch("database.core.atomic.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session

            # Configure mock to raise exception on flush
            mock_session.flush.side_effect = sqlalchemy.exc.IntegrityError(
                "Mock integrity error", None, None
            )

            # Act & Assert
            with pytest.raises(sqlalchemy.exc.IntegrityError):
                create_device_info(device_info)

            # Verify rollback was called
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()

    def test_create_device_rollback_on_commit_failure(self):
        """Test rollback when commit operation fails"""
        # Arrange
        ip = "commit.fail.ip"
        user_agent = "commit-fail-agent"
        accept_language = "en-US"
        user_id = 998

        device_info = DeviceInfo(
            ip=ip,
            user_agent=user_agent,
            accept_language=accept_language,
            user_id=user_id,
        )

        # Mock the database session to raise an exception during commit
        with patch("database.core.atomic.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session

            # Configure mock to raise exception on commit
            mock_session.commit.side_effect = sqlalchemy.exc.DatabaseError(
                "Mock database error", None, None
            )

            # Act & Assert
            with pytest.raises(sqlalchemy.exc.DatabaseError):
                create_device_info(device_info)

            # Verify rollback was called
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()

    def test_device_atomic_transaction_functionality(self):
        """Test the atomic_transaction decorator behavior with device operations"""

        # First create a valid user for the device
        from database.models.user import User

        test_user = User(
            user_name="Test Device User",
            user_email=f"devicetest+{str(uuid4())[:8]}@test.com",
            user_uuid=str(uuid4()),
        )
        created_user = create_user(test_user)

        @atomic_transaction
        def failing_device_function(db):
            """A function that will fail after doing some database work"""
            # Create a device info
            device_info = DeviceInfo(
                ip="temp.device.ip",
                user_agent="temp-device-agent",
                accept_language="en-US",
                user_id=created_user["id"],
            )
            db.add(device_info)
            db.flush()  # This will assign an ID

            # Now raise an exception to trigger rollback
            raise ValueError("Intentional device test failure")

        # Arrange
        initial_device_count = self._count_devices_in_db()

        # Act & Assert
        with pytest.raises(ValueError, match="Intentional device test failure"):
            failing_device_function()

        # Verify no devices were actually committed due to rollback
        final_device_count = self._count_devices_in_db()
        assert final_device_count == initial_device_count

    def test_successful_device_transaction_commits(self):
        """Test that successful device transactions properly commit"""

        # First create a valid user for the device
        from database.models.user import User

        test_user = User(
            user_name="Success Device User",
            user_email=f"devicetest+{str(uuid4())[:8]}@test.com",
            user_uuid=str(uuid4()),
        )
        created_user = create_user(test_user)

        @atomic_transaction
        def successful_device_function(db):
            """A function that will succeed"""
            device_info = DeviceInfo(
                ip="success.device.ip",
                user_agent="success-device-agent",
                accept_language="en-US",
                user_id=created_user["id"],
            )
            db.add(device_info)
            db.flush()
            return device_info

        # Arrange
        initial_device_count = self._count_devices_in_db()

        # Act
        result = successful_device_function()

        # Assert
        assert result is not None
        final_device_count = self._count_devices_in_db()
        assert final_device_count == initial_device_count + 1

    def test_multiple_device_operations_rollback(self):
        """Test rollback behavior when exception occurs after multiple device operations"""

        # First create valid users for the devices
        from database.models.user import User

        created_users = []
        for i in range(3):
            test_user = User(
                user_name=f"Batch Device User {i}",
                user_email=f"batchtest{i}+{str(uuid4())[:8]}@test.com",
                user_uuid=str(uuid4()),
            )
            created_user = create_user(test_user)
            created_users.append(created_user)

        @atomic_transaction
        def complex_failing_device_function(db):
            """Function that does multiple device operations then fails"""
            # Add multiple devices
            devices = []
            for i in range(3):
                device_info = DeviceInfo(
                    ip=f"batch.device.{i}.ip",
                    user_agent=f"batch-device-{i}-agent",
                    accept_language="en-US",
                    user_id=created_users[i]["id"],
                )
                db.add(device_info)
                devices.append(device_info)

            db.flush()  # Flush to get IDs

            # Verify devices have IDs (meaning they would be committed)
            for device in devices:
                assert device.id is not None

            # Now fail - this should rollback all the devices
            raise RuntimeError("Batch device operation failed")

        # Arrange
        initial_device_count = self._count_devices_in_db()

        # Act & Assert
        with pytest.raises(RuntimeError, match="Batch device operation failed"):
            complex_failing_device_function()

        # Verify none of the devices were committed
        final_device_count = self._count_devices_in_db()
        assert final_device_count == initial_device_count

    def _count_devices_in_db(self):
        """Helper method to count total device info records in database"""
        db = Session()
        try:
            count = db.query(DeviceInfo).count()
            return count
        finally:
            db.close()


# Legacy test for backwards compatibility
def test_device_info():
    """Legacy device info test case - kept for backwards compatibility"""
    # Store values to avoid DetachedInstanceError later
    ip = f"127.0.0.{str(uuid4())[:3]}"
    user_agent = "test"
    accept_language = "en-US"
    user_id = 1

    device_info = DeviceInfo(
        ip=ip, user_agent=user_agent, accept_language=accept_language, user_id=user_id
    )

    created_device_info = create_device_info(device_info)
    got_device_info = get_device_info(ip)

    assert got_device_info is not None
    assert got_device_info["id"] is not None
    assert got_device_info["ip"] == ip
    assert got_device_info["user_agent"] == user_agent
    assert got_device_info["accept_language"] == accept_language
    assert got_device_info["user_id"] == user_id
