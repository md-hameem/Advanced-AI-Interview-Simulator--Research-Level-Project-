"""
Advanced AI Interview Simulator - Pydantic Schemas
Request/Response models for API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ─── Candidate Schemas ───────────────────────────────────────────────────

class CandidateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: Optional[str] = None
    target_role: Optional[str] = None
    experience_years: int = Field(default=0, ge=0)
    skills: list[str] = Field(default_factory=list)


class CandidateResponse(BaseModel):
    id: str
    name: str
    email: Optional[str]
    target_role: Optional[str]
    experience_years: int
    skills: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Interview Schemas ───────────────────────────────────────────────────

class InterviewCreate(BaseModel):
    candidate_id: str
    interview_type: str = Field(default="mixed", pattern="^(technical|behavioral|coding|system_design|mixed)$")
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard|expert)$")
    total_questions: int = Field(default=10, ge=1, le=30)


class InterviewResponse(BaseModel):
    id: str
    candidate_id: str
    interview_type: str
    status: str
    difficulty: str
    current_question_index: int
    total_questions: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    overall_score: Optional[float]
    technical_score: Optional[float]
    communication_score: Optional[float]
    problem_solving_score: Optional[float]
    recommendation: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Question Schemas ────────────────────────────────────────────────────

class QuestionResponse(BaseModel):
    id: str
    order_index: int
    question_text: str
    question_type: str
    difficulty: str
    topic: Optional[str]
    is_follow_up: int
    hints: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class AnswerSubmit(BaseModel):
    answer_text: str = Field(..., min_length=1)


class EvaluationResponse(BaseModel):
    question_id: str
    correctness_score: float
    depth_score: float
    clarity_score: float
    reasoning_score: float
    overall_question_score: float
    feedback: str
    strengths: list[str]
    weaknesses: list[str]
    next_question: Optional[QuestionResponse] = None
    interview_completed: bool = False


# ─── Report Schemas ──────────────────────────────────────────────────────

class InterviewReportResponse(BaseModel):
    interview_id: str
    candidate_name: str
    target_role: Optional[str]
    interview_type: str
    overall_score: float
    technical_score: float
    communication_score: float
    problem_solving_score: float
    recommendation: str
    total_questions: int
    questions_answered: int
    strengths: list[str]
    weaknesses: list[str]
    detailed_feedback: str
    question_scores: list[dict]


# ─── Speech Schemas ──────────────────────────────────────────────────────

class SpeechMetrics(BaseModel):
    transcript: str
    words_per_minute: float
    pause_count: int
    filler_word_count: int
    filler_words_detected: list[str]
    confidence_score: float  # 0-1
    total_duration_seconds: float
