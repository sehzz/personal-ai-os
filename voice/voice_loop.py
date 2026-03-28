from shared.utils import build_prompt
from shared.memory_service import MemoryService
from shared.ollama_service import OllamaService
from voice.stt import STTService, record_until_silent
from voice.tts import TTSService

class VoiceLoop:
    def __init__(self, ollama_service: OllamaService, memory_service: MemoryService, stt_service: STTService, tts_service: TTSService):
        self.ollama = ollama_service
        self.memory = memory_service
        self.stt = stt_service
        self.tts = tts_service

    def run_once(self) -> None:
        audio_path = record_until_silent()
        text = self.stt.transcribe(audio_path)
        memory = self.memory.retrieve(text)
        prompt = build_prompt(text, memory)
        response = self.ollama.generate(prompt)

        self.tts.speak(response)
        self.memory.store(f"User: {text}\nAssistant: {response}")