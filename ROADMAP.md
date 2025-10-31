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
- [x] The Stack (priority, responses, counters) **COMPLETE**
- [x] Instant-speed interaction **COMPLETE**
- [x] Priority passing system **COMPLETE**
- [x] Stack-based spell resolution **COMPLETE**
- [ ] Triggered abilities and state-based actions
- [ ] Replacement effects
- [ ] Layers system (for complex interactions)
- [ ] Keywords (haste, flying, trample, etc.)

**Phase 4 Achievement Summary:**
- ✅ 9 comprehensive stack tests
- ✅ 13 instant-speed interaction tests
- ✅ 38 total tests passing (100% pass rate)
- ✅ Stack data structure with LIFO ordering
- ✅ Priority system for 2-4 players
- ✅ 8 instant spells in database
- ✅ 2 stack-awareness tools (GetStackStateTool, CanRespondTool)
- ✅ LLM prompts teach stack mechanics
- ✅ Instant-speed response recommendations

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
- [ ] Mandatory strategic tool sequence before actions
- [ ] Tool call validation in agent
- [ ] Require: `evaluate_position()` → `analyze_opponent()` → `recommend_strategy()` → action
- [ ] Add "thinking budget" - minimum 3-5 tool calls per decision
- [ ] Block `execute_action()` if strategic tools not called
- [ ] Update prompts to explain requirements

### 5a.2 Multi-Turn Planning
- [ ] New tool: `plan_next_turns()` - Creates 2-3 turn plans
- [ ] Plan storage and validation in agent
- [ ] Plan adaptation when opponents disrupt
- [ ] Reference plans in decision reasoning

### 5a.3 Memory & Context Between Turns
- [ ] Turn history tracking (last 5 turns)
- [ ] Opponent pattern recognition
- [ ] "What worked/failed" analysis
- [ ] Inject context into LLM prompts
- [ ] Adapt strategy based on history

### 5a.4 Enhanced Combat Intelligence
- [ ] Political target selection (attack the archenemy)
- [ ] Threat-based attack decisions
- [ ] Multi-target attack logic
- [ ] Alliance-aware combat
- [ ] Combat reasoning in prompts

### 5a.5 Improved Prompt Engineering
- [ ] Phase-specific thinking templates
- [ ] Self-reflection prompts
- [ ] Reasoning quality requirements
- [ ] Test across LLM providers

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
- **Language**: Python 3.13+ (excellent LLM libraries)
- **LLM Framework**: LangChain or LlamaIndex (tool calling, agents)
- **LLM Provider**: 
  - OpenAI GPT-4 (best reasoning)
  - Anthropic Claude 3.5 Sonnet (great for complex tasks)
  - Local: Ollama with Llama 3.1 or Qwen2.5 (cost-effective testing)

### Supporting Libraries
- **Data**: Pydantic for models, SQLite for card database
- **Vector DB**: Qdrant or Chroma (for card similarity)
- **Testing**: Pytest
- **API Integration**: Scryfall API for card data

### Optional Enhancements
- **Embeddings**: sentence-transformers (local)
- **Visualization**: Rich library for CLI, or Gradio/Streamlit for web
- **Logging**: Structured logging for decision analysis

---

## Success Metrics

### Phase 1-2 Metrics
- Percentage of legal moves made (target: >95%)
- Games completed without errors (target: >90%)
- Basic threat identification accuracy

### Phase 3-4 Metrics
- Win rate against random AI (target: >80%)
- Win rate against simple heuristic AI (target: >50%)
- Political decision quality (human evaluation)

### Phase 5 Metrics
- Win rate against competent human players (target: 25-40%)
- Decision explanation quality (human evaluation)
- Game completion time (reasonable turn times)

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
