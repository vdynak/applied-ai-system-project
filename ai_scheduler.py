"""
AI-Powered Scheduling Module for PawPal+

This module integrates OpenAI's GPT API to provide intelligent,
explainable pet care scheduling. It wraps the existing rule-based
Scheduler as a fallback and adds:

- Natural language reasoning for schedule decisions
- Responsible AI guardrails (input validation, output parsing, fallback)
- Transparent explanations of why tasks are ordered a certain way
"""

import json
import os
from dataclasses import dataclass
from typing import List, Optional, Tuple

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # Graceful degradation — falls back to rule-based scheduling

from pawpal_system import Owner, Pet, Scheduler, Task


@dataclass
class AIScheduleResult:
    """Holds the AI-generated schedule along with metadata."""
    tasks: List[Task]
    reasoning: str           # Natural language explanation of the plan
    warnings: List[str]      # Any conflict or concern warnings
    used_fallback: bool      # True if AI failed and rule-based scheduler was used
    confidence: str          # "high", "medium", or "low"


class InputValidator:
    """Responsible AI guardrail: validates inputs before sending to LLM."""

    MAX_TASKS = 50
    MAX_TASK_DESC_LENGTH = 200
    VALID_TASK_TYPES = {"walk", "feed", "play", "groom", "meds", "enrichment", "vet", "training", "other"}
    MAX_AVAILABLE_TIME = 1440  # 24 hours in minutes

    @staticmethod
    def validate_owner(owner: Owner) -> Tuple[bool, List[str]]:
        """Validate owner data before AI processing."""
        issues = []

        if not owner.name or not owner.name.strip():
            issues.append("Owner name is empty.")
        if owner.available_time <= 0:
            issues.append("Available time must be greater than 0 minutes.")
        if owner.available_time > InputValidator.MAX_AVAILABLE_TIME:
            issues.append(f"Available time exceeds maximum ({InputValidator.MAX_AVAILABLE_TIME} min).")
        if not owner.pets:
            issues.append("Owner has no pets. Add at least one pet.")

        total_tasks = sum(len(pet.tasks) for pet in owner.pets)
        if total_tasks == 0:
            issues.append("No tasks found. Add tasks before generating a schedule.")
        if total_tasks > InputValidator.MAX_TASKS:
            issues.append(f"Too many tasks ({total_tasks}). Maximum is {InputValidator.MAX_TASKS}.")

        for pet in owner.pets:
            for task in pet.tasks:
                if len(task.description) > InputValidator.MAX_TASK_DESC_LENGTH:
                    issues.append(f"Task '{task.description[:30]}...' description is too long.")

        return (len(issues) == 0, issues)


class OutputParser:
    """Responsible AI guardrail: parses and validates LLM output."""

    @staticmethod
    def parse_ai_response(response_text: str, available_tasks: List[Task]) -> Tuple[List[Task], str, str]:
        """
        Parse the AI's JSON response into a task order, reasoning, and confidence.
        Returns (ordered_tasks, reasoning, confidence).
        """
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response_text)
            if json_match:
                data = json.loads(json_match.group(1).strip())
            else:
                raise ValueError("AI response was not valid JSON.")

        schedule_order = data.get("schedule_order", [])
        reasoning = data.get("reasoning", "No reasoning provided.")
        confidence = data.get("confidence", "medium")

        if confidence not in ("high", "medium", "low"):
            confidence = "medium"

        # Map AI-suggested order back to actual Task objects
        task_lookup = {task.description.lower().strip(): task for task in available_tasks}
        ordered_tasks = []
        for item in schedule_order:
            task_name = item.get("task", "").lower().strip()
            if task_name in task_lookup:
                ordered_tasks.append(task_lookup[task_name])

        return ordered_tasks, reasoning, confidence

    @staticmethod
    def validate_schedule(tasks: List[Task], available_time: int) -> Tuple[List[Task], List[str]]:
        """Ensure the AI schedule respects time constraints."""
        scheduler = Scheduler()
        valid_tasks = []
        total_time = 0
        warnings = []

        for task in tasks:
            minutes = scheduler.time_to_minutes(task.time)
            if total_time + minutes <= available_time:
                valid_tasks.append(task)
                total_time += minutes
            else:
                warnings.append(
                    f"Removed '{task.description}' — would exceed available time "
                    f"({total_time + minutes} min > {available_time} min)."
                )

        return valid_tasks, warnings


