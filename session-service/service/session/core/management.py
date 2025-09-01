"""
Redis Session Management Module

This module provides asynchronous Redis-based session management functionality
for handling user sessions with automatic expiration and data serialization.
"""

import json
import logging
from typing import Dict, Union

from config.init_config import redis_config
from redis.asyncio import Redis as AsyncRedis

logger = logging.getLogger(__name__)


class InitRedis:
    """
    Asynchronous Redis session manager for handling user session data.

    This class provides methods to create, retrieve, update, and delete user sessions
    stored in Redis with automatic JSON serialization/deserialization and configurable
    expiration times.

    Attributes:
        r (AsyncRedis): Asynchronous Redis client instance
        message (dict): Default response message for non-existent sessions
    """

    def __init__(self):
        """
        Initialize Redis connection and default configuration.

        Sets up connection to Redis server running on localhost:6379 with database 0
        and initializes default error messages for session operations.
        """
        self.r = AsyncRedis(
            host=redis_config["host"], port=redis_config["port"], db=redis_config["db"]
        )
        self.message = {"response": "Does Not Exist!"}

    async def ping(self) -> bool:
        """
        Test Redis server connectivity.

        Returns:
            bool: True if Redis server is reachable and responding, False otherwise

        Raises:
            redis.exceptions.ConnectionError: If unable to connect to Redis server
        """
        return await self.r.ping()

    async def set_session(self, session_id: str, session_data: dict) -> None:
        """
        Store session data in Redis with automatic expiration.

        Serializes the session data as JSON and stores it in Redis with the given
        session ID as the key. Sessions automatically expire after 60 seconds.

        Args:
            session_id (str): Unique identifier for the session
            session_data (dict): Session data to be stored (must be JSON serializable)

        Raises:
            TypeError: If session_data contains non-serializable objects
            redis.exceptions.RedisError: If Redis operation fails
        """
        byted_data = json.dumps(session_data).encode("utf-8")
        await self.r.set(session_id, byted_data, ex=60)

    async def get_session(self, session_id: str) -> Union[Dict, str]:
        """
        Retrieve session data from Redis.

        Fetches and deserializes session data associated with the given session ID.

        Args:
            session_id (str): Unique identifier for the session to retrieve

        Returns:
            Union[Dict, str]:
                - Dict: Deserialized session data if session exists
                - str: Error message if session does not exist or has expired

        Raises:
            json.JSONDecodeError: If stored data is not valid JSON
            redis.exceptions.RedisError: If Redis operation fails
        """
        logger.info(f"Getting session: {session_id}")
        byted_data = await self.r.get(session_id)
        logger.info(f"Byted data: {byted_data}")
        if byted_data:
            return json.loads(byted_data.decode("utf-8"))
        else:
            return self.message.get("response")

    async def delete_session(self, session_id: str) -> bool:
        """
        Remove session data from Redis.

        Permanently deletes the session data associated with the given session ID.

        Args:
            session_id (str): Unique identifier for the session to delete

        Returns:
            bool: True if deletion operation completed successfully

        Note:
            Returns True even if the session ID did not exist in Redis

        Raises:
            redis.exceptions.RedisError: If Redis operation fails
        """
        await self.r.delete(session_id)
        return True
