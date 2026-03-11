"""
Advanced AI Interview Simulator - Behavioral Interview Analyzer
STAR framework detection, behavioral question bank, and LLM-based behavioral assessment.
"""
import logging
import json
import random
from typing import Optional

from services.llm_client import llm_client

logger = logging.getLogger(__name__)


# ─── STAR Framework Components ──────────────────────────────────────────
# Situation, Task, Action, Result
STAR_INDICATORS = {
    "situation": [
        "at my previous", "when i was", "in my last role", "at the time",
        "we were facing", "there was a", "our team was", "the company",
        "last year", "a few months ago", "during my time", "while working",
        "the context was", "the background is", "at that point",
        "i was working on", "the project involved", "we had a situation",
    ],
    "task": [
        "my responsibility", "i was tasked", "i needed to", "the goal was",
        "i was supposed to", "my role was", "i had to", "the objective",
        "the challenge was", "what i needed", "i was asked to",
        "the expectation", "my assignment", "i was responsible for",
        "the requirement was", "we needed to deliver",
    ],
    "action": [
        "i decided to", "i implemented", "i created", "i built",
        "i organized", "i led", "i spoke with", "i collaborated",
        "i analyzed", "i researched", "i proposed", "i developed",
        "i designed", "i refactored", "i communicated", "i scheduled",
        "i initiated", "i set up", "i stepped in", "i took the initiative",
        "my approach was", "the steps i took", "i first", "then i",
    ],
    "result": [
        "as a result", "the outcome was", "we achieved", "this led to",
        "the impact was", "we improved", "we reduced", "we increased",
        "the team was able", "it resulted in", "the project was",
        "we successfully", "the metric", "we delivered", "ultimately",
        "in the end", "the final result", "this saved", "this generated",
        "the feedback was", "i learned that",
    ],
}

# ─── Behavioral Competencies ───────────────────────────────────────────
BEHAVIORAL_COMPETENCIES = [
    "leadership",
    "teamwork",
    "conflict_resolution",
    "problem_solving",
    "communication",
    "adaptability",
    "ownership",
    "initiative",
    "time_management",
    "mentoring",
]

# ─── Behavioral Question Bank ──────────────────────────────────────────
BEHAVIORAL_QUESTIONS = [
    # Leadership
    {
        "id": "bq_lead_1",
        "question": "Tell me about a time you led a project or team through a difficult challenge.",
        "competency": "leadership",
        "difficulty": "medium",
        "follow_ups": [
            "How did you keep the team motivated?",
            "What would you do differently if faced with a similar situation?",
        ],
    },
    {
        "id": "bq_lead_2",
        "question": "Describe a situation where you had to make a tough decision without full information.",
        "competency": "leadership",
        "difficulty": "hard",
        "follow_ups": [
            "How did you mitigate the risk of making a wrong decision?",
            "What was the outcome and what did you learn?",
        ],
    },
    # Teamwork
    {
        "id": "bq_team_1",
        "question": "Give me an example of a time you worked effectively with a cross-functional team.",
        "competency": "teamwork",
        "difficulty": "easy",
        "follow_ups": [
            "What was your specific role in the team?",
            "How did you handle differing perspectives?",
        ],
    },
    {
        "id": "bq_team_2",
        "question": "Tell me about a time a teammate disagreed with your approach. How did you handle it?",
        "competency": "teamwork",
        "difficulty": "medium",
        "follow_ups": [
            "Were you able to find common ground?",
            "How did the relationship evolve afterward?",
        ],
    },
    # Conflict Resolution
    {
        "id": "bq_conflict_1",
        "question": "Describe a time you had a significant conflict with a coworker. How did you resolve it?",
        "competency": "conflict_resolution",
        "difficulty": "medium",
        "follow_ups": [
            "What was the root cause of the disagreement?",
            "How did you ensure it didn't affect the project?",
        ],
    },
    # Problem Solving
    {
        "id": "bq_solve_1",
        "question": "Tell me about a complex technical problem you solved. Walk me through your approach.",
        "competency": "problem_solving",
        "difficulty": "medium",
        "follow_ups": [
            "What alternatives did you consider?",
            "How did you validate your solution?",
        ],
    },
    {
        "id": "bq_solve_2",
        "question": "Describe a time when you had to debug an issue under tight time pressure.",
        "competency": "problem_solving",
        "difficulty": "hard",
        "follow_ups": [
            "How did you prioritize what to investigate first?",
            "What processes did you put in place to prevent similar issues?",
        ],
    },
    # Adaptability
    {
        "id": "bq_adapt_1",
        "question": "Tell me about a time you had to quickly learn a new technology or tool for a project.",
        "competency": "adaptability",
        "difficulty": "easy",
        "follow_ups": [
            "What was your learning strategy?",
            "How long did it take to become productive?",
        ],
    },
    # Ownership
    {
        "id": "bq_own_1",
        "question": "Describe a time you went above and beyond what was expected of you.",
        "competency": "ownership",
        "difficulty": "easy",
        "follow_ups": [
            "What motivated you to take extra initiative?",
            "How was your effort recognized?",
        ],
    },
    {
        "id": "bq_own_2",
        "question": "Tell me about a time you took ownership of a failing project and turned it around.",
        "competency": "ownership",
        "difficulty": "hard",
        "follow_ups": [
            "What was the state of the project when you stepped in?",
            "What specific changes did you make?",
        ],
    },
    # Communication
    {
        "id": "bq_comm_1",
        "question": "Give me an example of a time you had to explain a complex technical concept to a non-technical stakeholder.",
        "competency": "communication",
        "difficulty": "medium",
        "follow_ups": [
            "How did you gauge their understanding?",
            "What techniques did you use to simplify the concept?",
        ],
    },
    # Initiative
    {
        "id": "bq_init_1",
        "question": "Tell me about a time you identified a problem before anyone else and took steps to solve it.",
        "competency": "initiative",
        "difficulty": "medium",
        "follow_ups": [
            "How did you convince others that this was worth addressing?",
            "What was the impact of your proactive approach?",
        ],
    },
]


