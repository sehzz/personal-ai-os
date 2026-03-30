import time

from shared.utils import build_prompt
from shared.memory_service import MemoryService
from shared.ollama_service import OllamaService
from voice.state_machine import State, StateMachine
from voice.stt import STTService, record_until_silent
from voice.tts import TTSService
from lib.log import logger

log = logger.get_logger()


class VoiceLoop:
    def __init__(self, ollama_service: OllamaService, memory_service: MemoryService, stt_service: STTService, tts_service: TTSService, machine_state: StateMachine):
        self.ollama = ollama_service
        self.memory = memory_service
        self.stt = stt_service
        self.tts = tts_service
        self.machine_state = machine_state

    def run_once(self) -> None:
        self.machine_state.transition(State.LISTENING)
        total_start = time.time()

        stt_start = time.time()
        audio_path = record_until_silent()
        text = self.stt.transcribe(audio_path)
        log.info(f"STT:    {time.time() - stt_start:.2f}s  -> '{text}'")
        if not text or len(text.strip()) < 3:
            log.info("Empty transcription — returning to SLEEPING")
            self.machine_state.transition(State.SLEEPING)
            return

        mem_start = time.time()
        memory = self.memory.retrieve(text, match_count=3)
        prompt = build_prompt(text, memory, mode="voice")
        log.info(f"Memory: {time.time() - mem_start:.2f}s")

        self.machine_state.transition(State.PROCESSING)
        llm_start = time.time()
        response = self.ollama.generate(prompt)
        log.info(f"LLM:    {time.time() - llm_start:.2f}s")

        self.machine_state.transition(State.SPEAKING)
        tts_start = time.time()
        self.tts.speak(response)
        log.info("Sleep time starting...")
        time.sleep(3)
        log.info("Sleep time completed.")
        log.info(f"TTS:    {time.time() - tts_start:.2f}s")


        self.memory.store(f"User: {text}\nAssistant: {response}")
        log.info(f"Total:  {time.time() - total_start:.2f}s")
        self.machine_state.transition(State.SLEEPING)
