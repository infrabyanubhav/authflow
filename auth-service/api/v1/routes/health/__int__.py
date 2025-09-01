from datetime import datetime

from fastapi import APIRouter
from service.logs.logger import logger

router = APIRouter()


@router.get("/health")
def health():
    logger.info("Health endpoint called", {"version": "1.0.0", "timestamp": datetime.now().isoformat(), "status": "ok", "message": "Auth service is running"})
    return {
        "status": "ok", 
        "message": "Auth service is running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }
    