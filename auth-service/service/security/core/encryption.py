import os

from cryptography.fernet import Fernet
from service.logs.logger import logger


class Encryption:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.fernet = Fernet(self.key)

    def create_key_file(self):
        if (
            not os.path.exists("key_store/key.txt")
            or os.path.getsize("key_store/key.txt") == 0
        ):
            with open("key_store/key.txt", "wb") as f:
                f.write(self.key)
        else:
            logger.info("Key file already exists")


class SecurityOperations:
    def __init__(self):
        self.path = "key_store/key.txt"

    def decrypt(self, message: str):
        logger.info("Decrypting message")
        with open(self.path, "rb") as f:
            self.key = f.read()
            self.fernet = Fernet(self.key)
            return self.fernet.decrypt(message.encode()).decode()

    def encrypt(self, message: str):
        logger.info("Encrypting message")
        with open(self.path, "rb") as f:
            self.key = f.read()
            self.fernet = Fernet(self.key)
            return self.fernet.encrypt(message.encode()).decode()