class AIScheduler:
    """
    AI-enhanced scheduler that uses OpenAI GPT to generate intelligent,
    explainable pet care schedules with automatic fallback to the
    rule-based Scheduler.
    """

    SYSTEM_PROMPT = """You are PawPal+'s AI scheduling assistant. Your job is to create
an optimal daily pet care schedule for a pet owner.

RULES YOU MUST FOLLOW:
1. Prioritize animal welfare — feeding, medication, and health tasks come first.
2. Space out similar activities (e.g., don't schedule two walks back-to-back).
3. Respect the owner's available time budget — do not exceed it.
4. Consider the pet's age and type when ordering tasks.
5. Explain your reasoning clearly so the owner understands WHY you chose this order.
6. If you're uncertain about a recommendation, say so — do not fabricate confidence.
7. Never suggest skipping medication or veterinary tasks.

RESPOND WITH VALID JSON ONLY in this exact format:
{
  "schedule_order": [
    {"task": "task description here", "reason": "why this task is at this position"}
  ],
  "reasoning": "A 2-3 sentence overall explanation of the schedule strategy.",
  "confidence": "high" | "medium" | "low"
}"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key from parameter or environment."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.rule_based_scheduler = Scheduler()
        self._client = None

    @property
    def client(self):
        """Lazy-initialize the OpenAI client."""
        if self._client is None and self.api_key and OpenAI is not None:
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def _build_user_prompt(self, owner: Owner) -> str:
        """Build the task context prompt for the AI."""
        pet_info = []
        for pet in owner.pets:
            tasks_desc = []
            for task in pet.tasks:
                tasks_desc.append(
                    f"  - {task.description} (time: {task.time}, "
                    f"priority: {task.priority}/5, type: {task.type}, "
                    f"frequency: {task.frequency}, "
                    f"completed: {task.completion_status})"
                )
            pet_info.append(
                f"Pet: {pet.name} ({pet.type}, age {pet.age})\nTasks:\n"
                + "\n".join(tasks_desc)
            )

        return f"""Owner: {owner.name}
Available time: {owner.available_time} minutes
Preferences: {owner.preferences if owner.preferences else 'None specified'}

{chr(10).join(pet_info)}

Create an optimal daily schedule using ONLY the incomplete tasks listed above.
Respect the {owner.available_time}-minute time budget."""

    def generate_ai_schedule(self, owner: Owner) -> AIScheduleResult:
        """
        Generate an AI-powered schedule with explainability.
        Falls back to rule-based scheduling if AI is unavailable or fails.
        """
        # Step 1: Validate inputs (responsible AI guardrail)
        is_valid, issues = InputValidator.validate_owner(owner)
        if not is_valid:
            return AIScheduleResult(
                tasks=[],
                reasoning="Could not generate schedule due to input issues: "
                          + "; ".join(issues),
                warnings=issues,
                used_fallback=False,
                confidence="low",
            )

        # Step 2: Try AI-powered scheduling
        if self.client:
            try:
                return self._call_ai(owner)
            except Exception as e:
                # Step 3: Fallback to rule-based scheduler
                return self._fallback_schedule(
                    owner,
                    fallback_reason=f"AI scheduling unavailable ({type(e).__name__}). "
                                    "Using rule-based scheduler instead.",
                )
        else:
            return self._fallback_schedule(
                owner,
                fallback_reason="No OpenAI API key configured. "
                                "Using rule-based scheduler.",
            )

    def _call_ai(self, owner: Owner) -> AIScheduleResult:
        """Make the actual OpenAI API call and parse the response."""
        user_prompt = self._build_user_prompt(owner)

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,  # Low temperature for more consistent scheduling
            max_tokens=1000,
        )

        ai_text = response.choices[0].message.content

        # Parse AI output (responsible AI guardrail)
        incomplete_tasks = [
            task for pet in owner.pets for task in pet.tasks
            if not task.completion_status
        ]
        ordered_tasks, reasoning, confidence = OutputParser.parse_ai_response(
            ai_text, incomplete_tasks
        )

        # Validate the schedule respects time constraints
        valid_tasks, time_warnings = OutputParser.validate_schedule(
            ordered_tasks, owner.available_time
        )

        # Add conflict warnings from rule-based system
        conflict_warnings = self.rule_based_scheduler.detect_time_conflicts(owner)

        all_warnings = time_warnings + conflict_warnings

        return AIScheduleResult(
            tasks=valid_tasks,
            reasoning=reasoning,
            warnings=all_warnings,
            used_fallback=False,
            confidence=confidence,
        )

    def _fallback_schedule(self, owner: Owner, fallback_reason: str) -> AIScheduleResult:
        """Use the rule-based scheduler as a fallback with generated reasoning."""
        plan = self.rule_based_scheduler.generate_plan(owner)
        conflicts = getattr(self.rule_based_scheduler, "conflicts", [])
        time_conflicts = self.rule_based_scheduler.detect_time_conflicts(owner)

        reasoning = (
            f"{fallback_reason} "
            "Tasks are ordered by priority (highest first), then by scheduled time. "
            "This ensures the most important care activities happen first within "
            f"your {owner.available_time}-minute time budget."
        )

        return AIScheduleResult(
            tasks=plan,
            reasoning=reasoning,
            warnings=conflicts + time_conflicts,
            used_fallback=True,
            confidence="medium",
        )
