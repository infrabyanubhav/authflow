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
        await self.redis.set_session(session_id, session_data)
