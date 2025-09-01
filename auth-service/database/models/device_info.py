from datetime import datetime

from database.core.engine import Base, Engine
from service.logs.logger import logger
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String


class DeviceInfo(Base):
    __tablename__ = "device_info"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    ip = Column(String)
    user_id = Column(Integer, ForeignKey("user.id"))
    user_agent = Column(String)
    accept_language = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(self, ip: str, user_agent: str, accept_language: str, user_id: int):
        logger.info("Initializing device info")
        self.ip = ip
        self.user_agent = user_agent
        self.user_id = user_id
        self.accept_language = accept_language
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


Base.metadata.create_all(bind=Engine)
