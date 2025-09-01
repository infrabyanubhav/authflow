from service.session.core.management import InitRedis
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
        await self.redis.delete_session(session_id)
