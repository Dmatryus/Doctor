"""
Download API endpoints - placeholder
"""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/{file_id}")
async def download_file(file_id: str):
    """Download file endpoint - placeholder"""
    raise HTTPException(status_code=501, detail="Download endpoint not implemented yet")