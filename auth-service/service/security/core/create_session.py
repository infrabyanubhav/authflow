import uuid

from service.logs.logger import logger


def create_session():
    logger.info("Creating session")
    session_id = uuid.uuid4()
    logger.info("Session created: %s", session_id)
    session_key = f"{session_id}"
    return session_key
