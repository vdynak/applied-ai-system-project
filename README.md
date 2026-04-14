# PawPal+ AI — Applied AI Pet Care Scheduling System

PawPal+ AI is an intelligent pet care scheduling system that uses OpenAI's GPT to generate optimized daily plans with transparent, explainable reasoning. It evolves the original PawPal+ Module 2 prototype into a full applied AI system with responsible design principles.

## What This System Does

PawPal+ AI helps busy pet owners plan their daily pet care by combining rule-based scheduling logic with LLM-powered intelligence. The system:

- Accepts owner profiles, pets, and care tasks through a Streamlit interface
- Sends task data to OpenAI GPT-4o-mini to generate an optimized schedule
- Returns the schedule alongside natural language reasoning explaining **why** tasks are ordered the way they are
- Validates all inputs before AI processing and all outputs after
- Falls back gracefully to rule-based scheduling if the AI is unavailable

## System Architecture

![System Architecture](assets/architecture.png)

The system follows a three-layer design:

1. **User Interface (Streamlit)** — Collects owner, pet, and task data. Displays schedules with AI reasoning.
2. **AI Scheduling Pipeline** — Validates inputs, calls OpenAI, parses output, and enforces constraints.
3. **Rule-Based Fallback** — The original Module 2 scheduler serves as a safety net when AI is unavailable.

Three responsible AI guardrails (shown in orange) sit between each stage: `InputValidator` sanitizes data before the LLM sees it, `OutputParser` ensures the AI response is valid JSON mapping to real tasks, and `validate_schedule` enforces the owner's time budget regardless of what the AI suggests.

## Responsible AI Design

This project demonstrates responsible AI through several concrete mechanisms:

**Input Guardrails (`InputValidator`):**
- Rejects empty owner names, zero/negative time budgets, and missing pets or tasks
- Caps maximum tasks at 50 to prevent prompt injection via excessive input
- Limits task description length to 200 characters

**Output Guardrails (`OutputParser`):**
- Parses AI JSON strictly; extracts from markdown code blocks if needed
- Maps AI-suggested task names back to actual Task objects (prevents hallucinated tasks)
- Validates confidence values to an allowed set ("high", "medium", "low")

**Time Constraint Enforcement:**
- Even if the AI suggests a schedule exceeding the time budget, `validate_schedule` removes overflow tasks and generates warnings

**Transparent Fallback:**
- Every `AIScheduleResult` includes `used_fallback` so users always know whether AI or rules generated their plan
- The fallback produces its own reasoning string explaining the rule-based strategy

**Explainability:**
- Every schedule includes a reasoning paragraph from the AI
- A confidence indicator (high/medium/low) is displayed
- An optional transparency panel shows model metadata and processing details

## How the AI Works

When a user clicks "Generate Schedule," the system:

1. **Validates** the owner, pets, and tasks using `InputValidator`
2. **Builds a prompt** describing all pets, their tasks, priorities, and the time budget
3. **Sends the prompt** to GPT-4o-mini with a system prompt that enforces pet welfare rules (e.g., never skip medication, prioritize feeding)
4. **Parses the response** as JSON, mapping suggested task names back to real Task objects
5. **Enforces constraints** — removes any tasks that would exceed the time budget
6. **Adds conflict warnings** from the rule-based system's time-slot detector
7. **Returns** the schedule, reasoning, warnings, confidence level, and fallback status

If steps 3-4 fail for any reason (no API key, network error, malformed response), the system automatically falls back to the original rule-based scheduler and tells the user.

## Project Structure

```
applied-ai-system-project/
├── app.py                  # Streamlit UI (updated for AI features)
├── pawpal_system.py        # Original domain classes (Task, Pet, Owner, Scheduler)
├── ai_scheduler.py         # NEW: AI scheduling module with guardrails
├── main.py                 # CLI demo script
├── requirements.txt        # Dependencies (streamlit, pytest, openai)
├── reflection.md           # Module 2 reflection (preserved)
├── assets/
│   ├── architecture.mmd    # Mermaid source for system architecture diagram
│   ├── architecture.png    # Exported architecture diagram
│   ├── uml_final.mmd       # Original UML diagram source
│   ├── uml_final.png       # Original UML diagram
│   ├── pawpal_diagram.md   # Original diagram notes
│   └── app.png             # Original app screenshot
└── tests/
    ├── test_pawpal.py      # Original scheduler tests (3 tests)
    └── test_ai_scheduler.py # NEW: AI module tests (11 tests)
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Set your OpenAI API key:
```bash
export OPENAI_API_KEY="sk-..."  # macOS/Linux
set OPENAI_API_KEY=sk-...       # Windows
```

Or enter it directly in the app's sidebar (it is not stored).

## Running the App

```bash
streamlit run app.py
```

## Running Tests

```bash
python -m pytest tests/ -v
```

All 14 tests run without an API key. The AI module tests validate input guardrails, output parsing, fallback behavior, and constraint enforcement using mocked/structured data.

## Evolution from Module 2

| Aspect | Module 2 (Original) | Module 4 (This Project) |
|--------|---------------------|------------------------|
| Scheduling | Rule-based priority sorting | AI-powered with LLM reasoning |
| Explainability | None | Natural language reasoning for every schedule |
| Guardrails | None | Input validation, output parsing, time enforcement |
| Fallback | N/A | Automatic rule-based fallback on AI failure |
| Transparency | None | Confidence indicators, fallback disclosure, debug panel |
| Tests | 3 tests | 14 tests (original + AI module) |
| Architecture | Single module | Layered: UI → AI Pipeline → Fallback |

## Testing

```bash
python -m pytest tests/ -v
```

**Confidence Level: ★★★★☆ (4/5)**

The test suite validates all guardrails, parsing, and fallback paths without requiring an API key. Live AI integration tests would require mocking the OpenAI client, which is a logical next step.
