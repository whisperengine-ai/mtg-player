# Phase 5: Strategic Reasoning Enhancement

## 🎯 Goal
Improve how the LLM uses existing tools for more sophisticated gameplay without adding new game rules. Make the AI think strategically by enforcing proper decision-making patterns.

## 📊 Current State (Phase 4 Complete)

### What's Already Built ✅
- **11 Strategic Tools**:
  - `get_game_state()` - Complete game visibility
  - `get_legal_actions()` - Available moves
  - `execute_action()` - Validated action execution
  - `analyze_threats()` - Opponent board analysis
  - `get_stack_state()` - Stack awareness
  - `can_respond()` - Instant-speed recommendations
  - `get_pending_triggers()` - Trigger tracking
  - `evaluate_position()` - Position scoring (0.0-1.0)
  - `can_i_win()` - Lethal detection
  - `recommend_strategy()` - Strategic guidance (RAMP/DEFEND/ATTACK/CLOSE)
  - `analyze_opponent()` - Opponent deck archetype detection

- **Complete Rules Engine**:
  - Stack and instant-speed interaction
  - Commander mechanics (damage, tax, command zone)
  - Multiplayer support (2-4 players)
  - Priority system
  - Combat resolution
  - Triggered abilities (ETB, dies)

- **Robust Architecture**:
  - Agent → Tools → Rules Engine separation
  - Heuristic fallback for testing
  - Comprehensive logging
  - 53+ passing tests

### What's Missing 🎯
- **Strategic Thinking Enforcement**: LLM doesn't consistently use strategic tools before acting
- **Multi-Turn Planning**: No memory or planning beyond current turn
- **Decision Quality**: Sometimes makes "legal but dumb" moves
- **Political Intelligence**: Doesn't reason about multiplayer dynamics deeply
- **Opponent Modeling**: Has the tool but doesn't integrate insights into decisions
- **Context Between Turns**: Forgets what happened last turn

## 🚀 Phase 5 Implementation Plan

### 5.1 Chain-of-Thought Enforcement (Week 15) ⭐ HIGH PRIORITY
*Goal: Force the LLM to think before acting*

#### Problem Statement
Currently, the LLM CAN call strategic tools but often doesn't. It might:
- Cast a spell without checking `evaluate_position`
- Attack without calling `can_i_win` or `analyze_opponent`
- Pass turn without using `recommend_strategy`

#### Solution: Mandatory Strategic Tool Sequence
Before making any action, the LLM MUST call strategic tools in order:

```
REQUIRED SEQUENCE:
1. evaluate_position() → Get position score (0.0-1.0)
2. analyze_opponent()  → Understand opponent threats
3. recommend_strategy() → Get strategic guidance
4. can_i_win()         → Check for lethal (combat phases only)
5. get_legal_actions() → See available moves
6. execute_action()    → Make the move
```

#### Implementation Tasks
- [ ] Add `_validate_decision_chain()` method to MTGAgent
- [ ] Track which strategic tools have been called this decision
- [ ] Block `execute_action()` if strategic tools not called
- [ ] Add prompt: "You MUST call these tools before deciding: ..."
- [ ] Add "thinking budget" - require minimum 3-5 tool calls per decision
- [ ] Test with unit tests for enforcement

#### Success Criteria
- ✅ Every action preceded by at least 3 strategic tool calls
- ✅ LLM reasoning references tool results explicitly
- ✅ Fewer "legal but dumb" moves (subjective evaluation)

---

### 5.2 Multi-Turn Planning (Week 15-16)
*Goal: Think 2-3 turns ahead*

#### Problem Statement
LLM makes one-shot decisions without considering sequences:
- "I'll play this creature" (but needed mana for removal next turn)
- "I'll attack now" (but should have built board first)

#### Solution: Planning Tool & Plan Validation

**New Tool: `plan_next_turns()`**
```python
def plan_next_turns(num_turns: int = 3) -> Dict:
    """
    Ask LLM to plan next N turns.
    Returns: {
        "turns": [
            {"turn": 1, "goal": "Ramp", "actions": ["play land", "cast ramp spell"]},
            {"turn": 2, "goal": "Build board", "actions": ["play creature"]},
            {"turn": 3, "goal": "Attack", "actions": ["attack with all"]}
        ],
        "win_condition": "Commander damage on Player 2",
        "risks": ["Player 3 has removal", "Low on cards"]
    }
    """
```

