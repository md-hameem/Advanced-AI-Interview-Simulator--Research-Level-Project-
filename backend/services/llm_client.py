"""
Advanced AI Interview Simulator - LLM Client
Abstracted LLM interface using Google Gemini.
"""
import json
import logging
from typing import Optional

from groq import AsyncGroq

from config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Abstracted LLM client for generating questions, evaluations, and feedback."""

    def __init__(self):
        if not settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set — LLM features will be unavailable.")
            self.client = None
            return

        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    async def generate(self, prompt: str, temperature: Optional[float] = None) -> str:
        """Generate a text response from the LLM."""
        if not self.client:
            raise RuntimeError("LLM not configured. Set GROQ_API_KEY in .env file.")

        try:
            response = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=settings.LLM_MODEL,
                temperature=temperature or settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise

    async def generate_json(self, prompt: str, temperature: Optional[float] = None) -> dict:
        """Generate a JSON response from the LLM. Parses the result into a dict."""
        json_prompt = f"""{prompt}\n\nIMPORTANT: Return ONLY valid JSON. No markdown code blocks, no extra text. Just the JSON object."""

        if not self.client:
            raise RuntimeError("LLM not configured. Set GROQ_API_KEY in .env file.")

        try:
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful API that only returns valid JSON objects."},
                    {"role": "user", "content": json_prompt}
                ],
                model=settings.LLM_MODEL,
                temperature=temperature or 0.3,
                max_tokens=settings.LLM_MAX_TOKENS,
                response_format={"type": "json_object"}
            )
            raw = response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise

        # Clean up common LLM response artifacts if they bleed through
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

PERSONA_GUIDANCE = {
    "default": "Conduct a standard, balanced technical interview. Focus on assessing technical competence and clear communication.",
    "google": "Act as a Google interviewer. Be highly analytical and academically rigorous. Focus heavily on algorithmic optimality (Time/Space complexity), edge cases, scalability limits, and deep theoretical understanding of data structures and systems.",
    "amazon": "Act as an Amazon interviewer. Focus relentlessly on the Leadership Principles (Customer Obsession, Ownership, Deliver Results, Dive Deep). Demand specific, quantifiable examples of past behavior using the STAR method. Probe for data-driven decisions and customer impact.",
    "startup": "Act as a fast-paced Startup founder. Focus on practical engineering impact, speed of delivery, dealing with ambiguity, wearing multiple hats, and getting things done efficiently rather than academic perfection. Favor scrappy, scalable solutions."
}

GENERATE_QUESTION_PROMPT = """{persona_guidance}

Generate an interview question based on the following parameters:

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


EVALUATE_ANSWER_PROMPT = """{persona_guidance}

Evaluate the candidate's answer using a structured rubric.

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


GENERATE_FOLLOW_UP_PROMPT = """{persona_guidance}

Based on the candidate's answer, generate an appropriate follow-up question.

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

Emotion Tracking Data (if available):
{emotion_data}

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


GENERATE_LEARNING_PLAN_PROMPT = """You are an expert career coach and technical mentor.
Analyze the following aggregated weaknesses and feedback from the candidate's recent mock interviews.

Candidate Name: {candidate_name}
Target Role: {target_role}

Recent Interview Weaknesses:
{history_context}

Create a highly actionable, personalized 4-week learning plan in Markdown format.
Include recommended reading topics, practice areas, and specific actionable advice to address these recurring weaknesses.
Do not use generic advice; tie everything back to the detected weaknesses.
"""


# Singleton
llm_client = LLMClient()
