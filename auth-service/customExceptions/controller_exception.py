from customExceptions.base import BaseException
from customExceptions.messages import Message as MessageType
from service.logs.logger import logging


class ControllerException(BaseException):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
        logging.error(f"{MessageType['CONTROLLER_ERROR']}  =>{self.message}")

    def __str__(self):
        return f"ControllerException: {self.message}"