class BehavioralAnalyzer:
    """
    Analyzes behavioral interview answers using:
    1. Rule-based STAR component detection (keyword matching)
    2. LLM-based deep STAR analysis and scoring
    3. Competency mapping and assessment
    """

    def get_question(
        self, competency: str | None = None, difficulty: str = "medium"
    ) -> dict:
        """Get a behavioral question, optionally filtered by competency/difficulty."""
        pool = BEHAVIORAL_QUESTIONS
        if competency:
            pool = [q for q in pool if q["competency"] == competency]
        diff_pool = [q for q in pool if q["difficulty"] == difficulty]
        if diff_pool:
            pool = diff_pool
        if not pool:
            pool = BEHAVIORAL_QUESTIONS
        return random.choice(pool)

    def get_question_by_id(self, question_id: str) -> dict | None:
        """Look up a behavioral question by ID."""
        for q in BEHAVIORAL_QUESTIONS:
            if q["id"] == question_id:
                return q
        return None

    def get_all_questions(self, competency: str | None = None) -> list[dict]:
        """Get all behavioral questions, optionally filtered."""
        if competency:
            return [q for q in BEHAVIORAL_QUESTIONS if q["competency"] == competency]
        return BEHAVIORAL_QUESTIONS

    # ─── Rule-Based STAR Detection ───────────────────────────────────

    def detect_star_components(self, answer: str) -> dict:
        """
        Detect STAR components using keyword matching.
        Returns which components are present with confidence and matched phrases.
        """
        answer_lower = answer.lower()
        results = {}

        for component, indicators in STAR_INDICATORS.items():
            matches = []
            for indicator in indicators:
                if indicator in answer_lower:
                    matches.append(indicator)

            # Score based on number of matching indicators
            if len(matches) >= 3:
                confidence = "strong"
                score = 1.0
            elif len(matches) >= 2:
                confidence = "moderate"
                score = 0.7
            elif len(matches) >= 1:
                confidence = "weak"
                score = 0.4
            else:
                confidence = "missing"
                score = 0.0

            results[component] = {
                "detected": len(matches) > 0,
                "confidence": confidence,
                "score": score,
                "matched_indicators": matches,
                "indicator_count": len(matches),
            }

        # Overall STAR score
        component_scores = [v["score"] for v in results.values()]
        overall_star_score = sum(component_scores) / 4  # Average of S, T, A, R

        # Coverage: how many components are present
        components_present = sum(1 for v in results.values() if v["detected"])

        return {
            "components": results,
            "overall_star_score": round(overall_star_score, 2),
            "components_present": components_present,
            "components_total": 4,
            "star_completeness": f"{components_present}/4",
            "is_complete_star": components_present == 4,
        }

    # ─── LLM-Based Deep Analysis ─────────────────────────────────────

    async def llm_analyze(
        self, answer: str, question: dict, rule_based: dict
    ) -> dict:
        """Deep STAR analysis using LLM."""
        prompt = f"""You are an expert behavioral interview evaluator. Analyze this answer using the STAR framework.

## Question
"{question['question']}"
(Competency being assessed: {question['competency']})

## Candidate's Answer
"{answer}"

## Rule-Based Detection (for reference)
- Situation: {rule_based['components']['situation']['confidence']} ({rule_based['components']['situation']['indicator_count']} indicators)
- Task: {rule_based['components']['task']['confidence']} ({rule_based['components']['task']['indicator_count']} indicators)
- Action: {rule_based['components']['action']['confidence']} ({rule_based['components']['action']['indicator_count']} indicators)
- Result: {rule_based['components']['result']['confidence']} ({rule_based['components']['result']['indicator_count']} indicators)

## Instructions
Evaluate the answer and return a JSON object with:

- "situation_score": 0-5 (how well they described the context/situation)
- "situation_summary": string (what situation they described)
- "task_score": 0-5 (clarity of their specific task/responsibility)
- "task_summary": string (what task they described)
- "action_score": 0-5 (quality and detail of actions taken)
- "action_summary": string (what actions they took)
- "result_score": 0-5 (clarity and impact of results)
- "result_summary": string (what results they achieved)
- "competency_score": 0-5 (how well they demonstrated {question['competency']})
- "communication_score": 0-5 (storytelling clarity, conciseness)
- "specificity_score": 0-5 (concrete examples vs vague generalities)
- "impact_score": 0-5 (measurable impact, quantified results)
- "overall_behavioral_score": 0-10 (weighted overall assessment)
- "feedback": string (detailed evaluation feedback)
- "strengths": list of strengths in their answer
- "improvements": list of specific improvement suggestions
- "missing_elements": list of STAR elements that were weak or missing
- "red_flags": list of any concerning patterns (vague, hypothetical, blaming others)

Return ONLY valid JSON, no markdown.
"""
        try:
            response = await llm_client.generate(prompt)
            analysis = json.loads(response)

            # Ensure all required fields exist
            defaults = {
                "situation_score": 2.5, "situation_summary": "",
                "task_score": 2.5, "task_summary": "",
                "action_score": 2.5, "action_summary": "",
                "result_score": 2.5, "result_summary": "",
                "competency_score": 2.5, "communication_score": 2.5,
                "specificity_score": 2.5, "impact_score": 2.5,
                "overall_behavioral_score": 5,
                "feedback": "", "strengths": [], "improvements": [],
                "missing_elements": [], "red_flags": [],
            }
            for k, v in defaults.items():
                if k not in analysis:
                    analysis[k] = v

            return analysis

        except Exception as e:
            logger.error(f"LLM behavioral analysis failed: {e}")
            # Fall back to rule-based scoring
            star = rule_based
            comp = star["components"]
            return {
                "situation_score": comp["situation"]["score"] * 5,
                "situation_summary": "Analysis unavailable",
                "task_score": comp["task"]["score"] * 5,
                "task_summary": "Analysis unavailable",
                "action_score": comp["action"]["score"] * 5,
                "action_summary": "Analysis unavailable",
                "result_score": comp["result"]["score"] * 5,
                "result_summary": "Analysis unavailable",
                "competency_score": 2.5,
                "communication_score": 2.5,
                "specificity_score": 2.5,
                "impact_score": 2.5,
                "overall_behavioral_score": star["overall_star_score"] * 10,
                "feedback": "LLM analysis unavailable. Scores based on keyword detection.",
                "strengths": [],
                "improvements": [],
                "missing_elements": [k for k, v in comp.items() if not v["detected"]],
                "red_flags": [],
            }

    # ─── Full Analysis Pipeline ──────────────────────────────────────

    async def analyze(self, answer: str, question_id: str) -> dict:
        """
        Full behavioral analysis pipeline:
        1. Rule-based STAR detection
        2. LLM-based deep analysis
        3. Combined scoring
        """
        question = self.get_question_by_id(question_id)
        if not question:
            return {"error": f"Question '{question_id}' not found"}

        # Step 1: Rule-based detection
        rule_based = self.detect_star_components(answer)

        # Step 2: LLM deep analysis
        llm_analysis = await self.llm_analyze(answer, question, rule_based)

        return {
            "question_id": question_id,
            "question_text": question["question"],
            "competency": question["competency"],
            "star_detection": rule_based,
            "analysis": llm_analysis,
            "follow_up_questions": question.get("follow_ups", []),
        }


# Singleton
behavioral_analyzer = BehavioralAnalyzer()
