from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from service.logs.logger import logger

router = APIRouter()


@router.get("/")
async def welcome():
    logger.info(f"Welcome endpoint called")
    return RedirectResponse("/api/v1/simple_auth/")


@router.get("/test-coverage")
async def test_coverage():
    logger.info(f"Test coverage endpoint called")
    return {"message": "Test coverage"}
