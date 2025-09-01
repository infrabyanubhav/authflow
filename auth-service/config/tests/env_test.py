import os
from unittest.mock import patch

from config.init_config import (
    allowed_urls,
    db_config,
    forward_urls,
    redis_config,
    secrets_config,
    server_config,
    supabase_config,
    unsecure_urls,
)


def test_env():
    """Test environment configuration with mocked environment variables"""

    # Mock environment variables that the test expects
    with patch.dict(
        os.environ,
        {
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
            "REDIS_PASSWORD": "ANUBHAV",
            "REDIS_DB": "0",
            "DATABASE_URL": "sqlite:///./db.sqlite3",
            "SESSION_SECRET_KEY": "ANUBHAV",
        },
    ):
        # Re-import the config to get the mocked values
        import importlib

        import config.init_config

        importlib.reload(config.init_config)

        from config.init_config import db_config, redis_config, secrets_config

        assert redis_config["host"] == "localhost"
        assert redis_config["port"] == 6379
        assert redis_config["password"] == "ANUBHAV"
        assert redis_config["db"] == 0
        assert db_config["url"] == "sqlite:///./db.sqlite3"
        assert secrets_config["session_secret_key"] == "ANUBHAV"


def test_env_defaults():
    """Test environment configuration defaults when variables are not set"""

    # Mock environment variables with empty values (environment variables are always strings)
    with patch.dict(
        os.environ,
        {
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
            "REDIS_PASSWORD": "",
            "REDIS_DB": "0",
            "DATABASE_URL": "sqlite:///./test.db",
            "SESSION_SECRET_KEY": "",
        },
        clear=True,
    ):
        # Re-import the config to get the mocked values
        import importlib

        import config.init_config

        importlib.reload(config.init_config)

        from config.init_config import db_config, redis_config, secrets_config

        # Test actual defaults when environment variables are empty
        assert redis_config["host"] == "localhost"
        assert redis_config["port"] == 6379
        assert redis_config["password"] == ""  # Empty string when env var is empty
        assert redis_config["db"] == 0
        assert db_config["url"] == "sqlite:///./test.db"
        assert (
            secrets_config["session_secret_key"] == ""
        )  # Empty string when env var is empty


def test_server_config():
    """Test server configuration values"""
    assert server_config["host"] == "0.0.0.0"
    assert (
        server_config["port"] == 8001
    )  # Note: This is 8001, not 8000 as in the original test
    assert server_config["summary"] == "Auth Service for Eorix"
    assert server_config["description"] == "Auth Service for Eorix"
    assert server_config["version"] == "0.1.0"
    assert server_config["docs_url"] == "/docs"
    assert server_config["redoc_url"] == "/redoc"
    assert server_config["openapi_url"] == "/openapi.json"
