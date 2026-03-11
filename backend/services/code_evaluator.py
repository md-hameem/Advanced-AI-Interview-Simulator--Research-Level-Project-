"""
Advanced AI Interview Simulator - Code Evaluator Service
Handles code execution, testing, complexity analysis, and LLM-based code review.
"""
import re
import ast
import sys
import logging
import subprocess
import tempfile
import os
import time
from typing import Optional

from services.llm_client import llm_client

logger = logging.getLogger(__name__)

# ─── Supported Languages ────────────────────────────────────────────────
LANGUAGE_CONFIG = {
    "python": {
        "extension": ".py",
        "command": [sys.executable, "{file}"],
        "timeout": 10,
        "comment": "#",
    },
    "javascript": {
        "extension": ".js",
        "command": ["node", "{file}"],
        "timeout": 10,
        "comment": "//",
    },
    "typescript": {
        "extension": ".ts",
        "command": ["npx", "ts-node", "{file}"],
        "timeout": 15,
        "comment": "//",
    },
}

# ─── Coding Questions Bank ──────────────────────────────────────────────
CODING_QUESTIONS = [
    {
        "id": "two_sum",
        "title": "Two Sum",
        "difficulty": "easy",
        "description": (
            "Given an array of integers `nums` and an integer `target`, return indices "
            "of the two numbers such that they add up to target.\n\n"
            "You may assume that each input would have exactly one solution, "
            "and you may not use the same element twice.\n\n"
            "**Example:**\n```\nInput: nums = [2,7,11,15], target = 9\nOutput: [0,1]\n"
            "Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].\n```"
        ),
        "test_cases": [
            {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
            {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2]},
            {"input": {"nums": [3, 3], "target": 6}, "expected": [0, 1]},
        ],
        "starter_code": {
            "python": 'def two_sum(nums: list[int], target: int) -> list[int]:\n    """Return indices of two numbers that add up to target."""\n    # Your code here\n    pass\n',
            "javascript": 'function twoSum(nums, target) {\n  // Your code here\n}\n',
        },
        "optimal_complexity": {"time": "O(n)", "space": "O(n)"},
        "topics": ["hash_map", "arrays"],
    },
    {
        "id": "reverse_linked_list",
        "title": "Reverse Linked List",
        "difficulty": "easy",
        "description": (
            "Given the head of a singly linked list, reverse the list, and return the reversed list.\n\n"
            "**Example:**\n```\nInput: head = [1,2,3,4,5]\nOutput: [5,4,3,2,1]\n```"
        ),
        "test_cases": [
            {"input": {"values": [1, 2, 3, 4, 5]}, "expected": [5, 4, 3, 2, 1]},
            {"input": {"values": [1, 2]}, "expected": [2, 1]},
            {"input": {"values": [1]}, "expected": [1]},
        ],
        "starter_code": {
            "python": 'class ListNode:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef reverse_list(head: ListNode) -> ListNode:\n    """Reverse a singly linked list."""\n    # Your code here\n    pass\n',
            "javascript": 'class ListNode {\n  constructor(val = 0, next = null) {\n    this.val = val;\n    this.next = next;\n  }\n}\n\nfunction reverseList(head) {\n  // Your code here\n}\n',
        },
        "optimal_complexity": {"time": "O(n)", "space": "O(1)"},
        "topics": ["linked_list", "pointers"],
    },
    {
        "id": "valid_parentheses",
        "title": "Valid Parentheses",
        "difficulty": "easy",
        "description": (
            "Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, "
            "determine if the input string is valid.\n\n"
            "An input string is valid if:\n"
            "1. Open brackets must be closed by the same type of brackets.\n"
            "2. Open brackets must be closed in the correct order.\n"
            "3. Every close bracket has a corresponding open bracket.\n\n"
            "**Example:**\n```\nInput: s = \"()[]{}\"\nOutput: true\n```"
        ),
        "test_cases": [
            {"input": {"s": "()"}, "expected": True},
            {"input": {"s": "()[]{}"}, "expected": True},
            {"input": {"s": "(]"}, "expected": False},
            {"input": {"s": "({[]})"}, "expected": True},
        ],
        "starter_code": {
            "python": 'def is_valid(s: str) -> bool:\n    """Check if parentheses are valid."""\n    # Your code here\n    pass\n',
            "javascript": 'function isValid(s) {\n  // Your code here\n}\n',
        },
        "optimal_complexity": {"time": "O(n)", "space": "O(n)"},
        "topics": ["stack", "strings"],
    },
    {
        "id": "max_subarray",
        "title": "Maximum Subarray",
        "difficulty": "medium",
        "description": (
            "Given an integer array `nums`, find the subarray with the largest sum, and return its sum.\n\n"
            "**Example:**\n```\nInput: nums = [-2,1,-3,4,-1,2,1,-5,4]\nOutput: 6\n"
            "Explanation: The subarray [4,-1,2,1] has the largest sum 6.\n```"
        ),
        "test_cases": [
            {"input": {"nums": [-2, 1, -3, 4, -1, 2, 1, -5, 4]}, "expected": 6},
            {"input": {"nums": [1]}, "expected": 1},
            {"input": {"nums": [5, 4, -1, 7, 8]}, "expected": 23},
        ],
        "starter_code": {
            "python": 'def max_sub_array(nums: list[int]) -> int:\n    """Find the maximum subarray sum."""\n    # Your code here\n    pass\n',
            "javascript": 'function maxSubArray(nums) {\n  // Your code here\n}\n',
        },
        "optimal_complexity": {"time": "O(n)", "space": "O(1)"},
        "topics": ["dynamic_programming", "arrays"],
    },
    {
        "id": "lru_cache",
        "title": "LRU Cache",
        "difficulty": "hard",
        "description": (
            "Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.\n\n"
            "Implement the `LRUCache` class:\n"
            "- `LRUCache(capacity)` — Initialize with positive size capacity.\n"
            "- `get(key)` — Return the value if key exists, otherwise return -1.\n"
            "- `put(key, value)` — Update or insert value. Evict LRU key if at capacity.\n\n"
            "Both `get` and `put` must run in **O(1)** average time complexity.\n\n"
            "**Example:**\n```\ncache = LRUCache(2)\ncache.put(1, 1)\ncache.put(2, 2)\ncache.get(1)    # returns 1\n"
            "cache.put(3, 3) # evicts key 2\ncache.get(2)    # returns -1\n```"
        ),
        "test_cases": [
            {
                "input": {
                    "operations": ["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"],
                    "args": [[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]],
                },
                "expected": [None, None, None, 1, None, -1, None, -1, 3, 4],
            }
        ],
        "starter_code": {
            "python": 'class LRUCache:\n    def __init__(self, capacity: int):\n        """Initialize LRU Cache with given capacity."""\n        # Your code here\n        pass\n\n    def get(self, key: int) -> int:\n        """Get value by key, return -1 if not found."""\n        # Your code here\n        pass\n\n    def put(self, key: int, value: int) -> None:\n        """Put key-value pair, evict LRU if at capacity."""\n        # Your code here\n        pass\n',
            "javascript": 'class LRUCache {\n  constructor(capacity) {\n    // Your code here\n  }\n\n  get(key) {\n    // Your code here\n  }\n\n  put(key, value) {\n    // Your code here\n  }\n}\n',
        },
        "optimal_complexity": {"time": "O(1)", "space": "O(n)"},
        "topics": ["hash_map", "doubly_linked_list", "design"],
    },
]


