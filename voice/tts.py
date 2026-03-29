import subprocess
import os
import tempfile
import time

from lib.environment import get_conf_for

class TTSService:
    def __init__(self):
        self.conf = get_conf_for("piper")
        self.piper_binary_path = self.conf.get("binary_path")
        self.piper_model_path = self.conf.get("model_path")
    
    def speak(self, text: str) -> None:

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            output_path = f.name
        subprocess.run(
            [self.piper_binary_path, "--model", self.piper_model_path, "--output_file", output_path],
            input=text.encode(),
            check=True
        )
        time.sleep(0.1)
        os.startfile(output_path)



if __name__ == "__main__":
    tts_service = TTSService()
    tts_service.speak("It was a cold, fog-shrouded morning in London when I found Sherlock Holmes standing by the window of our rooms in Baker Street. He had been silent for hours, his thin, eagle-like nose pressed almost against the glass as he watched the yellow vapor swirl around the gas lamps below. To the casual observer, he looked like a man lost in thought. To me, he looked like a predator waiting for the slightest ripple in the tall grass.")