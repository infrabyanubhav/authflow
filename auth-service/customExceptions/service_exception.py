from customExceptions.base import BaseException
from customExceptions.messages import Message as MessageType
from service.logs.logger import logging


class ServiceException(BaseException):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
        logging.error(f"{MessageType['SERVICE_ERROR']} {self.message}")

    def __str__(self):
        return f"ServiceException: {self.message}"
