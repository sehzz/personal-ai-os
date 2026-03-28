# Changelog

All notable changes to this project will be documented here.

---

## [Phase 3]
### Added
- `STTService` — transcribes audio to text via faster-whisper (base model, CPU)
- `record_until_silent()` — records mic input until 1.5 seconds of silence detected, saves to temp `.wav` file
- `TTSService` — converts text to speech via piper-tts and plays it locally
- `VoiceLoop` — orchestrates the full voice turn: record → transcribe → retrieve memory → LLM → speak → store
- `POST /voice` — endpoint that triggers one full voice turn

---

## [Phase 2]
### Added
- `EmbeddingService` — converts text to 768-dim vectors via nomic-embed-text (Ollama)
- `MemoryService` — stores and retrieves memories using pgvector cosine similarity
- `match_memories` Supabase RPC function for vector similarity search
- Memory injection into `/chat` — relevant memories retrieved and added to prompt
- Post-stream memory storage — full exchange stored after streaming completes

---

## [Phase 1]
### Added
- `OllamaService` — wraps Ollama REST API with `generate` and `generate_stream` methods
- `ChatRequest` Pydantic model for `/chat` endpoint
- `POST /chat` endpoint with streaming response via `StreamingResponse`
- `GET /health` endpoint
- FastAPI lifespan pattern for service initialisation

---

## [Phase 0]
### Added
- Project repository and folder structure
- Initial Supabase schema migration
- `shared_identity` seeded with base profile
- README and CHANGELOG
- Ollama installed with `mistral:7b` and `nomic-embed-text`