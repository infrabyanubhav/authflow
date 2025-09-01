import config.init_config as init_config
from fastapi import HTTPException, Request
from service.logs.logger import logger


class AllowedURLMiddleware:
    """
    Middleware to restrict access to a predefined list of allowed URLs.

    This middleware checks if the incoming request URL is present in the
    allowed URLs defined in the configuration. If the URL is allowed, the
    request proceeds to the next middleware or endpoint. Otherwise, it
    returns a message depending on the environment (development or production).

    Attributes:
        allowed_urls (list[str]): A list of URLs allowed to be accessed.
    """

    def __init__(self):
        """Initialize the middleware with allowed URLs from configuration."""
        self.allowed_urls = init_config.allowed_urls

    def __call__(self, request: Request, call_next):
        """
        Process the incoming request and allow or deny access based on URL.

        Args:
            request (Request): The incoming FastAPI request object.
            call_next (Callable): The next middleware or endpoint function to call.

        Returns:
            Response | dict: If the URL is allowed, returns the response from
            `call_next`. If not allowed, returns a dictionary message indicating
            forbidden access or misconfiguration.
        """
        logger.info(f"Allowed URL middleware called for {request.url.path}")
        if request.url.path in self.allowed_urls:
            logger.info(f"Allowed URL middleware passed for {request.url.path}")
            return call_next(request)
        else:
            if init_config.env == "development":
                return {
                    "message": "Allowed URL not found kind of like 404, Check your config"
                }
            else:
                logger.error(
                    f"Forbidden, Something Fishy is going on",
                    request.url.path,
                    request.method,
                    request.headers,
                )
                return {"message": "Forbidden, Something Fishy is going on"}
