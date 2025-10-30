# 🎯 Getting Started: Your Journey into Agentic AI

Welcome! This guide is designed for developers who have used LLMs for basic text generation (like "write me a poem") but haven't yet built **agentic AI systems** that can take actions and use tools.

**By the end of this guide, you will:**
- ✅ Understand what "agentic AI" means
- ✅ Know how to use function calling / tool use
- ✅ Build confidence with structured AI systems
- ✅ Make your first contribution to the codebase

**Estimated time:** 90 minutes (broken into phases)

---

## 📖 What You're About to Learn

### From Basic Prompting to Agentic AI

**Where you probably are now:**
```python
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Write a poem"}]
)
print(response)  # Just text!
```

**Where you'll be after this guide:**
```python
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Play a turn of Magic"}],
    tools=[get_game_state, execute_action, analyze_threats]  # ← AI can DO things!
)

# AI decides: "I'll call get_game_state(), then execute_action('play_land')"
# Your code executes those functions
# AI sees results and makes next decision
```

**The difference?**
- Basic LLM: Can only **talk** about things
- Agentic AI: Can **do** things through tools

This project teaches you the second approach!

---

## ✅ Phase 1: Conceptual Understanding (15 minutes)

### 📚 Read These Documents (in order):

#### 1. README.md (5 min)
- [ ] Read the **Overview** section
- [ ] Understand the project's goal (AI plays Magic)
- [ ] See the **Quick Start** commands

**Key Question:** Why is Magic a good problem for agentic AI?
<details>
<summary>Answer (click to reveal)</summary>

