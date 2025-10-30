# MTG Commander AI - Implementation Guide

## Getting Started

This guide will walk you through setting up and understanding the proof-of-concept agentic AI for playing Magic: The Gathering Commander.

## Table of Contents
1. [Setup](#setup)
2. [Architecture Overview](#architecture-overview)
3. [Key Concepts](#key-concepts)
4. [Running the PoC](#running-the-poc)
5. [Extending the System](#extending-the-system)
6. [Integrating Real LLMs](#integrating-real-llms)

---

## Setup

### 1. Clone and Install

```bash
# Navigate to project
cd mtg-player

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys (if using LLM)
# For PoC, you can run without API keys using simple heuristics
```

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/
```

### 4. Run the Game

```bash
# Run with verbose output
python src/main.py --verbose

# Run quietly
python src/main.py
```

---

## Architecture Overview

### Three-Layer Design

```
┌─────────────────────────────────────┐
│          LLM Agent                  │  ← Strategic reasoning
│  (Makes decisions, plans ahead)     │
└──────────────┬──────────────────────┘
               │ Tool Calls
┌──────────────▼──────────────────────┐
│          Tools Layer                │  ← Bridge between LLM & Rules
│  (Translates intent to actions)     │
└──────────────┬──────────────────────┘
               │ Validated Actions
┌──────────────▼──────────────────────┐
│        Rules Engine                 │  ← Ground truth
│  (Game logic, validation)           │
└─────────────────────────────────────┘
```

### Why This Architecture?

1. **Separation of Concerns**: LLM doesn't need to know game rules, just strategy
2. **Validation**: All actions validated before execution (no hallucinated moves)
3. **Testability**: Each layer can be tested independently
4. **Explainability**: Can see LLM's reasoning and the resulting actions
5. **Flexibility**: Easy to swap LLM providers or add new tools

---

## Key Concepts

### 1. Game State (`src/core/game_state.py`)

Central source of truth for the game:
- Player information (life, cards, etc.)
- Turn structure (phase, step)
- Stack (spells being cast)
- Win/loss conditions

### 2. Rules Engine (`src/core/rules_engine.py`)

Enforces MTG rules:
- Validates all actions
- Manages turn structure
- Resolves combat
- Checks win conditions

**Key principle**: The LLM cannot break the rules because all actions go through validation.

### 3. Tools (`src/tools/game_tools.py`)

Interface between LLM and game:

**Information Tools**:
- `get_game_state()` - View current game
- `get_legal_actions()` - See available moves
- `analyze_threats()` - Threat assessment

**Action Tools**:
- `execute_action()` - Perform validated moves

### 4. LLM Agent (`src/agent/llm_agent.py`)

Makes strategic decisions:
- Analyzes game state
- Uses Chain-of-Thought reasoning
- Calls tools to gather info
- Executes actions

---

## Running the PoC

### Current Status: Phase 1 (Foundation)

The PoC currently includes:
- ✅ Basic game state representation
- ✅ Minimal rules engine (turns, mana, combat)
- ✅ Simple tool system
- ✅ Rule-based decision making (no LLM yet)
- ✅ ~50 basic cards

### What Happens When You Run It

1. **Game Setup**:
   - Creates 2 players
   - Builds simple decks (100 cards each)
   - Initializes game state

2. **Game Loop**:
   - Each player takes turns
   - Agent makes decisions using simple heuristics
   - Actions are validated and executed
   - Game continues until win condition or turn limit

3. **Output**:
   - Turn-by-turn narration
   - Decision explanations
   - Final game results

### Example Run

```bash
$ python src/main.py --verbose

🎮 Setting up Magic: The Gathering Commander game...
  ✓ Created Player 1 with 100 card deck
  ✓ Created Player 2 with 100 card deck
✓ Game initialized with 2 players

============================================================
🎲 GAME START
============================================================

Turn 1 - Player 1's turn
Phase: beginning/untap
============================================================
Life: 40
Hand: 7 cards
Battlefield: 0 permanents
Creatures: 0

🤔 Decision: play_land
💭 Reasoning: Playing a land to increase mana availability
✅ Played Forest
...
```

---

## Extending the System

### Adding New Cards

1. Edit `src/data/cards.py`
2. Create card definitions:

```python
Card(
    id="my_card",
    name="My Awesome Card",
    mana_cost=ManaCost(generic=2, blue=1),
    card_types=[CardType.CREATURE],
    colors=[Color.BLUE],
    power=3,
    toughness=2,
    keywords=["flying"],
    oracle_text="Flying. When this enters, draw a card."
)
```

### Adding New Tools

1. Create new tool class in `src/tools/`:

```python
class MyNewTool(Tool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="What this tool does"
        )
        self.game_state = None
    
    def execute(self) -> Dict[str, Any]:
        # Implementation
        return {"success": True, "data": ...}
```

2. Register tool in `MTGAgent._setup_tools()`

### Adding Rules

1. Edit `src/core/rules_engine.py`
2. Add validation and execution logic
3. Add tests in `tests/test_rules_engine.py`

---

## Integrating Real LLMs

### Step 1: Choose Provider

Uncomment in `requirements.txt`:
```
openai>=1.0.0        # For GPT-4
anthropic>=0.25.0    # For Claude
langchain>=0.1.0     # For framework
```

### Step 2: Configure API Keys

Edit `.env`:

**For OpenAI:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
```

**For Anthropic:**
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

**For OpenRouter:**
```bash
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
# Optional: for rankings on OpenRouter
OPENROUTER_SITE_URL=https://your-site.com
OPENROUTER_APP_NAME=MTG-Commander-AI
```

**For Ollama (local):**
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

### Step 3: Implement LLM Integration

Replace `_make_simple_decision()` in `llm_agent.py`:

```python
def _make_llm_decision(self) -> Optional[Dict[str, Any]]:
    """Use LLM for decision making."""
    
    # Get game state
    game_state_tool = self.tools["get_game_state"]
    game_state = game_state_tool.execute()
    
    # Get legal actions
    legal_actions_tool = self.tools["get_legal_actions"]
    actions = legal_actions_tool.execute()
    
    # Build prompt
    prompt = f"""
    Game State:
    {json.dumps(game_state, indent=2)}
    
    Available Actions:
    {json.dumps(actions, indent=2)}
    
    What action should you take? Think step by step:
    1. Analyze the situation
    2. Consider your options
    3. Choose the best action
    
    Respond with the action to take.
    """
    
    # Call LLM (example for OpenAI/OpenRouter)
    response = self.llm_client.chat.completions.create(
        model="gpt-4",  # or your chosen model
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        tools=self._convert_tools_to_openai_format(),
        tool_choice="auto"
    )
    
    # Parse response and execute action
    # ... implementation ...
```

### Step 3a: OpenRouter-Specific Setup

OpenRouter uses an OpenAI-compatible API, so you can use the `openai` library:

```python
import os
from openai import OpenAI

# Initialize OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    default_headers={
        "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", ""),  # Optional
        "X-Title": os.getenv("OPENROUTER_APP_NAME", "MTG-AI"),  # Optional
    }
)

# Use like normal OpenAI client
response = client.chat.completions.create(
    model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
    messages=[...],
    tools=[...],
)
```

**Popular OpenRouter Models:**
- `anthropic/claude-3.5-sonnet` - Best reasoning
- `openai/gpt-4-turbo` - Strong all-around
- `meta-llama/llama-3.1-70b-instruct` - Open source, cost-effective
- `google/gemini-pro-1.5` - Large context window
- `qwen/qwen-2.5-72b-instruct` - Great value for complex tasks

### Step 4: Function Calling Format

Convert tools to OpenAI format:

```python
def _convert_tools_to_openai_format(self):
    return [
        {
            "type": "function",
            "function": {
                "name": "execute_action",
                "description": "Execute a game action",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action_type": {
                            "type": "string",
                            "enum": ["pass", "play_land", "cast_spell", ...]
                        },
                        "card_id": {"type": "string"},
                        # ... other params ...
                    }
                }
            }
        }
    ]
```

---

## Troubleshooting

### Import Errors

If you see relative import errors:
```bash
# Run from project root
python -m src.main
```

Or add to PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python src/main.py
```

### Pydantic Errors

Make sure you have Pydantic v2:
```bash
pip install --upgrade pydantic
```

### LLM API Errors

- Check API key in `.env`
- Verify you have credits/access
- Try a simpler model first (gpt-3.5-turbo)

---

## Next Steps

1. **Phase 1 Completion**:
   - Add more cards (current: ~50, goal: 200+)
   - Implement more rules (keywords, abilities)
   - Add comprehensive tests

2. **Phase 2 Integration**:
   - Integrate real LLM with tool calling
   - Implement Chain-of-Thought prompting
   - Add memory/context management

3. **Phase 3 Enhancement**:
   - 4-player Commander support
   - Political decision-making
   - Commander-specific rules (command zone, tax, damage)

4. **Phase 4 Optimization**:
   - Caching and performance
   - Advanced strategic reasoning
   - Monte Carlo tree search for planning

See [ROADMAP.md](ROADMAP.md) for complete development plan.

---

## Learning Resources

### MTG Rules
- [Comprehensive Rules](https://magic.wizards.com/en/rules)
- [Commander Format](https://mtgcommander.net/index.php/rules/)
- [Scryfall API](https://scryfall.com/docs/api) for card data

### AI/LLM Development
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Anthropic Tool Use](https://docs.anthropic.com/claude/docs/tool-use)
- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)

### Game AI
- [Monte Carlo Tree Search](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search)
- [AlphaGo Paper](https://www.nature.com/articles/nature16961)

---

## Contributing

This is primarily a learning project. Feel free to:
- Try implementing features from the roadmap
- Experiment with different LLM providers
- Add new cards or rules
- Optimize performance

Focus on learning and experimentation over perfection!
