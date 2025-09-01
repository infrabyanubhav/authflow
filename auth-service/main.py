import os

from config.init_config import setup_environment
from server.init_server import app
from server.start_server import start_server

if __name__ == "__main__":
    setup_environment("development")
    print(os.getenv("DATABASE_URL"))
    start_server(app)
