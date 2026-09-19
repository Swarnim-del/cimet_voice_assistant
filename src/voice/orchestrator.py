import uuid
import os
import tempfile
from src.voice.stt import WhisperSTT
from src.voice.tts import OpenAITTS
from src.backend.graph.builder import app as graph_app
from src.backend.schemas.state import CallState
from src.logger import logger
from src.backend.repo.database import db
from src.backend.repo.models import CallSession, ConversationMessage, Customer, JourneyData
from src.backend.crm.websocket import manager

class VoiceOrchestrator:
    def __init__(self):
        self.stt = WhisperSTT()
        self.tts = OpenAITTS()

    async def handle_audio(self, audio_filepath: str, session_id: str, state: CallState) -> tuple[str, CallState]:
        """
        Processes one turn of the conversation:
        1. Audio -> Transcript (Whisper)
        2. Transcript -> LangGraph State Update -> AI Response Text
        3. AI Response Text -> Audio (Kokoro)
        Returns the path to the generated TTS audio file and the updated state.
        """
        logger.info(f"[{session_id}] Processing incoming audio from {audio_filepath}")
        
        # 1. Transcribe Audio (Voice Service)
        transcript = await self.stt.transcribe(audio_filepath)
        logger.info(f"[{session_id}] Extracted Transcript: {transcript}")
        
        # 2. Persist Customer Message
        async with db.async_session_maker() as db_session:
            call_sess = await db_session.get(CallSession, session_id)
            if not call_sess:
                customer = await db_session.get(Customer, "L_WS_100")
                if not customer:
                    customer = Customer(id="L_WS_100", lead_id="LEAD_TEST", name="John Doe", phone="555")
                    db_session.add(customer)
                call_sess = CallSession(session_id=session_id, customer_id="L_WS_100")
                db_session.add(call_sess)
            
            user_msg = ConversationMessage(session_id=session_id, speaker="customer", text=transcript)
            db_session.add(user_msg)
            await db_session.commit()
            
        # Broadcast to CRM
        await manager.broadcast(session_id, {
            "type": "transcript",
            "speaker": "customer",
            "text": transcript
        })
            
        # 3. Add to state and invoke Graph (Conversation Service)
        if "messages" not in state:
            state["messages"] = []
            
        state["messages"].append({"role": "user", "content": transcript})
        
        logger.info(f"[{session_id}] Invoking LangGraph Conversation Service...")
        updated_state = graph_app.invoke(state)
        
        ai_response = updated_state["messages"][-1]["content"] if updated_state.get("messages") else "I'm sorry, I didn't get that."
        logger.info(f"[{session_id}] AI Text Response: {ai_response}")
        
        # 4. Persist AI Message and Update Session
        async with db.async_session_maker() as db_session:
            ai_msg = ConversationMessage(session_id=session_id, speaker="ai", text=ai_response)
            db_session.add(ai_msg)
            
            call_sess = await db_session.get(CallSession, session_id)
            if call_sess:
                call_sess.current_node = updated_state.get("current_node", call_sess.current_node)
                if call_sess.current_node == "handoff_node":
                    call_sess.status = "LIVE"
                    call_sess.escalation_reason = updated_state.get("handoff_reason", "Customer requested handoff.")
            
            # Update JourneyData
            fields = updated_state.get("extracted_fields", {})
            if fields:
                journey = await db_session.get(JourneyData, session_id)
                if not journey:
                    journey = JourneyData(session_id=session_id)
                    db_session.add(journey)
                if "moving" in fields: journey.moving = fields["moving"]
                if "address" in fields: journey.address = fields["address"]
                if "fuel_type" in fields: journey.fuel_type = fields["fuel_type"]
                if "solar" in fields: journey.solar = fields["solar"]
                if "life_support" in fields: journey.life_support = fields["life_support"]
                if "concession" in fields: journey.concession = fields["concession"]
                
            await db_session.commit()
            
        # Broadcast AI Transcript to CRM
        await manager.broadcast(session_id, {
            "type": "transcript",
            "speaker": "ai",
            "text": ai_response
        })
        
        # Broadcast Journey Update to CRM
        await manager.broadcast(session_id, {
            "type": "journey_update",
            "fields": updated_state.get("extracted_fields", {})
        })
            
        # Write transcript state to JSON file in logs directory
        import json
        logs_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(logs_dir, exist_ok=True)
        with open(os.path.join(logs_dir, f"{session_id}.json"), "w") as f:
            json.dump(updated_state, f, indent=2)
        
        # 5. Synthesize Speech (Voice Service)
        temp_dir = tempfile.gettempdir()
        output_filepath = os.path.join(temp_dir, f"{session_id}_response_{uuid.uuid4().hex[:6]}.wav")
        
        await self.tts.synthesize(ai_response, output_filepath)
        logger.info(f"[{session_id}] Audio generated at {output_filepath}")
        
        return output_filepath, updated_state
