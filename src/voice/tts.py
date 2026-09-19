import os
import soundfile as sf
import numpy as np
from openai import AsyncOpenAI

class OpenAITTS:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    async def synthesize(self, text: str, output_filepath: str):
        """
        Synthesize speech from text using OpenAI TTS and save to output_filepath.
        """
        if not os.environ.get("OPENAI_API_KEY"):
            print(f"[MOCK TTS] Synthesizing text to {output_filepath}: {text}")
            sample_rate = 24000
            samples = np.zeros((sample_rate,))
            sf.write(output_filepath, samples, sample_rate)
            return output_filepath
            
        print(f"[OpenAI TTS] Generating audio for: {text}")
        response = await self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        response.stream_to_file(output_filepath)
        return output_filepath
