# Logging System

The MTG Commander AI includes comprehensive logging to help you understand game progression and LLM decision-making.

## Log Files

All logs are saved to the `logs/` directory with timestamped filenames:

### Game Logs
**File**: `logs/game_YYYYMMDD_HHMMSS_gameid.log`

**Contains**:
- Turn start announcements
- Phase transitions
- Player actions (play land, cast spell, attack, etc.)
- Card draws per draw step
- Life total changes from combat damage
- Stack events:
	- When a spell is put on the stack
	- When the top of the stack resolves (with outcome)
	- Priority pass chain (who passed, who gets priority next, all passed)
- Turn summaries at end of each turn (per player: life, hand, creatures)
- Game state snapshots
- Win/loss conditions
- Errors and forced phase advances

**Example**:
```
2025-10-30 05:42:57,553 - INFO - Game started: 963c7491-4a74-4dca-92b7-261293787425
2025-10-30 05:42:57,571 - INFO - TURN 1 | Player 1 (Ramp) | beginning/untap
2025-10-30 05:42:58,123 - INFO - PHASE CHANGE | beginning/untap → beginning/upkeep
2025-10-30 05:42:58,456 - INFO - PHASE CHANGE | beginning/upkeep → beginning/draw
2025-10-30 05:42:58,457 - INFO - DRAW | Player 1 (Ramp) | Hand: 8
2025-10-30 05:42:59,456 - INFO - ACTION | Player 1 (Ramp) | play_land | Forest
2025-10-30 05:43:00,101 - INFO - STACK | PUSH | Player 1 (Ramp) | Lightning Bolt | targets: Player 2 (Control)
2025-10-30 05:43:00,102 - INFO - PRIORITY | pass | Player 1 (Ramp)
2025-10-30 05:43:00,103 - INFO - PRIORITY | to | Player 2 (Control)
2025-10-30 05:43:00,203 - INFO - PRIORITY | pass | Player 2 (Control)
2025-10-30 05:43:00,203 - INFO - PRIORITY | all passed | action: resolve_top
2025-10-30 05:43:00,204 - INFO - STACK | RESOLVE | Player 1 (Ramp) | Lightning Bolt | to graveyard
2025-10-30 05:43:10,012 - INFO - LIFE | Player 2 (Control) | -3 -> 37 | combat damage from Commander Bear
2025-10-30 05:43:10,500 - INFO - TURN SUMMARY | 1 | Player 1 (Ramp) | Life: 40 | Hand: 7 | Creatures: 0
2025-10-30 05:43:10,500 - INFO - TURN SUMMARY | 1 | Player 2 (Control) | Life: 37 | Hand: 7 | Creatures: 0
2025-10-30 05:43:15,789 - INFO - GAME END | Winner: Player 1 (Ramp) | Reason: all opponents eliminated
```

### LLM Logs
**File**: `logs/llm_YYYYMMDD_HHMMSS_gameid.log`

**Contains**:
- Complete prompts sent to the LLM (system + user messages)
- Full LLM responses
- Extended thinking/reasoning (for o-series models)
- Tool calls with arguments
- Tool execution results (untruncated JSON)
- Final decisions with reasoning
- Token usage statistics (prompt, completion, reasoning tokens)

