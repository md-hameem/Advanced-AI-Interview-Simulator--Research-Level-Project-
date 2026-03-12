"""
ML Pipeline - Synthetic Dataset Generator
Generates training data for all specialized models.
"""
import os
import json
import random
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ─── Technical Q&A Templates ───────────────────────────────────────────

TECH_QUESTIONS = [
    "Explain the difference between a process and a thread.",
    "What is a hash table and how does it handle collisions?",
    "Describe the CAP theorem and its implications for distributed systems.",
    "What are the SOLID principles in object-oriented design?",
    "Explain how garbage collection works in Python.",
    "What is the difference between TCP and UDP?",
    "Describe database normalization and its forms.",
    "What are microservices and how do they compare to monolithic architecture?",
    "Explain Big-O notation with examples.",
    "What is dependency injection and why is it useful?",
    "How does a REST API differ from GraphQL?",
    "Explain the concept of eventual consistency.",
    "What is a binary search tree and what are its time complexities?",
    "Describe the MVC architecture pattern.",
    "What is containerization and how does Docker work?",
]

GOOD_ANSWER_TEMPLATES = [
    "A {concept_a} and a {concept_b} differ in several key ways. First, {detail_1}. Second, {detail_2}. In practice, {practical}. For example, {example}. The key trade-off is {tradeoff}.",
    "The {concept} works by {mechanism}. It achieves this through {detail_1}, which enables {benefit}. A concrete example would be {example}. One important consideration is {consideration}, because {reason}.",
    "There are several aspects to consider. {detail_1}. Additionally, {detail_2}. From a practical standpoint, {practical}. I've used this approach in {experience} where {outcome}.",
]

POOR_ANSWER_TEMPLATES = [
    "I think it's something about {vague_concept}. Not really sure about the details.",
    "{concept} is like a thing that does stuff. It's important I guess.",
    "I don't remember exactly but I think {vague_concept} is related to {wrong_concept}.",
]

# ─── Behavioral Answer Templates ──────────────────────────────────────

STAR_COMPLETE = [
    "At my previous company, {situation}. My task was to {task}. I decided to {action_1}, and then {action_2}. As a result, {result}.",
    "When I was working at {company}, we faced {situation}. I was responsible for {task}. I took the initiative to {action_1} and also {action_2}. This led to {result}, which was recognized by {recognition}.",
    "During my time at {company}, {situation}. The goal was to {task}. My approach was to first {action_1}, then {action_2}. The outcome was {result}, and I learned that {learning}.",
]

STAR_PARTIAL = [
    "I was working on {situation}. I think I did {vague_action}. It went okay.",
    "There was a time when {situation}. I needed to {task}. I'm not sure exactly what I did but it worked out.",
    "At my old job, {situation}. I had to figure it out somehow. The result was decent.",
]

# ─── Code Samples ─────────────────────────────────────────────────────

GOOD_CODE = [
    '''def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []''',
    '''def is_valid(s):
    stack = []
    pairs = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in pairs.values():
            stack.append(char)
        elif char in pairs:
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()
    return len(stack) == 0''',
    '''def max_subarray(nums):
    max_sum = current = nums[0]
    for num in nums[1:]:
        current = max(num, current + num)
        max_sum = max(max_sum, current)
    return max_sum''',
]

POOR_CODE = [
    '''def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]''',
    '''def is_valid(s):
    s = s.replace("()", "").replace("[]", "").replace("{}", "")
    s = s.replace("()", "").replace("[]", "").replace("{}", "")
    s = s.replace("()", "").replace("[]", "").replace("{}", "")
    return s == ""''',
    '''def maxsubarray(nums):
    m = -99999999
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            s = 0
            for k in range(i, j+1):
                s += nums[k]
            if s > m:
                m = s
    return m''',
]

# ─── Generator Functions ────────────────────────────────────────────

def _rand(low: float, high: float) -> float:
    return round(random.uniform(low, high), 2)


