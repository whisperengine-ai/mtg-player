# 🎯 Getting Started Checklist

Your step-by-step guide to understanding and running the MTG Commander AI!

---

## ✅ Phase 1: Understanding (15 minutes)

### Read These First (in order):
- [ ] **README.md** (5 min) - Get the big picture
- [ ] **PROJECT_SUMMARY.md** (5 min) - Understand what's included
- [ ] **ARCHITECTURE.md** (5 min) - See how it works

### Quick Understanding Check:
- [ ] Can you explain what "agentic AI" means?
- [ ] Do you understand why we use tools instead of fine-tuning?
- [ ] Can you name the three main layers of the architecture?

---

## ✅ Phase 2: Setup (10 minutes)

### Installation Steps:
- [ ] Open terminal in `/Users/markcastillo/git/mtg-player`
- [ ] Create virtual environment: `python3 -m venv venv`
- [ ] Activate it: `source venv/bin/activate`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify installation: `python -c "import pydantic; print('OK')"`

### Verify Setup:
- [ ] Run tests: `pytest` (should pass)
- [ ] Check file structure: `ls -la src/`

---

## ✅ Phase 3: First Run (5 minutes)

### Run the Game:
- [ ] Basic run: `python src/main.py`
- [ ] Verbose run: `python src/main.py --verbose`
- [ ] Watch a complete game play out

### Observe:
- [ ] Game initializes with 2 players
- [ ] Each player has 40 life
- [ ] AI makes decisions (play land, cast spells, attack)
- [ ] Combat resolves correctly
- [ ] Game ends with a winner

---

## ✅ Phase 4: Code Exploration (20 minutes)

### Read These Files (in order):
1. [ ] **src/core/card.py** (5 min)
   - Understand `Card` and `CardInstance` classes
   - See how mana costs work
   - Look at creature stats (power/toughness)

2. [ ] **src/core/rules_engine.py** (8 min)
   - Find `play_land()` - how does it validate?
   - Find `cast_spell()` - what checks are performed?
   - Find `resolve_combat_damage()` - how does combat work?

3. [ ] **src/agent/llm_agent.py** (7 min)
   - Find `_setup_tools()` - what tools are available?
   - Find `_make_simple_decision()` - how does AI choose actions?
   - See the decision flow

### Code Understanding Check:
- [ ] Can you trace what happens when AI plays a land?
- [ ] Can you find where combat damage is calculated?
- [ ] Do you understand how tools connect to the rules engine?

---

## ✅ Phase 5: Make Your First Change (15 minutes)

### Challenge: Add a New Card

1. [ ] Open `src/data/cards.py`

2. [ ] Add this card to `create_basic_cards()`:
```python
Card(
    id="giant_growth",
    name="Giant Growth",
    mana_cost=ManaCost(green=1),
    card_types=[CardType.INSTANT],
    colors=[Color.GREEN],
    oracle_text="Target creature gets +3/+3 until end of turn."
)
```

3. [ ] Add it to a deck archetype (e.g., midrange):
Open `src/data/cards.py` and locate `create_midrange_deck()`. Add one or two copies near the "Interaction" section:
```python
# Interaction (example)
deck.append(cards["counterspell"])  # existing
deck.append(cards["swan_song"])    # existing
deck.append(cards["giant_growth"]) # add your new card here
```

4. [ ] Run the game: `python run.py --verbose`

5. [ ] Verify:
   - [ ] Game runs without errors
    - [ ] Your card appears in the deck/hand during play

### 🎉 Congratulations! You just extended the game!

---

## ✅ Phase 6: Run Tests & Understand Validation (10 minutes)

### Run the Test Suite:
- [ ] Run all tests: `pytest -v`
- [ ] Check coverage: `pytest --cov=src tests/`
- [ ] Read test output - understand what's being validated

