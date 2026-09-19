from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from src.backend.deps import get_db
from src.backend.crm import service
from src.backend.crm import repository
from src.backend.crm.websocket import manager

router = APIRouter()

@router.get("/leads")
async def get_leads(db: AsyncSession = Depends(get_db)):
    """Fetch the sales queue."""
    leads = await service.get_all_leads(db)
    return leads

@router.get("/session/{session_id}")
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch a single customer workspace."""
    try:
        workspace = await service.get_workspace(db, session_id)
        return workspace
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")

@router.post("/session/{session_id}/accept")
async def accept_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Move status from WAITING to LIVE."""
    await repository.update_status(db, session_id, "LIVE")
    return {"status": "success", "session_id": session_id}

@router.post("/session/{session_id}/complete")
async def complete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Move status from LIVE to COMPLETED."""
    await repository.update_status(db, session_id, "COMPLETED")
    return {"status": "success", "session_id": session_id}

@router.websocket("/live/{session_id}")
async def crm_live_websocket(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        while True:
            # CRM Dashboard only receives data, it doesn't send anything.
            # But we must await receive_text() to keep connection open and detect disconnects.
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
