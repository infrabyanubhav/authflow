from datetime import datetime

from database.core.engine import Base, Engine
from service.logs.logger import logger
from sqlalchemy import Column, DateTime, Integer, String


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    user_uuid = Column(String, unique=True)
    user_name = Column(String)
    user_email = Column(String)
    user_avatar = Column(String, nullable=True)

    def __init__(
        self,
        user_name: str,
        user_email: str,
        user_avatar: str = None,
        user_uuid: str = None,
    ):
        logger.info(f"Initializing user")
        self.user_name = user_name
        self.user_email = user_email
        self.user_avatar = user_avatar
        self.user_uuid = user_uuid


Base.metadata.create_all(bind=Engine)