### Read Test File:
- [ ] Open `tests/test_rules_engine.py`
- [ ] Read `test_land_drop()` - see how it validates land drops
- [ ] Read `test_cannot_play_two_lands()` - see rule enforcement
- [ ] Read `test_win_condition()` - see game-over detection

### Challenge: Write a Test
- [ ] Add a test for casting a creature
- [ ] Run it: `pytest tests/test_rules_engine.py::test_your_test_name -v`

---

## ✅ Phase 7: Deep Dive on Tools (15 minutes)

### Understand the Tool Layer:
1. [ ] Open `src/tools/game_tools.py`

2. [ ] Study each tool:
   - [ ] `GetGameStateTool.execute()` - Returns game state as dict
   - [ ] `GetLegalActionsTool.execute()` - What actions are available?
   - [ ] `ExecuteActionTool.execute()` - How are actions validated?
   - [ ] `AnalyzeThreatsTool.execute()` - How are threats assessed?

3. [ ] Trace a tool call:
   - [ ] Agent calls `get_legal_actions()`
   - [ ] Tool queries rules engine
   - [ ] Returns JSON with available actions
   - [ ] Agent chooses one
   - [ ] Agent calls `execute_action()`
   - [ ] Tool validates and executes
   - [ ] Game state updates

### Understanding Check:
- [ ] Can you explain why tools are necessary?
- [ ] What prevents the LLM from making illegal moves?
- [ ] How does the agent know what actions are available?

---

## ✅ Phase 8: Study the Decision-Making (20 minutes)

### Current Implementation (Simple Heuristics):
1. [ ] Open `src/agent/llm_agent.py`

2. [ ] Read `_make_simple_decision()` carefully:
   - [ ] Main phase: Play land → Cast spell → Pass
   - [ ] Combat: Attack with all → Pass
   - [ ] Blocking: Block first attacker → Pass

3. [ ] Understand the flow:
```
get_legal_actions()
    ↓
evaluate options (simple rules)
    ↓
choose best action
    ↓
execute_action()
```

### Future Implementation (LLM-based):
1. [ ] Read `IMPLEMENTATION_GUIDE.md` → "Integrating Real LLMs"

2. [ ] Understand the future flow:
```
get_game_state()
    ↓
LLM analyzes (Chain-of-Thought)
    ↓
LLM calls tools to explore
    ↓
LLM decides on action
    ↓
execute_action()
```

### Challenge: Design a Better Heuristic
- [ ] Think: How could the AI be smarter?
- [ ] Ideas: Save mana? Hold blockers? Target weak opponent?
- [ ] Optional: Implement your idea!

---

## ✅ Phase 9: Read the Roadmap (10 minutes)

### Understand the Development Plan:
- [ ] Open `ROADMAP.md`

- [ ] Read each phase:
  - [ ] **Phase 1**: Foundation (you are here!)
  - [ ] **Phase 2**: Chain-of-Thought & LLM integration
  - [ ] **Phase 3**: Commander-specific features
  - [ ] **Phase 4**: Complex rules & optimization
  - [ ] **Phase 5**: Polish & expansion

### Pick Your Next Goal:
- [ ] I want to: ___________________________
- [ ] It's in Phase: _______
- [ ] I'll need to learn: ___________________________

---

## ✅ Phase 10: Choose Your Path (Next Steps)

### Path A: Add More Cards (Easiest)
- Goal: Expand card database to 100-200 cards
- Skills: Data modeling, MTG knowledge
- Start: `src/data/cards.py`
- Time: 2-4 hours

### Path B: Integrate Real LLM (Most Exciting)
- Goal: Replace heuristics with GPT-4/Claude
- Skills: API integration, prompt engineering
- Start: `IMPLEMENTATION_GUIDE.md` → LLM integration
- Time: 4-8 hours

### Path C: Implement Complex Rules (Most Challenging)
- Goal: Add keywords (flying, trample, etc.)
- Skills: Game logic, software architecture
- Start: `src/core/rules_engine.py`
- Time: 8-16 hours

