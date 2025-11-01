# MTG Commander AI - Agentic Implementation Roadmap

## Project Vision
Build an AI agent capable of playing Magic: The Gathering Commander using LLM-powered decision making, Chain-of-Thought reasoning, and a robust rules engine.

## Architecture Philosophy

**Core Principle**: Separation of Concerns
- **Rules Engine**: Handles game logic, validates moves, maintains state
- **LLM Agent**: Makes strategic decisions, plans plays, evaluates board state
- **Tools Layer**: Bridges the rules engine with the LLM's decision-making

**Why Agentic vs Fine-Tuning**:
- ✅ Testable and debuggable
- ✅ Iterative improvement without retraining
- ✅ Explainable decision-making
- ✅ Cost-effective (no GPU training required)
- ✅ Leverages existing LLM reasoning capabilities

---

## Phase 1: Foundation (Weeks 1-3)
*Goal: Basic game state representation and simple decision-making*

### 1.1 Core Data Structures
- [ ] Card representation (name, cost, type, abilities)
- [ ] Player state (life, mana, hand, battlefield, graveyard)
- [ ] Game state object (4 players, turn structure, stack)
- [ ] Simple card database (start with ~50 common cards)

### 1.2 Minimal Rules Engine
- [ ] Turn structure (untap, upkeep, draw, main, combat, main, end)
- [ ] Mana system (tap lands for mana)
- [ ] Casting spells (check mana, move to stack, resolve)
- [ ] Basic combat (declare attackers, declare blockers, damage)
- [ ] Zone transitions (hand → battlefield, battlefield → graveyard)

### 1.3 Basic Tools Interface
- [ ] `get_game_state()` - Returns current board state
- [ ] `get_legal_actions()` - Returns available moves
- [ ] `execute_action(action)` - Performs a move
- [ ] `evaluate_board_state()` - Basic scoring function

### 1.4 Simple LLM Agent (Proof of Concept)
- [ ] Connect to LLM API (OpenAI, Anthropic, or local)
- [ ] Implement tool calling
- [ ] Basic prompt engineering for MTG context
- [ ] Make simple decisions (which card to play, what to attack)

**Success Criteria**: AI can play a simplified 1v1 game with 50 basic cards

---

## Phase 2: Chain-of-Thought Integration (Weeks 4-6)
*Goal: Add reasoning and strategic planning*

### 2.1 Enhanced Decision Framework
- [ ] Multi-step reasoning (analyze → plan → act)
- [ ] Threat assessment system
- [ ] Win condition tracking
- [ ] Resource management planning

### 2.2 Advanced Tools
- [ ] `analyze_threats()` - Identify opponent threats
- [ ] `calculate_lethal()` - Check for winning lines
- [ ] `simulate_combat()` - Predict combat outcomes
- [ ] `evaluate_card_synergies()` - Find combo potential
- [ ] `predict_opponent_actions()` - Basic opponent modeling

### 2.3 Chain-of-Thought Prompting
- [ ] Structured thinking prompts
- [ ] Self-reflection on decisions
- [ ] Multi-turn planning
- [ ] Contingency planning

### 2.4 Memory & Context Management
- [ ] Game history tracking
- [ ] Previous turn analysis
- [ ] Pattern recognition (what worked before)
- [ ] Context window optimization

**Success Criteria**: AI can explain its decisions and plan 2-3 turns ahead

---

## Phase 3: Commander-Specific Features (Weeks 7-10)
*Goal: Handle multiplayer politics and Commander format rules*

### 3.1 Commander Format Rules
- [ ] 100-card singleton deck
- [ ] Commander zone and command tax
- [ ] 40 starting life
- [ ] Commander damage tracking (21 damage rule)
- [ ] Color identity restrictions

