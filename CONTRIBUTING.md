# Contributing to AI Interview Simulator

Thank you for considering contributing to this project! Here's how you can help.

## 🚀 Getting Started

### Prerequisites

- **Python** 3.11+
- **Node.js** 18+
- **npm** 9+
- A **Google Gemini API key** ([get one free](https://aistudio.google.com/apikey))

### Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/md-hameem/Advanced-AI-Interview-Simulator--Research-Level-Project-.git
cd ai-interview-simulator

# 2. Backend setup
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# 3. Frontend setup
cd ../frontend
npm install

# 4. Run both
# Terminal 1: uvicorn main:app --reload  (from backend/)
# Terminal 2: npm run dev                (from frontend/)
```

## 📁 Project Structure

```
├── backend/           → FastAPI server, LLM services, database models
├── frontend/          → Next.js 16 app with TailwindCSS
├── data/              → Seed datasets and question banks
└── ml/                → ML model training scripts and notebooks
```

## 🔄 Development Workflow

1. **Create a branch** from `main` for your feature or fix
2. **Write code** following the existing code patterns
3. **Test** your changes — run the backend and frontend, verify the feature
4. **Commit** with a clear, descriptive message following [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat: add speech analytics endpoint`
   - `fix: correct score clamping in evaluation`
   - `docs: update API documentation`
5. **Push** and open a Pull Request

## 📐 Code Style

### Python (Backend)
- Follow **PEP 8**
- Use **type hints** for function signatures
- Docstrings for all classes and public methods
- Format with `black` and lint with `ruff`

### TypeScript (Frontend)
- Use **TypeScript** — no `any` types unless absolutely necessary
- Components use **functional style** with hooks
- Follow the existing naming conventions (PascalCase for components, camelCase for functions)

## 🧪 Testing

```bash
# Backend tests
cd backend
python -m pytest tests/ -v

# Frontend build check
cd frontend
npm run build
```

## 🐛 Reporting Issues

When reporting bugs, please include:
1. Steps to reproduce
2. Expected vs actual behavior
3. Browser / OS / Python version
4. Error logs or screenshots

## 💡 Feature Requests

Open an issue with the `enhancement` label describing:
- The problem you're trying to solve
- Your proposed solution
- Any alternatives you've considered

## 📄 License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
