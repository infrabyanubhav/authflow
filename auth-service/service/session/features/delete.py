from service.logs.logger import logger
from service.session.features.base import BaseSession

"""
DeleteSession class for deleting session data from Redis.

This class provides a method to delete the session data for a given session ID.

Attributes:
    redis (AsyncRedis): Asynchronous Redis client instance
"""


class DeleteSession(BaseSession):
    """
    DeleteSession class for deleting session data from Redis.

    This class provides a method to delete the session data for a given session ID.

    Attributes:
        redis (AsyncRedis): Asynchronous Redis client instance
    """

    async def delete_session(self, session_id: str):
        logger.info(f"Deleting session: {session_id}")
        await self.redis.delete_session(session_id)
        logger.info(f"Session deleted: {session_id}")
