from service.logs.logger import logger
from service.security.core.encryption import Encryption


def generate_key():
    key = Encryption()
    key.create_key_file()
    logger.info(f"Key generated")
