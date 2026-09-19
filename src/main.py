import os
import tempfile
import aiofiles
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.config import settings
from src.logger import logger
from src.backend.deps import get_db
from src.backend.graph.builder import app as graph_app
from pydantic import BaseModel
from typing import Dict, Any, List
from src.voice.orchestrator import VoiceOrchestrator
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.future import select
from sqlalchemy import desc
from src.backend.repo.models import CallSession, ConversationMessage

class ChatRequest(BaseModel):
    session_id: str
    message: str

app = FastAPI(
    title="CIMET Voice Assistant API",
    description="Backend for the CIMET Hackathon AI voice assistant",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Voice Orchestrator
voice_orchestrator = VoiceOrchestrator()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up CIMET Voice Assistant API")

# Mount the static directory for the browser UI
import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def get_ui():
    return FileResponse(os.path.join(static_dir, "index.html"))

# ---------------------------------------------------------
# Voice Service API (Audio Only)
# ---------------------------------------------------------
@app.websocket("/ws/voice/{session_id}")
async def voice_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for the Voice Service.
    Client sends raw audio bytes.
    Server processes Audio -> STT -> LangGraph -> TTS -> Audio bytes.
    """
    await websocket.accept()
    logger.info(f"WebSocket connected for session: {session_id}")
    
    # Initialize state
    state = {
        "session_id": session_id,
        "lead_id": "L_WS_100",
        "messages": [],
        "extracted_fields": {},
        "current_node": "greeting_node",
        "retry_count": 0,
        "sentiment": "neutral",
        "needs_handoff": False,
        "handoff_reason": ""
    }
    
    try:
        while True:
            # 1. Receive audio chunk from client
            data = await websocket.receive_bytes()
            logger.info(f"Received {len(data)} bytes of audio for session {session_id}")
            
            # Save bytes to a temp file for Whisper
            temp_dir = tempfile.gettempdir()
            input_audio_path = os.path.join(temp_dir, f"{session_id}_input.wav")
            async with aiofiles.open(input_audio_path, 'wb') as out_file:
                await out_file.write(data)
                
            # 2. Orchestrate: Audio -> STT -> Graph -> TTS -> Audio
            output_audio_path, state = await voice_orchestrator.handle_audio(input_audio_path, session_id, state)
            
            # 3. Send TTS audio back to client
            async with aiofiles.open(output_audio_path, 'rb') as in_file:
                out_data = await in_file.read()
                await websocket.send_bytes(out_data)
                
            logger.info(f"Sent {len(out_data)} bytes of TTS audio back to client.")
            
            # Cleanup
            if os.path.exists(input_audio_path):
                os.remove(input_audio_path)
            if os.path.exists(output_audio_path):
                os.remove(output_audio_path)
                
            if state.get("current_node") in ["handoff_node", "end"]:
                await websocket.close()
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass
    finally:
        import json
        logs_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(logs_dir, exist_ok=True)
        log_path = os.path.join(logs_dir, f"{session_id}.json")
        try:
            with open(log_path, "w") as f:
                json.dump(state, f, indent=2)
            logger.info(f"Saved call log to {log_path}")
        except Exception as e:
            logger.error(f"Failed to save call log: {e}")

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok", "message": "CIMET Voice Assistant is running"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    logger.info(f"Received message for session {request.session_id}")
    
    # 1. Fetch existing state from DB (mocked for now, assuming starting fresh if not provided)
    # Ideally, we would load `CallState` from Postgres here based on session_id.
    
    # For now, we will just initialize a fresh state or pass the message in
    # In a real scenario, we use LangGraph's checkpointer or our DB to resume.
    initial_state = {
        "session_id": request.session_id,
        "lead_id": "L12345",
        "messages": [{"role": "user", "content": request.message}],
        "extracted_fields": {},
        "current_node": "greeting_node",
        "retry_count": 0,
        "sentiment": "neutral",
        "needs_handoff": False,
        "handoff_reason": ""
    }
    
    # Run the graph
    # (Since we haven't wired up Postgres checkpointer yet, this runs stateless per request for testing)
    result_state = graph_app.invoke(initial_state)
    
    # Get the last AI message
    last_message = result_state["messages"][-1]["content"] if result_state.get("messages") else "No response."
    
    return {
        "session_id": request.session_id,
        "response": last_message,
        "current_node": result_state.get("current_node"),
        "extracted_fields": result_state.get("extracted_fields")
    }

# Example of using the db dependency
@app.get("/db-check")
async def db_check(db: AsyncSession = Depends(get_db)):
    logger.info("DB check endpoint called")
    return {"status": "ok", "db_url_configured": bool(settings.database_url)}

# ---------------------------------------------------------
# Logs API for Observability Dashboard
# ---------------------------------------------------------
@app.get("/api/logs/sessions")
async def get_sessions(db: AsyncSession = Depends(get_db)):
    stmt = select(CallSession).order_by(desc(CallSession.session_id))
    result = await db.execute(stmt)
    return result.scalars().all()

@app.get("/api/logs/sessions/{session_id}/messages")
async def get_messages(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ConversationMessage).where(ConversationMessage.session_id == session_id).order_by(ConversationMessage.id)
    result = await db.execute(stmt)
    return result.scalars().all()

from src.backend.crm.router import router as crm_router

app.include_router(crm_router, prefix="/api/crm", tags=["CRM"])
