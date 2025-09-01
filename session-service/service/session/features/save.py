import logging

from service.session.features.base import BaseSession

logger = logging.getLogger(__name__)


class SaveSession(BaseSession):
    """Save session data to Redis"""

    async def save_session(self, session_id: str, session_data: dict):
        """Save session data with basic logging"""
        try:
            logger.debug(f"Saving session: {session_id}")
            await self.redis.set_session(session_id, session_data)
            logger.info(f"Session saved: {session_id}")
        except Exception as e:
            logger.error(f"Failed to save session {session_id}: {str(e)}")
            raise
