# Model Card — PawPal+ AI

## Model Details

PawPal+ AI uses **OpenAI GPT-4o-mini** via the OpenAI Chat Completions API to generate optimized pet care schedules with natural language reasoning. The model is called with a temperature of 0.3 and a max token limit of 1000. A system prompt enforces pet welfare rules (prioritize feeding and medication, never skip vet tasks, explain reasoning, disclose uncertainty). The system falls back to a rule-based scheduler when the AI is unavailable.

## Intended Use

This system is designed for busy pet owners who want help planning their daily pet care tasks. It is a scheduling assistant, not a veterinary advisor. It should not be used for medical decisions, medication dosing, or any situation where professional veterinary judgment is needed.

## Training Data

GPT-4o-mini was trained by OpenAI on a broad internet corpus. PawPal+ does not fine-tune or retrain the model. All task-specific behavior comes from the system prompt and the structured user prompt built at runtime.

## Evaluation and Testing Results

14 out of 14 automated tests pass. The tests cover input validation (5 tests), output parsing (3 tests), time-budget enforcement (1 test), fallback behavior (3 tests), and original scheduler logic (3 tests). All tests run without an API key by using structured/mocked data.

Confidence scores: the AI returns "high" for simple 2-3 task schedules and "medium" for more complex multi-pet plans. The system defaults to "medium" if the AI returns an invalid confidence value.

Human evaluation: manual testing through the Streamlit interface confirmed the AI consistently prioritizes feeding and medication first, spaces out similar activities, and provides clear reasoning. The time-budget guardrail caught overflow tasks in roughly 1 in 4 complex schedules, confirming it is necessary.

## Limitations and Biases

- The system inherits whatever biases exist in GPT-4o-mini's training data regarding pet care practices.
- The system prompt hard-codes a welfare-first priority order (medication, feeding, then exercise). This is a reasonable default but may not match every owner's preferences or situation.
- Only English is supported.
- Conflict detection is limited to exact time-match collisions — partial duration overlaps are not detected.
- The system assumes task durations are accurate as entered and cannot verify whether they are realistic for a specific pet.
- The AI sometimes wraps JSON in markdown code blocks despite explicit instructions, requiring a regex fallback in the parser.

## Ethical Considerations

**Could this system be misused?** The risk is low given the pet scheduling domain. Input validation caps tasks at 50 and descriptions at 200 characters to prevent prompt injection. The output parser maps AI suggestions back to real Task objects, preventing hallucinated tasks from appearing in schedules. API keys are never stored.

If extended to handle veterinary recommendations or medication dosing, the stakes would increase significantly and would require professional veterinary review and stricter guardrails.

**Transparency:** Every schedule includes a confidence indicator, a natural language reasoning paragraph, and a `used_fallback` flag. An optional debug panel shows model metadata. Users always know whether AI or rules generated their plan.

## AI Collaboration Reflection

**Helpful AI suggestion:** VS Code Copilot recommended using a Python dataclass for `AIScheduleResult` to bundle tasks, reasoning, warnings, fallback status, and confidence into a single return type. This was a great suggestion — it simplified the code, made the UI layer cleaner, and made testing easier because every result had the same predictable structure.

**Flawed AI suggestion:** Copilot proposed a full interval-overlap conflict detection algorithm using datetime arithmetic. While technically correct for the general case, it was far too complex for this project's scope, introduced edge-case bugs around midnight-crossing time slots, and was harder to test and explain. I rejected it in favor of a simpler exact time-match approach that is lightweight, easy to test, and gives useful feedback without over-engineering the system.

**What surprised me:** The most surprising finding during testing was how often GPT-4o-mini wrapped its JSON response in markdown code blocks even when explicitly told to return raw JSON. This happened roughly 1 in 5 times and would have caused a hard failure without the regex fallback. It reinforced that LLMs follow instructions probabilistically, not deterministically, and every output format assumption needs a code-level safety net.

## Key Takeaway

The developer must stay the lead architect when using AI tools. AI accelerates coding and brainstorming, but strong outcomes come from setting clear constraints, validating suggestions with tests, and choosing designs that balance correctness, clarity, and maintainability for the actual project context.
