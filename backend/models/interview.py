"""
Advanced AI Interview Simulator - Database Models
Interview, Question, Answer, and Score models.
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime, ForeignKey, JSON, Enum
)
from sqlalchemy.orm import relationship
import enum

from database import Base


# ─── Enums ───────────────────────────────────────────────────────────────

class InterviewStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class QuestionType(str, enum.Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    CODING = "coding"
    SYSTEM_DESIGN = "system_design"


class Difficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class Persona(str, enum.Enum):
    DEFAULT = "default"
    GOOGLE = "google"
    AMAZON = "amazon"
    STARTUP = "startup"


# ─── Models ──────────────────────────────────────────────────────────────

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=True)
    target_role = Column(String(200), nullable=True)
    experience_years = Column(Integer, default=0)
    skills = Column(JSON, default=list)  # ["python", "ml", "system_design"]
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interviews = relationship("Interview", back_populates="candidate")


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False)
    interview_type = Column(String(50), default="mixed")  # technical, behavioral, coding, mixed
    status = Column(String(20), default=InterviewStatus.PENDING.value)
    difficulty = Column(String(20), default=Difficulty.MEDIUM.value)
    persona = Column(String(20), default=Persona.DEFAULT.value)
    current_question_index = Column(Integer, default=0)
    total_questions = Column(Integer, default=10)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Aggregate scores (filled on completion)
    overall_score = Column(Float, nullable=True)
    technical_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    problem_solving_score = Column(Float, nullable=True)
    recommendation = Column(String(50), nullable=True)  # strong_hire, hire, no_hire

    # Interview context for adaptive questioning
    context = Column(JSON, default=dict)  # Stores conversation history, performance tracking

    # Relationships
    candidate = relationship("Candidate", back_populates="interviews")
    questions = relationship("InterviewQuestion", back_populates="interview", order_by="InterviewQuestion.order_index")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id = Column(String, ForeignKey("interviews.id"), nullable=False)
    order_index = Column(Integer, nullable=False)

    # Question details
    question_text = Column(Text, nullable=False)
    question_type = Column(String(30), default=QuestionType.TECHNICAL.value)
    difficulty = Column(String(20), default=Difficulty.MEDIUM.value)
    topic = Column(String(200), nullable=True)  # e.g., "hash tables", "system design"
    is_follow_up = Column(Integer, default=0)  # 0=original, 1=follow-up
    parent_question_id = Column(String, ForeignKey("interview_questions.id"), nullable=True)

    # Expected answer info (for reference)
    expected_concepts = Column(JSON, default=list)  # Key concepts the answer should cover
    hints = Column(JSON, default=list)  # Progressive hints

    # Candidate's response
    answer_text = Column(Text, nullable=True)
    answer_audio_path = Column(String(500), nullable=True)
    answered_at = Column(DateTime, nullable=True)

    # Evaluation scores
    correctness_score = Column(Float, nullable=True)  # 0-5
    depth_score = Column(Float, nullable=True)  # 0-5
    clarity_score = Column(Float, nullable=True)  # 0-5
    reasoning_score = Column(Float, nullable=True)  # 0-5
    overall_question_score = Column(Float, nullable=True)  # 0-10

    # Detailed feedback
    evaluation_feedback = Column(Text, nullable=True)
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)

    # Speech analytics (if audio provided)
    speech_metrics = Column(JSON, nullable=True)  # WPM, pauses, fillers, confidence

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interview = relationship("Interview", back_populates="questions")
    follow_ups = relationship("InterviewQuestion", backref="parent_question", remote_side=[id])
