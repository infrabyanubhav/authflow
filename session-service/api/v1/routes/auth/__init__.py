from config.init_config import auth_config
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
import logging
from datetime import datetime


logger = logging.getLogger(__name__)

router = APIRouter()

"""
Forward to auth route.

This route redirects to the authentication URL.
"""


@router.get("/")
async def forward_to_auth(request: Request):
    """
    Forward to auth route.

    This route redirects to the authentication URL.
    """
    if request.headers.get("x_forwarded_for") is None:
        
        logger.info(f"Forwarding request to {auth_config.get('auth_url')} from {request.client.host}", "at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    else:

        logger.info(f"Forwarding request to {auth_config.get('auth_url')} from {request.headers.get('x_forwarded_for')}", "at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    return RedirectResponse(url=auth_config.get("auth_url"), status_code=302)

