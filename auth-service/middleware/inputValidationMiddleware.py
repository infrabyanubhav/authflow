from schema.auth_input import validate_input
from service.logs.logger import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# List of endpoints that require input validation
url_list = [
    "/auth/simple_auth/signin",
    "/auth/simple_auth/signup",
]


class InputValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate JSON input for specific POST endpoints.

    This middleware intercepts POST requests to certain authentication
    endpoints and validates the request body using the `validate_input` function.
    If validation fails, it returns a 400 response. Otherwise, the request
    proceeds to the next middleware or endpoint.

    Attributes:
        url_list (list[str]): List of endpoints that require input validation.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Intercept incoming requests and validate input for POST endpoints.

        Args:
            request (Request): The incoming HTTP request.
            call_next (Callable): The next middleware or endpoint in the stack.

        Returns:
            Response: If input is valid, returns the response from the next
            middleware/endpoint. If invalid, returns a JSONResponse with
            an error message and status code 400.
        """
        logger.info(f"Input validation middleware called for {request.url.path}")

        if request.method == "POST" and request.url.path in url_list:
            logger.info(f"Input validation middleware passed for {request.url.path}")
            try:
                body = await request.json()
                validated_input = await validate_input(body)
                if validated_input is None:
                    return JSONResponse(
                        status_code=400, content={"error": "Invalid input"}
                    )
                return await call_next(request)
            except Exception as e:
                return JSONResponse(status_code=400, content={"error": str(e)})

        return await call_next(request)
