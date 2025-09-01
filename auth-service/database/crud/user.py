from typing import Optional

from database.core.atomic import atomic_transaction
from database.core.engine import Session as db_session
from database.models.user import User
from service.logs.logger import logger
from sqlalchemy.orm import Session


@atomic_transaction
def create_user(db, user: User):
    """Create a new user - session provided by atomic_transaction decorator"""
    db.add(user)
    db.flush()  # Flush to get the ID
    return {
        "id": user.id,
        "user_name": user.user_name,
        "user_email": user.user_email,
        "user_avatar": user.user_avatar,
        "user_uuid": user.user_uuid,
    }


def get_user(user_email: str) -> Optional[dict]:
    """Get user by email - creates its own session and returns detached data"""
    db = db_session()
    try:
        existing_user = db.query(User).filter_by(user_email=user_email).first()
        if existing_user is not None:
            logger.info("Existing user found: %s", existing_user.user_name)
            # Create a detached copy with all the data
            user_data = {
                "id": existing_user.id,
                "user_name": existing_user.user_name,
                "user_email": existing_user.user_email,
                "user_avatar": existing_user.user_avatar,
                "user_uuid": existing_user.user_uuid,
            }
            return user_data
        else:
            logger.info("No user found with email: %s", user_email)
            return None
    except Exception as e:
        logger.error("Error getting user: %s", e)
        raise e
    finally:
        db.close()
