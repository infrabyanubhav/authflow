import uvicorn
from config.init_config import logger
from fastapi import FastAPI

"""
Start the FastAPI server.

This function starts the FastAPI server on the specified host and port.

Attributes:
    app (FastAPI): FastAPI application instance
"""


def start_server(app: FastAPI):
    """
    Start the FastAPI server.

    This function starts the FastAPI server on the specified host and port.

    Attributes:
        app (FastAPI): FastAPI application instance
    """
    logger.info("Starting server")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
