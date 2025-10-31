# Phase 5a.4: Political Combat Intelligence — Implementation Summary

**Status**: ✅ COMPLETE  
**Date**: January 2025  
**Purpose**: Teach the LLM multiplayer combat politics — who to attack based on threat level, vulnerability, revenge motivation, and political safety.

---

## Overview

Phase 5a.4 adds sophisticated combat target recommendation to the MTG agent, enabling politically-aware multiplayer decisions. Instead of naively attacking the lowest-life opponent, the agent now considers:

- **Threat Level (30%)**: Who's winning and dangerous?
- **Vulnerability (25%)**: Who can be eliminated or punished?
- **Revenge (25%)**: Who attacked me recently? (integrates with Phase 5a.3 turn history)
- **Political Safety (20%)**: Is it safe to attack this player?

---

## Implementation

### 1. Core Tool: `RecommendCombatTargetsTool`

**Location**: `src/tools/evaluation_tools.py` (lines ~1511-1779)

**Key Methods**:

```python
def execute(self, player_name: str, **kwargs) -> dict:
    """
    Returns:
    {
        "targets": [
            {
                "player_name": "Player 2",
                "priority_score": 0.75,  # Weighted: 30% threat + 25% vuln + 25% revenge + 20% political
                "threat_score": 0.8,
                "vulnerability_score": 0.6,
                "revenge_score": 1.0,
                "political_score": 0.9,
                "reasoning": "High threat • Attacked you recently • Safe to attack"
            },
            ...
        ],
        "primary_target": {...},  # Highest priority
        "political_advice": "⚔️ Player 2 is biggest threat | 🎯 Retaliation sends message",
        "summary": "Attack Player 2 (priority: 0.75) for revenge and threat elimination"
    }
    """
```

**Scoring Algorithms**:

1. **Threat Score** (`_calculate_threat_score`):
   - Life advantage: `(max_life - their_life) / max_life`
   - Board presence: `their_creatures / max_creatures`
   - Hand size: `their_hand_size / 7`
   - Weighted average (max 1.0)

2. **Vulnerability Score** (`_calculate_vulnerability_score`):
   - Low life: `1.0 - (their_life / max_life)`
   - Few blockers: `1.0 - (min(their_creatures, 5) / 5)`
   - Weighted average (max 1.0)

3. **Revenge Score** (`_calculate_revenge_score`):
   - Checks last 3 turns for attacks against you
   - Returns 1.0 if they attacked you recently, else 0.0
   - **Integrates with Phase 5a.3**: Uses `game_state.get_recent_history(3, event_filter="attack")`

4. **Political Score** (`_calculate_political_score`):
   - Safe to attack leaders: `score = 0.6 + 0.4 * (their_life / max_life)`
   - Risky to attack trailing players: `score = their_life / max_life`
   - Weighted by life total distribution

5. **Priority Score** (weighted combination):
   ```python
   priority = (threat * 0.30) + (vuln * 0.25) + (revenge * 0.25) + (political * 0.20)
   ```

**Political Advice Generation** (`_generate_political_advice`):
- Emojis: ⚔️ (threat), 🎯 (revenge), 💀 (eliminate), 🔀 (spread damage), ⚠️ (warning)
- Examples:
  - `"⚔️ Player 2 is biggest threat | 🎯 Retaliation sends message"`
  - `"💀 Player 3 can be eliminated | 🔀 Then spread damage"`
  - `"⚠️ Player 4 is trailing — politically risky to attack"`

---

### 2. Agent Integration

**Files Modified**:
- `src/agent/llm_agent.py`:
  - Import: `from src.tools.evaluation_tools import RecommendCombatTargetsTool`
  - Wiring: Instantiate and link `game_state` in `_setup_tools()`
  - Schema: Register tool in `_get_tool_schemas()`
  - Tool count: **11 → 12 → 13 tools**

- `src/agent/prompts.py`:
  - **SYSTEM_PROMPT**: Updated to 13 tools, added Phase 5a.4 section
  - **COMBAT_PROMPT**: Enhanced with 5-step combat process:
    1. **Get Combat Target Recommendations** (NEW!)
    2. **Check Recent History** (integrates Phase 5a.3)
    3. Analyze Opponents (Phase 5a.1)
    4. Check for Lethal (Phase 4)
    5. Make Smart Combat Decisions (multiplayer politics)

**Prompt Guidance**:
```
### 1. Get Combat Target Recommendations (NEW! Phase 5a.4)
- Use `recommend_combat_targets()` to see WHO you should attack
- Returns prioritized target list with:
  - **Threat scores**: Who's winning and dangerous
  - **Revenge opportunities**: Who attacked you recently
  - **Elimination chances**: Who you can kill this turn
  - **Political advice**: Who it's safe/smart to attack
- Example: "Attack Player 2 (high threat + attacked you last turn) over Player 3 (low life but politically risky)"
```

---

### 3. Integration with Phase 5a.3 (Turn History)

**Revenge Scoring Dependency**:
- `RecommendCombatTargetsTool._calculate_revenge_score()` calls:
  ```python
  recent_attacks = self.game_state.get_recent_history(turns=3, event_filter="attack")
  for event in recent_attacks:
      if event["attacker"] == target_player and "you" in event.get("targets", []):
          return 1.0  # They attacked you recently!
  return 0.0
  ```

**Why This Matters**:
- Without turn history: Agent attacks randomly or by simple heuristics
- With turn history + revenge scoring: Agent remembers who attacked it and retaliates
- Multiplayer dynamics: "Don't attack me or I'll attack you back" (deterrence)

---

## Testing Strategy

