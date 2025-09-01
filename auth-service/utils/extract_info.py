from typing import Dict

from fastapi import Request
from service.logs.logger import logger


async def extract_info(request: Request) -> Dict:
    """Extract device information from request"""
    try:
        user_agent = request.headers.get("User-Agent", "Unknown")
        accept_language = request.headers.get("Accept-Language", "")

        # Get IP with fallback
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if not x_forwarded_for:
            x_forwarded_for = request.client.host if request.client else "Unknown"

        device_info = {
            "user_agent": user_agent,
            "accept_language": accept_language,
            "x_forwarded_for": x_forwarded_for,
        }

        logger.info("Device info extracted")
        return device_info

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(f"Failed to extract device info: {str(e)}")
        return {
            "user_agent": "Unknown",
            "accept_language": "",
            "x_forwarded_for": "Unknown",
        }
