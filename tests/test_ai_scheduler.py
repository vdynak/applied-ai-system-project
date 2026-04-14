"""
Tests for the AI scheduling module.

These tests validate:
- Input validation guardrails
- Output parsing and safety checks
- Fallback behavior when AI is unavailable
- End-to-end schedule generation without an API key
"""

import json

from pawpal_system import Owner, Pet, Task
from ai_scheduler import AIScheduler, InputValidator, OutputParser


# --- Input Validation Tests ---

def test_input_validator_rejects_empty_owner_name():
    """Owners with empty names should fail validation."""
    owner = Owner("", {}, 60)
    owner.add_pet(Pet("Max", "dog", 3, [Task("Walk", "00:30", 5, "walk", "daily")]))

    is_valid, issues = InputValidator.validate_owner(owner)

    assert is_valid is False
    assert any("name" in issue.lower() for issue in issues)


def test_input_validator_rejects_zero_time():
    """Available time of 0 minutes should fail validation."""
    owner = Owner("Jordan", {}, 0)
    owner.add_pet(Pet("Max", "dog", 3, [Task("Walk", "00:30", 5, "walk", "daily")]))

    is_valid, issues = InputValidator.validate_owner(owner)

    assert is_valid is False
    assert any("time" in issue.lower() for issue in issues)


def test_input_validator_rejects_no_pets():
    """Owner with no pets should fail validation."""
    owner = Owner("Jordan", {}, 60)

    is_valid, issues = InputValidator.validate_owner(owner)

    assert is_valid is False
    assert any("pet" in issue.lower() for issue in issues)


def test_input_validator_rejects_no_tasks():
    """Owner with pets but no tasks should fail validation."""
    owner = Owner("Jordan", {}, 60)
    owner.add_pet(Pet("Max", "dog", 3, []))

    is_valid, issues = InputValidator.validate_owner(owner)

    assert is_valid is False
    assert any("task" in issue.lower() for issue in issues)


def test_input_validator_accepts_valid_owner():
    """A well-formed owner with pets and tasks should pass validation."""
    owner = Owner("Jordan", {}, 120)
    pet = Pet("Max", "dog", 3, [])
    pet.add_task(Task("Walk", "00:30", 5, "walk", "daily"))
    owner.add_pet(pet)

    is_valid, issues = InputValidator.validate_owner(owner)

    assert is_valid is True
    assert issues == []


# --- Output Parsing Tests ---

def test_output_parser_handles_valid_json():
    """Parser should correctly map AI JSON output to Task objects."""
    tasks = [
        Task("Morning walk", "00:30", 5, "walk", "daily"),
        Task("Feed breakfast", "00:15", 4, "feed", "daily"),
    ]

    ai_response = json.dumps({
        "schedule_order": [
            {"task": "Feed breakfast", "reason": "Nutrition first"},
            {"task": "Morning walk", "reason": "Exercise after eating"},
        ],
        "reasoning": "Feed before walk for energy.",
        "confidence": "high",
    })

    ordered, reasoning, confidence = OutputParser.parse_ai_response(ai_response, tasks)

    assert len(ordered) == 2
    assert ordered[0].description == "Feed breakfast"
    assert ordered[1].description == "Morning walk"
    assert confidence == "high"
    assert "Feed" in reasoning


def test_output_parser_handles_invalid_json():
    """Parser should raise ValueError for non-JSON output."""
    tasks = [Task("Walk", "00:30", 5, "walk", "daily")]

    try:
        OutputParser.parse_ai_response("This is not JSON at all.", tasks)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_output_parser_handles_json_in_code_block():
    """Parser should extract JSON from markdown code blocks."""
    tasks = [Task("Walk", "00:30", 5, "walk", "daily")]

    ai_response = '```json\n{"schedule_order": [{"task": "Walk", "reason": "Only task"}], "reasoning": "One task.", "confidence": "high"}\n```'

    ordered, reasoning, confidence = OutputParser.parse_ai_response(ai_response, tasks)

    assert len(ordered) == 1
    assert ordered[0].description == "Walk"


def test_output_validator_respects_time_budget():
    """Schedule validator should remove tasks that exceed available time."""
    tasks = [
        Task("Long walk", "01:00", 5, "walk", "daily"),   # 60 min
        Task("Play", "00:45", 3, "play", "daily"),          # 45 min
        Task("Groom", "00:30", 2, "groom", "daily"),        # 30 min
    ]

    valid, warnings = OutputParser.validate_schedule(tasks, 90)  # 90 min budget

    assert len(valid) == 2  # Only first two fit (60 + 45 = 105 > 90, so 60 + 30)
    # Actually: 60 fits, then 45 would make 105 > 90, so only 60 fits, then 30 = 90
    # Let's check: 60 + 45 = 105 > 90, so Play is removed. 60 + 30 = 90 <= 90, Groom fits.
    assert valid[0].description == "Long walk"
    assert valid[1].description == "Groom"
    assert len(warnings) == 1
    assert "Play" in warnings[0]


# --- Fallback Behavior Tests ---

def test_fallback_without_api_key():
    """Without an API key, should use rule-based fallback gracefully."""
    owner = Owner("Jordan", {}, 120)
    pet = Pet("Max", "dog", 3, [])
    pet.add_task(Task("Walk", "00:30", 5, "walk", "daily"))
    pet.add_task(Task("Feed", "00:15", 4, "feed", "daily"))
    owner.add_pet(pet)

    ai_sched = AIScheduler(api_key=None)
    result = ai_sched.generate_ai_schedule(owner)

    assert result.used_fallback is True
    assert result.confidence == "medium"
    assert "rule-based" in result.reasoning.lower() or "Rule-based" in result.reasoning


def test_fallback_produces_valid_schedule():
    """Fallback schedule should respect time constraints and return tasks."""
    owner = Owner("Jordan", {}, 60)
    pet = Pet("Max", "dog", 3, [])
    pet.add_task(Task("Walk", "00:30", 5, "walk", "daily"))
    pet.add_task(Task("Feed", "00:15", 4, "feed", "daily"))
    owner.add_pet(pet)

    ai_sched = AIScheduler(api_key=None)
    result = ai_sched.generate_ai_schedule(owner)

    total_minutes = sum(
        ai_sched.rule_based_scheduler.time_to_minutes(t.time) for t in result.tasks
    )
    assert total_minutes <= owner.available_time
    assert len(result.tasks) > 0


def test_ai_scheduler_returns_warnings_for_conflicts():
    """AI scheduler should surface conflict warnings from the rule-based system."""
    owner = Owner("Jordan", {}, 600)
    pet1 = Pet("Max", "dog", 3, [])
    pet2 = Pet("Luna", "cat", 2, [])
    pet1.add_task(Task("Walk Max", "08:00", 5, "walk", "daily"))
    pet2.add_task(Task("Feed Luna", "08:00", 4, "feed", "daily"))
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    ai_sched = AIScheduler(api_key=None)
    result = ai_sched.generate_ai_schedule(owner)

    assert any("08:00" in w for w in result.warnings)
