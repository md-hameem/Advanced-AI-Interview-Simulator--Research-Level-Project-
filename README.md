<div align="center">

# 🧠 AI Interview Simulator

**A research-level AI system that conducts realistic technical interviews, evaluates answers using multi-signal analysis, and produces structured candidate assessment reports.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![Gemini](https://img.shields.io/badge/Google_Gemini-2.0-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

[Features](#-features) · [Architecture](#-architecture) · [Quick Start](#-quick-start) · [API Reference](#-api-reference) · [Roadmap](#-roadmap) · [Contributing](#contributing)

</div>

---

## 🎯 Overview

The AI Interview Simulator goes beyond simple Q&A — it creates a **multi-dimensional evaluation pipeline** similar to what companies like Google and Amazon use internally. The system evaluates:

| Signal | How |
|--------|-----|
| **Technical Correctness** | LLM rubric scoring against expected concepts |
| **Depth of Understanding** | Probing follow-up questions when answers are mediocre |
| **Communication Clarity** | Structured clarity scoring on every response |
| **Problem-Solving Ability** | Reasoning analysis with adaptive difficulty |
| **Speech & Confidence** | *(Planned)* Whisper ASR + audio feature analysis |

---

## ✨ Features

### Core Interview Engine
- 🔄 **Adaptive Questioning** — Difficulty auto-adjusts based on consecutive performance
- 🎯 **Follow-Up Probing** — AI generates deeper follow-ups when answers score 3–6/10
- 💡 **Progressive Hint System** — 3 levels of hints (subtle → moderate → direct)
- 📊 **Rubric-Based Scoring** — Structured 0–5 scores for correctness, depth, clarity, and reasoning
- 🔀 **Topic Rotation** — Covers data structures, algorithms, system design, ML, and behavioral

### Interview Types
| Type | Description |
|------|-------------|
| `mixed` | Rotates through technical, coding, system design, and behavioral |
| `technical` | Data structures, algorithms, concepts |
| `coding` | Problem-solving and code evaluation |
| `behavioral` | Leadership, teamwork, STAR method |
| `system_design` | Architecture and scalability |

### Assessment & Reporting
- 📄 **Professional Reports** — Executive summary, strengths, weaknesses, and study recommendations
- ✅ **Hiring Recommendations** — `strong_hire` / `hire` / `lean_no_hire` / `no_hire`
- 📈 **Analytics Dashboard** — Aggregate statistics, score trends, candidate directory

### Premium Dark-Theme UI
- 🌑 Glassmorphism design with gradient accents
- ⚡ Micro-animations and glow effects
- 💬 Chat-style interview interface with real-time evaluation
- 📱 Fully responsive layout

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js 16)                         │
│  Landing ─── New Interview ─── Live Session ─── Report ─── Dashboard │
└─────────────────────────────┬────────────────────────────────────────┘
                              │ REST API (JSON)
┌─────────────────────────────▼────────────────────────────────────┐
│                      BACKEND (FastAPI)                           │
│                                                                  │
│  ┌─────────────┐   ┌──────────────────┐   ┌──────────────────┐   │
│  │   Router     │──▶│ Interview Agent  │──▶│   LLM Client   │   │
│  │  (REST API)  │   │  (Adaptive Flow) │   │ (Google Gemini) │   │
│  └──────┬──────┘   └────────┬─────────┘   └──────────────────┘   │
│         │                   │                                    │
│  ┌──────▼──────────────────▼──────────────────────────────────┐  │
│  │                    SQLAlchemy ORM                          │  │
│  │         Candidate │ Interview │ InterviewQuestion          │  │
│  └─────────────────────────┬──────────────────────────────────┘  │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                     ┌────────▼───────────┐
                     │  SQLite / Postgres │
                     └────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- A [Google Gemini API key](https://aistudio.google.com/apikey) (free tier works)

### 1. Clone & Setup Backend

```bash
git clone https://github.com/md-hameem/Advanced-AI-Interview-Simulator--Research-Level-Project-.git
cd Advanced-AI-Interview-Simulator--Research-Level-Project-

# Backend
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env → set GEMINI_API_KEY=your_key_here

# Start backend
uvicorn main:app --reload
```

> 📖 API docs available at **http://localhost:8000/docs**

### 2. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

> 🌐 Open **http://localhost:3000**

### 3. Run Your First Interview

1. Click **Start Interview** on the landing page
2. Fill in your candidate profile (name, role, skills)
3. Choose interview type and difficulty
4. Answer adaptive questions — get real-time feedback
5. View your **assessment report** with detailed scores

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/candidates` | Register a new candidate |
| `GET` | `/api/candidates` | List all candidates |
| `POST` | `/api/interviews` | Create an interview session |
| `GET` | `/api/interviews` | List all interviews |
| `POST` | `/api/interviews/{id}/start` | Start interview → first question |
| `POST` | `/api/interviews/{id}/questions/{qid}/answer` | Submit answer → evaluation + next Q |
| `POST` | `/api/interviews/{id}/hint` | Get a progressive hint |
| `GET` | `/api/interviews/{id}/report` | Full candidate assessment report |
| `GET` | `/api/analytics/overview` | Dashboard aggregate stats |

> Full interactive docs at `/docs` (Swagger UI) or `/redoc` (ReDoc).

---

## 📁 Project Structure

```
ai-interview-simulator/
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── config.py                  # Pydantic settings + env vars
│   ├── database.py                # SQLAlchemy engine + sessions
│   ├── schemas.py                 # Request/response Pydantic models
│   ├── models/
│   │   └── interview.py           # DB models (Candidate, Interview, Question)
│   ├── routers/
│   │   └── interview.py           # API endpoint definitions
│   ├── services/
│   │   ├── llm_client.py          # Google Gemini client + prompt templates
│   │   └── interview_agent.py     # Core adaptive interview logic
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx           # Landing page
│   │   │   ├── layout.tsx         # Root layout
│   │   │   ├── globals.css        # Design system
│   │   │   ├── interview/
│   │   │   │   ├── new/page.tsx   # Interview setup
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx   # Live interview session
│   │   │   │       └── report/page.tsx  # Assessment report
│   │   │   └── dashboard/page.tsx # Analytics dashboard
│   │   └── lib/
│   │       └── api.ts             # Typed API client
│   └── package.json
├── data/
│   └── interview_questions.json   # 70+ seed questions
├── ml/                            # ML training (coming soon)
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

---

## 🗺️ Roadmap

- [ ] **Speech Intelligence** — Whisper ASR + speech analytics (WPM, fillers, confidence)
- [ ] **Coding Evaluator** — Monaco editor + sandboxed code execution + complexity analysis
- [ ] **STAR Detection** — Behavioral answer analysis using Situation-Task-Action-Result
- [ ] **PDF Export** — Downloadable professional assessment reports
- [ ] **ML Models** — Fine-tuned BERT/DeBERTa for answer quality, CodeBERT for code evaluation
- [ ] **Meta-Model** — XGBoost/LightGBM aggregator for final hire/no-hire prediction
- [ ] **Emotion Detection** — Facial + voice tone analysis (OpenCV, DeepFace)
- [ ] **Interviewer Personalities** — Google / Amazon / Startup interview styles
- [ ] **Multi-Agent System** — Interviewer, Evaluator, Code Reviewer, Behavioral Analyst

---

## 🤝 Contributing

Contributions are welcome! Please read the [Contributing Guide](CONTRIBUTING.md) for details on the development workflow, coding standards, and how to submit pull requests.

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Built with ❤️ using FastAPI, Next.js, and Google Gemini</sub>
</div>
