"""
Advanced AI Interview Simulator - LLM Client
Abstracted LLM interface using Google Gemini.
"""
import json
import logging
from typing import Optional

import google.generativeai as genai

from config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Abstracted LLM client for generating questions, evaluations, and feedback."""

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set — LLM features will be unavailable.")
            self.model = None
            return

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.LLM_MODEL)

    async def generate(self, prompt: str, temperature: Optional[float] = None) -> str:
        """Generate a text response from the LLM."""
        if not self.model:
            raise RuntimeError("LLM not configured. Set GEMINI_API_KEY in .env file.")

        config = genai.GenerationConfig(
            temperature=temperature or settings.LLM_TEMPERATURE,
            max_output_tokens=settings.LLM_MAX_TOKENS,
        )

        try:
            response = self.model.generate_content(prompt, generation_config=config)
            return response.text
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise

    async def generate_json(self, prompt: str, temperature: Optional[float] = None) -> dict:
        """Generate a JSON response from the LLM. Parses the result into a dict."""
        json_prompt = f"""{prompt}

IMPORTANT: Return ONLY valid JSON. No markdown code blocks, no extra text. Just the JSON object."""

        raw = await self.generate(json_prompt, temperature=temperature or 0.3)

        # Clean up common LLM response artifacts
        cleaned = raw.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {raw[:200]}")
            raise ValueError(f"LLM returned invalid JSON: {e}")


# ─── Prompt Templates ────────────────────────────────────────────────────

GENERATE_QUESTION_PROMPT = """You are an expert technical interviewer. Generate an interview question based on the following parameters:

Interview Type: {interview_type}
Difficulty: {difficulty}
Topic Area: {topic}
Candidate Experience: {experience_years} years
Skills: {skills}

Previous questions asked (avoid repetition):
{previous_questions}

Performance context:
{performance_context}

Generate a single interview question that is:
1. Appropriate for the difficulty level
2. Relevant to the topic area
3. Different from previous questions asked
4. Designed to test understanding, not just memorization

Return JSON in this exact format:
{{
    "question_text": "The interview question",
    "question_type": "technical|behavioral|coding|system_design",
    "topic": "specific topic",
    "difficulty": "easy|medium|hard|expert",
    "expected_concepts": ["concept1", "concept2", "concept3"],
    "hints": ["hint1 (subtle)", "hint2 (moderate)", "hint3 (direct)"]
}}"""


EVALUATE_ANSWER_PROMPT = """You are an expert technical interview evaluator. Evaluate the candidate's answer using a structured rubric.

Question: {question_text}
Question Type: {question_type}
Topic: {topic}
Difficulty: {difficulty}
Expected Key Concepts: {expected_concepts}

Candidate's Answer: {answer_text}

Evaluate the answer on these criteria (each 0-5):

1. **Technical Correctness** (0-5): Is the answer factually correct? Are there any errors?
2. **Depth of Explanation** (0-5): Does the answer demonstrate deep understanding or just surface-level knowledge?
3. **Communication Clarity** (0-5): Is the answer well-organized, clear, and easy to follow?
4. **Reasoning & Problem Solving** (0-5): Does the answer show good analytical thinking and methodical approach?

Also provide:
- An overall score (0-10)
- Specific strengths (list)
- Specific weaknesses (list)
- Constructive feedback paragraph

Return JSON in this exact format:
{{
    "correctness_score": 0.0,
    "depth_score": 0.0,
    "clarity_score": 0.0,
    "reasoning_score": 0.0,
    "overall_question_score": 0.0,
    "feedback": "Detailed constructive feedback...",
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"]
}}"""


GENERATE_FOLLOW_UP_PROMPT = """You are an expert technical interviewer. Based on the candidate's answer, generate an appropriate follow-up question.

Original Question: {original_question}
Candidate's Answer: {answer_text}
Evaluation Summary: The candidate scored {overall_score}/10

Their strengths were: {strengths}
Their weaknesses were: {weaknesses}

Generate a follow-up question that:
1. Probes deeper into areas where the candidate was weak
2. Tests understanding at a deeper level
3. Is a natural continuation of the conversation

Return JSON:
{{
    "question_text": "The follow-up question",
    "question_type": "{question_type}",
    "topic": "{topic}",
    "difficulty": "{adjusted_difficulty}",
    "expected_concepts": ["concept1", "concept2"],
    "hints": ["hint1", "hint2"]
}}"""


GENERATE_REPORT_PROMPT = """You are an expert interview evaluator. Generate a comprehensive candidate assessment report.

Candidate: {candidate_name}
Target Role: {target_role}
Interview Type: {interview_type}

Question-by-Question Results:
{question_results}

Overall Scores:
- Technical: {technical_score}/5
- Communication: {communication_score}/5
- Problem Solving: {problem_solving_score}/5
- Overall: {overall_score}/10

Generate a professional assessment report with:
1. Executive summary (2-3 sentences)
2. Top 3-5 strengths with examples
3. Top 3-5 areas for improvement with examples
4. Hiring recommendation: "strong_hire", "hire", "lean_hire", "lean_no_hire", or "no_hire"
5. Specific study recommendations for the candidate

Return JSON:
{{
    "executive_summary": "...",
    "strengths": ["strength with example 1", "strength 2", ...],
    "weaknesses": ["weakness with example 1", "weakness 2", ...],
    "recommendation": "hire|no_hire|strong_hire|lean_hire|lean_no_hire",
    "study_recommendations": ["topic1", "topic2", ...],
    "detailed_feedback": "Multi-paragraph detailed feedback..."
}}"""


# Singleton
llm_client = LLMClient()