**Plan Tracking:**
- Cache the plan in agent state
- Each turn, check if current action aligns with plan
- If opponent disrupts plan, call `plan_next_turns()` again

#### Implementation Tasks
- [ ] Create `PlanNextTurnsTool` in `tools/evaluation_tools.py`
- [ ] Add plan storage to MTGAgent (`self.current_plan`)
- [ ] Add plan validation: "Does this action match the plan?"
- [ ] Add plan adaptation: "Opponent countered my spell, replan"
- [ ] Update prompts to mention planning
- [ ] Add tests for planning logic

#### Success Criteria
- ✅ LLM creates coherent 3-turn plans
- ✅ Plans reference specific win conditions
- ✅ Plans adapt when disrupted

---

### 5.3 Memory & Context Between Turns (Week 16)
*Goal: Remember what happened and learn from it*

#### Problem Statement
LLM has no memory:
- Player 2 countered my last spell → LLM forgets and tries again
- Player 3 is playing aggro → LLM doesn't prepare defenses
- Last turn I ramped → LLM doesn't follow up with payoff

#### Solution: Turn History Tracking

**Context Structure:**
```python
{
    "last_5_turns": [
        {
            "turn": 8,
            "player": "Player 1",
            "actions": ["cast Cultivate", "ramped to 6 lands"],
            "opponent_actions": [
                {"player": "Player 2", "action": "countered my spell"},
                {"player": "Player 3", "action": "attacked me for 4"}
            ],
            "key_events": ["Lost spell to counter", "Took damage"]
        },
        # ... more turns
    ],
    "opponent_patterns": {
        "Player 2": {
            "archetype": "Control",
            "has_countered": 2,
            "last_counter": "Turn 8",
            "threat_level": "high"
        },
        "Player 3": {
            "archetype": "Aggro",
            "total_damage_dealt": 12,
            "threat_level": "critical"
        }
    },
    "my_strategy_so_far": "Ramping to cast big creatures",
    "what_worked": ["Early ramp was successful"],
    "what_failed": ["Spell got countered by Player 2"]
}
```

#### Implementation Tasks
- [ ] Add `TurnHistory` class to track events
- [ ] Add `_record_turn()` method to MTGAgent
- [ ] Add `_build_context_summary()` to inject into prompts
- [ ] Extend `analyze_opponent()` to include historical data
- [ ] Add "lessons learned" tracking
- [ ] Add tests for context building

#### Success Criteria
- ✅ LLM references past events in reasoning
- ✅ Adapts to opponent patterns (e.g., "Player 2 counters big spells, so I'll bait first")
- ✅ Follows through on multi-turn strategies

---

### 5.4 Enhanced Combat Intelligence (Week 16-17)
*Goal: Make smart political combat decisions*

#### Problem Statement
Current combat is simple:
- Attacks first opponent only
- No political reasoning ("attack the archenemy")
- No threat-based targeting
- No fake attacks or bluffing

#### Solution: Political Combat System

**Combat Decision Framework:**
```python
def _decide_combat_target() -> str:
    """
    Choose attack target based on:
    1. Who's winning? (attack the archenemy)
    2. Who hurt me recently? (revenge attacks)
    3. Who can't block well? (vulnerable player)
    4. Political messaging ("I'm not the threat!")
    """
    
    # Get position of all players
    positions = evaluate_all_players()
    
    # Identify archenemy
    archenemy = max(positions, key=lambda p: p["score"])
    
    # Consider threats to ME
    threats_to_me = analyze_threats()
    biggest_threat = max(threats_to_me, key=lambda t: t["threat_score"])
    
    # Decision logic
    if archenemy.score > 0.7:
        return archenemy.id  # Attack the winner
    elif biggest_threat in recent_attackers:
        return biggest_threat.id  # Revenge attack
    else:
        return weakest_player.id  # Attack vulnerable player
```

#### Implementation Tasks
- [ ] Add `_choose_attack_target()` to heuristic decision logic
- [ ] Extend `declare_attackers` to accept target parameter
- [ ] Add political reasoning to prompts
- [ ] Add multi-target attack logic (split attacks)
- [ ] Add "fake attack" logic (declare but hold back some)
- [ ] Add tests for target selection

#### Success Criteria
- ✅ Attacks archenemy when appropriate
- ✅ Considers political implications
- ✅ References combat reasoning in logs

---