### Path D: Add 4-Player Support (Strategic)
- Goal: Full Commander multiplayer
- Skills: Game state management, political AI
- Start: `src/core/game_state.py`
- Time: 8-12 hours

### Path E: Build Testing Suite (Foundation)
- Goal: Comprehensive test coverage
- Skills: Testing, validation, edge cases
- Start: `tests/test_rules_engine.py`
- Time: 4-8 hours

**Your choice**: [ ] Path _____ (Write A, B, C, D, or E)

---

## 📊 Progress Tracker

Track your journey through the codebase!

### Understanding
- [ ] Read all documentation
- [ ] Understand architecture
- [ ] Traced a complete action flow
- [ ] Explained it to someone (even yourself!)

### Setup & Running
- [ ] Installed dependencies
- [ ] Ran the game successfully
- [ ] Ran tests successfully
- [ ] Game plays without errors

### Code Exploration
- [ ] Read core game logic files
- [ ] Read agent decision-making
- [ ] Read tool implementations
- [ ] Understand data flow

### First Contributions
- [ ] Added a new card
- [ ] Modified a rule
- [ ] Wrote a test
- [ ] Fixed a bug (if you found one!)

### Advanced Understanding
- [ ] Can explain agentic architecture
- [ ] Understand tool-based validation
- [ ] Know how to add new features
- [ ] Ready to integrate LLM

---

## 🎯 Completion Goals

### Beginner Goal (2-3 hours)
- [ ] Completed Phases 1-5
- [ ] Successfully ran the game
- [ ] Added 1-2 new cards
- [ ] Understand basic architecture

### Intermediate Goal (8-12 hours)
- [ ] Completed Phases 1-8
- [ ] Added 20+ new cards
- [ ] Wrote 3+ new tests
- [ ] Implemented a new rule or ability
- [ ] Modified AI decision-making

### Advanced Goal (20+ hours)
- [ ] Completed all phases
- [ ] Integrated real LLM (GPT-4 or Claude)
- [ ] Implemented Chain-of-Thought reasoning
- [ ] Added 100+ cards
- [ ] 4-player support
- [ ] Comprehensive test suite

---

## 🤝 Next Actions

**Right now, you should:**
1. [ ] Complete Phase 1 (Understanding) if you haven't
2. [ ] Complete Phase 2 (Setup)
3. [ ] Complete Phase 3 (First Run)
4. [ ] Choose a learning path from Phase 10

**After that:**
1. [ ] Read `IMPLEMENTATION_GUIDE.md` for your chosen path
2. [ ] Start coding!
3. [ ] Test your changes
4. [ ] Iterate and learn

---

## 💡 Tips for Success

### Learning Tips:
- **Don't rush** - Understanding is more important than speed
- **Run the code** - See it in action, don't just read
- **Modify things** - Break stuff, fix stuff, learn
- **Use tests** - They're your safety net

### Debugging Tips:
- **Use verbose mode** - `python src/main.py --verbose`
- **Add print statements** - See what's happening
- **Read error messages** - They tell you exactly what's wrong
- **Check the tests** - They show expected behavior

### Development Tips:
- **Start small** - Add one card before adding 50
- **Test frequently** - Don't write 100 lines without testing
- **Read existing code** - Pattern match your changes
- **Document changes** - Future you will thank you

---

## 🎉 Congratulations!

You now have:
- ✅ A complete MTG Commander AI codebase
- ✅ Comprehensive documentation
- ✅ A clear roadmap for development
- ✅ A structured learning path

**Now go build something amazing! 🚀**

---

**Questions? Stuck?**
- Re-read the relevant `.md` file
- Check `IMPLEMENTATION_GUIDE.md` for how-tos
- Look at existing code for patterns
- Write a test to understand behavior

**Remember**: This is a learning project. The goal is to understand modern AI architecture, not to build the perfect MTG AI. Have fun! 🎲✨