def generate_answer_quality_data(n: int = 2000) -> list[dict]:
    """Generate (question, answer, score) triples for answer quality model."""
    data = []
    for _ in range(n):
        question = random.choice(TECH_QUESTIONS)

        if random.random() < 0.6:
            # Good answer
            answer_len = random.randint(80, 300)
            answer = f"This is a well-structured technical explanation about the topic. " * (answer_len // 60)
            answer = answer[:answer_len]
            score = _rand(6.0, 10.0)
        elif random.random() < 0.7:
            # Medium answer
            answer_len = random.randint(40, 150)
            answer = f"The concept relates to the technical topic being discussed. " * (answer_len // 55)
            answer = answer[:answer_len]
            score = _rand(3.5, 6.5)
        else:
            # Poor answer
            answer = random.choice(POOR_ANSWER_TEMPLATES).format(
                vague_concept="that thing", concept="it",
                wrong_concept="something else"
            )
            score = _rand(0.5, 3.5)

        data.append({
            "question": question,
            "answer": answer,
            "score": score,
        })
    return data


def generate_communication_data(n: int = 2000) -> list[dict]:
    """Generate answer texts with communication clarity labels."""
    data = []
    for _ in range(n):
        if random.random() < 0.5:
            # Clear communication
            text = (
                "To answer this question, I'll break it down into three parts. "
                "First, the fundamental concept involves understanding how components interact. "
                "Second, the practical application demonstrates real-world usage. "
                "Finally, the trade-offs must be considered for each approach."
            )
            clarity = _rand(3.5, 5.0)
            fluency = _rand(3.5, 5.0)
            structure = _rand(3.5, 5.0)
        elif random.random() < 0.6:
            # Medium
            text = (
                "So basically this thing works by doing stuff. "
                "I mean, it's like when you have a thing and it does the other thing. "
                "But yeah, it's pretty important for reasons."
            )
            clarity = _rand(2.0, 3.5)
            fluency = _rand(2.0, 3.5)
            structure = _rand(1.5, 3.0)
        else:
            # Poor
            text = "um yeah so like I think its uh related to like that concept or whatever"
            clarity = _rand(0.5, 2.0)
            fluency = _rand(0.5, 2.0)
            structure = _rand(0.5, 1.5)

        data.append({
            "text": text,
            "clarity": clarity,
            "fluency": fluency,
            "structure": structure,
        })
    return data


def generate_star_data(n: int = 2000) -> list[dict]:
    """Generate behavioral answers with STAR component scores."""
    data = []

    situations = ["our team was behind on deadlines", "a critical bug appeared in production", "we had conflicting requirements"]
    tasks = ["deliver the MVP on time", "fix the issue within 24 hours", "align stakeholders on priorities"]
    actions = ["organized daily standups", "implemented comprehensive logging", "scheduled a decision-making meeting"]
    results = ["we shipped 2 days early", "the issue was resolved in 8 hours", "all stakeholders agreed on a plan"]

    for _ in range(n):
        if random.random() < 0.4:
            # Complete STAR
            tmpl = random.choice(STAR_COMPLETE)
            text = tmpl.format(
                situation=random.choice(situations),
                task=random.choice(tasks),
                action_1=random.choice(actions),
                action_2="followed up with status reports",
                result=random.choice(results),
                company="Acme Corp",
                recognition="my manager",
                learning="communication is key",
            )
            s, t, a, r = _rand(3.5, 5.0), _rand(3.5, 5.0), _rand(3.5, 5.0), _rand(3.5, 5.0)
        elif random.random() < 0.5:
            # Partial STAR
            tmpl = random.choice(STAR_PARTIAL)
            text = tmpl.format(
                situation=random.choice(situations),
                task=random.choice(tasks),
                vague_action="some stuff",
            )
            s = _rand(2.0, 4.0)
            t = _rand(1.5, 3.5)
            a = _rand(1.0, 3.0)
            r = _rand(0.5, 2.5)
        else:
            # No STAR
            text = "I'm good at working with people and solving problems. I think teamwork is important."
            s, t, a, r = _rand(0.5, 1.5), _rand(0.5, 1.5), _rand(0.5, 1.5), _rand(0.5, 1.5)

        data.append({
            "text": text,
            "situation_score": s,
            "task_score": t,
            "action_score": a,
            "result_score": r,
        })
    return data


def generate_code_eval_data(n: int = 1500) -> list[dict]:
    """Generate code samples with quality/efficiency/style scores."""
    data = []
    for _ in range(n):
        if random.random() < 0.5:
            code = random.choice(GOOD_CODE)
            quality = _rand(3.5, 5.0)
            efficiency = _rand(3.5, 5.0)
            style = _rand(3.5, 5.0)
        elif random.random() < 0.6:
            code = random.choice(POOR_CODE)
            quality = _rand(1.0, 3.0)
            efficiency = _rand(0.5, 2.5)
            style = _rand(1.0, 3.0)
        else:
            code = "pass # TODO"
            quality = _rand(0.5, 1.5)
            efficiency = _rand(0.5, 1.0)
            style = _rand(0.5, 1.5)

        data.append({
            "code": code,
            "quality": quality,
            "efficiency": efficiency,
            "style": style,
        })
    return data


def generate_meta_scorer_data(n: int = 3000) -> list[dict]:
    """Generate feature vectors for the meta-model aggregator."""
    data = []
    for _ in range(n):
        aq = _rand(1.0, 10.0)
        cc = _rand(0.5, 5.0)
        cf = _rand(0.5, 5.0)
        cs = _rand(0.5, 5.0)
        ss = _rand(0.5, 5.0)
        st = _rand(0.5, 5.0)
        sa = _rand(0.5, 5.0)
        sr = _rand(0.5, 5.0)
        cq = _rand(0.5, 5.0)
        ce = _rand(0.5, 5.0)
        cst = _rand(0.5, 5.0)
        wpm = _rand(80, 200)
        conf = _rand(0.2, 1.0)
        filler = _rand(0.0, 0.15)
        diff = random.choice([1, 2, 3, 4])
        ans_len = _rand(0.1, 1.0)

        # Weighted formula for final score
        final = (
            aq * 0.25
            + ((cc + cf + cs) / 3) * 0.15
            + ((ss + st + sa + sr) / 4) * 0.15
            + ((cq + ce + cst) / 3) * 0.15
            + conf * 2 * 0.10
            + (1 - filler * 5) * 0.05
            + (min(wpm, 160) / 160) * 0.05
            + ans_len * 0.10
        )
        final = max(0.5, min(10.0, round(final + _rand(-0.5, 0.5), 2)))

        data.append({
            "answer_quality_score": aq,
            "communication_clarity": cc,
            "communication_fluency": cf,
            "communication_structure": cs,
            "star_situation": ss,
            "star_task": st,
            "star_action": sa,
            "star_result": sr,
            "code_quality": cq,
            "code_efficiency": ce,
            "code_style": cst,
            "speech_wpm": wpm,
            "speech_confidence": conf,
            "speech_filler_ratio": filler,
            "question_difficulty_numeric": diff,
            "answer_length_normalized": ans_len,
            "final_score": final,
        })
    return data


def generate_all(output_dir: str, n_per_dataset: int = 2000):
    """Generate all training datasets."""
    os.makedirs(output_dir, exist_ok=True)

    datasets = {
        "answer_quality": generate_answer_quality_data(n_per_dataset),
        "communication": generate_communication_data(n_per_dataset),
        "star_analyzer": generate_star_data(n_per_dataset),
        "code_evaluator": generate_code_eval_data(int(n_per_dataset * 0.75)),
        "meta_scorer": generate_meta_scorer_data(int(n_per_dataset * 1.5)),
    }

    for name, data in datasets.items():
        path = os.path.join(output_dir, f"{name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Generated {len(data)} samples → {path}")

    logger.info(f"All datasets saved to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate ML training data")
    parser.add_argument("--output", default=os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ml_training"))
    parser.add_argument("--n", type=int, default=2000, help="Samples per dataset")
    args = parser.parse_args()
    generate_all(args.output, args.n)
