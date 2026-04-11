# Personal AI OS — Development Log

## Phase 0: Project Foundation & Infrastructure

### What was built
I established the core environment and data layer for the OS. This phase focused on ensuring a robust, scalable foundation before layering on agent logic.

- **Repository & Structure**: Initialized GitHub repository with a folder structure covering 7 top-level directories (`admin/`, `managers/`, `shared/`, `skills/`, `voice/`, `infra/`, `tests/`).
- **Database Infrastructure**: Provisioned a Supabase instance and executed a comprehensive 25-table migration SQL script. Enabled the `pgvector` extension to support future vector embeddings.
- **Local LLM Setup**: Installed Ollama and pulled the `mistral:7b` (reasoning) and `nomic-embed-text` (embeddings) models to ensure complete local processing.

### Multi-agent architecture decision
The first major architectural decision was whether to use a single monolithic LLM for everything or a team of specialized agents. I opted for a multi-agent approach to optimize memory efficiency and performance. By assigning specific domains to individual agents, I reduce the total model context required for any single task, as each "manager" only handles relevant data.

```
Core architectural principles:
├── Multi-agent architecture (Society of Mind pattern)
├── Domain-isolated memory per manager
├── Skill-based permission system (least privilege)
├── Parallel execution with result synthesis
├── Three-tier alert system (low/medium/high)
├── Admin orchestration with full audit trail
└── Proactive + reactive modes
```

### Database design
The schema was designed around the principle of strict domain isolation:
- **Data Ownership**: Each manager owns its specific data; no manager reads another’s tables directly. All cross-communication is handled via the Admin orchestrator.
- **Centralized Shared Data**: Common entities live in shared tables to prevent data duplication.
- **Auditability**: Every record is timestamped to provide a clear timeline of when data was written, updated, or accessed.
- **Vector Support**: Each manager has access to isolated tables plus a `_memory_vectors` table to support Retrieval-Augmented Generation (RAG).

### Key design decisions

#### Supabase Cloud over Local Docker
To optimize local hardware resources for LLM inference, I chose the Supabase cloud-based PostgreSQL service rather than running a local PostgreSQL container via Docker. This ensures the CPU/GPU is dedicated to agent performance.

#### The 25-Table Schema
I implemented an isolated table structure so that managers maintain specialized knowledge bases. This "compartmentalization" ensures that the AI doesn't become overwhelmed with irrelevant context, as the Admin knows exactly which specific manager to query for a given topic.

#### Privacy-First & Local Inference
A core constraint of this project is data sovereignty. To ensure no sensitive data leaves the machine (excluding unavoidable integrations like Gmail or Google Calendar), I have ruled out cloud-based providers like OpenAI or Anthropic. All LLM reasoning, Speech-to-Text (STT), and Text-to-Speech (TTS) processes are executed locally.


## Phase 1: LLM Core + Text Chat

### What was built
In this phase, I transitioned from infrastructure to the functional core of the OS: the communication layer between the user and the LLM.
- **Core Services**: Developed `OllamaService`, a wrapper for the Ollama REST API supporting both standard and streaming generation.
- **API Foundation**: Built a FastAPI-based server utilizing the Lifespan pattern, ensuring the `OllamaService` is initialized once at startup and shared across the application state for resource efficiency.
- **Streaming Architecture**: Implemented real-time token streaming from day one to ensure a responsive UI, bypassing the latency of full-response generation.
- **Data Validation**: Created the `ChatRequest` Pydantic model to enforce strict typing for incoming user messages and session management.
- **Health Check**: Exposed a `GET /health` endpoint to verify service availability.

### How it works
The system follows a reactive flow to provide low-latency feedback:
1. Request Intake: The `POST /chat` endpoint receives a JSON payload containing the user's message and a `session_id`.
2. Service Delegation: The endpoint calls `OllamaService.generate_stream()`, which connects to the local Ollama API.
3. Stream Processing: As Ollama generates the response, the service parses the JSON-line stream from the local model.
4. Token Yielding: Individual tokens are yielded one by one. If a `session_id` is missing, the system automatically generates one to maintain context.
5. Client Delivery: The server returns a `StreamingResponse` to the client, allowing the UI to render text as it is being "thought" by the model.

