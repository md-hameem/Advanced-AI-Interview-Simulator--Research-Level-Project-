"""
Advanced AI Interview Simulator - Interview API Router
Endpoints for managing interviews, submitting answers, and getting reports.
"""
import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from models.interview import Candidate, Interview, InterviewQuestion, InterviewStatus
from schemas import (
    CandidateCreate, CandidateResponse,
    InterviewCreate, InterviewResponse,
    QuestionResponse, AnswerSubmit, EvaluationResponse,
    InterviewReportResponse,
)
from services.interview_agent import interview_agent
from services.pdf_generator import pdf_generator

router = APIRouter(prefix="/api", tags=["interview"])


# ─── Candidate Endpoints ─────────────────────────────────────────────────

@router.post("/candidates", response_model=CandidateResponse)
def create_candidate(data: CandidateCreate, db: Session = Depends(get_db)):
    """Register a new candidate."""
    candidate = Candidate(
        name=data.name,
        email=data.email,
        target_role=data.target_role,
        experience_years=data.experience_years,
        skills=data.skills,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.get("/candidates", response_model=list[CandidateResponse])
def list_candidates(db: Session = Depends(get_db)):
    """List all candidates."""
    return db.query(Candidate).order_by(Candidate.created_at.desc()).all()


@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: str, db: Session = Depends(get_db)):
    """Get a specific candidate."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.get("/candidates/{candidate_id}/learning-plan")
async def get_learning_plan(candidate_id: str, db: Session = Depends(get_db)):
    """Generate a personalized learning plan based on past interview weaknesses."""
    try:
        plan = await interview_agent.generate_learning_plan(db, candidate_id)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Interview Endpoints ─────────────────────────────────────────────────

@router.post("/interviews", response_model=InterviewResponse)
def create_interview(data: InterviewCreate, db: Session = Depends(get_db)):
    """Create a new interview session."""
    candidate = db.query(Candidate).filter(Candidate.id == data.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    interview = Interview(
        candidate_id=data.candidate_id,
        interview_type=data.interview_type,
        difficulty=data.difficulty,
        persona=data.persona,
        total_questions=data.total_questions,
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


@router.get("/interviews", response_model=list[InterviewResponse])
def list_interviews(db: Session = Depends(get_db)):
    """List all interviews."""
    return db.query(Interview).order_by(Interview.created_at.desc()).all()


@router.get("/interviews/{interview_id}", response_model=InterviewResponse)
def get_interview(interview_id: str, db: Session = Depends(get_db)):
    """Get interview details."""
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview


# ─── Interview Flow ──────────────────────────────────────────────────────

@router.post("/interviews/{interview_id}/start", response_model=QuestionResponse)
async def start_interview(interview_id: str, db: Session = Depends(get_db)):
    """Start an interview session — generates the first question."""
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if interview.status != InterviewStatus.PENDING.value:
        raise HTTPException(status_code=400, detail="Interview already started or completed")

    try:
        question = await interview_agent.start_interview(db, interview_id)
        return question
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interviews/{interview_id}/questions/{question_id}/answer")
async def submit_answer(
    interview_id: str,
    question_id: str,
    data: AnswerSubmit,
    db: Session = Depends(get_db),
):
    """Submit an answer to a question. Returns evaluation and next question."""
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if interview.status != InterviewStatus.IN_PROGRESS.value:
        raise HTTPException(status_code=400, detail="Interview is not in progress")

    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == question_id,
        InterviewQuestion.interview_id == interview_id,
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    if question.answer_text:
        raise HTTPException(status_code=400, detail="Question already answered")

    try:
        result = await interview_agent.submit_answer(db, interview_id, question_id, data.answer_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/interviews/{interview_id}/questions", response_model=list[QuestionResponse])
def get_interview_questions(interview_id: str, db: Session = Depends(get_db)):
    """Get all questions for an interview."""
    questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.interview_id == interview_id
    ).order_by(InterviewQuestion.order_index).all()
    return questions


@router.post("/interviews/{interview_id}/hint")
def get_hint(interview_id: str, db: Session = Depends(get_db)):
    """Get a hint for the current question."""
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    current_question = db.query(InterviewQuestion).filter(
        InterviewQuestion.interview_id == interview_id,
        InterviewQuestion.answer_text.is_(None),
    ).order_by(InterviewQuestion.order_index.desc()).first()

    if not current_question:
        raise HTTPException(status_code=404, detail="No unanswered question found")

    hints = current_question.hints or []
    context = interview.context or {}
    hints_given = context.get(f"hints_given_{current_question.id}", 0)

    if hints_given >= len(hints):
        return {"hint": "No more hints available.", "hints_remaining": 0}

    hint = hints[hints_given]
    context[f"hints_given_{current_question.id}"] = hints_given + 1
    interview.context = context
    db.commit()

    return {
        "hint": hint,
        "hints_remaining": len(hints) - hints_given - 1,
    }


# ─── Report Endpoints ────────────────────────────────────────────────────

@router.get("/interviews/{interview_id}/report")
async def get_interview_report(interview_id: str, db: Session = Depends(get_db)):
    """Get the full candidate evaluation report."""
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if interview.status != InterviewStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail="Interview not yet completed")

    try:
        report = await interview_agent.generate_report(db, interview_id)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/interviews/{interview_id}/report/pdf")
async def download_report_pdf(interview_id: str, db: Session = Depends(get_db)):
    """Download the candidate assessment report as a PDF."""
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if interview.status != InterviewStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail="Interview not yet completed")

    try:
        report = await interview_agent.generate_report(db, interview_id)
        pdf_bytes = pdf_generator.generate(report)

        candidate_name = report.get("candidate_name", "candidate").replace(" ", "_").lower()
        filename = f"interview_report_{candidate_name}_{interview_id[:8]}.pdf"

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


# ─── Dashboard / Analytics ───────────────────────────────────────────────

@router.get("/analytics/overview")
def get_analytics_overview(db: Session = Depends(get_db)):
    """Get overall analytics data for the dashboard."""
    total_candidates = db.query(Candidate).count()
    total_interviews = db.query(Interview).count()
    completed_interviews = db.query(Interview).filter(
        Interview.status == InterviewStatus.COMPLETED.value
    ).count()

    # Average scores across all completed interviews
    completed = db.query(Interview).filter(Interview.status == InterviewStatus.COMPLETED.value).all()

    if completed:
        avg_overall = sum(i.overall_score or 0 for i in completed) / len(completed)
        avg_technical = sum(i.technical_score or 0 for i in completed) / len(completed)
        avg_communication = sum(i.communication_score or 0 for i in completed) / len(completed)
    else:
        avg_overall = avg_technical = avg_communication = 0

    return {
        "total_candidates": total_candidates,
        "total_interviews": total_interviews,
        "completed_interviews": completed_interviews,
        "average_scores": {
            "overall": round(avg_overall, 2),
            "technical": round(avg_technical, 2),
            "communication": round(avg_communication, 2),
        },
    }
