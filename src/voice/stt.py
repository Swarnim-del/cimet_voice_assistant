from openai import AsyncOpenAI
import os

class WhisperSTT:
    def __init__(self):
        # We assume OPENAI_API_KEY is in the environment
        self.client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    async def transcribe(self, audio_filepath: str) -> str:
        """
        Transcribe an audio file using OpenAI's Whisper API.
        """
        if not os.environ.get("OPENAI_API_KEY"):
            print("[MOCK STT] OPENAI_API_KEY not found. Returning mock transcript.")
            return "Yes, I am moving into a new place next week."
            
        with open(audio_filepath, "rb") as audio_file:
            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text