### Endpoints
| Endpoint      | Method | Description                                                                   |
|---------------|--------|-------------------------------------------------------------------------------|
| /health       | GET    | Verifies the API is active and the Ollama service is reachable.   |
| /chat         | POST   | Primary entry point for messages; returns a `StreamingResponse` (chunked transfer encoding). |

### Sample Request
```json
{
  "message": "What do you know about me?",
  "session_id": "optional-leave-blank-for-auto"
}
```

### Sample Response
Tokens stream back progressively as the model generates them. The response is `text/plain` 
chunked transfer encoding, not a JSON blob:
```text
Based on the conversations we've had so far, it appears that I don't have any information 
about your personal experiences...
```

Response headers:
```
transfer-encoding: chunked
content-type: text/plain; charset=utf-8
```

### Key design decisions
#### Why Ollama over cloud APIs 
In alignment with the Phase 0 privacy constraint, I chose Ollama to keep 100% of the conversation data on my local hardware. This eliminates reliance on OpenAI or Anthropic, ensures zero API costs, and removes the risk of being throttled by rate limits during heavy development.

#### Why mistral:7b
I selected `mistral:7b` as the primary reasoning engine because it offers the best "bang for your buck" on consumer hardware. It provides high-quality reasoning while fitting entirely within RAM, allowing it to run smoothly on a CPU without requiring a high-end dedicated GPU.

#### Why Streaming
Running LLMs on a CPU can lead to a 2–5 second delay before a full response is ready. Without streaming, the user experience feels broken. By implementing streaming, the first tokens appear in under a second. The perceived speed is significantly higher, creating a fluid, conversational feel even if the total generation time remains the same.

#### Lifespan Pattern
Instead of instantiating the `OllamaService` on every request—which would be computationally wasteful—I used the FastAPI lifespan pattern. The service is instantiated once when the server starts and is stored in `app.state`. This ensures rapid response times and better memory management.


## Phase 2: Long-Term Memory (RAG)

### What was built
I implemented a Retrieval-Augmented Generation (RAG) layer to provide the OS with long-term memory. This allows the system to recall facts across different sessions without needing to resend the entire conversation history.

- **Core Memory Services**: Developed the `EmbeddingService` for vector generation and the `MemoryService` for managing the storage and retrieval logic.
- **Database Logic**: Created the `match_memories` RPC function in Supabase to handle high-speed vector similarity searches.
- **The `stream_and_store` Wrapper**: Designed a specialized handler that collects streaming tokens in real-time and, only once the stream is complete, triggers the storage of the full exchange.
- **Context Injection**: Updated the chat logic to automatically pull relevant past "memories" and inject them into the system prompt before the LLM generates a response.

### How it works
The memory system operates through two distinct automated flows:
1. The Store Flow (Post-Response)
- The user receives the stream in real-time.
- Once the last token is delivered, `stream_and_store` passes the full conversation pair to `MemoryService.store()`.
- The `EmbeddingService` converts the text into a vector, which is then saved to the Supabase `_memory_vectors` table.

2. The Retrieve Flow (Pre-Response)
- A new message arrives.
- `MemoryService.retrieve()` triggers the `EmbeddingService` to turn the current query into a vector.
- A cosine similarity search is performed via the `match_memories` RPC.
- The top 3 most relevant memories are returned and injected into the LLM's prompt as "Context," allowing it to answer based on previous knowledge.

### Memory in Action
**Before RAG — Asked across sessions with no memory:**

```
User: "What do you know about me?"
AI: "I don't have any information about you. I am a stateless AI assistant."
```

**After RAG — Same question with memory active:**

```
User: "What do you know about me?"
AI: "Based on our conversations, I know your favorite café in Kalk is Slow Moe's and you are a Software Engineering student based in Cologne."
```

### Why RAG over simple conversation history?
Standard conversation history is "volatile"—once a session ends or the buffer fills up, the AI "forgets." Passing 500 previous messages into a prompt is computationally expensive and hits model context limits quickly.

RAG solves this by being selective. Instead of remembering everything, it uses cosine similarity to find memories that are "semantically similar" to the current question. In plain English: if you ask about "rent," the system ignores your recipes and only retrieves your financial discussions.

