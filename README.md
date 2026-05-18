# Personal AI OS

A self-hosted, privacy-first Personal Life Operating System built on a 
multi-agent architecture. Specialised AI managers each own a domain of 
your life, coordinated by a central Admin that is the only thing you 
ever talk to.

> Everything runs locally. No data leaves your machine except Google 
> services (Gmail, Calendar) which are unavoidable.

---

## Architecture
```
You (Voice / Chat)
       ↓
Admin Orchestrator
       ↓
┌──────────────────────────────────┐
│  Life Admin │ Finance │ Content  │
│        Relationships             │
└──────────────────────────────────┘
       ↓
Skills + Tools (n8n, Gmail, Notion, Calendar)
       ↓
Shared Memory (pgvector + Supabase)
```

---

## Tech Stack

| Layer         | Technology                |
|---------------|---------------------------|
| LLM           | Ollama + mistral:7b       |
| Embeddings    | Ollama + nomic-embed-text |
| API           | FastAPI                   |
| Memory / RAG  | Supabase + pgvector       |
| Orchestration | n8n                       |
| Alerts        | Telegram Bot API          |
| Voice STT     | faster-whisper, webrtcvad-wheels, sounddevice               |
| Voice TTS     | piper-tts                 |

---

## Project Status

| Phase | Description                 | Status      |
|-------|-----------------------------|-------------|
| 0     | Foundation & Infrastructure | ✅ Complete |
| 1     | LLM Core + Text Chat        | ✅ Complete |
| 2     | Long-Term Memory (RAG)      | ✅ Complete |
| 3     | Voice I/O                   | ✅ Complete |
| 4     | Wake Word                   | ✅ Complete |
| 5     | Multi-Agent Architecture    | ✅ Complete |
| 6     | Skills                      | ✅ Complete  |
| 7     | Autonomous Scheduling       | 🔄 Up next  |
| 8     | Voice Identity Recognition  | ⏳ Planned  |
| 9     | Polish + Portfolio          | ⏳ Planned  |

---

## Setup

### Prerequisites
- Python 3.11+
- Ollama installed natively
- Supabase project with pgvector enabled

### Installation
```bash
git clone https://github.com/sehzz/personal-ai-os.git
cd personal-ai-os
pip install -r requirements.txt
```

### Pull models
```bash
ollama pull mistral:7b
ollama pull nomic-embed-text
```

### Run migrations

Copy `infra/migrations/001_initial_schema.sql` into your Supabase 
SQL Editor and run it.

### Start the server
```bash
uvicorn main:app --reload
```

---

## API

| Method | Endpoint  | Description                  |
|--------|-----------|------------------------------|
| GET    | `/health` | Health check                 |
| POST   | `/chat`   | Chat with streaming response |
| POST   | `/voice`  | triggers one full voice turn |

### Example
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What do you remember about me?"}'
```

---

## Project Structure
```
personal-ai-os/
├── admin/              # Orchestrator, intent classifier, health monitor
├── managers/           # Life Admin, Finance, Content, Relationships
├── shared/             # Config, DB, embedding, memory, models
├── skills/             # Core and domain-specific skills
├── voice/              # Wake word, STT, TTS
├── infra/              # Docker, migrations, n8n workflows
├── tests/              # Unit and integration tests
├── main.py             # FastAPI entry point
└── requirements.txt
```

---
