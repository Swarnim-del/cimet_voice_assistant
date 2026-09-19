import uuid
import os
import tempfile
from src.voice.stt import WhisperSTT
from src.voice.tts import KokoroTTS
from src.backend.graph.builder import app as graph_app
from src.backend.schemas.state import CallState
from src.logger import logger

class VoiceOrchestrator:
    def __init__(self):
        self.stt = WhisperSTT()
        self.tts = KokoroTTS()

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
        
        # 2. Add to state and invoke Graph (Conversation Service)
        if "messages" not in state:
            state["messages"] = []
            
        state["messages"].append({"role": "user", "content": transcript})
        
        logger.info(f"[{session_id}] Invoking LangGraph Conversation Service...")
        updated_state = graph_app.invoke(state)
        
        ai_response = updated_state["messages"][-1]["content"] if updated_state.get("messages") else "I'm sorry, I didn't get that."
        logger.info(f"[{session_id}] AI Text Response: {ai_response}")
        
        # 3. Synthesize Speech (Voice Service)
        temp_dir = tempfile.gettempdir()
        output_filepath = os.path.join(temp_dir, f"{session_id}_response_{uuid.uuid4().hex[:6]}.wav")
        
        await self.tts.synthesize(ai_response, output_filepath)
        logger.info(f"[{session_id}] Audio generated at {output_filepath}")
        
        return output_filepath, updated_state
