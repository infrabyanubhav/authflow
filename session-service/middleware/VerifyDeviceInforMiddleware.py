import logging
from datetime import datetime
from config.init_config import auth_config, excluded_paths
from service.security.core.fingerprint import generate_fingerprint
from service.session.features.fetch import FetchSession
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from utils.extract_info import extract_info
from time import sleep
logger = logging.getLogger(__name__)

"""
VerifyDeviceInfoMiddleware class for verifying device information in the request.

This middleware provides comprehensive security by:
- Validating session cookies on each request
- Generating and comparing device fingerprints
- Preventing session hijacking and device switching attacks
- Comprehensive logging for security monitoring

"""


class VerifyDeviceInfoMiddleware(BaseHTTPMiddleware):
    """
    VerifyDeviceInfoMiddleware class for verifying device information in the request.

    This middleware checks if a session ID is present in the request cookies.
    If not, it redirects to the authentication URL.

    Attributes:
        request (Request): The incoming request
        call_next (Callable): The next middleware function to call
    """

    async def dispatch(self, request: Request, call_next):
        """Validate session and device fingerprint"""
        try:
            # Check session cookie

            logger.info(f"Request path: {request.url.path} from {request.client.host} {request.cookies.items()} ")

            if request.url.path in excluded_paths:
                return await call_next(request)
        
            session_id = request.cookies.get("session_id")
            logger.info(f"Session ID: {session_id}")
            if session_id is None:
                logger.warning(f"No session cookie: {request.url.path}")
                logger.info(f"Forwarding request to {auth_config.get('auth_url')} from {request.client.host}", "at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))      
                return RedirectResponse(auth_config["auth_url"], status_code=302)

            # Get device info and fingerprint
            info = await extract_info(request=request)
            logger.info(f"Info: {info}")
            fingerprint = await generate_fingerprint(info)
            logger.info(f"Fingerprint: {fingerprint}")

            # Check session exists
            verify_session = FetchSession()
            session_data = await verify_session.fetch_session(session_id)
            logger.info(f"Session data: {session_data}")

            if session_data is None or isinstance(session_data, str):
                logger.warning(f"Invalid session: {session_id}")
                return RedirectResponse(auth_config["auth_url"], status_code=302)

            # Check fingerprint match
            if session_data.get("fingerprint") != fingerprint:
                logger.warning(f"Fingerprint mismatch: {session_id}")
                return RedirectResponse(auth_config["auth_url"], status_code=302)

            logger.info(f"Session verified: {session_id}")
            return await call_next(request)

        except Exception as e:
            logger.error(f"Middleware error: {str(e)}")
            return RedirectResponse(auth_config["auth_url"], status_code=302)