class CodeEvaluator:
    """
    Evaluates candidate code through:
    1. Sandboxed execution with test cases
    2. Static analysis (complexity estimation)
    3. LLM-based code review (style, correctness, edge cases)
    """

    def get_coding_question(self, difficulty: str = "easy", topic: str | None = None) -> dict:
        """Get a coding question matching the requested difficulty/topic."""
        filtered = [q for q in CODING_QUESTIONS if q["difficulty"] == difficulty]
        if topic:
            filtered = [q for q in filtered if topic in q.get("topics", [])]
        if not filtered:
            filtered = CODING_QUESTIONS
        import random
        return random.choice(filtered)

    def get_question_by_id(self, question_id: str) -> dict | None:
        """Look up a coding question by ID."""
        for q in CODING_QUESTIONS:
            if q["id"] == question_id:
                return q
        return None

    # ─── Code Execution ──────────────────────────────────────────────

    async def execute_code(
        self, code: str, language: str, stdin: str = ""
    ) -> dict:
        """Execute code in a sandboxed subprocess and return output."""
        if language not in LANGUAGE_CONFIG:
            return {
                "success": False,
                "error": f"Unsupported language: {language}",
                "stdout": "",
                "stderr": "",
                "execution_time_ms": 0,
            }

        config = LANGUAGE_CONFIG[language]
        suffix = config["extension"]
        timeout = config["timeout"]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=suffix, delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            temp_path = f.name

        try:
            cmd = [c.replace("{file}", temp_path) for c in config["command"]]
            start = time.perf_counter()

            result = subprocess.run(
                cmd,
                input=stdin,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tempfile.gettempdir(),
            )

            exec_time = (time.perf_counter() - start) * 1000

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "execution_time_ms": round(exec_time, 2),
                "return_code": result.returncode,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Time Limit Exceeded ({timeout}s)",
                "stdout": "",
                "stderr": "",
                "execution_time_ms": timeout * 1000,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
                "execution_time_ms": 0,
            }
        finally:
            os.unlink(temp_path)

    # ─── Test Runner ─────────────────────────────────────────────────

    async def run_tests(
        self, code: str, language: str, test_cases: list[dict]
    ) -> dict:
        """Run code against test cases and return results."""
        results = []
        total_passed = 0

        for i, tc in enumerate(test_cases):
            # Build a test wrapper that calls the function and prints the result
            test_code = self._build_test_wrapper(code, tc, language)
            execution = await self.execute_code(test_code, language)

            if execution["success"]:
                actual_output = execution["stdout"].strip()
                expected_str = str(tc["expected"])

                # Normalize comparison
                passed = self._compare_output(actual_output, expected_str)
                if passed:
                    total_passed += 1

                results.append({
                    "test_index": i,
                    "passed": passed,
                    "input": tc["input"],
                    "expected": tc["expected"],
                    "actual": actual_output,
                    "execution_time_ms": execution["execution_time_ms"],
                })
            else:
                results.append({
                    "test_index": i,
                    "passed": False,
                    "input": tc["input"],
                    "expected": tc["expected"],
                    "actual": None,
                    "error": execution.get("error") or execution.get("stderr", ""),
                    "execution_time_ms": execution["execution_time_ms"],
                })

        return {
            "total_tests": len(test_cases),
            "passed": total_passed,
            "failed": len(test_cases) - total_passed,
            "pass_rate": total_passed / max(len(test_cases), 1),
            "results": results,
        }

    def _build_test_wrapper(self, code: str, test_case: dict, language: str) -> str:
        """Build a wrapper that executes the user's code with test input."""
        if language == "python":
            args = test_case["input"]
            # Build function call from the arguments
            arg_str = ", ".join(f"{k}={repr(v)}" for k, v in args.items())

            # Detect the main function name from the code
            func_name = self._extract_function_name(code, language)
            if not func_name:
                func_name = "solution"

            return f"""{code}

# Test runner
result = {func_name}({arg_str})
print(result)
"""
        elif language in ("javascript", "typescript"):
            args = test_case["input"]
            arg_str = ", ".join(repr(v) for v in args.values())
            func_name = self._extract_function_name(code, language)

            return f"""{code}

// Test runner
const result = {func_name}({arg_str});
console.log(JSON.stringify(result));
"""
        return code

    def _extract_function_name(self, code: str, language: str) -> str | None:
        """Extract the main function name from user code."""
        if language == "python":
            match = re.search(r"^def\s+(\w+)\s*\(", code, re.MULTILINE)
            if match:
                # Skip __init__ and other dunder methods
                name = match.group(1)
                if not name.startswith("__"):
                    return name
            # Also check for class definitions
            match = re.search(r"^class\s+(\w+)", code, re.MULTILINE)
            if match:
                return match.group(1)
        elif language in ("javascript", "typescript"):
            match = re.search(r"function\s+(\w+)\s*\(", code)
            if match:
                return match.group(1)
            # Arrow function: const name = ...
            match = re.search(r"(?:const|let|var)\s+(\w+)\s*=", code)
            if match:
                return match.group(1)
        return None

    def _compare_output(self, actual: str, expected: str) -> bool:
        """Flexible comparison of outputs."""
        # Direct string match
        if actual == expected:
            return True

        # Try parsing as Python literals for structural comparison
        try:
            actual_val = ast.literal_eval(actual)
            expected_val = ast.literal_eval(expected)

            # Handle lists that could be in any order (like two_sum)
            if isinstance(actual_val, list) and isinstance(expected_val, list):
                if sorted(map(str, actual_val)) == sorted(map(str, expected_val)):
                    return True

            return actual_val == expected_val
        except (ValueError, SyntaxError):
            pass

        # Case-insensitive + whitespace normalized
        return actual.strip().lower() == expected.strip().lower()

    # ─── Complexity Analysis ─────────────────────────────────────────

    def analyze_complexity(self, code: str, language: str = "python") -> dict:
        """Static analysis to estimate time and space complexity."""
        if language != "python":
            return {"time": "Unknown", "space": "Unknown", "details": "Static analysis only supports Python"}

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {"time": "Unknown", "space": "Unknown", "details": "Syntax error in code"}

        loop_depth = self._max_loop_depth(tree)
        has_recursion = self._has_recursion(tree)
        uses_sorting = self._uses_sorting(code)
        uses_set_or_dict = self._uses_set_or_dict(code)

        # Estimate time complexity
        if has_recursion and loop_depth >= 1:
            time_complexity = "O(n * 2^n)"
        elif has_recursion:
            time_complexity = "O(2^n) or O(n log n)"
        elif uses_sorting:
            time_complexity = f"O(n log n)" if loop_depth <= 1 else f"O(n^{loop_depth} log n)"
        elif loop_depth == 0:
            time_complexity = "O(1)"
        elif loop_depth == 1:
            time_complexity = "O(n)"
        elif loop_depth == 2:
            time_complexity = "O(n²)"
        else:
            time_complexity = f"O(n^{loop_depth})"

        # Estimate space complexity
        if uses_set_or_dict:
            space_complexity = "O(n)"
        elif has_recursion:
            space_complexity = "O(n)"  # call stack
        else:
            space_complexity = "O(1)"

        return {
            "time": time_complexity,
            "space": space_complexity,
            "details": {
                "loop_depth": loop_depth,
                "has_recursion": has_recursion,
                "uses_sorting": uses_sorting,
                "uses_auxiliary_data_structures": uses_set_or_dict,
            },
        }

    def _max_loop_depth(self, node, depth=0) -> int:
        """Find maximum nesting depth of loops."""
        max_d = depth
        for child in ast.walk(node):
            if isinstance(child, (ast.For, ast.While)):
                inner = self._max_loop_depth(child, depth + 1)
                max_d = max(max_d, inner)
        return max_d

    def _has_recursion(self, tree) -> bool:
        """Detect if any function calls itself."""
        func_names = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_names.add(node.name)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in func_names:
                    return True
        return False

    def _uses_sorting(self, code: str) -> bool:
        return bool(re.search(r"\.(sort|sorted)\s*\(", code))

    def _uses_set_or_dict(self, code: str) -> bool:
        return bool(re.search(r"\b(set|dict|defaultdict|Counter|OrderedDict|{})\b", code))

    # ─── LLM Code Review ─────────────────────────────────────────────

    async def llm_code_review(
        self,
        code: str,
        question: dict,
        test_results: dict,
        complexity: dict,
        language: str = "python",
    ) -> dict:
        """Use LLM to review code quality, style, and correctness."""
        prompt = f"""You are a senior software engineer conducting a code review during a technical interview.

## Problem
**{question['title']}** ({question['difficulty']})
{question['description']}

## Candidate's Code ({language})
```{language}
{code}
```

## Test Results
- Passed: {test_results['passed']}/{test_results['total_tests']}
- Pass Rate: {test_results['pass_rate']*100:.0f}%

## Complexity Analysis
- Time: {complexity['time']}
- Space: {complexity['space']}
- Optimal: Time {question.get('optimal_complexity', {}).get('time', 'Unknown')}, Space {question.get('optimal_complexity', {}).get('space', 'Unknown')}

## Instructions
Evaluate the code and return a JSON object with these fields:
- "code_quality_score": 0-5 (readability, naming, structure)
- "correctness_score": 0-5 (handles all cases, no bugs)
- "efficiency_score": 0-5 (compared to optimal solution)
- "style_score": 0-5 (idiomatic code, best practices)
- "overall_code_score": 0-10 (weighted overall)
- "feedback": string with detailed review
- "strengths": list of strengths
- "weaknesses": list of areas to improve
- "suggestions": list of specific improvement suggestions
- "edge_cases_missed": list of edge cases not handled
- "optimal_approach": brief description of the optimal solution

Return ONLY valid JSON, no markdown.
"""
        try:
            response = await llm_client.generate(prompt)
            import json
            review = json.loads(response)

            # Ensure all fields exist
            defaults = {
                "code_quality_score": 3,
                "correctness_score": test_results["pass_rate"] * 5,
                "efficiency_score": 3,
                "style_score": 3,
                "overall_code_score": 5,
                "feedback": "Code review completed.",
                "strengths": [],
                "weaknesses": [],
                "suggestions": [],
                "edge_cases_missed": [],
                "optimal_approach": "",
            }
            for k, v in defaults.items():
                if k not in review:
                    review[k] = v

            return review
        except Exception as e:
            logger.error(f"LLM code review failed: {e}")
            return {
                "code_quality_score": 3,
                "correctness_score": round(test_results["pass_rate"] * 5, 1),
                "efficiency_score": 3,
                "style_score": 3,
                "overall_code_score": 5,
                "feedback": "Code review could not be completed via LLM. Scores based on test results.",
                "strengths": [],
                "weaknesses": [],
                "suggestions": [],
                "edge_cases_missed": [],
                "optimal_approach": "",
            }

    # ─── Full Evaluation Pipeline ────────────────────────────────────

    async def evaluate(
        self,
        code: str,
        question_id: str,
        language: str = "python",
    ) -> dict:
        """
        Full code evaluation pipeline:
        1. Run test cases
        2. Analyze complexity
        3. LLM code review
        """
        question = self.get_question_by_id(question_id)
        if not question:
            return {"error": f"Question '{question_id}' not found"}

        # 1. Run tests
        test_results = await self.run_tests(code, language, question["test_cases"])

        # 2. Complexity analysis
        complexity = self.analyze_complexity(code, language)

        # 3. LLM code review
        llm_review = await self.llm_code_review(
            code, question, test_results, complexity, language
        )

        return {
            "question_id": question_id,
            "question_title": question["title"],
            "language": language,
            "test_results": test_results,
            "complexity": complexity,
            "review": llm_review,
            "optimal_complexity": question.get("optimal_complexity", {}),
        }


# Singleton
code_evaluator = CodeEvaluator()
