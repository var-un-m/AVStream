# client.py
import asyncio
import websockets
import pyaudio
import numpy as np
import cv2
import json
import base64
import multiprocessing as mp
from datetime import datetime, timedelta


class AudioStreamClient:
    def __init__(self):
        
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.p.get_format_from_width(4),
                            channels=1,
                            rate=16000,
                            output=True)       
       
    async def stream_audio(self, server_ip):
        uri = f"ws://{server_ip}" 
        async with websockets.connect(uri) as websocket:
            while True:
                try:
                    response = json.loads(await websocket.recv())
                
                    frame_data = base64.b64decode(response['frame'])
                    frame_array = np.frombuffer(frame_data, dtype=np.uint8).reshape(response['shape'])
                    cv2.imshow('Audio Visualization', frame_array)

                    audio_data = base64.b64decode(response['audio'])
                    self.stream.write(audio_data)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                except Exception as e:
                    print(f'Error: {e}')
    
   
    def run(self, server_ip):
        asyncio.get_event_loop().run_until_complete(self.stream_audio(server_ip))
   
    def cleanup(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    import sys
    server_ip = sys.argv[1] # TODO: take from argparse
    client = AudioStreamClient()
    try:
        client.run(server_ip)
    finally:
        client.cleanup()