import hashlib
import logging
from typing import Dict

logger = logging.getLogger(__name__)


async def generate_fingerprint(info: Dict) -> str:
    """Generate device fingerprint using SHA-256"""
    try:
        ip = info.get("x_forwarded_for", "Unknown")
        user_agent = info.get("user_agent", "Unknown")
        accept_language = info.get("accept_language", "")

        raw = f"{ip}|{user_agent}|{accept_language}"
        fingerprint = hashlib.sha256(raw.encode("utf-8")).hexdigest()

        logger.debug(f"Fingerprint generated: {fingerprint[:16]}...")
        return fingerprint

    except Exception as e:
        logger.error(f"Failed to generate fingerprint: {str(e)}")
        raise
