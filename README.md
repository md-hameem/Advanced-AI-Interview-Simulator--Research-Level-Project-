# 🧠 Advanced AI Interview Simulator

A **research-level** AI system that conducts realistic technical interviews, evaluates answers using multiple signals, and produces structured candidate assessment reports.

## Architecture

```
User → Frontend (Next.js) → Backend API (FastAPI) → LLM (Google Gemini)
                                    ↓
                              SQLite Database
                                    ↓
                          Evaluation Pipeline
                            ├── Rubric Scoring
                            ├── Speech Analytics
                            ├── Code Evaluation
                            └── Behavioral Analysis
                                    ↓
                          Candidate Report (PDF)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, SQLAlchemy |
| Frontend | Next.js 15, TailwindCSS, TypeScript |
| LLM | Google Gemini (via google-generativeai) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Speech | OpenAI Whisper, Librosa |
| ML | PyTorch, HuggingFace Transformers |

## Quick Start

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
uvicorn main:app --reload
```

API docs: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py             # App configuration
│   ├── database.py           # SQLAlchemy setup
│   ├── schemas.py            # Pydantic request/response models
│   ├── models/
│   │   └── interview.py      # Database models
│   ├── routers/
│   │   └── interview.py      # API endpoints
│   └── services/
│       ├── llm_client.py     # Google Gemini client
│       └── interview_agent.py # Core interview logic
├── frontend/
│   └── src/
│       ├── app/              # Next.js pages
│       └── lib/api.ts        # API client
├── data/
│   └── interview_questions.json # Seed question bank
└── ml/                        # ML model training (coming soon)
```

## Features

- **Adaptive Interview Agent** — Dynamic difficulty adjustment based on performance
- **Rubric-Based Evaluation** — Structured scoring: correctness, depth, clarity, reasoning (0-5)
- **Follow-Up Questions** — AI probes deeper on mediocre answers
- **Hint System** — Progressive hints for candidates who are stuck
- **Professional Reports** — Comprehensive candidate assessment with hire/no-hire recommendation
- **Analytics Dashboard** — Performance tracking and score visualization
