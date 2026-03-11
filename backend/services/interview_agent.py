"""
Advanced AI Interview Simulator - Interview Agent Service
Core logic for adaptive interview flow, question generation, and evaluation.
"""
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from models.interview import (
    Candidate, Interview, InterviewQuestion,
    InterviewStatus, Difficulty, QuestionType,
)
from services.llm_client import (
    llm_client,
    GENERATE_QUESTION_PROMPT,
    EVALUATE_ANSWER_PROMPT,
    GENERATE_FOLLOW_UP_PROMPT,
    GENERATE_REPORT_PROMPT,
)

logger = logging.getLogger(__name__)


# ─── Topic pools for question generation ─────────────────────────────────

TOPIC_POOLS = {
    "technical": [
        "data structures", "algorithms", "hash tables", "trees and graphs",
        "dynamic programming", "sorting and searching", "string manipulation",
        "linked lists", "stacks and queues", "recursion", "bit manipulation",
        "concurrency", "databases", "networking", "operating systems",
        "object-oriented programming", "design patterns", "API design",
        "machine learning basics", "python internals",
    ],
    "system_design": [
        "URL shortener", "chat system", "news feed", "search engine",
        "notification system", "rate limiter", "load balancer",
        "distributed cache", "message queue", "file storage system",
    ],
    "behavioral": [
        "leadership", "teamwork", "conflict resolution", "failure handling",
        "time management", "decision making", "communication",
        "adaptability", "initiative", "mentoring",
    ],
    "coding": [
        "array problems", "string problems", "tree traversal",
        "graph algorithms", "dynamic programming", "two pointers",
        "sliding window", "binary search", "backtracking", "greedy algorithms",
    ],
}


