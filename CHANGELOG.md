# Changelog

All notable changes to the **AI Interview Simulator** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] — 2026-03-12

### 🚀 Added

#### Backend (FastAPI)
- **FastAPI application** with CORS, lifecycle management, and Swagger docs at `/docs`
- **SQLAlchemy database models**: `Candidate`, `Interview`, `InterviewQuestion` with full scoring fields
- **Pydantic schemas** for type-safe request/response validation
- **Google Gemini LLM client** with structured prompt templates for:
  - Adaptive question generation
  - Rubric-based answer evaluation (correctness, depth, clarity, reasoning 0–5)
  - Follow-up question generation
  - Comprehensive report generation
- **Adaptive Interview Agent** with:
  - Difficulty adjustment based on consecutive performance
  - Follow-up probing for mediocre answers (score 3–6)
  - Progressive hint system
  - Topic rotation across categories
- **REST API endpoints**:
  - `POST /api/candidates` — Register candidate
  - `POST /api/interviews` — Create interview session
  - `POST /api/interviews/{id}/start` — Start interview, get first question
  - `POST /api/interviews/{id}/questions/{qid}/answer` — Submit answer, get evaluation + next question
  - `POST /api/interviews/{id}/hint` — Get progressive hints
  - `GET /api/interviews/{id}/report` — Full candidate assessment report
  - `GET /api/analytics/overview` — Dashboard aggregated statistics
- **Configuration** via `pydantic-settings` with `.env` file support

#### Frontend (Next.js 16 + TailwindCSS)
- **Premium dark-theme UI** with glassmorphism, gradient text, glow effects, and micro-animations
- **Landing page** (`/`) — Hero section, feature grid, how-it-works steps, CTA
- **New Interview** (`/interview/new`) — 2-step flow: candidate profile → interview configuration (type, difficulty, question count)
- **Live Interview Session** (`/interview/[id]`) — Chat-style Q&A with:
  - Real-time evaluation display with expandable score breakdowns
  - Progress bar and elapsed time timer
  - Hint system integration
  - Difficulty and question type badges
  - Completion overlay with final scores
- **Assessment Report** (`/interview/[id]/report`) — Professional report with:
  - Overall + category scores with visual bars
  - Hire/no-hire recommendation badge
  - Strengths & weaknesses analysis
  - Question-by-question breakdown
  - Study topic recommendations
- **Dashboard** (`/dashboard`) — Stats cards, recent interviews list, candidate directory
- **Typed API client** (`src/lib/api.ts`) — Axios wrapper with full TypeScript interfaces

#### Data
- **Seed question bank** — 70+ interview questions across data structures, algorithms, system design, machine learning, and behavioral categories at easy/medium/hard difficulty levels

#### DevOps
- `.env.example` with configuration template
- `requirements.txt` with all Python dependencies
- `README.md` with architecture diagram, tech stack, and quick start guide

---

## [0.2.0] — 2026-03-12

### 🎙️ Added — Speech Intelligence (Module 2)

#### Backend
- **`speech_processor.py`** — Full speech analysis pipeline:
  - OpenAI Whisper ASR transcription (lazy-loaded model)
  - Filler word detection (um, uh, like, you know, etc.)
  - Pause analysis from segment timing (>500ms gaps)
  - WPM (words-per-minute) calculation
  - Librosa audio features (pitch F0, RMS energy, onset variability)
  - Composite confidence score (0–1) based on speech characteristics
- **`routers/speech.py`** — 3 new API endpoints:
  - `POST /api/speech/transcribe` — Whisper transcription
  - `POST /api/speech/analyze` — Full speech metrics
  - `POST /api/speech/answer/{id}/{qid}` — Submit voice answer (transcribe + analyze + evaluate)

#### Frontend
- **`useAudioRecorder` hook** — MediaRecorder API with start/stop/pause/resume and error handling
- **Voice/Type mode toggle** in interview session — switch between keyboard and microphone input
- **Recording UI** — Live recording animation with duration timer and waveform visualization
- **Speech metrics display** — WPM, confidence %, filler count shown on voice-answered bubbles
- **Speech API client functions** — `submitSpeechAnswer()` and `analyzeSpeech()` in `api.ts`

---

## [0.3.0] — 2026-03-12

### 💻 Added — Coding Interview Evaluator (Module 5)

#### Backend
- **`code_evaluator.py`** — Full code evaluation pipeline:
  - Sandboxed code execution via subprocess (Python, JavaScript, TypeScript)
  - Test runner with flexible output comparison (literal, structural, case-insensitive)
  - AST-based complexity analysis (loop depth, recursion detection, sorting, auxiliary DS)
  - LLM code review via Gemini (quality, correctness, efficiency, style scores)
  - 5 coding problems: Two Sum, Reverse Linked List, Valid Parentheses, Max Subarray, LRU Cache
- **`routers/coding.py`** — 7 new API endpoints:
  - `GET /api/coding/questions` — List/filter coding problems
  - `GET /api/coding/questions/{id}` — Get problem with starter code
  - `GET /api/coding/random` — Random problem by difficulty
  - `POST /api/coding/execute` — Run code (sandboxed)
  - `POST /api/coding/test/{id}` — Run test cases
  - `POST /api/coding/evaluate/{id}` — Full evaluation (tests + complexity + LLM review)
  - `POST /api/coding/complexity` — Static complexity analysis

#### Frontend
- **Coding Practice page** (`/coding`) — 3-pane IDE layout:
  - Left: problem list, description with formatted markdown, test count, optimal complexity
  - Center: Monaco Editor with Python/JavaScript toggle, syntax highlighting
  - Bottom: Results panel with Run output, expandable test results, complexity comparison, LLM review scores

---

## [Unreleased]

### Planned
- STAR Behavioral Framework Detection
- PDF report export
- ML model training pipeline (BERT, CodeBERT, XGBoost)
- Emotion detection (OpenCV + DeepFace)
- AI interviewer personalities
- Multi-agent interview system