### Embedding model choice: `nomic-embed-text`
I chose `nomic-embed-text` because it is a high-performance open-source model that runs locally via Ollama.

- **Dimensions**: It converts text into a 768-dimensional vector—enough detail to capture complex semantic nuances without being a heavy burden on the CPU.
- **Performance**: On my i7, embedding a standard sentence takes under 200ms, making the retrieval process feel instantaneous to the user.

### Key design decisions
#### `pgvector` over a dedicated Vector DB
While services like Pinecone or Weaviate are popular, they introduce extra cloud dependencies and costs. By using `pgvector` inside my existing Supabase instance, I kept the architecture lean and maintained total data privacy within my established database layer.

#### The `stream_and_store` Pattern
You cannot store a response until it actually exists. This wrapper creates a clean separation of concerns: it manages the "live" user experience (streaming) and then handles the "archival" process (storing) once the data is finalized.

#### Isolated Memory per Manager
To ensure the AI doesn't get confused, I implemented isolated memory pools. The Finance Manager only searches `fin_memory_vectors`, while the Life Admin Manager searches its own. This prevents "cross-contamination" and ensures that financial queries aren't answered with personal hobby data.

#### Singleton Service Pattern
Following the lifespan principle from Phase 1, the `EmbeddingService` is instantiated once within `MemoryService`. This avoids the overhead of reloading the embedding logic for every single retrieval or storage call.


## Phase 3: Voice I/O

### What was built
I implemented a complete local voice processing pipeline, enabling the OS to hear, process, and speak without any cloud latency or privacy leaks.
- Core Services: Developed `STTService` (Speech-to-Text), `TTSService` (Text-to-Speech), and the `VoiceLoop` orchestrator.
- Voice Activity Detection (VAD): Integrated `webrtcvad` into a `record_until_silent()` function to automatically detect when I stop speaking.
- Local Processing Stack: Leveraged `faster-whisper` for transcription and `piper-tts` for high-speed synthesis.
- Voice Endpoint: Created the `POST /voice` entry point to trigger a single "listen-think-speak" cycle.

### The Voice Pipeline
The system processes a voice turn through a strictly ordered six-step sequence:
1. Mic Input: Captures raw audio via the system microphone.
2. Silence Detection: `webrtcvad` monitors 30ms audio chunks; recording stops after 1.5 seconds of sustained silence.
3. STT (Transcription): `faster-whisper` converts the saved `.wav` file into a text string.
4. Context Building: The system retrieves relevant RAG memories (from Phase 2) and builds the prompt.
5. LLM Reasoning: The model generates a response (optimized for brevity).
6. TTS & Playback: `piper-tts` synthesizes the text into audio and plays it through the local speakers.

### Latency Profiling Results
To make the interaction feel natural, I moved from `mistral:7b` to `llama3.2:3b` for voice mode and added a "brevity prompt" to keep responses concise.

| Component    | Latency | Notes                                              |
|--------------|---------|----------------------------------------------------|
| STT          | ~5.0s   | Includes physical speaking time and 1.5s silence buffer |
| Memory (RAG) | ~1.0s   | Vector search and prompt injection                 |
| LLM          | ~5.0s   | Switched to llama3.2:3b for faster CPU inference |
| TTS          | ~2.0s   | Synthesis and initial playback buffer              |
| **Total**    | **~13.0s** | From end of speech to start of AI response      |

### Key Design Decisions
#### `faster-whisper` for STT
I chose the `base` model of `faster-whisper` because it is highly optimized for CPUs via `int8` quantization. It strikes the perfect balance: it is accurate enough for daily commands but fast enough to keep the pipeline moving.

#### `webrtcvad` for Silence Detection
Instead of using simple volume thresholds (which fail in noisy rooms), I used `webrtcvad`. It is a battle-tested tool used in production VoIP systems that detects actual human speech patterns at a frame level, ensuring the mic doesn't stay open indefinitely.

#### `piper-tts` for Speech Synthesis
`piper` was selected because it is arguably the fastest local TTS available. It produces natural-sounding speech that starts playing almost the moment the LLM finishes its thought. Like the rest of the stack, all synthesis happens on-device — no audio data is sent to any external service.

