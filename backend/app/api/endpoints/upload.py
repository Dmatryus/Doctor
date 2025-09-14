"""
Upload API endpoints - placeholder
"""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/file")
async def upload_file():
    """Upload file endpoint - placeholder"""
    raise HTTPException(status_code=501, detail="Upload file endpoint not implemented yet")


@router.post("/text")
async def upload_text():
    """Upload text endpoint - placeholder"""
    raise HTTPException(status_code=501, detail="Upload text endpoint not implemented yet")


@router.post("/url")
async def upload_url():
    """Upload from URL endpoint - placeholder"""
    raise HTTPException(status_code=501, detail="Upload URL endpoint not implemented yet")


@router.get("/status/{task_id}")
async def upload_status(task_id: str):
    """Upload status endpoint - placeholder"""
    raise HTTPException(status_code=501, detail="Upload status endpoint not implemented yet")