class InterviewAgent:
    """Orchestrates the full adaptive interview flow."""

    # ─── Interview Lifecycle ──────────────────────────────────────────

    async def start_interview(self, db: Session, interview_id: str) -> InterviewQuestion:
        """Start an interview and generate the first question."""
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise ValueError(f"Interview {interview_id} not found")

        candidate = db.query(Candidate).filter(Candidate.id == interview.candidate_id).first()

        interview.status = InterviewStatus.IN_PROGRESS.value
        interview.started_at = datetime.utcnow()
        interview.context = {
            "performance_history": [],
            "topics_covered": [],
            "current_difficulty": interview.difficulty,
            "consecutive_correct": 0,
            "consecutive_incorrect": 0,
        }
        db.commit()

        # Generate first question
        question = await self._generate_question(db, interview, candidate)
        return question

    async def submit_answer(
        self, db: Session, interview_id: str, question_id: str, answer_text: str
    ) -> dict:
        """Submit an answer, evaluate it, and generate the next question or complete the interview."""
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise ValueError(f"Interview {interview_id} not found")

        question = db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id).first()
        if not question:
            raise ValueError(f"Question {question_id} not found")

        candidate = db.query(Candidate).filter(Candidate.id == interview.candidate_id).first()

        # Save the answer
        question.answer_text = answer_text
        question.answered_at = datetime.utcnow()
        db.commit()

        # Evaluate the answer
        evaluation = await self._evaluate_answer(question)

        # Update question with scores
        question.correctness_score = evaluation["correctness_score"]
        question.depth_score = evaluation["depth_score"]
        question.clarity_score = evaluation["clarity_score"]
        question.reasoning_score = evaluation["reasoning_score"]
        question.overall_question_score = evaluation["overall_question_score"]
        question.evaluation_feedback = evaluation["feedback"]
        question.strengths = evaluation["strengths"]
        question.weaknesses = evaluation["weaknesses"]
        db.commit()

        # Update interview context for adaptive difficulty
        self._update_context(interview, evaluation)
        db.commit()

        # Determine next action
        result = {
            "question_id": question_id,
            **evaluation,
            "next_question": None,
            "interview_completed": False,
        }

        answered_count = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_id == interview_id,
            InterviewQuestion.answer_text.isnot(None),
        ).count()

        if answered_count >= interview.total_questions:
            # Interview complete
            await self._complete_interview(db, interview)
            result["interview_completed"] = True
        else:
            # Generate next question (or follow-up)
            should_follow_up = self._should_generate_follow_up(evaluation)

            if should_follow_up:
                next_q = await self._generate_follow_up(db, interview, question, evaluation)
            else:
                next_q = await self._generate_question(db, interview, candidate)

            result["next_question"] = {
                "id": next_q.id,
                "order_index": next_q.order_index,
                "question_text": next_q.question_text,
                "question_type": next_q.question_type,
                "difficulty": next_q.difficulty,
                "topic": next_q.topic,
                "is_follow_up": next_q.is_follow_up,
                "hints": next_q.hints or [],
            }

        return result

    # ─── Question Generation ──────────────────────────────────────────

    async def _generate_question(
        self, db: Session, interview: Interview, candidate: Candidate
    ) -> InterviewQuestion:
        """Generate an adaptive question using LLM."""
        context = interview.context or {}
        topics_covered = context.get("topics_covered", [])
        current_difficulty = context.get("current_difficulty", interview.difficulty)

        # Select topic pool
        interview_type = interview.interview_type
        if interview_type == "mixed":
            # Rotate through types
            type_rotation = ["technical", "coding", "system_design", "behavioral"]
            idx = len(topics_covered) % len(type_rotation)
            interview_type = type_rotation[idx]

        topic_pool = TOPIC_POOLS.get(interview_type, TOPIC_POOLS["technical"])
        # Pick a topic not yet covered
        available_topics = [t for t in topic_pool if t not in topics_covered]
        if not available_topics:
            available_topics = topic_pool
        topic = available_topics[0]

        # Get previous questions text
        prev_questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_id == interview.id
        ).all()
        prev_q_text = "\n".join([f"- {q.question_text}" for q in prev_questions]) or "None"

        # Performance context
        perf_history = context.get("performance_history", [])
        perf_text = "No answers yet." if not perf_history else \
            f"Last {len(perf_history)} scores: {[round(p, 1) for p in perf_history[-5:]]}"

        prompt = GENERATE_QUESTION_PROMPT.format(
            interview_type=interview_type,
            difficulty=current_difficulty,
            topic=topic,
            experience_years=candidate.experience_years,
            skills=", ".join(candidate.skills) if candidate.skills else "general",
            previous_questions=prev_q_text,
            performance_context=perf_text,
        )

        try:
            question_data = await llm_client.generate_json(prompt)
        except Exception as e:
            logger.error(f"LLM question generation failed: {e}, using fallback")
            question_data = {
                "question_text": f"Explain the concept of {topic} and its common use cases.",
                "question_type": interview_type,
                "topic": topic,
                "difficulty": current_difficulty,
                "expected_concepts": [topic],
                "hints": [
                    "Think about the basic definition first.",
                    "Consider real-world applications.",
                    f"How does {topic} relate to other concepts?",
                ],
            }

        # Create question record
        next_index = len(prev_questions)
        q = InterviewQuestion(
            interview_id=interview.id,
            order_index=next_index,
            question_text=question_data.get("question_text", f"Explain {topic}"),
            question_type=question_data.get("question_type", interview_type),
            difficulty=question_data.get("difficulty", current_difficulty),
            topic=question_data.get("topic", topic),
            expected_concepts=question_data.get("expected_concepts", []),
            hints=question_data.get("hints", []),
            is_follow_up=0,
        )
        db.add(q)

        # Update covered topics
        topics_covered.append(topic)
        context["topics_covered"] = topics_covered
        interview.context = context
        interview.current_question_index = next_index
        db.commit()
        db.refresh(q)
        return q

    async def _generate_follow_up(
        self, db: Session, interview: Interview, parent_question: InterviewQuestion, evaluation: dict
    ) -> InterviewQuestion:
        """Generate a follow-up question probing the candidate's weaknesses."""
        prompt = GENERATE_FOLLOW_UP_PROMPT.format(
            original_question=parent_question.question_text,
            answer_text=parent_question.answer_text,
            overall_score=evaluation["overall_question_score"],
            strengths=", ".join(evaluation.get("strengths", [])),
            weaknesses=", ".join(evaluation.get("weaknesses", [])),
            question_type=parent_question.question_type,
            topic=parent_question.topic,
            adjusted_difficulty=parent_question.difficulty,
        )

        try:
            follow_up_data = await llm_client.generate_json(prompt)
        except Exception:
            follow_up_data = {
                "question_text": f"Can you elaborate more on your answer about {parent_question.topic}?",
                "question_type": parent_question.question_type,
                "topic": parent_question.topic,
                "difficulty": parent_question.difficulty,
                "expected_concepts": [],
                "hints": [],
            }

        prev_questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_id == interview.id
        ).all()
        next_index = len(prev_questions)

        q = InterviewQuestion(
            interview_id=interview.id,
            order_index=next_index,
            question_text=follow_up_data.get("question_text", "Can you elaborate?"),
            question_type=follow_up_data.get("question_type", parent_question.question_type),
            difficulty=follow_up_data.get("difficulty", parent_question.difficulty),
            topic=follow_up_data.get("topic", parent_question.topic),
            expected_concepts=follow_up_data.get("expected_concepts", []),
            hints=follow_up_data.get("hints", []),
            is_follow_up=1,
            parent_question_id=parent_question.id,
        )
        db.add(q)
        interview.current_question_index = next_index
        db.commit()
        db.refresh(q)
        return q

    # ─── Answer Evaluation ────────────────────────────────────────────

    async def _evaluate_answer(self, question: InterviewQuestion) -> dict:
        """Evaluate a candidate's answer using the rubric-based LLM evaluation."""
        prompt = EVALUATE_ANSWER_PROMPT.format(
            question_text=question.question_text,
            question_type=question.question_type,
            topic=question.topic or "general",
            difficulty=question.difficulty,
            expected_concepts=", ".join(question.expected_concepts or []),
            answer_text=question.answer_text,
        )

        try:
            evaluation = await llm_client.generate_json(prompt)
            # Clamp scores
            for key in ["correctness_score", "depth_score", "clarity_score", "reasoning_score"]:
                evaluation[key] = max(0, min(5, float(evaluation.get(key, 0))))
            evaluation["overall_question_score"] = max(0, min(10, float(evaluation.get("overall_question_score", 0))))
            evaluation.setdefault("feedback", "No feedback available.")
            evaluation.setdefault("strengths", [])
            evaluation.setdefault("weaknesses", [])
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            evaluation = {
                "correctness_score": 2.5,
                "depth_score": 2.5,
                "clarity_score": 2.5,
                "reasoning_score": 2.5,
                "overall_question_score": 5.0,
                "feedback": "Evaluation temporarily unavailable. Score is a placeholder.",
                "strengths": [],
                "weaknesses": [],
            }

        return evaluation

    # ─── Adaptive Logic ───────────────────────────────────────────────

    def _update_context(self, interview: Interview, evaluation: dict):
        """Update interview context with performance data for adaptive difficulty."""
        context = interview.context or {}
        perf_history = context.get("performance_history", [])
        perf_history.append(evaluation["overall_question_score"])

        score = evaluation["overall_question_score"]
        consecutive_correct = context.get("consecutive_correct", 0)
        consecutive_incorrect = context.get("consecutive_incorrect", 0)

        if score >= 7.0:
            consecutive_correct += 1
            consecutive_incorrect = 0
        elif score < 4.0:
            consecutive_incorrect += 1
            consecutive_correct = 0
        else:
            consecutive_correct = 0
            consecutive_incorrect = 0

        # Adjust difficulty
        difficulty_order = ["easy", "medium", "hard", "expert"]
        current = context.get("current_difficulty", interview.difficulty)
        current_idx = difficulty_order.index(current) if current in difficulty_order else 1

        if consecutive_correct >= 2 and current_idx < 3:
            current_idx += 1  # Increase difficulty
        elif consecutive_incorrect >= 2 and current_idx > 0:
            current_idx -= 1  # Decrease difficulty

        context["current_difficulty"] = difficulty_order[current_idx]
        context["performance_history"] = perf_history
        context["consecutive_correct"] = consecutive_correct
        context["consecutive_incorrect"] = consecutive_incorrect
        interview.context = context

    def _should_generate_follow_up(self, evaluation: dict) -> bool:
        """Decide if a follow-up question should be generated."""
        score = evaluation["overall_question_score"]
        # Generate follow-up if answer was mediocre (3-6 range) — probe deeper
        # Very good or very bad answers move to next topic
        return 3.0 <= score <= 6.0

    # ─── Interview Completion ─────────────────────────────────────────

    async def _complete_interview(self, db: Session, interview: Interview):
        """Complete the interview and calculate aggregate scores."""
        questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_id == interview.id,
            InterviewQuestion.answer_text.isnot(None),
        ).all()

        if not questions:
            return

        # Calculate aggregate scores
        correctness_scores = [q.correctness_score for q in questions if q.correctness_score is not None]
        depth_scores = [q.depth_score for q in questions if q.depth_score is not None]
        clarity_scores = [q.clarity_score for q in questions if q.clarity_score is not None]
        reasoning_scores = [q.reasoning_score for q in questions if q.reasoning_score is not None]
        overall_scores = [q.overall_question_score for q in questions if q.overall_question_score is not None]

        avg = lambda lst: sum(lst) / len(lst) if lst else 0

        technical_avg = avg(correctness_scores + depth_scores) if correctness_scores else 0
        communication_avg = avg(clarity_scores) if clarity_scores else 0
        problem_solving_avg = avg(reasoning_scores) if reasoning_scores else 0
        overall_avg = avg(overall_scores) if overall_scores else 0

        interview.technical_score = round(technical_avg, 2)
        interview.communication_score = round(communication_avg, 2)
        interview.problem_solving_score = round(problem_solving_avg, 2)
        interview.overall_score = round(overall_avg, 2)

        # Generate recommendation
        if overall_avg >= 8.0:
            interview.recommendation = "strong_hire"
        elif overall_avg >= 6.5:
            interview.recommendation = "hire"
        elif overall_avg >= 5.0:
            interview.recommendation = "lean_no_hire"
        else:
            interview.recommendation = "no_hire"

        interview.status = InterviewStatus.COMPLETED.value
        interview.completed_at = datetime.utcnow()
        db.commit()

    async def generate_report(self, db: Session, interview_id: str) -> dict:
        """Generate a comprehensive candidate evaluation report."""
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise ValueError("Interview not found")

        candidate = db.query(Candidate).filter(Candidate.id == interview.candidate_id).first()
        questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_id == interview_id,
            InterviewQuestion.answer_text.isnot(None),
        ).order_by(InterviewQuestion.order_index).all()

        question_results = "\n".join([
            f"Q{q.order_index + 1}: {q.question_text}\n"
            f"  Answer: {q.answer_text[:200]}...\n"
            f"  Score: {q.overall_question_score}/10 | "
            f"Correctness: {q.correctness_score}/5 | "
            f"Depth: {q.depth_score}/5 | "
            f"Clarity: {q.clarity_score}/5 | "
            f"Reasoning: {q.reasoning_score}/5\n"
            f"  Strengths: {', '.join(q.strengths or [])}\n"
            f"  Weaknesses: {', '.join(q.weaknesses or [])}\n"
            for q in questions
        ])

        prompt = GENERATE_REPORT_PROMPT.format(
            candidate_name=candidate.name,
            target_role=candidate.target_role or "Software Engineer",
            interview_type=interview.interview_type,
            question_results=question_results,
            technical_score=interview.technical_score or 0,
            communication_score=interview.communication_score or 0,
            problem_solving_score=interview.problem_solving_score or 0,
            overall_score=interview.overall_score or 0,
        )

        try:
            report = await llm_client.generate_json(prompt)
        except Exception:
            report = {
                "executive_summary": "Report generation temporarily unavailable.",
                "strengths": [],
                "weaknesses": [],
                "recommendation": interview.recommendation or "pending",
                "study_recommendations": [],
                "detailed_feedback": "Please try regenerating the report.",
            }

        # Build the full response
        question_scores = [
            {
                "question": q.question_text,
                "type": q.question_type,
                "score": q.overall_question_score,
                "correctness": q.correctness_score,
                "depth": q.depth_score,
                "clarity": q.clarity_score,
                "reasoning": q.reasoning_score,
            }
            for q in questions
        ]

        return {
            "interview_id": interview.id,
            "candidate_name": candidate.name,
            "target_role": candidate.target_role,
            "interview_type": interview.interview_type,
            "overall_score": interview.overall_score or 0,
            "technical_score": interview.technical_score or 0,
            "communication_score": interview.communication_score or 0,
            "problem_solving_score": interview.problem_solving_score or 0,
            "recommendation": report.get("recommendation", interview.recommendation or "pending"),
            "total_questions": interview.total_questions,
            "questions_answered": len(questions),
            "strengths": report.get("strengths", []),
            "weaknesses": report.get("weaknesses", []),
            "detailed_feedback": report.get("detailed_feedback", ""),
            "study_recommendations": report.get("study_recommendations", []),
            "question_scores": question_scores,
        }


# Singleton
interview_agent = InterviewAgent()
