import uuid

import config.init_config as init_config
from fastapi import Request
from service.logs.logger import logger


async def sessionMiddleware(request: Request, call_next):
    """
    Middleware to create and attach a unique session ID for allowed session URLs.

    This middleware checks if the incoming request URL is present in the
    `allowed_urls["session_service"]` configuration. If allowed, it generates
    a new UUID and stores it in `request.session["session_id"]`. If not allowed,
    it returns a JSON-like message depending on the environment.

    Args:
        request (Request): The incoming FastAPI request object.
        call_next (Callable): The next middleware or endpoint function to call.

    Returns:
        Response | dict: If the URL is allowed, returns the response from
        `call_next`. Otherwise, returns a dictionary with an error message
        depending on the environment (development or production).
    """
    logger.info(f"Session middleware called for {request.url.path}")

    if request.url.path in init_config.allowed_urls["session_service"]:
        request.session["session_id"] = uuid.uuid4()
        logger.info(f"Session middleware passed for {request.url.path}")
        return await call_next(request)
    else:
        logger.info(f"Session middleware failed for {request.url.path}")
        if init_config.env == "development":
            return {
                "message": "Session URL not found kind of like 404, Check your config"
            }
        else:
            return {"message": "Forbidden, Something Fishy is going on"}
