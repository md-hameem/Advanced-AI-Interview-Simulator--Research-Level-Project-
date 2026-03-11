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

## [Unreleased]

### Planned
- Speech Intelligence (Whisper ASR + speech analytics)
- Coding Interview Evaluator (Monaco editor + code sandbox)
- STAR Behavioral Framework Detection
- PDF report export
- ML model training pipeline (BERT, CodeBERT, XGBoost)
- Emotion detection (OpenCV + DeepFace)
- AI interviewer personalities
- Multi-agent interview system