### 5.5 Improved Prompts & Reasoning Templates (Week 17)
*Goal: Better prompt engineering for strategic thinking*

#### Enhancements

**1. Phase-Specific Thinking Templates**
```
MAIN_PHASE_THINKING = """
Before acting, think through:
1. Where am I? (call evaluate_position)
2. Who's the threat? (call analyze_opponent)
3. What's my strategy? (call recommend_strategy)
4. What's my plan for next 2-3 turns?
5. Do I need to adapt my plan?
6. What's the risk if I pass?

Then decide your action.
"""
```

**2. Combat Thinking Template**
```
COMBAT_THINKING = """
Before attacking, answer:
1. Can I win THIS turn? (call can_i_win)
2. Who should I attack? (most threatening? weakest?)
3. What can go wrong? (blockers? tricks?)
4. Am I making myself a target?
5. Should I hold back creatures for defense?

Then decide your attacks.
"""
```

**3. Response Thinking Template**
```
INSTANT_RESPONSE_THINKING = """
Stack is not empty. Before responding:
1. What's on the stack? (call get_stack_state)
2. Can I respond? (call can_respond)
3. Should I respond? (is it worth it?)
4. What happens if I don't respond?
5. What happens if I do respond?

Then decide: respond or pass.
"""
```

#### Implementation Tasks
- [ ] Add thinking templates to `prompts.py`
- [ ] Inject templates based on phase
- [ ] Add "self-reflection" prompts ("Did I consider all options?")
- [ ] Add "explain your reasoning" requirement
- [ ] Test with different LLM providers (GPT-4, Claude, etc.)

---

## 📈 Success Metrics

### Quantitative Metrics
- **Tool Usage Rate**: % of decisions with ≥3 strategic tool calls (target: 100%)
- **Planning Depth**: Average turns planned ahead (target: 2-3)
- **Context Awareness**: % of decisions referencing past events (target: >50%)
- **Combat Intelligence**: % of attacks targeting highest-threat player (target: >70%)
- **Win Rate**: vs Phase 4 baseline (target: +15-20%)

### Qualitative Metrics (Human Evaluation)
- Decision quality: "Does this make sense strategically?"
- Reasoning clarity: "Can I understand why the AI did this?"
- Adaptability: "Does it adjust to opponent actions?"
- Political awareness: "Does it understand multiplayer dynamics?"

## 🧪 Testing Strategy

### Unit Tests
- [ ] Test tool call enforcement logic
- [ ] Test plan creation and validation
- [ ] Test context building and injection
- [ ] Test combat target selection

### Integration Tests
- [ ] Run 10 games with Phase 5 vs Phase 4
- [ ] Compare decision quality manually
- [ ] Verify strategic tool usage in logs
- [ ] Check win rates

### Manual Testing
- [ ] Play against the AI yourself
- [ ] Review LLM logs for reasoning quality
- [ ] Identify edge cases and failures

## 🚧 Known Limitations & Future Work

### Won't Be Perfect
- LLM can still make mistakes (it's AI, not perfect)
- Planning can be disrupted by opponents
- Some situations are genuinely ambiguous

### Future Enhancements (Phase 6+)
- **Alliance System**: Formal deals and pacts between players
- **Bluffing**: Fake plays to manipulate opponents
- **Meta-Learning**: Learn from previous games
- **Deck-Specific Strategies**: Adapt to different Commander decks
- **Card Synergy Recognition**: Identify combos dynamically

## 📚 Documentation Updates Needed

- [x] Create this document (PHASE5_STRATEGIC_REASONING.md)
- [ ] Update ROADMAP.md with Phase 5a section
- [ ] Add examples to ARCHITECTURE.md showing CoT flow
- [ ] Update README.md with Phase 5 status
- [ ] Create example log showing strategic reasoning

## 🎯 Current Focus: Chain-of-Thought Enforcement

**Starting Point**: `src/agent/llm_agent.py`
**Key Changes**:
1. Add `_validate_strategic_tools_called()` method
2. Track tool calls in `self._tool_call_history`
3. Block `execute_action` if validation fails
4. Update prompts to explain requirement
5. Add tests in `tests/test_llm_agent.py`

**Expected Outcome**: Every action is preceded by strategic analysis, leading to better decisions overall.

---

*Last Updated: 2025-10-30*
*Status: Phase 5.1 In Progress - Chain-of-Thought Enforcement*
