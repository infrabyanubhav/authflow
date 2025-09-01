from config.init_config import logger
from fastapi import FastAPI
from server.init_server import app
from server.start_server import start_server

if __name__ == "__main__":
    logger.info("Starting server")
    start_server(app)
