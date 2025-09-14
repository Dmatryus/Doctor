"""
WebSocket status endpoints - placeholder
"""

from fastapi import APIRouter, WebSocket, HTTPException

router = APIRouter()


@router.websocket("/status/{task_id}")
async def websocket_status(websocket: WebSocket, task_id: str):
    """WebSocket status endpoint - placeholder"""
    await websocket.accept()
    await websocket.send_json({
        "error": "WebSocket status endpoint not implemented yet",
        "task_id": task_id
    })
    await websocket.close()