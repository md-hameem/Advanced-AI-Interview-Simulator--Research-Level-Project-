"""
Advanced AI Interview Simulator - Multi-Agent Evaluation Service
Refactors evaluation to use a panel of specialized agents (Tech Lead, HR) 
and a Coordinator for final aggregation.
"""
import asyncio
import logging
from typing import Dict, Any

from models.interview import Interview, InterviewQuestion
from services.llm_client import llm_client, PERSONA_GUIDANCE

logger = logging.getLogger(__name__)

# ─── Specialized Agent Prompts ──────────────────────────────────────────

TECH_LEAD_PROMPT = """You are a strictly technical 'Tech Lead' evaluator on an interview panel.
Your ONLY job is to assess the technical accuracy, depth, and reasoning of the candidate's answer.
Ignore their communication style or formatting. Focus purely on engineering.

{persona_guidance}

Question: {question_text}
Topic: {topic}
Difficulty: {difficulty}
Expected Concepts: {expected_concepts}

Candidate's Answer: {answer_text}

Evaluate on:
1. Technical Correctness (0-5)
2. Depth of Explanation (0-5)
3. Reasoning & Problem Solving (0-5)

Return JSON:
{{
    "correctness_score": 0.0,
    "depth_score": 0.0,
    "reasoning_score": 0.0,
    "technical_feedback": "Specific technical critique..."
}}"""

HR_AGENT_PROMPT = """You are a behavioral 'HR / Recruiter' evaluator on an interview panel.
Your ONLY job is to assess the communication clarity, structure, professionalism, and confidence of the candidate's answer.
Do not verify technical correctness.

{persona_guidance}

Question: {question_text}
Candidate's Answer: {answer_text}

Evaluate on:
1. Communication Clarity (0-5)

Return JSON:
{{
    "clarity_score": 0.0,
    "communication_feedback": "Specific communication critique...",
    "identified_strengths": ["...", "..."],
    "identified_weaknesses": ["...", "..."]
}}"""

COORDINATOR_PROMPT = """You are the Coordinator of an interview panel. You have received feedback from two specialized agents: a Tech Lead and an HR representative.
Your job is to aggregate their scores and feedback into a final, unified response for the candidate.

Tech Lead Score & Feedback:
{tech_lead_feedback}

HR Score & Feedback:
{hr_feedback}

Combine these into a cohesive evaluation. The scores should generally match what the agents provided, but you can adjust if there is a massive discrepancy.
Calculate an `overall_question_score` (0-10) based on their inputs.

Return JSON in this EXACT format:
{{
    "correctness_score": 0.0,
    "depth_score": 0.0,
    "clarity_score": 0.0,
    "reasoning_score": 0.0,
    "overall_question_score": 0.0,
    "feedback": "Unified, highly constructive feedback combining technical and communication aspects.",
    "strengths": ["...", "..."],
    "weaknesses": ["...", "..."]
}}"""

class MultiAgentEvaluator:
    """Uses multiple specialized LLM agents to evaluate an answer."""
    
    async def evaluate_answer(self, interview: Interview, question: InterviewQuestion) -> Dict[str, Any]:
        """Runs the multi-agent evaluation pipeline."""
        
        persona_guidance = PERSONA_GUIDANCE.get(getattr(interview, "persona", "default"), PERSONA_GUIDANCE["default"])
        
        # 1. Prepare prompts for parallel execution
        tech_prompt = TECH_LEAD_PROMPT.format(
            persona_guidance=persona_guidance,
            question_text=question.question_text,
            topic=question.topic or "general",
            difficulty=question.difficulty,
            expected_concepts=", ".join(question.expected_concepts or []),
            answer_text=question.answer_text,
        )
        
        hr_prompt = HR_AGENT_PROMPT.format(
            persona_guidance=persona_guidance,
            question_text=question.question_text,
            answer_text=question.answer_text,
        )

        try:
            # 2. Run specialized agents concurrently
            tech_task = asyncio.create_task(llm_client.generate_json(tech_prompt))
            hr_task = asyncio.create_task(llm_client.generate_json(hr_prompt))
            
            tech_result, hr_result = await asyncio.gather(tech_task, hr_task, return_exceptions=True)
            
            # Handle potential failures gracefully
            if isinstance(tech_result, Exception):
                logger.error(f"Tech Lead Agent failed: {tech_result}")
                tech_result = {"correctness_score": 2.5, "depth_score": 2.5, "reasoning_score": 2.5, "technical_feedback": "Evaluation failed."}
                
            if isinstance(hr_result, Exception):
                logger.error(f"HR Agent failed: {hr_result}")
                hr_result = {"clarity_score": 2.5, "communication_feedback": "Evaluation failed.", "identified_strengths": [], "identified_weaknesses": []}

            # 3. Coordinator Agent step
            coordinator_prompt = COORDINATOR_PROMPT.format(
                tech_lead_feedback=str(tech_result),
                hr_feedback=str(hr_result),
            )
            
            final_eval = await llm_client.generate_json(coordinator_prompt)
            
            # Clamp final scores
            for key in ["correctness_score", "depth_score", "clarity_score", "reasoning_score"]:
                final_eval[key] = max(0, min(5, float(final_eval.get(key, 0))))
            final_eval["overall_question_score"] = max(0, min(10, float(final_eval.get("overall_question_score", 0))))
            
            return final_eval

        except Exception as e:
            logger.error(f"Multi-Agent Evaluation Pipeline Failed: {e}")
            return {
                "correctness_score": 2.5,
                "depth_score": 2.5,
                "clarity_score": 2.5,
                "reasoning_score": 2.5,
                "overall_question_score": 5.0,
                "feedback": "Evaluation temporarily unavailable. Score is a placeholder.",
                "strengths": [],
                "weaknesses": [],
            }

multi_agent_evaluator = MultiAgentEvaluator()
