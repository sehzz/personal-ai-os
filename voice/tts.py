import subprocess
import os
import tempfile

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
        os.startfile(output_path)



if __name__ == "__main__":
    tts_service = TTSService()
    tts_service.speak("Hello, this is a test of the text to speech service.")