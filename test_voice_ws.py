import asyncio
import websockets
import os
import wave
import struct
import numpy as np

async def test_voice_ws():
    uri = "ws://localhost:8000/ws/voice/test_ws_session"
    print(f"Connecting to {uri}...")
    
    # 1. Create a dummy .wav file to simulate a customer speaking
    dummy_wav = "dummy_customer_audio.wav"
    sample_rate = 16000
    # 1 second of silence
    samples = np.zeros(sample_rate, dtype=np.int16) 
    
    with wave.open(dummy_wav, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for s in samples:
            wav_file.writeframes(struct.pack('<h', s))
            
    print(f"Created dummy audio chunk: {dummy_wav}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            
            # 2. Send the audio
            with open(dummy_wav, "rb") as f:
                audio_data = f.read()
                
            print(f"Sending {len(audio_data)} bytes to Voice Service...")
            await websocket.send(audio_data)
            
            # 3. Receive the response audio
            print("Waiting for TTS audio response...")
            response_data = await websocket.recv()
            
            print(f"Received {len(response_data)} bytes of TTS audio back from AI!")
            
            # Save the response
            output_wav = "ai_response_audio.wav"
            with open(output_wav, "wb") as f:
                f.write(response_data)
            print(f"Saved AI response audio to {output_wav}")
            
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Make sure your Docker container is running and rebuilt!")

if __name__ == "__main__":
    asyncio.run(test_voice_ws())

    