**Example**:
```
2025-10-30 05:42:57,571 - INFO - ================================================================================
2025-10-30 05:42:57,571 - INFO - LLM CALL #1 | Player 1 (Ramp) | Turn 1 | beginning/untap
2025-10-30 05:42:57,571 - INFO - Model: openai/gpt-4o-mini
2025-10-30 05:42:57,571 - INFO - --------------------------------------------------------------------------------
2025-10-30 05:42:57,571 - INFO - MESSAGES:
2025-10-30 05:42:57,571 - INFO -   [0] SYSTEM:
2025-10-30 05:42:57,571 - INFO -     You are an AI agent playing Magic: The Gathering Commander format.
2025-10-30 05:42:57,571 - INFO -     
2025-10-30 05:42:57,571 - INFO -     Your goal is to make strategic decisions to win the game...
2025-10-30 05:42:57,571 - INFO -   [1] USER:
2025-10-30 05:42:57,571 - INFO -     It's your turn. Current phase: beginning, Step: untap
2025-10-30 05:42:57,571 - INFO -     
2025-10-30 05:42:57,571 - INFO -     Think through this step by step...
2025-10-30 05:42:57,571 - INFO - --------------------------------------------------------------------------------
2025-10-30 05:42:57,571 - INFO - TOOLS: 7 available
2025-10-30 05:42:57,571 - DEBUG -   - get_game_state
2025-10-30 05:42:57,571 - DEBUG -   - get_legal_actions
2025-10-30 05:42:57,571 - DEBUG -   - execute_action
2025-10-30 05:42:57,571 - DEBUG -   - analyze_threats
2025-10-30 05:42:57,571 - DEBUG -   - get_stack_state
2025-10-30 05:42:57,571 - DEBUG -   - can_respond
2025-10-30 05:43:03,392 - INFO - --------------------------------------------------------------------------------
2025-10-30 05:43:03,392 - INFO - LLM RESPONSE:
2025-10-30 05:43:03,392 - INFO - Thinking: [Model used 64 reasoning tokens]
2025-10-30 05:43:03,392 - INFO - Tool Calls: 5
2025-10-30 05:43:03,392 - INFO -   - get_game_state({})
2025-10-30 05:43:03,392 - INFO -   - get_stack_state({})
2025-10-30 05:43:03,392 - INFO -   - can_respond({})
2025-10-30 05:43:03,392 - INFO -   - analyze_threats({})
2025-10-30 05:43:03,392 - INFO -   - get_legal_actions({})
2025-10-30 05:43:03,392 - INFO -   - evaluate_position({})
### Heuristic Logs
**File**: `logs/heuristic_YYYYMMDD_HHMMSS_gameid.log`

Used only when running with `--no-llm` (heuristic mode). This log cleanly separates non-LLM decision flow from LLM logs.

**Contains**:
- Decision context: player, turn, phase/step
- Threats observed and legal actions count
- Position evaluation: score, status, breakdown, summary
- Tool executions relevant to heuristics
- Final decision with reasoning

**Example**:
```
2025-10-30 05:42:57,571 - INFO - Heuristic Logger initialized for game: 963c7491
2025-10-30 05:42:57,571 - INFO - ================================================================================================
2025-10-30 05:42:57,571 - INFO - HEURISTIC | Player 1 (Ramp) | Turn 1 | beginning/main
2025-10-30 05:42:57,571 - INFO - Threats observed: 0 | Legal actions: 3
2025-10-30 05:42:59,456 - INFO - TOOL EXEC | evaluate_position
2025-10-30 05:42:59,456 - INFO -   Result:
2025-10-30 05:42:59,456 - INFO -     {
2025-10-30 05:42:59,456 - INFO -       "score": 0.58,
2025-10-30 05:42:59,456 - INFO -       "position": "even",
2025-10-30 05:42:59,456 - INFO -       "breakdown": { "life": 0.9, "board": 0.1, ... },
2025-10-30 05:42:59,456 - INFO -       "summary": "You're slightly ahead on life but behind on board..."
2025-10-30 05:42:59,456 - INFO -     }
2025-10-30 05:42:59,456 - INFO - POSITION | even (0.58)
2025-10-30 05:43:03,392 - INFO - --------------------------------------------------------------------------------
2025-10-30 05:43:03,392 - INFO - DECISION | Player 1 (Ramp)
2025-10-30 05:43:03,392 - INFO -   Action: play_land
2025-10-30 05:43:03,392 - INFO -   Reasoning: Ramping: Playing land for mana development
```
2025-10-30 05:43:03,392 - INFO - Token Usage:
2025-10-30 05:43:03,392 - INFO -   Prompt: 245
2025-10-30 05:43:03,392 - INFO -   Completion: 150
2025-10-30 05:43:03,392 - INFO -   Total: 395
2025-10-30 05:43:03,392 - INFO -   Reasoning: 64
2025-10-30 05:43:03,392 - INFO - Finish Reason: tool_calls
2025-10-30 05:43:03,392 - INFO - ================================================================================
2025-10-30 05:43:03,392 - INFO - TOOL EXEC | get_game_state
2025-10-30 05:43:03,392 - DEBUG -   Args: {}
2025-10-30 05:43:03,392 - INFO -   Result:
2025-10-30 05:43:03,392 - INFO -     {
2025-10-30 05:43:03,392 - INFO -       "success": true,
2025-10-30 05:43:03,392 - INFO -       "game_state": {
2025-10-30 05:43:03,392 - INFO -         "game_id": "963c7491-4a74-4dca-92b7-261293787425",
2025-10-30 05:43:03,392 - INFO -         "turn_number": 1,
2025-10-30 05:43:03,392 - INFO -         ...
```

