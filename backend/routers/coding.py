"""
Advanced AI Interview Simulator - Coding API Router
Endpoints for coding questions, code execution, and evaluation.
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.code_evaluator import code_evaluator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/coding", tags=["coding"])


class CodeSubmission(BaseModel):
    code: str
    language: str = "python"


class CodeExecution(BaseModel):
    code: str
    language: str = "python"
    stdin: str = ""


# ─── Coding Questions ───────────────────────────────────────────────

@router.get("/questions")
def list_coding_questions(difficulty: str | None = None):
    """List available coding questions, optionally filtered by difficulty."""
    from services.code_evaluator import CODING_QUESTIONS
    questions = CODING_QUESTIONS
    if difficulty:
        questions = [q for q in questions if q["difficulty"] == difficulty]
    return [
        {
            "id": q["id"],
            "title": q["title"],
            "difficulty": q["difficulty"],
            "topics": q["topics"],
        }
        for q in questions
    ]


@router.get("/questions/{question_id}")
def get_coding_question(question_id: str, language: str = "python"):
    """Get a specific coding question with its starter code."""
    q = code_evaluator.get_question_by_id(question_id)
    if not q:
        raise HTTPException(status_code=404, detail=f"Question '{question_id}' not found")
    return {
        "id": q["id"],
        "title": q["title"],
        "difficulty": q["difficulty"],
        "description": q["description"],
        "starter_code": q["starter_code"].get(language, q["starter_code"].get("python", "")),
        "topics": q["topics"],
        "optimal_complexity": q["optimal_complexity"],
        "num_test_cases": len(q["test_cases"]),
    }


@router.get("/random")
def get_random_question(difficulty: str = "easy", language: str = "python"):
    """Get a random coding question matching the difficulty."""
    q = code_evaluator.get_coding_question(difficulty)
    return {
        "id": q["id"],
        "title": q["title"],
        "difficulty": q["difficulty"],
        "description": q["description"],
        "starter_code": q["starter_code"].get(language, q["starter_code"].get("python", "")),
        "topics": q["topics"],
        "optimal_complexity": q["optimal_complexity"],
        "num_test_cases": len(q["test_cases"]),
    }


# ─── Code Execution ─────────────────────────────────────────────────

@router.post("/execute")
async def execute_code(body: CodeExecution):
    """Execute code and return output (sandboxed)."""
    result = await code_evaluator.execute_code(body.code, body.language, body.stdin)
    return result


# ─── Full Evaluation ─────────────────────────────────────────────────

@router.post("/evaluate/{question_id}")
async def evaluate_code(question_id: str, body: CodeSubmission):
    """
    Full code evaluation pipeline:
    - Run test cases
    - Analyze complexity
    - LLM code review
    """
    result = await code_evaluator.evaluate(body.code, question_id, body.language)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ─── Individual Steps ────────────────────────────────────────────────

@router.post("/test/{question_id}")
async def run_tests(question_id: str, body: CodeSubmission):
    """Run test cases only (without LLM review)."""
    q = code_evaluator.get_question_by_id(question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    result = await code_evaluator.run_tests(body.code, body.language, q["test_cases"])
    return result


@router.post("/complexity")
def analyze_complexity(body: CodeSubmission):
    """Analyze time and space complexity (Python only)."""
    result = code_evaluator.analyze_complexity(body.code, body.language)
    return result