Magic requires:
- **Observation** (what's on the board?)
- **Reasoning** (what's the best play?)
- **Action** (cast spell, attack)
- **Validation** (is this move legal?)

This mirrors real-world agentic AI: observe → reason → act → validate!
</details>

#### 2. ARCHITECTURE.md (7 min)
- [ ] Read **"Introduction: What is Agentic AI?"**
- [ ] Read **"Core Concepts: Tools vs Fine-tuning"**
- [ ] Read **"Our Three-Layer Architecture"**

**Key Question:** What are the three layers and why are they separate?
<details>
<summary>Answer (click to reveal)</summary>

1. **Agent Layer** - Makes decisions (LLM or heuristic)
2. **Tools Layer** - Interface for actions
3. **Rules Engine** - Validates everything

They're separate so you can:
- Swap the AI (OpenAI → Anthropic)
- Test without AI (heuristic mode)
- Validate all actions (no illegal moves)
</details>

#### 3. PROJECT_SUMMARY.md (3 min)
- [ ] Skim the **Implementation Status**
- [ ] See what features exist

### 🧠 Understanding Check

Before moving on, make sure you can answer:
- [ ] What does "agentic AI" mean? (AI that uses tools to take actions)
- [ ] Why use tools instead of fine-tuning? (Faster, cheaper, more reliable)
- [ ] What's the role of the Rules Engine? (Validates all actions)

If you're unsure, re-read the sections above!

---

## ✅ Phase 2: Environment Setup (10 minutes)

### Installation

Open your terminal and run these commands:

```bash
# Navigate to project
cd /Users/markcastillo/git/mtg-player

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import pydantic; print('✅ Setup complete!')"
```

### Verification Tests

- [ ] Run tests: `pytest` (should pass)
- [ ] Check structure: `ls -la src/`
- [ ] Verify tools exist: `ls src/tools/game_tools.py`

**Troubleshooting:**
- If `pytest` fails, read TROUBLESHOOTING.md
- If imports fail, make sure venv is activated
- If dependencies fail, try `pip install --upgrade pip` first

---

## ✅ Phase 3: First Run (Heuristic Mode) (10 minutes)

**Why heuristic mode first?** 
- No API key needed
- Faster iterations
- See the architecture in action
- Understand tool flow

### Run the Game

### Understanding the Agent

The agent is where decisions happen! Let's see how.

#### File: `src/agent/llm_agent.py`

Read these methods in order:

1. **`_setup_tools()`** - What tools does the agent have access to?
   - [ ] Read the tool list
   - [ ] Understand: Agent doesn't know HOW tools work, just WHAT they do

2. **`_make_llm_decision()`** (LLM mode) OR `_make_simple_decision()` (Heuristic mode)
   - [ ] Compare the two approaches
   - [ ] See: Both call the same tools!

3. **Tool calling flow:**
```python
# LLM Mode
response = llm.chat(messages, tools)
if response.tool_calls:
    for call in response.tool_calls:
        result = execute_tool(call)
        
# Heuristic Mode  
state = get_game_state()
threats = analyze_threats()
actions = get_legal_actions()
# ... simple rules to choose action ...
execute_action(chosen_action)
```

### 🧠 Key Insight

Both modes demonstrate **separation of concerns**:
- **Agent** decides what to do
- **Tools** provide interface
- **Rules Engine** enforces rules

This is the essence of agentic AI architecture!

---

## ✅ Phase 9: Experiment with Prompts (10 minutes)

Want to change how the AI thinks? Edit the prompts!

#### File: `src/agent/prompts.py`

This file contains all the instructions given to the LLM.

### Exercise: Make the AI More Aggressive

1. Open `src/agent/prompts.py`
2. Find the strategy section
3. Add emphasis on attacking:

```python
STRATEGY_GUIDELINES = """
...existing text...

AGGRESSIVE PLAY:
- Attack whenever you have an advantage
- Prioritize dealing damage over board development
- Take calculated risks to pressure opponents
"""
```

4. Run the game: `python run.py --verbose`
5. Observe: Does the AI attack more?

### What You're Learning

**Prompt engineering** is how you control LLM behavior WITHOUT retraining!

- Change prompts → Change behavior
- No code changes needed
- Iterate quickly

---

## ✅ Phase 10: Advanced Challenges (Optional)

Ready to go deeper? Try these challenges:

### Challenge 1: Add a New Tool

Create a tool that counts life advantage:

```python
# Add to src/tools/game_tools.py

class GetLifeAdvantageTool(BaseTool):
    """Calculate life advantage over opponents."""
    
    name = "get_life_advantage"
    description = "Returns life differential between you and opponents"
    
    def _run(self, player_idx: int) -> dict:
        player = self.rules_engine.game_state.players[player_idx]
        opponents = [p for i, p in enumerate(self.rules_engine.game_state.players) if i != player_idx]
        
        avg_opp_life = sum(p.life for p in opponents) / len(opponents)
        advantage = player.life - avg_opp_life
        
        return {
            "my_life": player.life,
            "avg_opponent_life": avg_opp_life,
            "advantage": advantage
        }
```

Then:
1. Register the tool in `_setup_tools()`
2. Update prompts to mention it
3. Test: `python run.py --verbose`

### Challenge 2: Write a Complex Test

Test the entire game loop:

```python
# Add to tests/test_rules_engine.py

def test_complete_turn_sequence(rules_engine: RulesEngine):
    """Test a full turn: untap, upkeep, draw, main, combat, main, end."""
    # Setup
    # ... add setup code ...
    
    # Untap phase
    # Upkeep phase
    # Draw phase
    # Main phase 1
    # Combat phase
    # Main phase 2
    # End phase
    
    # Assert all phases executed correctly
```

### Challenge 3: Compare LLM Strategies

Run multiple games and compare:

```bash
# Run 5 games with different prompts
for i in {1..5}; do
    python run.py --verbose > "game_$i.log"
done

# Analyze: Which prompt strategy won more?
```

---

## 🎓 What You've Learned

Congratulations! You now understand:

✅ **Agentic AI Concepts**
- What makes AI "agentic" (tool use)
- Why tools beat fine-tuning for structured tasks
- How to design tool-based systems

✅ **Architecture Patterns**
- Three-layer architecture (Agent, Tools, Rules)
- Separation of concerns
- Validation and error handling

✅ **Practical Skills**
- Function calling / tool use APIs
- JSON schema design
- Prompt engineering
- Testing AI systems

✅ **This Specific Project**
- How to run games (LLM and heuristic modes)
- How to add cards
- How to create tools
- How to modify AI behavior

---

## 📚 Next Steps

### Beginner Path
1. ✅ Read all phase 4 documentation (PHASE4_*.md files)
2. ✅ Try different deck archetypes
3. ✅ Experiment with prompt modifications
4. ✅ Add more test cards

### Intermediate Path
1. ✅ Implement a new tool (e.g., "predict next turn")
2. ✅ Add a new deck archetype
3. ✅ Improve heuristic AI logic
4. ✅ Write comprehensive tests

### Advanced Path
1. ✅ Implement instant-speed response system
2. ✅ Add multiplayer support (3-4 players)
3. ✅ Build tournament mode (multiple games, track wins)
4. ✅ Add memory/learning (agent improves over games)
5. ✅ Integrate different LLM providers (Anthropic, etc.)

---

## 🤝 Contributing

Want to contribute? Great!

### Good First Issues
- Add more cards to `src/data/cards.py`
- Improve test coverage
- Add docstrings to functions
- Write more examples in documentation

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

---

## ❓ FAQ

**Q: Do I need an expensive GPU?**  
A: No! We use API-based LLMs (OpenAI, Anthropic, etc.). Runs on any computer.

**Q: How much do API calls cost?**  
A: ~$0.01-0.05 per game with GPT-4. Use `--no-llm` for free testing.

**Q: Can I use different LLM providers?**  
A: Yes! Check `src/agent/llm_agent.py` to see how to add providers.

**Q: Why Magic: The Gathering?**  
A: Magic is complex (teaches agentic patterns) but structured (rules validate everything). Perfect for learning!

**Q: What if I don't know Magic rules?**  
A: That's fine! The rules engine handles everything. Focus on the AI architecture.

**Q: Can I use this for other games?**  
A: Absolutely! The architecture works for any turn-based game. Swap out the rules engine!

---

## 📖 Additional Resources

### Documentation
- **ARCHITECTURE.md** - Deep dive on design decisions
- **LOGGING.md** - Understanding the logging system
- **PHASE4_*.md** - Advanced features documentation

### External Learning
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [Anthropic Tool Use Guide](https://docs.anthropic.com/claude/docs/tool-use)
- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)

### Community
- Open an issue: Questions, bugs, feature requests
- Discussions: Share your experiments, ask for help

---

## 🎉 You Did It!

You've gone from basic LLM prompting to understanding agentic AI architecture!

**What you can do now:**
- ✅ Build tool-based AI systems
- ✅ Design clean, testable architectures
- ✅ Use function calling APIs
- ✅ Validate AI actions with rules engines
- ✅ Iterate quickly with prompt engineering

**Next time someone asks "How do I make an AI that can DO things?"** - you know the answer: **Tools!**

Happy coding! 🚀
python run.py --no-llm --verbose

# Look for your card in the output
# It should appear in hand or on battlefield
```

#### Step 4: Verify

- [ ] Game runs without errors
- [ ] Your card appears in the deck
- [ ] No crashes when drawn

### 🎉 Congratulations! You just extended the game!

**What you learned:**
- How to add data (cards)
- How the deck building system works
- How to test changes

---

## ✅ Phase 7: Understanding Tests (15 minutes)

Tests teach you how the system SHOULD work.

### Run the Test Suite

```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_rules_engine.py -v

# Run with coverage
pytest --cov=src tests/
```

### Read a Test File

Open `tests/test_rules_engine.py` and read these tests:

#### Test: `test_land_drop()`
```python
def test_land_drop(rules_engine: RulesEngine):
    # Setup: Player has a Forest in hand
    # Action: Play the land
    # Assert: Land is now on battlefield
```

**What it teaches:** How to interact with the rules engine programmatically.

#### Test: `test_cannot_play_two_lands()`
```python
def test_cannot_play_two_lands(rules_engine: RulesEngine):
    # Setup: Player has two Forests
    # Action: Play first land (succeeds)
    # Action: Try to play second land (fails!)
    # Assert: Second attempt raises ValueError
```

**What it teaches:** Rules engine enforces game rules.

### 🧠 Challenge: Write Your Own Test

Add this test to `tests/test_rules_engine.py`:

```python
def test_casting_creature(rules_engine: RulesEngine):
    """Test that casting a creature works correctly."""
    player_idx = 0
    player = rules_engine.game_state.players[player_idx]
    
    # Setup: Give player mana and a creature
    # (You fill this in!)
    
    # Cast the creature
    # (You fill this in!)
    
    # Assert creature is on battlefield
    # (You fill this in!)
```

Run it: `pytest tests/test_rules_engine.py::test_casting_creature -v`

---

## ✅ Phase 8: Deep Dive on Agent Decision-Making (15 minutes)
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
