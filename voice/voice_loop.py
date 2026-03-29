import time

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
        total_start = time.time()

        stt_start = time.time()
        audio_path = record_until_silent()
        text = self.stt.transcribe(audio_path)
        print(f"STT:    {time.time() - stt_start:.2f}s  -> '{text}'")

        mem_start = time.time()
        memory = self.memory.retrieve(text, match_count=3)
        prompt = build_prompt(text, memory, mode="voice")
        print(f"Memory: {time.time() - mem_start:.2f}s")

        llm_start = time.time()
        response = self.ollama.generate(prompt)
        print(f"LLM:    {time.time() - llm_start:.2f}s")

        tts_start = time.time()
        self.tts.speak(response)
        print(f"TTS:    {time.time() - tts_start:.2f}s")


        self.memory.store(f"User: {text}\nAssistant: {response}")
        print(f"Total:  {time.time() - total_start:.2f}s")