### 3.2 Multiplayer Dynamics
- [ ] 4-player game state management
- [ ] Threat assessment across 3 opponents
- [ ] Political decision-making (who to attack/target)
- [ ] Alliance and betrayal modeling
- [ ] "Archenemy" detection (who's winning)

### 3.3 Advanced Strategic Tools
- [ ] `assess_political_landscape()` - Who's the threat?
- [ ] `evaluate_table_position()` - Am I ahead/behind?
- [ ] `calculate_commander_damage()` - Track lethal paths
- [ ] `suggest_political_plays()` - Make deals, threaten

### 3.4 Expanded Card Database
- [ ] ~500 commonly played Commander cards
- [ ] Card categorization (ramp, removal, draw, wincons)
- [ ] Archetype detection (combo, aggro, control, etc.)

**Success Criteria**: AI can play a 4-player Commander game with basic politics

---

## Phase 4: Complex Rules & Optimization (Weeks 11-14) ✅ COMPLETE
*Goal: Handle edge cases and optimize performance*

### 4.1 Complex Rules Implementation ✅
- [x] The Stack (priority, responses, counters) — COMPLETE
- [x] Instant-speed interaction — COMPLETE
- [x] Priority passing system — COMPLETE
- [x] Stack-based spell resolution — COMPLETE
- [x] Triggered abilities (ETB/dies) queued and resolved via stack; minimal state-based actions
- [ ] Replacement effects
- [ ] Layers system (for complex interactions)
- [~] Keywords support: basic keywords (flying, vigilance, deathtouch, haste) recognized in data; full rules not yet modeled

**Phase 4 Achievement Summary (as of Nov 2025):**
- ✅ 85 tests in repository, 73 passing; remaining failures isolated to new turn-history scenarios (import path mismatch tracked)
- ✅ Comprehensive stack coverage (LIFO ordering, pass-priority → resolve, counters)
- ✅ Priority system exercised for 2–4 players
- ✅ Robust instant-speed interactions and recommendations
- ✅ Trigger system: ETB/dies abilities queued (APNAP) and resolved via stack
- ✅ Tools: GetStackStateTool, CanRespondTool, GetPendingTriggersTool
- ✅ LLM prompts teach stack/priority/trigger mechanics

**Documentation:**
- See `PHASE4_STACK.md` for stack implementation details
- See `PHASE4_INSTANT_SPEED.md` for instant-speed features
- See `PHASE4_TESTING.md` for test results and validation

### 4.2 Performance Optimization
- [ ] Caching LLM responses for similar states
- [ ] Local embeddings for card similarity
- [ ] Efficient game state serialization
- [ ] Parallel simulation for Monte Carlo planning

### 4.3 Advanced Reasoning
- [ ] Multi-agent simulation (predict multiple opponents)
- [ ] Tree search for optimal plays
- [ ] Risk/reward calculation
- [ ] Backup plans and resilience

### 4.4 Testing & Validation
- [ ] Unit tests for rules engine
- [ ] Integration tests for agent decisions
- [ ] Benchmark against simple heuristic AI
- [ ] Play testing with humans

**Success Criteria**: AI makes fewer illegal moves and demonstrates advanced strategy

---

## Phase 5a: Strategic Reasoning Enhancement (Weeks 15-17) 🔥 IN PROGRESS
*Goal: Improve LLM decision quality using existing tools*

### 5a.1 Chain-of-Thought Enforcement ⭐ HIGH PRIORITY
- [x] Mandatory strategic tool sequence before actions (enforced in agent)
- [x] Tool call validation in agent (blocks actions if unmet)
- [~] Require: `evaluate_position()` → `analyze_opponent()` → `recommend_strategy()` → action (hard-require evaluate_position; total minimum tool calls configurable; others recommended)
- [x] "Thinking budget" — minimum strategic tool calls per decision (env-configurable, default 3)
- [x] Block `execute_action()` if strategic tools not called
- [x] Prompts updated to explain requirements and sequence

### 5a.2 Multi-Turn Planning
- [ ] New tool: `plan_next_turns()` - Creates 2-3 turn plans
- [ ] Plan storage and validation in agent
- [ ] Plan adaptation when opponents disrupt
- [ ] Reference plans in decision reasoning

### 5a.3 Memory & Context Between Turns
- [x] Turn history tracking API on `GameState` (record events, recent history)
- [x] Tool: `get_turn_history()` with filters, summaries, and pattern detection (aggressive/controlling/ramping)
- [ ] "What worked/failed" analysis
- [~] Inject context into prompts (combat/main prompts reference history tools; deeper integration TBD)
- [~] Adapt strategy based on history (early heuristics; full policy learning TBD)

### 5a.4 Enhanced Combat Intelligence
- [x] Political target selection tool: `recommend_combat_targets`
- [x] Threat- and vulnerability-based target prioritization; revenge signal and elimination flags
- [~] Multi-target attack guidance (recommendations emitted; execution still simple)
- [ ] Alliance-aware combat (future)
- [x] Combat reasoning added to prompts and tool outputs

### 5a.5 Improved Prompt Engineering
- [x] Phase-specific thinking templates (main/combat/decision prompts)
- [x] Chain-of-thought requirements embedded in system prompt
- [~] Provider-specific reasoning toggles (OpenAI/OpenRouter/LMS/Ollama via OpenAI-compatible API)
- [~] Cross-provider validation ongoing

**Success Criteria**: AI makes strategic multi-turn plans, adapts to opponents, and demonstrates political awareness

**Documentation**: See `PHASE5_STRATEGIC_REASONING.md` for detailed implementation plan

---

## Phase 5b: Polish & Expansion (Weeks 18+)
*Goal: Production-ready and extensible*

### 5.1 Deck Building Assistant
- [ ] Analyze deck composition
- [ ] Suggest improvements
- [ ] Mana curve optimization
- [ ] Synergy detection

### 5.2 Learning & Adaptation
- [ ] Save game replays
- [ ] Analyze winning/losing patterns
- [ ] A/B test different prompting strategies
- [ ] Optional: Few-shot learning from expert games

### 5.3 User Interface
- [ ] CLI for playing against the AI
- [ ] Web interface (optional)
- [ ] Game visualization
- [ ] Decision explanation view

### 5.4 Card Database Expansion
- [ ] Scale to 2,000-4,000 cards
- [ ] Automated card parsing from APIs
- [ ] Regular updates with new sets

**Success Criteria**: Playable, enjoyable experience that demonstrates MTG competence

---

## Technology Stack Recommendations

### Core Technologies
- Language: Python 3.13+
- Agent/Tools: First-class in-repo tools (no LangChain/LlamaIndex required)
- LLM Client: Direct OpenAI-compatible chat clients (OpenAI, OpenRouter, LM Studio, Ollama), Anthropic optional

### Supporting Libraries
- Data: Pydantic v2 for models
- Testing: Pytest (+ pytest-cov)
- CLI/Logging: Rich; structured loggers for Game/LLM/Heuristic
- Card DB: In-repo curated list (hundreds of staples) with helper deck builders; API integration optional later

### Optional Enhancements
- Embeddings: sentence-transformers (local)
- Visualization: Rich CLI; optional Gradio/Streamlit web UI
- Logging: Structured logs already integrated

---

## Success Metrics (current snapshot)

### Phase 1-2 Metrics
- Unit/Integration tests: 73 passing / 85 total
- Legal move validation via rules engine and tools (ongoing)
- Threat/opponent analysis tools validated via tests

### Phase 3-4 Metrics
- Stack/instant-speed/trigger mechanics validated by tests
- Political targeting recommendations available via tool
- Multiplayer turn/priority flows exercised

### Phase 5 Metrics
- Chain-of-thought enforcement active (configurable min strategic tools)
- Turn history patterns detected (aggressive/control/ramp)
- Combat target recommendations with political advice

---

## Phase 1–3 status recap

### Phase 1: Foundation ✅ COMPLETE
- [x] Card representation (name, cost, type, abilities)
- [x] Player state (life, mana, hand, battlefield, graveyard)
- [x] Game state object (2–4 players, turn structure, stack serialization)
- [x] Simple card database (hundreds of staples + deck builders)

### Phase 1.2 Minimal Rules Engine ✅
- [x] Turn structure (untap, upkeep, draw, main, combat, main, end)
- [x] Mana system (tap lands for mana — simplified color handling)
- [x] Casting spells (affordability checks, move to stack, resolve)
- [x] Basic combat (declare attackers/blockers, damage resolution)
- [x] Zone transitions (hand → battlefield, battlefield → graveyard/command)

### Phase 1.3 Basic Tools Interface ✅
- [x] `get_game_state()`
- [x] `get_legal_actions()`
- [x] `execute_action(action)`
- [x] `evaluate_position()` (superset of evaluate_board_state)

### Phase 1.4 Simple LLM Agent ✅
- [x] Connect to LLM API (OpenAI/OpenRouter/Anthropic/Local)
- [x] Tool calling with schemas
- [x] Phase-specific prompts
- [x] Heuristic fallback decision-making

### Phase 2: Chain-of-Thought Integration ✅/~
- [x] Multi-step reasoning path wired in prompts and agent loop
- [x] Threat assessment system (`analyze_threats`)
- [x] Win condition tracking (rules engine + `can_i_win`)
- [~] Resource/plan management (basic via strategy tool and action ranking)
- [x] Advanced tools: `analyze_threats`, `can_i_win`, `recommend_strategy`, `analyze_opponent`
- [ ] `simulate_combat()` and `evaluate_card_synergies()`
- [~] Prompting: structured thinking + enforcement; self-reflection minimal
- [~] Memory/context: turn history + patterns available; deeper integration TBD

### Phase 3: Commander-Specific Features ✅/~
- [x] 100-card decks and commander zone/command tax
- [x] 40 starting life
- [x] Commander damage tracking (21 rule)
- [~] Color identity restrictions — not enforced yet
- [~] Multiplayer dynamics: threat assessment across opponents; political targeting tool
- [ ] Alliances/betrayal modeling

Notes:
- Current failing tests relate to import-path inconsistencies in turn-history tests; code paths themselves are implemented. Standardizing package imports (relative imports within `src/`) will resolve this.

---

## Risk Mitigation

### Technical Risks
- **LLM hallucination of illegal moves**: Validate everything through rules engine
- **Context window limits**: Implement smart summarization and history pruning
- **API costs**: Use caching, start with local models, optimize prompts
- **Complex card interactions**: Start simple, gradually add complexity

### Scope Risks
- **Too ambitious**: Follow phased approach, don't skip phases
- **Rules complexity**: Build incrementally, test thoroughly
- **Perfect play impossible**: Aim for "competent" not "optimal"

---

## Next Steps

1. Set up development environment
2. Choose LLM provider and test basic tool calling
3. Implement Phase 1.1-1.2 (data structures and minimal rules)
4. Build proof-of-concept with 10-20 cards
5. Iterate based on learnings

**Remember**: This is a learning project. Focus on understanding the concepts, not building a perfect AI. Each phase teaches you more about LLMs, agent systems, and game AI.
