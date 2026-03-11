"""
Advanced AI Interview Simulator - Behavioral Interview API Router
Endpoints for behavioral questions, STAR analysis, and competency assessment.
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.behavioral_analyzer import behavioral_analyzer, BEHAVIORAL_COMPETENCIES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/behavioral", tags=["behavioral"])


class BehavioralAnswer(BaseModel):
    answer: str


# ─── Questions ──────────────────────────────────────────────────────

@router.get("/competencies")
def list_competencies():
    """List all behavioral competencies."""
    return {"competencies": BEHAVIORAL_COMPETENCIES}


@router.get("/questions")
def list_behavioral_questions(competency: str | None = None):
    """List behavioral questions, optionally filtered by competency."""
    questions = behavioral_analyzer.get_all_questions(competency)
    return [
        {
            "id": q["id"],
            "question": q["question"],
            "competency": q["competency"],
            "difficulty": q["difficulty"],
        }
        for q in questions
    ]


@router.get("/questions/{question_id}")
def get_behavioral_question(question_id: str):
    """Get a specific behavioral question with follow-ups."""
    q = behavioral_analyzer.get_question_by_id(question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return q


@router.get("/random")
def get_random_behavioral_question(
    competency: str | None = None, difficulty: str = "medium"
):
    """Get a random behavioral question."""
    q = behavioral_analyzer.get_question(competency, difficulty)
    return q


# ─── Analysis ───────────────────────────────────────────────────────

@router.post("/detect-star")
def detect_star_components(body: BehavioralAnswer):
    """Quick rule-based STAR component detection (no LLM)."""
    result = behavioral_analyzer.detect_star_components(body.answer)
    return result


@router.post("/analyze/{question_id}")
async def analyze_behavioral_answer(question_id: str, body: BehavioralAnswer):
    """
    Full behavioral analysis pipeline:
    - Rule-based STAR detection
    - LLM-based deep analysis (situation, task, action, result scoring)
    - Competency assessment
    """
    result = await behavioral_analyzer.analyze(body.answer, question_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