#### `generate` vs. `generate_stream`
While I used streaming for the text chat (Phase 1), voice mode uses standard `generate`. This is a necessary tradeoff: `piper-tts` requires the complete text string to produce high-quality, natural prosody. Streaming text to a voice engine often results in "choppy" or robotic delivery.

#### The Voice Brevity Prompt
Initially, the LLM took ~42s to respond because it tried to be too verbose. By adding "Answer in 2 sentences max" to the voice system prompt, I reduced LLM time from 42s to 5s. This didn't just save tokens; it allowed the model to reach its "stop" token significantly faster, which is critical for voice UX.


## Phase 4: Wake Word Detection
### What was built
- **WakeWordService & StateMachine**: Integrated a passive listening layer and a logic gate to manage system transitions.
- **Background Threading**: The system now starts listening passively on startup via the `main.py` lifespan—no manual button press required.
- **Decoupled Callback Pattern**: Implemented an `on_detected` callback; the `WakeWordService` has no knowledge of the `VoiceLoop`, it simply triggers a function when the phrase is recognized.
- **Updated VoiceLoop**: Modified the core loop to handle automated triggers and state transitions.

### How it works
1. Startup: The server starts and launches `WakeWordService` in a background daemon thread.
2. Detection: The service monitors the audio stream for "Hey Jarvis" with a 0.5 minimum confidence score.
3. Verification: Once detected, the callback fires and checks if the system is in the `SLEEPING` state.
4. Execution: If valid, the state transitions, `VoiceLoop.run_once()` executes, and the system returns to `SLEEPING` upon completion.

### The state machine

| State      | Description                                                        |
|------------|--------------------------------------------------------------------|
| SLEEPING   | Passive mode; waiting for the wake word trigger.                   |
| LISTENING  | Wake word detected; actively recording user microphone input.      |
| PROCESSING | Transcribing audio (STT), fetching RAG memories, and LLM reasoning.|
| SPEAKING   | Executing local TTS audio playback.                                |

### Challenges & how they were solved
#### The Echo Problem
The assistant's own voice would occasionally trigger the wake word (e.g., the frequency of the TTS "thinking" it heard "Jarvis").
- Solution: Implemented a `last_sleeping_at` timestamp. I added a 10-second buffer after the system returns to `SLEEPING` where new triggers are ignored to allow the room audio to settle.

#### False Trigger Cascades
A single "Hey Jarvis" would sometimes fire the callback 30+ times in a fraction of a second due to how the buffer processed the audio.
- Solution: Added a 15-second cooldown period between successful detections to ensure only one voice turn is initiated per utterance.

#### Ghost Transcriptions
Background noise (like a door slam) would occasionally trigger the wake word, but the resulting STT would be empty or nonsensical.
- Solution: Added a `len(text.strip()) < 3` guard. If no substantive speech is detected after the wake word, the system transitions straight back to `SLEEPING` to avoid wasting LLM resources.

### Key design decisions
#### Background Thread with daemon=True
The `WakeWordService` starts in the background so the main application remains responsive. Using `daemon=True` ensures that when the main FastAPI process exits, the microphone thread is killed automatically, preventing "zombie" processes from holding the mic hardware.

#### Callback Pattern
By passing `on_detected: callable` to the service, I achieved loose coupling. The `WakeWordService` doesn't need to know about the `VoiceLoop` or `StateMachine` logic, making it easy to swap out the wake word engine later without rewriting the OS logic.

#### State Check Before Firing
The callback checks `State.SLEEPING` before calling `run_once()`. This is a critical safety "interlock" that prevents the assistant from trying to record a new command while it is already in the middle of `PROCESSING` or `SPEAKING`.

#### openWakeWord Choice
I chose `openWakeWord` because it runs entirely on the CPU with no cloud dependency. It is open-source and provides a clear path for training custom, personalized wake words in future phases.


## Phase 5: Multi-Agent Orchestration

### What was built
In this phase, I transformed the system from a simple chatbot into a "Society of Mind" architecture. The system now utilizes a central orchestrator to delegate tasks to specialized domain managers.

