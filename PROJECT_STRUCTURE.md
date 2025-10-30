# MTG Commander AI - Complete Project Structure

```
mtg-player/
│
├── 📚 Documentation (8 files)
│   ├── README.md                    # Project overview & introduction
│   ├── ROADMAP.md                   # 14-week development plan with phases
│   ├── IMPLEMENTATION_GUIDE.md      # Detailed setup & extension guide
│   ├── ARCHITECTURE.md              # System design with visual diagrams
│   ├── QUICKSTART.md                # Get running in 5 minutes
│   ├── PROJECT_SUMMARY.md           # High-level project summary
│   └── (You are here) ←───────────  PROJECT_STRUCTURE.md
│
├── ⚙️ Configuration (3 files)
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment variable template
│   └── .gitignore                   # Git ignore rules
│
├── 🎮 Source Code (src/)
│   │
│   ├── main.py                      # Entry point - run the game
│   │
│   ├── 🧠 core/                     # Game logic & rules
│   │   ├── __init__.py
│   │   ├── card.py                  # Card models & types
│   │   │   ├── Card class
│   │   │   ├── CardInstance class
│   │   │   ├── ManaCost class
│   │   │   ├── CardType enum
│   │   │   └── Color enum
│   │   │
│   │   ├── player.py                # Player state management
│   │   │   ├── Player class
│   │   │   ├── ManaPool class
│   │   │   └── Zone management (hand, battlefield, etc.)
│   │   │
│   │   ├── game_state.py            # Game state & turn structure
│   │   │   ├── GameState class
│   │   │   ├── Phase enum
│   │   │   ├── Step enum
│   │   │   └── Win condition checking
│   │   │
│   │   └── rules_engine.py          # Rules validation & execution
│   │       ├── RulesEngine class
│   │       ├── play_land()
│   │       ├── cast_spell()
│   │       ├── declare_attackers()
│   │       ├── declare_blockers()
│   │       ├── resolve_combat_damage()
│   │       └── advance_phase/turn()
│   │
│   ├── 🤖 agent/                    # AI decision-making
│   │   ├── __init__.py
│   │   │
│   │   ├── llm_agent.py             # Main AI agent
│   │   │   ├── MTGAgent class
│   │   │   ├── take_turn_action()
│   │   │   ├── analyze_position()
│   │   │   └── _make_simple_decision() (PoC heuristics)
│   │   │
│   │   └── prompts.py               # Prompt templates
│   │       ├── SYSTEM_PROMPT
│   │       ├── DECISION_PROMPT
│   │       ├── COMBAT_PROMPT
│   │       └── MAIN_PHASE_PROMPT
│   │
│   ├── 🔧 tools/                    # LLM tool interface
│   │   ├── __init__.py
│   │   │
│   │   └── game_tools.py            # Tool implementations
│   │       ├── Tool base class
│   │       ├── GetGameStateTool
│   │       ├── GetLegalActionsTool
│   │       ├── ExecuteActionTool
│   │       └── AnalyzeThreatsTool
│   │
│   └── 📦 data/                     # Card database
│       ├── __init__.py
│       │
│       └── cards.py                 # Card definitions
│           ├── create_basic_cards() - 151 cards (Commander staples)
│           ├── create_ramp_deck()/create_control_deck()/create_midrange_deck()
│           └── create_simple_deck(commander_card=None, archetype="midrange")
│
└── 🧪 tests/                        # Unit tests
    ├── __init__.py
    │
    └── test_rules_engine.py         # Rules engine tests
        ├── test_game_initialization()
        ├── test_land_drop()
        ├── test_cannot_play_two_lands()
        ├── test_turn_advancement()
        └── test_win_condition()
```

---

## File Statistics

### Code Files
- **Python files**: 14 (`.py`)
- **Total lines of code**: ~2,500
- **Documentation**: 8 markdown files
- **Tests**: 1 test file (expandable)

### Project Breakdown
```
Category              Files    Approx Lines
────────────────────────────────────────────
Core Game Logic       4        ~800 lines
Agent & AI            2        ~400 lines
Tools                 1        ~350 lines
Data & Cards          1        ~150 lines
Main Entry            1        ~200 lines
Tests                 1        ~100 lines
Documentation         8        ~2,000 lines
Configuration         3        ~50 lines
────────────────────────────────────────────
TOTAL                 21       ~4,050 lines
```

---

## Key Files Explained

### 🚀 Start Here
1. **README.md** - Understand what this project is
2. **QUICKSTART.md** - Get it running in 5 minutes
3. **src/main.py** - See how a game runs

### 📖 Learn the System
4. **ARCHITECTURE.md** - Understand the design
5. **IMPLEMENTATION_GUIDE.md** - Learn to extend it
6. **ROADMAP.md** - See the development plan

### 💻 Core Implementation
7. **src/core/rules_engine.py** - The heart of the game
8. **src/agent/llm_agent.py** - The AI brain
9. **src/tools/game_tools.py** - How LLM interacts with game

### 🔨 Extend & Build
10. **src/data/cards.py** - Add new cards here
11. **tests/test_rules_engine.py** - Add tests here

---

## Data Flow Through Files

```
┌─────────────────┐
│   main.py       │  1. Entry point
└────────┬────────┘
         │
         ├─► setup_game()
         │   └─► Creates: GameState, RulesEngine, Players
         │
         └─► play_game()
             │
             ├─► Creates MTGAgent for each player
             │   │
             │   └─► llm_agent.py
             │       │
             │       ├─► Uses: prompts.py (for thinking)
             │       │
             │       └─► Calls: game_tools.py
             │           │
             │           ├─► get_game_state()
             │           │   └─► Reads: game_state.py
             │           │
             │           ├─► get_legal_actions()
             │           │   └─► Queries: rules_engine.py
             │           │
             │           └─► execute_action()
             │               └─► Calls: rules_engine.py
             │                   └─► Updates: game_state.py
             │                       └─► Modifies: player.py
             │                           └─► Moves: card.py instances
             │
             └─► Loop until game_over or max_turns
```