### Manual Testing (Recommended First):
```bash
python run.py --verbose
# Watch for combat target recommendations in logs
# Verify:
# - Tool called before attacks
# - Priority scores make sense
# - Political advice is reasonable
# - Revenge scoring works when opponent attacked you
```

### Unit Testing (TODO):
Create `tests/test_combat_intelligence.py`:
```python
def test_recommend_combat_targets_basic():
    """Verify tool returns targets sorted by priority."""
    
def test_threat_scoring():
    """High life + board = high threat."""
    
def test_vulnerability_scoring():
    """Low life + few blockers = high vulnerability."""
    
def test_revenge_scoring():
    """Recent attacker gets revenge score = 1.0."""
    
def test_political_scoring():
    """Leaders safe to attack, trailing players risky."""
    
def test_priority_calculation():
    """Weighted combination: 30% threat + 25% vuln + 25% revenge + 20% political."""
```

### Integration Testing:
```bash
pytest tests/test_llm_agent.py -k "test_agent_tool_count"
# Should pass: 13 tools registered
```

---

## Expected Behavior

### Before Phase 5a.4:
```
[Player 1's turn - COMBAT]
Analyzing opponents...
Player 2: 15 life, 3 creatures
Player 3: 8 life, 1 creature
Player 4: 20 life, 4 creatures

Attacking Player 3 (lowest life)...
```

### After Phase 5a.4:
```
[Player 1's turn - COMBAT]
Getting combat target recommendations...

recommend_combat_targets() result:
{
  "primary_target": {
    "player_name": "Player 2",
    "priority_score": 0.75,
    "threat_score": 0.8,
    "vulnerability_score": 0.6,
    "revenge_score": 1.0,  # ← Attacked us last turn!
    "political_score": 0.9,
    "reasoning": "High threat • Attacked you recently • Safe to attack"
  },
  "political_advice": "⚔️ Player 2 is biggest threat | 🎯 Retaliation sends message"
}

Attacking Player 2 with all creatures...
(Sending a message: Don't attack me without consequences!)
```

---

## Design Rationale

### Why These Weights?
- **30% Threat**: Winning players are the biggest problem
- **25% Vulnerability**: Eliminating a player reduces threats permanently
- **25% Revenge**: Deterrence matters in multiplayer (tit-for-tat)
- **20% Political**: Don't attack trailing players (looks like bullying)

### Why Separate Revenge from Threat?
- Revenge is **binary** (attacked you or didn't)
- Threat is **continuous** (life/board/hand)
- Combining them would dilute revenge motivation
- 25% weight ensures recent attackers are prioritized

### Why Political Safety?
- Multiplayer has social dynamics beyond game state
- Attacking the losing player makes you a target ("Why attack them, not the leader?")
- Attacking the leader is politically justified ("They're winning, fair game")

---

## Known Limitations

1. **Single-Turn Memory**: Revenge only checks last 3 turns
   - Future: Could accumulate "grudge score" over entire game
   
2. **No Coalition Detection**: Doesn't notice if two players are working together
   - Future: Phase 5b could add "political alliance" scoring

3. **No Retaliation Prediction**: Doesn't model "If I attack, will they attack me back?"
   - Future: Could use opponent modeling archetype (aggressive vs defensive)

4. **Binary Revenge**: Either 1.0 or 0.0, no gradient
   - Future: Could weight by damage dealt or frequency of attacks

---

## Files Modified

### New Code:
- `src/tools/evaluation_tools.py` (+268 lines): `RecommendCombatTargetsTool` class

### Updated Code:
- `src/agent/llm_agent.py` (3 edits): Import, wiring, schema registration
- `src/agent/prompts.py` (2 edits): SYSTEM_PROMPT (13 tools), COMBAT_PROMPT (5-step process)
- `tests/test_llm_agent.py` (2 edits): Tool count assertions (12 → 13)

### Documentation:
- `PHASE5A4_COMBAT_INTELLIGENCE.md` (this file)
- `.github/copilot-instructions.md`: Already mentions Phase 5a.4

---

## Next Steps

1. **Validate in Gameplay**:
   ```bash
   python run.py --verbose --max-turns=10
   # Watch combat decisions with new tool
   ```

2. **Analyze Logs**:
   - Check `logs/game_YYYYMMDD_HHMMSS.log` for combat target calls
   - Verify political advice makes sense
   - Confirm revenge scoring triggers correctly

3. **Iterate if Needed**:
   - Adjust weights if behavior seems off (e.g., too much revenge, not enough threat)
   - Add unit tests for edge cases (e.g., all opponents equal life)

4. **Move to Next Phase**:
   - Phase 5a.2: Multi-turn Planning (needs reasoning model)
   - Phase 5b: Advanced Tactics (bluffing, hand estimation, etc.)

---

## Success Criteria

✅ **Tool Implementation**: RecommendCombatTargetsTool complete with 4-factor scoring  
✅ **Agent Integration**: Tool wired, schema registered, prompt updated  
✅ **Documentation**: This file + inline comments  
⏳ **Testing**: Manual testing pending, unit tests TODO  
⏳ **Validation**: Gameplay logs pending

---

## Summary

Phase 5a.4 transforms the agent from a naive "attack lowest life" bot into a politically-aware multiplayer player. By combining threat analysis, vulnerability assessment, revenge motivation, and political safety, the agent now makes strategic combat decisions that respect multiplayer dynamics. The 25% revenge weight (tied to Phase 5a.3's turn history) ensures the agent retaliates against aggressors, creating a deterrence effect. This is a major step toward human-like multiplayer play.

**Next**: Test in actual games to validate behavior, then move to Phase 5a.2 (Multi-turn Planning) or Phase 5b (Advanced Tactics).
