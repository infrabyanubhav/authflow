from config.init_config import backend_config
import logging
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

logger = logging.getLogger(__name__)

router = APIRouter()

"""
Forward to backend route.

This route redirects to the authentication URL.
"""


@router.get("/")
async def forward_to_backend():
    """
    Forward to backend route.

    This route redirects to the authentication URL.
    """
    logger.info("Forwarding to backend route")
    return RedirectResponse(url=backend_config.get("backend_url"))
