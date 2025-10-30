# Copilot Instructions — mtg-player

Purpose: give an AI coding agent the minimal, high-value knowledge to be productive in this repository.
Keep this short, concrete, and example-driven.

1) Big picture (one-paragraph):
- This project implements an agentic architecture for MTG: a Decision Agent (LLM or heuristic) calls Tools (in `src/tools`) which translate requests to the Rules Engine (`src/core/rules_engine.py`) that is the single source of truth for validation and state updates. Logging lives in `src/utils/logger.py` and entry is `src/main.py`.

2) Primary files to read first (order):
- `src/main.py` — entry, CLI flags, logger setup, agent wiring
- `src/agent/llm_agent.py` — agent loop, tool wiring, LLM call & response handling
- `src/tools/game_tools.py` — tool implementations (get_game_state, execute_action, etc.)
- `src/core/rules_engine.py` — validation, turn/phase flow, stack & combat resolution
- `src/utils/logger.py` — Game/LLM/Heuristic logging patterns and APIs
- `src/core/game_state.py`, `src/core/player.py`, `src/core/card.py` — domain models

3) Key architectural patterns & conventions (quick bullets):
- Tools return structured JSON and do NOT validate rules; the Rules Engine validates and executes.
- Agent NEVER mutates game state directly; use tools. See `MTGAgent._setup_tools()` and tool `execute()` patterns.
- Logging: three separate loggers (GameLogger, LLMLogger, HeuristicLogger). Pass instances into agent and rules engine.
- CLI flags control behavior: `--no-llm` / `--heuristic`, `--verbose`, `--players=`, `--max-turns=`, `--aggression=`, `--seed=`, `--llm-console`, `--no-turn-summaries`.
- Pydantic v2 is used for models — prefer constructing/returning serializable dicts for logs and tool results.

4) Developer workflows (commands you can run):
- Run a game (default):
```
python run.py
```
- Heuristic (no API):
```
python run.py --no-llm --verbose
```
- Use venv Python explicitly (if needed):
```
.venv/bin/python run.py --verbose
```
- Tests and types:
```
pytest
python -m mypy --config-file mypy.ini src
```
- Logs are in `logs/`; LLM logs include full prompts/responses and `--llm-console` prints one-line summaries.

5) Adding a tool (example pattern):
- File: `src/tools/game_tools.py`
- Create a Tool class with `execute(self, ...) -> dict` returning JSON. Inject `game_state` and `rules_engine` from the agent.
- Tools should call `rules_engine` methods (e.g., `rules_engine.cast_spell()`) and return `{"success": True/False, ...}`.

6) How to extend safely (rules):
- Write a unit test under `tests/` that exercises the new tool and rules path.
- Log via `game_logger` for game-visible events and `llm_logger` / `heuristic_logger` for decision traces.

7) Integration & external dependencies:
- LLM providers configured via `.env` (`LLM_PROVIDER`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `LMSTUDIO_BASE_URL`, etc.).
- Local options: Ollama or LM Studio — agent supports OpenAI-compatible endpoints.

8) Notable repo-specific gotchas:
- The rules engine is authoritative: duplicate validation in tools is discouraged.
- Tools and agent expect JSON-serializable return values; avoid returning raw Python objects.
- Use `execute_action` tool to mutate state; `get_game_state` / `analyze_threats` for read-only data.

9) Quick examples to reference in code:
- Turn summaries are emitted via `GameLogger.log_turn_summary(turn, player, life, hand, creatures)` in `src/core/rules_engine.py`.
- LLM logging: `LLMLogger.log_llm_call()` and `log_llm_response()` are called from `src/agent/llm_agent.py`.

10) When in doubt: run the tests and inspect `logs/` for detailed traces.

---
If you want, I can: (A) shorten further for a one-paragraph header, (B) expand with a small checklist for adding tools/tests, or (C) merge content into an existing `.github/copilot-instructions.md` if you already have one to update.
