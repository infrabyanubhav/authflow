import logging

from config.setup_environment import setup_environment
import os       



logging.basicConfig(
    filename="session-service.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


env = "development"
setup_environment(env)

excluded_paths = ["/docs", "/redoc", "/openapi.json", "/health", "/health/", "/auth", "/","/verified"]

server_config = {
    "host": "0.0.0.0",
    "port": 8000,
    "summary": "Session Service, Authflow",
    "description": "Session Servic",
    "version": "0.1.0",
    "docs_url": "/docs",
    "redoc_url": "/redoc",
    "openapi_url": "/openapi.json",
    "title": "Session Service",
    "description": "Session Service",
    "version": "0.1.0",
    "contact": {
        "name": "InfraByAnubhav",
        "url": "",
        "email": "infrabyanubhav@gmail.com",
    },
}

redis_config = {
    "host": os.getenv("REDIS_HOST") or "localhost",
    "port": os.getenv("PORT"),
    "db": 0,
}

auth_config = {"auth_url":os.getenv(
    "AUTH_URL"
) }

backend_config = {"backend_url":
                  os.getenv(
                      "BACKEND_URL"
                  )}
prefix_config = {"prefix":os.getenv(
                      "PREFIX"
                  )}