from typing import Union

from service.logs.logger import logger
from service.session.features.base import BaseSession

"""
FetchSession class for fetching session data from Redis.

This class provides a method to fetch the session data for a given session ID.

Attributes:
    redis (AsyncRedis): Asynchronous Redis client instance
"""


class FetchSession(BaseSession):
    """
    FetchSession class for fetching session data from Redis.

    This class provides a method to fetch the session data for a given session ID.

    Attributes:
        redis (AsyncRedis): Asynchronous Redis client instance
    """

    async def fetch_session(self, session_id: str) -> Union[dict, str]:
        logger.info(f"Fetching session: {session_id}")
        message = await self.redis.get_session(session_id)
        logger.info(f"Session fetched: {session_id}")
        return message
