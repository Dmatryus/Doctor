"""
Conversion API endpoints - placeholder
"""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/")
async def convert_document():
    """Convert document endpoint - placeholder"""
    raise HTTPException(status_code=501, detail="Convert endpoint not implemented yet")


@router.get("/formats")
async def get_formats():
    """Get supported formats endpoint - placeholder"""
    raise HTTPException(status_code=501, detail="Get formats endpoint not implemented yet")


@router.get("/themes")
async def get_themes():
    """Get available themes endpoint - placeholder"""
    raise HTTPException(status_code=501, detail="Get themes endpoint not implemented yet")


@router.get("/status/{task_id}")
async def conversion_status(task_id: str):
    """Conversion status endpoint - placeholder"""
    raise HTTPException(status_code=501, detail="Conversion status endpoint not implemented yet")