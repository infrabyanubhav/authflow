from service.logs.logger import logger
from service.session.features.base import BaseSession

"""
UpdateSession class for updating session data in Redis.

This class provides a method to update the session data for a given session ID.

Attributes:
    redis (AsyncRedis): Asynchronous Redis client instance
    message (dict): Default response message for non-existent sessions
"""


class UpdateSession(BaseSession):
    """
    UpdateSession class for updating session data in Redis.

    This class provides a method to update the session data for a given session ID.

    Attributes:
        redis (AsyncRedis): Asynchronous Redis client instance
        message (dict): Default response message for non-existent sessions
    """

    async def update_session(self, session_id: str, session_data: dict):
        logger.info(f"Updating session: {session_id}")
        await self.redis.set_session(session_id, session_data)
        logger.info(f"Session updated: {session_id}")
