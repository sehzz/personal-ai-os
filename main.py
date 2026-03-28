from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from shared.embedding_service import EmbeddingService
from shared.models import ChatRequest
from shared.ollama_service import OllamaService


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    app.state.ollama = OllamaService()
    app.state.embedding = EmbeddingService()
    yield

app = FastAPI(
    title="Personal AI OS",
    lifespan=lifespan
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(request: ChatRequest, req: Request):
    ollama = req.app.state.ollama
    response = ollama.generate_stream(request.message)

    return StreamingResponse(response, media_type="text/plain")

