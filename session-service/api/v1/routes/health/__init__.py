from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

"""
Health check route.

This route returns a simple health check response.
"""


@router.get("/")
async def health():
    return JSONResponse(content={"status": "ok"}, status_code=200)