## Console Output

When running with the `--verbose` flag, you'll see high-level game progress in the console:

```bash
python run.py --verbose
```

**Console shows**:
- ASCII art header
- Game setup (number of players, deck archetypes)
- Turn announcements
- Player life totals
- Hand size and battlefield state
- Creature counts
- Game end conditions
- Log file locations

**Console does NOT show** (by default):
- Detailed LLM prompts and responses
- Tool execution details
- Token usage statistics
- Extended reasoning content

This keeps the console output clean and readable while capturing all details in log files.

### Optional: LLM Console Summaries

Use the `--llm-console` flag to print a one-line summary to console after each LLM call:

```bash
python run.py --verbose --llm-console
```

**Example console output with `--llm-console`**:
```
🤖 LLM #1: gpt-4o-mini | tools: 5 | tool_calls
🤖 LLM #2: gpt-4o-mini | tools: 1 | stop
```

This is useful for:
- Monitoring LLM activity during live runs
- Quickly seeing which models are being used
- Tracking tool call patterns without opening log files
- Debugging without verbose file inspection

The summary format is: `🤖 LLM #{call_number}: {model_name} | tools: {tool_count} | {finish_reason}`

All detailed information (prompts, full responses, reasoning, token counts) remains in the LLM log file.

## Logging Architecture

### Three Loggers

**GameLogger** (`src/utils/logger.py`):
- Tracks game events
- Records turn progression
- Logs player actions
- Writes to file only (no console)

**LLMLogger** (`src/utils/logger.py`):
**HeuristicLogger** (`src/utils/logger.py`):
- Captures heuristic (non-LLM) decision flow
- Records context, position evaluation, and final decisions
- Writes to its own file for clean separation
- Captures all LLM API calls
- Records complete prompts and responses
- Logs tool calls and results
- Tracks token usage
- Extracts reasoning from o-series models
- Writes to file only (no console)

### No Truncation

All logs are **fully verbose** with no content truncation:
- Complete message content (no character limits)
- Full tool call arguments
- Complete tool execution results (entire JSON responses)
- Full reasoning and thinking content

This ensures you can debug and analyze every aspect of the game and AI decision-making.

## Usage Tips

### Finding Specific Games
Log files include timestamp and game ID:
```
logs/game_20251030_054257_963c7491.log
logs/llm_20251030_054257_963c7491.log
```

The timestamp format is `YYYYMMDD_HHMMSS`, making it easy to find recent games.

### Analyzing Decisions
To understand why the AI made a specific decision:
1. Find the turn in the game log
2. Open the LLM log at the same timestamp
3. Read the full prompt that was sent
4. Review the tool calls the AI made
5. Check the tool execution results
6. See the final decision with reasoning

### Token Usage
LLM logs include detailed token statistics:
- **Prompt tokens**: Input to the model
- **Completion tokens**: Model's response
- **Total tokens**: Sum of both
- **Reasoning tokens**: Extended thinking (o-series models only)

This helps track API costs and understand model efficiency.

### Debugging
If the game behaves unexpectedly:
1. Check game log for forced phase advances (indicates stuck AI)
2. Check LLM log for errors in tool calls
3. Review tool execution results for unexpected data
4. Verify the prompts are providing correct context

## Log Retention

Logs are not automatically deleted. The `logs/` directory is gitignored, so logs won't be committed to version control.

To clean up old logs:
```bash
# Remove all logs
rm logs/*.log

# Remove logs older than 7 days (Unix/Mac)
find logs/ -name "*.log" -mtime +7 -delete
```

## Implementation Details

The logging system is initialized in `src/main.py`:

```python
from utils.logger import setup_loggers

# Create unique game ID
game_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"

# Initialize loggers (game, LLM, heuristic)
game_logger, llm_logger, heuristic_logger = setup_loggers(game_id)

# Pass to game loop and agent
agents = {p.id: MTGAgent(..., llm_logger=llm_logger, heuristic_logger=heuristic_logger) for p in players}
```

The agent automatically logs all LLM interactions, and the main game loop logs all game events.
