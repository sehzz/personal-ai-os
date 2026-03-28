from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from shared.embedding_service import EmbeddingService
from shared.memory_service import MemoryService
from shared.models import ChatRequest
from shared.ollama_service import OllamaService


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    app.state.ollama = OllamaService()
    app.state.embedding = EmbeddingService()
    app.state.memory = MemoryService()
    yield

app = FastAPI(
    title="Personal AI OS",
    lifespan=lifespan
)

def build_prompt(message: str, memories: list[str]):
    if not memories:
        return message
    
    prompt = "You are a helpful assistant. Use the following memories to answer the question.\n\n"
    for i, memory in enumerate(memories):
        prompt += f"Memory {i+1}: {memory}\n"
    prompt += f"User message: {message}\n"

    return prompt

def stream_and_store(generator, memory: MemoryService, user_message: str):
    full_response = ""
    for chunk in generator:
        full_response += chunk
        yield chunk
    # streaming is done — now store the exchange
    memory.store(f"User: {user_message}\nAssistant: {full_response}")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(request: ChatRequest, req: Request):
    ollama = req.app.state.ollama
    memory = req.app.state.memory.retrieve(request.message)
    prompt = build_prompt(request.message, memory)


    response = ollama.generate_stream(prompt)
    wrapped = stream_and_store(response, req.app.state.memory, request.message)
    return StreamingResponse(wrapped, media_type="text/plain")