- Core Infrastructure: Developed the `BaseManager` abstract class, `ManagerRequest`, `ManagerResponse` models, and the `AdminOrchestrator`.
- Intelligence Layer: Created the `IntentClassifier` to parse user goals and the `HealthMonitor` to verify agent availability.
- Agent Stubs: Built four specialized manager stubs (`LifeAdmin`, `Finance`, `Content`, and `Relationships`) to test routing logic.
- Refactored API: Modified the `POST /chat` endpoint to route all traffic through the Admin rather than calling the LLM directly.

### How it works
`POST /chat` → `AdminOrchestrator.process()` → `IntentClassifier.classify()` → domain extracted → correct manager called → `ManagerResponse.summary` returned

The system now operates through an "Admin-first" delegation flow:
- Intake: `POST /chat` sends the user message to `AdminOrchestrator.process()`.
- Classification: The message is passed to `IntentClassifier.classify()`, which extracts the domain, urgency, and type.
- Delegation: If a specific domain is identified (e.g., `finance`), the Admin fetches the corresponding manager from a internal registry and calls its process() method.
- Fallback: If the domain is `unknown` or `multi`, the system falls back to a direct Ollama call to ensure the user still receives a response.
- Synthesis: The manager returns a `ManagerResponse` object; the Admin extracts the `summary` and returns it to the API.

### Multi-domain example:
User: "What should I focus on this week and how are my finances?"
System: Classified as `multi` and falls back to Ollama and full conversational response returned.


### The intent classifier
The classifier acts as the "receptionist" of the OS. It uses a strict JSON-only prompt to ensure the output can be parsed programmatically.

- Prompt Evolution: Early tests showed poor accuracy; for example, "What bills do I have due?" was incorrectly classified as `finance` instead of `life_admin`.
- The Fix: I added explicit domain descriptions to the system prompt. Defining exactly what each manager handles increased routing accuracy from ~40% to ~95%.
- Robustness: I implemented `.strip("json")` and backtick cleaning logic to handle cases where the LLM wraps its JSON output in Markdown, ensuring the system doesn't crash on formatting quirks.

### Routing Logic
The Admin maintains a `managers` dictionary that maps domain strings to manager instances. This makes the system highly extensible—adding a new specialized agent requires adding only a single line to the registry.

- *Single Domain*: Manager is called directly and stub returns a mock summary.
- *Unknown/Multi*: Bypasses specialized agents and goes directly to the base LLM.
- *Error Handling*: If a domain is returned that has no registered manager, the system logs a warning and provides a graceful "I couldn't process this" fallback to the user.

#### Example managers dict
```python
{
      "life_admin": LifeAdminManager(),
      "finance": FinanceManager(),
      "content": ContentManager(),
      "relationships": RelationshipManager(),
}
```
When no manager is found then a warning is logged and we simply return a "Sorry, I couldn't process your request."

### Key design decisions
#### BaseManager abstract class
I used Python’s `abc` module to define a strict interface for all agents. If a new manager is created without a `name` or a `process()` method, Python raises a `TypeError` at instantiation. This provides a "compile-time" safety net, ensuring no "broken" managers make it into the runtime environment.

#### Stub-first approach
I deliberately built stubs (empty managers) before building real tools. This allowed me to test the entire "plumbing" of the system—classification, state passing, and response synthesis—without the complexity of real database queries or API integrations getting in the way.

#### Single Entry Point (Encapsulation)
The `/chat` endpoint only knows about `admin.process()`. It has no knowledge of the 25-table schema or which manager is doing the work. This strict encapsulation means I can rewrite the entire backend agent logic without ever touching the API layer.

#### Health Monitoring on Startup
The `HealthMonitor.check_all()` method runs during the FastAPI lifespan startup. If a manager fails to initialize or is missing its required tables, the Admin knows immediately. This prevents "silent failures" where a user discovers a bug mid-conversation.

#### Classifier Prompt Engineering
This phase proved that prompt design is as critical as code architecture. By adding just 6 lines of domain definitions to the `IntentClassifier` prompt, the system's ability to correctly route complex requests (like bill management vs. bank balance) improved dramatically.