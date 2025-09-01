import logging
from typing import Dict

from fastapi import Request

logger = logging.getLogger(__name__)


async def extract_info(request: Request) -> Dict:
    """Extract device information from request"""
    try:
        user_agent = request.headers.get("User-Agent", "Unknown")
        accept_language = request.headers.get("Accept-Language", "")

        if user_agent is None:
            user_agent = "Unknown"
        if accept_language is None:
            accept_language = ""

        # Get IP with fallback
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for is None:
            x_forwarded_for = request.client.host if request.client else "Unknown"

        device_info = {
            "user_agent": user_agent,
            "accept_language": accept_language,
            "x_forwarded_for": x_forwarded_for,
        }

        if user_agent is None or accept_language is None:
            logger.info(f"Suspected request: ", device_info.get("x_forwarded_for"))


      
        return device_info

    except Exception as e:
        logger.error(f"Failed to extract device info: {str(e)}")
        return {
            "user_agent": "Unknown",
            "accept_language": "",
            "x_forwarded_for": "Unknown",
        }
