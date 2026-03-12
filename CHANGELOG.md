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

## [0.4.0] — 2026-03-12

### 🎯 Added — Behavioral Interview Analyzer (Module 6)

#### Backend
- **`behavioral_analyzer.py`** — Full STAR analysis pipeline:
  - Rule-based STAR component detection (60+ keyword indicators across S/T/A/R)
  - 12-question behavioral bank across 8 competencies (leadership, teamwork, conflict resolution, problem solving, communication, adaptability, ownership, initiative)
  - LLM-based deep STAR analysis with per-component scores and summaries
  - Competency, communication, specificity, and impact scoring
  - Red flag detection (vague answers, hypothetical, blaming)
- **`routers/behavioral.py`** — 6 new API endpoints:
  - `GET /api/behavioral/competencies` — List competencies
  - `GET /api/behavioral/questions` — List/filter behavioral questions
  - `GET /api/behavioral/questions/{id}` — Get question with follow-ups
  - `GET /api/behavioral/random` — Random question by competency/difficulty
  - `POST /api/behavioral/detect-star` — Quick STAR detection (no LLM)
  - `POST /api/behavioral/analyze/{id}` — Full STAR + competency analysis

#### Frontend
- **Behavioral Practice page** (`/behavioral`) — Premium UI:
  - Competency-grouped question cards with color-coded icons
  - STAR method tip banner
  - Visual STAR component analysis (S/T/A/R scores, confidence badges, summaries)
  - Additional assessment (competency, communication, specificity, impact)
  - Strengths, improvements, red flags, and follow-up questions display

---

## [0.5.0] — 2026-03-13

### 📄 Added — PDF Report Export (Module 7)

#### Backend
- **`pdf_generator.py`** — Professional PDF report using ReportLab:
  - Branded header with candidate info and date
  - Large overall score display with color coding
  - Category score breakdown (Technical, Communication, Problem Solving) with visual bars
  - Recommendation badge (Strong Hire / Hire / Lean No / No Hire)
  - Two-column strengths & weaknesses layout
  - Question-by-question scores table with per-dimension breakdown
  - Detailed feedback and study recommendations section
  - Branded footer with generation timestamp
- **`GET /api/interviews/{id}/report/pdf`** — Streams PDF as downloadable file

#### Frontend
- **Download PDF button** on report page (`/interview/[id]/report`)
  - Cyan gradient button with loading spinner
  - Fetches PDF as blob and triggers browser download
  - Error handling with user feedback

---

## [0.6.0] — 2026-03-13

### 🧠 Added — ML Model Training Pipeline (Module 8)

#### Training Infrastructure (`ml/`)
- **`config.py`** — Centralized hyperparameters for all 5 models (learning rates, architectures, batch sizes)
- **`dataset.py`** — Synthetic dataset generator (CLI: `python -m ml.dataset`):
  - Answer quality (Q+A → score), Communication (text → clarity/fluency/structure)
  - STAR behavioral (text → S/T/A/R scores), Code evaluator (code → quality/efficiency/style)
  - Meta-scorer (16-feature vector → final score)
- **`train.py`** — Unified training CLI (`python -m ml.train --all --epochs 5`):
  - Train individual or all models, auto-generate datasets, save training reports

#### 5 Specialized Models (`ml/models/`)
- **`answer_quality.py`** — DeBERTa-v3-small → regression (0-10 answer score)
- **`communication.py`** — DistilBERT → multi-head (clarity/fluency/structure)
- **`star_analyzer.py`** — DeBERTa-v3-small → 4-head STAR detection (S/T/A/R)
- **`code_evaluator.py`** — CodeBERT → multi-head (quality/efficiency/style)
- **`meta_scorer.py`** — XGBoost aggregator (16 features → final score), feature importance

#### Inference & API
- **`inference.py`** — Production inference service with lazy model loading
- **`routers/ml.py`** — 5 new API endpoints:
  - `GET /api/ml/status` — Model availability
  - `POST /api/ml/predict/answer-quality` — DeBERTa answer scoring
  - `POST /api/ml/predict/communication` — Communication dimensions
  - `POST /api/ml/predict/star` — STAR component detection
  - `POST /api/ml/predict/code-quality` — Code quality assessment

#### Jupyter Notebooks
- **`01_dataset_exploration.ipynb`** — Data generation + visualization:
  - Score distributions, correlation heatmaps, STAR radar chart, code quality scatter
  - Meta-scorer feature analysis, cross-dataset summary table
- **`02_model_training.ipynb`** — Full training + evaluation:
  - Per-model training with pred-vs-true scatter plots, residual distributions
  - XGBoost feature importance, training summary comparison, inference demo

#### Documentation
- **`ml/README.md`** — Comprehensive ML docs:
  - Per-dataset schema tables (fields, types, ranges, distributions)
  - Dataset download links (SQuAD, CoQA, HumanEval, CodeXGLUE, ASAP-AES)
  - Pre-trained model weights (Hugging Face links)
  - Quick start (notebooks, CLI, Python API), config reference

---

## [0.7.0] — 2026-03-13

### 🤖 Added — Advanced Interview Features (Phase 9)

#### Backend
- **AI Interviewer Personalities**: Custom LLM instructions for `Default`, `Google`, `Amazon`, and `Startup` personas, automatically adjusting rigorousness, follow-ups, and interaction style.
- **Multi-Agent Evaluation Panel**: Refactored evaluation logic in `multi_agent.py` introducing a panel of parallel evaluators: `Tech Lead` (technical depth/accuracy) and `HR Agent` (communication/clarity), with a `Coordinator` agent to aggregate unified feedback.
- **Emotion Tracking**: New `emotion_detector.py` service using OpenCV and DeepFace (optional) to measure candidate stress and confidence levels from webcam frames mapped to a `/api/vision/analyze-frame/` endpoint.
- **Personalized Learning Feedback**: Added `/api/candidates/{id}/learning-plan` to aggregate recurring weaknesses from past interviews and generate a customized 4-week study plan via the LLM.

#### Frontend
- **Interviewer Persona Selector**: New dynamic grid selector added to the interview configuration screen (`/interview/new`) allowing candidates to select their interviewer style before starting.
- **Webcam Emotion Tracking**: Integrated `useWebcam` React hook providing a Picture-in-Picture (PIP) UI in the interview session to silently capture video frames and stream semantic emotion telemetry to the backend evaluator.

---

## [Unreleased]

### Planned
- Dockerized deployment
- WebRTC real-time bidirectional audio streaming for speech interactions
