import pytest
from service.session.core.management import InitRedis
from service.session.features.delete import DeleteSession
from service.session.features.fetch import FetchSession
from service.session.features.save import SaveSession
from service.session.features.update import UpdateSession


@pytest.mark.asyncio
async def test_redis_connection():
    redis = InitRedis()
    assert await redis.ping()


@pytest.mark.asyncio
async def test_all_features():
    """
    Comprehensive test for all Redis session management features.

    Tests the complete lifecycle of a session:
    1. Save session data
    2. Fetch session data
    3. Update session data
    4. Delete session data
    5. Verify session is deleted
    """
    # Test data
    session_id = "test_session_123"
    initial_session_data = {
        "user_id": "user_123",
        "username": "test_user",
        "email": "test@example.com",
        "login_time": "2024-01-01T10:00:00Z",
        "permissions": ["read", "write"],
    }

    updated_session_data = {
        "user_id": "user_123",
        "username": "test_user_updated",
        "email": "test_updated@example.com",
        "login_time": "2024-01-01T10:00:00Z",
        "permissions": ["read", "write", "admin"],
        "last_activity": "2024-01-01T11:30:00Z",
    }

    # Initialize feature classes
    save_session = SaveSession()
    fetch_session = FetchSession()
    update_session = UpdateSession()
    delete_session = DeleteSession()

    try:
        # Test 1: Save session data
        await save_session.save_session(session_id, initial_session_data)
        print("✓ Session saved successfully")

        # Test 2: Fetch session data
        fetched_data = await fetch_session.fetch_session(session_id)
        assert isinstance(fetched_data, dict), "Fetched data should be a dictionary"
        assert fetched_data["user_id"] == initial_session_data["user_id"]
        assert fetched_data["username"] == initial_session_data["username"]
        assert fetched_data["email"] == initial_session_data["email"]
        assert fetched_data["permissions"] == initial_session_data["permissions"]
        print("✓ Session fetched and validated successfully")

        # Test 3: Update session data
        await update_session.update_session(session_id, updated_session_data)
        print("✓ Session updated successfully")

        # Test 4: Fetch updated session data
        updated_fetched_data = await fetch_session.fetch_session(session_id)
        assert isinstance(
            updated_fetched_data, dict
        ), "Updated fetched data should be a dictionary"
        assert updated_fetched_data["username"] == updated_session_data["username"]
        assert updated_fetched_data["email"] == updated_session_data["email"]
        assert "admin" in updated_fetched_data["permissions"]
        assert "last_activity" in updated_fetched_data
        print("✓ Updated session fetched and validated successfully")

        # Test 5: Delete session
        await delete_session.delete_session(session_id)
        print("✓ Session deleted successfully")

        # Test 6: Verify session is deleted
        deleted_result = await fetch_session.fetch_session(session_id)
        assert (
            deleted_result == "Does Not Exist!"
        ), f"Expected 'Does Not Exist!', got: {deleted_result}"
        print("✓ Session deletion verified successfully")

        print("\n🎉 All Redis session features tested successfully!")

    except Exception as e:
        # Cleanup in case of test failure
        try:
            await delete_session.delete_session(session_id)
        except:
            pass
        raise e


@pytest.mark.asyncio
async def test_non_existent_session():
    """
    Test fetching a session that doesn't exist.
    """
    fetch_session = FetchSession()
    non_existent_id = "non_existent_session_456"

    result = await fetch_session.fetch_session(non_existent_id)
    assert result == "Does Not Exist!", f"Expected 'Does Not Exist!', got: {result}"
    print("✓ Non-existent session handled correctly")


@pytest.mark.asyncio
async def test_session_expiration():
    """
    Test that sessions expire after the configured time.
    Note: This test takes 61+ seconds to complete due to expiration testing.
    """
    import asyncio

    session_id = "expiration_test_session"
    session_data = {"test": "expiration_data"}

    save_session = SaveSession()
    fetch_session = FetchSession()
    delete_session = DeleteSession()

    try:
        # Save session
        await save_session.save_session(session_id, session_data)

        # Verify session exists immediately
        result = await fetch_session.fetch_session(session_id)
        assert isinstance(result, dict), "Session should exist immediately after saving"
        print("✓ Session exists immediately after saving")

        # Wait for expiration (61 seconds to be safe)
        print("⏳ Waiting for session expiration (61 seconds)...")
        await asyncio.sleep(61)

        # Verify session has expired
        expired_result = await fetch_session.fetch_session(session_id)
        assert (
            expired_result == "Does Not Exist!"
        ), f"Session should have expired, got: {expired_result}"
        print("✓ Session expired correctly after timeout")

    except Exception as e:
        # Cleanup
        try:
            await delete_session.delete_session(session_id)
        except:
            pass
        raise e


@pytest.mark.asyncio
async def test_multiple_sessions():
    """
    Test managing multiple sessions simultaneously.
    """
    save_session = SaveSession()
    fetch_session = FetchSession()
    delete_session = DeleteSession()

    # Create multiple test sessions
    sessions = {
        "session_1": {"user": "alice", "role": "admin"},
        "session_2": {"user": "bob", "role": "user"},
        "session_3": {"user": "charlie", "role": "moderator"},
    }

    try:
        # Save all sessions
        for session_id, data in sessions.items():
            await save_session.save_session(session_id, data)
        print("✓ All sessions saved successfully")

        # Fetch and validate all sessions
        for session_id, expected_data in sessions.items():
            fetched_data = await fetch_session.fetch_session(session_id)
            assert isinstance(fetched_data, dict)
            assert fetched_data["user"] == expected_data["user"]
            assert fetched_data["role"] == expected_data["role"]
        print("✓ All sessions fetched and validated successfully")

        # Delete all sessions
        for session_id in sessions.keys():
            await delete_session.delete_session(session_id)
        print("✓ All sessions deleted successfully")

        # Verify all sessions are deleted
        for session_id in sessions.keys():
            result = await fetch_session.fetch_session(session_id)
            assert result == "Does Not Exist!"
        print("✓ All session deletions verified successfully")

    except Exception as e:
        # Cleanup
        for session_id in sessions.keys():
            try:
                await delete_session.delete_session(session_id)
            except:
                pass
        raise e
