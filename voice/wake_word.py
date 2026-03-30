from openwakeword.model import Model
import pyaudio
import numpy as np
import threading
import time
from lib.log import logger
from voice.state_machine import State

log = logger.get_logger()

class WakeWordService:

    def __init__(self, on_detected: callable, machine_state):
        self.on_detected = on_detected
        self.model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
        self.audio = pyaudio.PyAudio()
        self.running = True
        self.timestamp = 0
        self.machine_state = machine_state
        

    def start(self):
        stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1280)
        log.info("Listening for wake word... say 'Hey Jarvis'")
        thread = threading.Thread(target=self._listen, args=(stream,), daemon=True)
        thread.start()

    def _listen(self, stream):
        while self.running:
            audio_chunk = np.frombuffer(stream.read(1280), dtype=np.int16)
            prediction = self.model.predict(audio_chunk)
            score = prediction.get("hey_jarvis", 0)
            
            time_since_sleeping = time.time() - self.machine_state.last_sleeping_at
            
            if score > 0.5 and time.time() - self.timestamp > 15 and time_since_sleeping > 10:
                if self.machine_state.current_state == State.SLEEPING:
                    log.info(f"Wake word detected! Score: {score:.2f}")
                    self.timestamp = time.time()
                    self.on_detected()

    

    def stop(self):
        self.running = False
        self.audio.terminate()



if __name__ == "__main__":
    
    
    def on_wake():
        print("Callback fired - wake word heard!")
    
    service = WakeWordService(on_detected=on_wake)
    service.start()
    print(service.timestamp)
    
    time.sleep(30)
    service.stop()