---

## Import Dependencies

```
main.py
 ├─ imports: core.game_state (GameState)
 ├─ imports: core.player (Player)
 ├─ imports: core.rules_engine (RulesEngine)
 ├─ imports: core.card (Card, CardInstance)
 ├─ imports: agent.llm_agent (MTGAgent)
 └─ imports: data.cards (create_simple_deck)

llm_agent.py
 ├─ imports: core.game_state (GameState)
 ├─ imports: core.rules_engine (RulesEngine)
 ├─ imports: tools.game_tools (All Tool classes)
 └─ imports: agent.prompts (SYSTEM_PROMPT, etc.)

game_tools.py
 ├─ imports: pydantic (BaseModel, Field)
 └─ uses: game_state, rules_engine (via injection)

rules_engine.py
 ├─ imports: core.game_state (GameState, Phase, Step)
 ├─ imports: core.player (Player)
 └─ imports: core.card (Card, CardInstance)

game_state.py
 ├─ imports: pydantic (BaseModel, Field)
 ├─ imports: core.player (Player)
 └─ imports: core.card (CardInstance)

player.py
 ├─ imports: pydantic (BaseModel, Field)
 └─ imports: core.card (CardInstance, Color)

card.py
 └─ imports: pydantic (BaseModel, Field)
     (Base level - no internal imports)
```

---

## How to Navigate the Code

### 🎯 Scenario: "I want to add a new card"
1. Go to `src/data/cards.py`
2. Add card definition in `create_basic_cards()`
3. Test by running `python src/main.py`

### 🎯 Scenario: "I want to understand combat"
1. Read `src/core/rules_engine.py` → `resolve_combat_damage()`
2. See how it's called in `llm_agent.py`
3. Check tests in `tests/test_rules_engine.py`

### 🎯 Scenario: "I want to add a new LLM tool"
1. Create new class in `src/tools/game_tools.py`
2. Inherit from `Tool` base class
3. Register in `MTGAgent._setup_tools()` in `llm_agent.py`
4. Use in agent's decision-making

### 🎯 Scenario: "I want to integrate real LLM"
1. Read `IMPLEMENTATION_GUIDE.md` → "Integrating Real LLMs"
2. Install LLM library: `pip install openai`
3. Add API key to `.env`
4. Modify `llm_agent.py` → replace `_make_simple_decision()`

### 🎯 Scenario: "I want to implement a new rule"
1. Add method in `src/core/rules_engine.py`
2. Update validation logic
3. Add corresponding tool in `game_tools.py` (if needed)
4. Write test in `tests/`

---

## Development Workflow

```
1. Read Documentation
   └─► Understand architecture & goals

2. Set Up Environment
   └─► pip install -r requirements.txt

3. Run Tests
   └─► pytest (verify everything works)

4. Run the Game
   └─► python src/main.py --verbose

5. Make Changes
   ├─► Add cards (data/cards.py)
   ├─► Add rules (core/rules_engine.py)
   ├─► Add tools (tools/game_tools.py)
   └─► Improve AI (agent/llm_agent.py)

6. Test Changes
   ├─► Write unit tests
   └─► Run pytest

7. Integrate LLM (Future)
   ├─► Get API key
   ├─► Update llm_agent.py
   └─► Test tool calling

8. Iterate & Learn! 🚀
```

---

## File Size Reference

```
File                          Size Category
────────────────────────────────────────────
card.py                       Large (~300 lines)
rules_engine.py               Large (~350 lines)
game_tools.py                 Large (~350 lines)
llm_agent.py                  Medium (~200 lines)
game_state.py                 Medium (~150 lines)
player.py                     Medium (~170 lines)
main.py                       Medium (~200 lines)
cards.py                      Medium (~150 lines)
prompts.py                    Small (~80 lines)
test_rules_engine.py          Small (~100 lines)
```

---

## What's Not Included (Yet)

These are on the roadmap but not yet implemented:
- ❌ Real LLM integration (GPT-4/Claude API calls)
- ❌ Chain-of-Thought prompting (framework ready)
- ❌ 4-player Commander support (2-player only)
- ❌ Advanced rules (stack, priority passing, triggered abilities)
- ❌ Commander-specific rules (command zone, tax, 21 damage)
- ❌ Large card database (only ~50 basic cards)
- ❌ Deck building assistant
- ❌ Web UI (CLI only)
- ❌ Game replay/analysis
- ❌ Performance optimization (caching, etc.)

See **ROADMAP.md** for the full development plan!

---

## Quick Reference: Where Is...?

| What                          | File                          |
|-------------------------------|-------------------------------|
| Main entry point              | `src/main.py`                 |
| Card definitions              | `src/data/cards.py`           |
| Game rules logic              | `src/core/rules_engine.py`    |
| AI decision making            | `src/agent/llm_agent.py`      |
| LLM tools                     | `src/tools/game_tools.py`     |
| Prompt templates              | `src/agent/prompts.py`        |
| Game state                    | `src/core/game_state.py`      |
| Player state                  | `src/core/player.py`          |
| Card models                   | `src/core/card.py`            |
| Tests                         | `tests/test_rules_engine.py`  |
| Setup instructions            | `QUICKSTART.md`               |
| Architecture diagrams         | `ARCHITECTURE.md`             |
| Development roadmap           | `ROADMAP.md`                  |
| Extension guide               | `IMPLEMENTATION_GUIDE.md`     |

---

**🎉 You now have a complete map of the project! Start exploring! 🗺️**
