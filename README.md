# MTG Commander AI - Agentic Implementation

An AI agent that learns to play Magic: The Gathering Commander using LLM-powered reasoning, Chain-of-Thought decision making, and a custom rules engine.

Credit: Inspired by Discord User "SkillsMcGee" (210509006043742208)

## 🎯 Project Goals

- Build an AI that can play Commander format MTG
- Use **agentic architecture** (LLM + tools) instead of fine-tuning
- Implement Chain-of-Thought reasoning for strategic planning
- Create a testable, explainable, and extensible system
- Learn modern AI development practices

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   LLM Agent                         │
│  (GPT-4, Claude, or Local Model)                   │
│  • Strategic Decision Making                        │
│  • Chain-of-Thought Reasoning                       │
│  • Multi-turn Planning                              │
└─────────────┬───────────────────────────────────────┘
              │
              │ Tool Calls
              │
┌─────────────▼───────────────────────────────────────┐
│                  Tools Layer                        │
│  • get_game_state()                                 │
│  • get_legal_actions()                              │
│  • execute_action()                                 │
│  • analyze_threats()                                │
│  • calculate_lethal()                               │
└─────────────┬───────────────────────────────────────┘
              │
              │ Validated Actions
              │
┌─────────────▼───────────────────────────────────────┐
│              Rules Engine                           │
│  • Game State Management                            │
│  • Move Validation                                  │
│  • Turn Structure                                   │
│  • Combat Resolution                                │
│  • Stack Management                                 │
└─────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key (or Anthropic, or local Ollama)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd mtg-player

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API key
```

### Run the Game

```bash
python run.py                      # Default: 4 players, quiet mode
python run.py --verbose            # With turn-by-turn output to console
python run.py --players=2          # 2-player game
python run.py --players=2 --verbose  # 2-player with console output

# Alternative entry (without run.py)
PYTHONPATH=./src python src/main.py --verbose
```

### Logging

The game creates detailed log files in the `logs/` directory:

- **Game logs** (`logs/game_YYYYMMDD_HHMMSS_gameid.log`)
  - Turn progression
  - Phase changes
  - Player actions
  - Win/loss conditions

- **LLM logs** (`logs/llm_YYYYMMDD_HHMMSS_gameid.log`)
  - Full prompts sent to the LLM
  - Complete responses (including reasoning/thinking for o-series models)
  - Tool calls and results
  - Token usage statistics
  - Decision reasoning

**Console output** (with `--verbose` flag):
- High-level game progress
- Turn announcements
- Player life totals and board state
- Game results

All detailed logging goes to files only, keeping console output clean and readable.

## 📁 Project Structure (src layout)

```
mtg-player/
├── README.md
├── ROADMAP.md              # Detailed implementation roadmap
├── requirements.txt
├── .env.example
├── logs/                   # Auto-generated game and LLM logs
├── src/
│   ├── main.py            # Entry point (supports archetype decks)
│   ├── core/
│   │   ├── game_state.py  # Game state representation
│   │   ├── player.py      # Player state
│   │   ├── card.py        # Card models
│   │   ├── rules_engine.py # Core rules implementation
│   │   └── stack.py       # Stack implementation
│   ├── agent/
│   │   ├── llm_agent.py   # LLM decision-making agent
│   │   └── prompts.py     # Prompt templates
│   ├── tools/
│   │   └── game_tools.py  # Game state and action tools
│   ├── utils/
│   │   └── logger.py      # Game and LLM logging utilities
│   └── data/
│       └── cards.py       # Card database + deck builders
├── tests/
│   ├── test_rules_engine.py
│   ├── test_stack.py
│   ├── test_instant_speed.py
│   └── test_llm_agent.py
└── notebooks/
    └── exploration.ipynb  # For experimentation
```

## 🔧 Technology Stack

- Data Models: Pydantic v2
- LLM Providers: OpenAI and Anthropic (optional via .env)
- Testing: pytest
- Type Checking: mypy (src layout configured)
- CLI/Utilities: Rich (optional) and requests

## 📚 Key Concepts

### Agentic Architecture
Instead of fine-tuning a model, we give the LLM tools it can call to interact with the game. This allows:
- Validation of all actions through the rules engine
- Explainable decision-making
- Easy debugging and iteration
- No need for expensive GPU training

### Chain-of-Thought Reasoning
The AI is prompted to "think out loud" before making decisions:
1. **Analyze**: What's the current situation?
2. **Plan**: What are my goals this turn?
3. **Evaluate**: What are my options?
4. **Decide**: Which action is best?
5. **Execute**: Make the move

### Tool-Based Interaction
The LLM doesn't directly manipulate game state. Instead, it calls tools:
- `get_legal_actions()` - Ask what moves are available
- `execute_action(action)` - Perform a validated move
- `analyze_threats()` - Get strategic analysis

This ensures the AI can never make illegal moves or hallucinate game state.

## 🎮 Current Status

- Phase 4 core complete (stack and instant-speed interactions)
- 151-card Commander staples database
- Archetype-based deck builder: ramp, control, midrange
- 4-player Commander setup with 40 life and commander zone
- 38 tests passing (pytest)
- Type checks clean (mypy)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/
## ✅ Type Checking

```bash
python -m mymy --config-file mypy.ini src
```

## 🧰 Utilities

- Validate card data against Scryfall (optional):
```bash
python validate_cards.py
```

## 🧩 Deck Archetypes

Decks are built via archetype functions in `data/cards.py`:
- `create_ramp_deck()` – acceleration + big threats
- `create_control_deck()` – counters + removal + finishers
- `create_midrange_deck()` – balanced creatures and interaction

Use the dispatcher:
```python
from data.cards import create_simple_deck
deck = create_simple_deck(commander_card=None, archetype="control")
```

# Run specific test file
pytest tests/test_rules_engine.py -v
```

## 📖 Learning Resources

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [MTG Comprehensive Rules](https://magic.wizards.com/en/rules)
- [Scryfall API](https://scryfall.com/docs/api) - Card data
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)

## 🤝 Contributing

This is primarily a learning project, but feedback and suggestions are welcome!

1. Check the [ROADMAP.md](ROADMAP.md) for current priorities
2. Open an issue to discuss major changes
3. Keep the focus on learning and experimentation

## 📝 License

MIT License - Feel free to learn from and adapt this code.

## 🙏 Acknowledgments

- Inspired by the challenge of building AI for complex strategy games
- Thanks to the MTG community and Scryfall for card data
- Built to learn about agentic AI architectures and LLM tool use

---

**Remember**: The goal is not to build the perfect MTG AI, but to learn about modern AI development, agent architectures, and strategic reasoning systems. Have fun! 🎲✨
