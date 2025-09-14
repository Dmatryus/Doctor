"""
Preview API endpoints - placeholder
"""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/{file_id}")
async def get_preview(file_id: str):
    """Get file preview endpoint - placeholder"""
    raise HTTPException(status_code=501, detail="Preview endpoint not implemented yet")