from service.logs.logger import logging

Message = str


class BaseException(Exception):
    def __init__(self, message: Message):
        self.message = message
        super().__init__(self.message)
        logging.error(f"BaseException: {self.message}")

    def __str__(self):
        return f"BaseException: {self.message}"

    def __repr__(self):
        return f"BaseException: {self.message}"
