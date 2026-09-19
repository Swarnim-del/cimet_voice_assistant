import os
import soundfile as sf
import numpy as np
try:
    from kokoro_onnx import Kokoro
except ImportError:
    Kokoro = None

class KokoroTTS:
    def __init__(self, model_path="kokoro-v0_19.onnx", voices_path="voices.bin"):
        self.enabled = False
        if Kokoro is not None and os.path.exists(model_path) and os.path.exists(voices_path):
            self.kokoro = Kokoro(model_path, voices_path)
            self.enabled = True
        else:
            print("[WARNING] Kokoro TTS not fully initialized. Missing ONNX model/voices. Using mock fallback.")

    async def synthesize(self, text: str, output_filepath: str):
        """
        Synthesize speech from text and save to output_filepath.
        """
        if self.enabled:
            # Generate speech
            samples, sample_rate = self.kokoro.create(text, voice="af_sarah", speed=1.0, lang="en-us")
            sf.write(output_filepath, samples, sample_rate)
            return output_filepath
            
        # Fallback mock if weights aren't downloaded
        print(f"[MOCK TTS] Synthesizing text to {output_filepath}: {text}")
        # Create a dummy silent wav file (1 second at 24kHz)
        sample_rate = 24000
        samples = np.zeros((sample_rate,))
        sf.write(output_filepath, samples, sample_rate)
        return output_filepath
