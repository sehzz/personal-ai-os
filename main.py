from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from lib.log import logger
from shared.embedding_service import EmbeddingService
from shared.memory_service import MemoryService
from shared.models import ChatRequest
from shared.ollama_service import OllamaService
from shared.utils import build_prompt
from voice.state_machine import State, StateMachine
from voice.stt import STTService
from voice.tts import TTSService
from voice.voice_loop import VoiceLoop
from voice.wake_word import WakeWordService
from managers.life_admin.manager import LifeAdminManager
from managers.finance.manager import FinanceManager
from managers.content.manager import ContentManager
from managers.relationship.manager import RelationshipManager
from admin.orchestrator import AdminOrchestrator
from admin.health_monitor import HealthMonitor


log = logger.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    app.state.ollama = OllamaService()
    app.state.embedding = EmbeddingService()
    app.state.memory = MemoryService()
    app.state.machine = StateMachine()
    app.state.voice_loop = VoiceLoop(
        ollama_service=app.state.ollama,
        memory_service=app.state.memory,
        stt_service=STTService(),
        tts_service=TTSService(),
        machine_state=app.state.machine
        )
    
    managers = {
    "life_admin": LifeAdminManager(),
    "finance": FinanceManager(),
    "content": ContentManager(),
    "relationships": RelationshipManager(),
    }

    app.state.admin = AdminOrchestrator(
        managers=managers,
        ollama=app.state.ollama,
        memory=app.state.memory
        )
    app.state.health_monitor = HealthMonitor(managers)
    app.state.health_monitor.check_all()
    
    def on_wake_word():
        if app.state.machine.current_state != State.SLEEPING:
            log.info(f"Wake word ignored — currently {app.state.machine.current_state.name}")
            return
        app.state.voice_loop.run_once()

    app.state.wake_word = WakeWordService(on_detected=on_wake_word, machine_state=app.state.machine)
    app.state.wake_word.start()
    yield

app = FastAPI(
    title="Personal AI OS",
    lifespan=lifespan
)

def stream_and_store(generator, memory: MemoryService, user_message: str):
    full_response = ""
    for chunk in generator:
        full_response += chunk
        yield chunk
    memory.store(f"User: {user_message}\nAssistant: {full_response}")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(request: ChatRequest, req: Request):

    response = req.app.state.admin.process(request.message)
    
    return response

@app.post("/voice")
def voice(req: Request):
    req.app.state.voice_loop.run_once()

    return {"status": "ok"}