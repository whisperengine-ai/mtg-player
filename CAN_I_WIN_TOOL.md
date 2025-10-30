# Can I Win? Tool - Phase 2 Strategic Enhancement

## Overview

The **`CanIWinTool`** analyzes if a player can deal lethal damage to an opponent this turn by calculating total damage from:
- Attacking creatures on the battlefield
- Direct damage spells in hand

## Location
- **Implementation**: `src/tools/evaluation_tools.py` (class `CanIWinTool`)
- **Tests**: `tests/test_can_i_win_tool.py` (7 test cases, all passing ✅)

## Tool Behavior

### Input
```python
tool.execute(player_id: Optional[str] = None)
```
- `player_id`: (Optional) Specific player to check. Defaults to active player.

### Output
```python
{
    "success": True,
    "player_id": "p1",
    "player_name": "Alice",
    "can_win": True,                              # Can lethal be achieved?
    "lethal_target": "Bob",                       # Weakest opponent (if lethal possible)
    "damage": 12,                                 # Total damage potential
    "damage_breakdown": {
        "creatures": 9,                           # Damage from attacking creatures
        "spells": 3                               # Damage from spell casts
    },
    "line": "Attack with 3 creatures (9 damage) + Cast Lightning Bolt (3 damage)",
    "creatures_attacking": 3,
    "spells_to_cast": 1,
    "considerations": [                           # Warnings/notes
        "Not enough mana for all damage spells (need 5, have 3)"
    ],
    "summary": "YES! You can win this turn! Deal 12 damage to Bob (they have 11 life)..."
}
```

## Damage Calculation Logic

### Creature Damage
- Iterates through all creatures on battlefield
- Checks if creature can attack: `creature.can_attack()` (not tapped, not summoning sick, has power > 0)
- Includes power modifiers (counters, temporary bonuses)
- Sums total power

### Spell Damage
- Searches hand for damage-dealing spells (instants/sorceries)
- Extracts damage from card text using regex patterns:
  - `"Lightning Bolt"` → 3 damage
  - `"deals X damage"` → X damage
  - `"target opponent loses X life"` → X damage
  - Card names like "Shock" → predefined values
- Only includes spells player can afford (mana available)
- Tracks minimum mana needed

### Lethal Detection
- Compares total damage against each opponent's remaining life
- Identifies all possible lethal targets
- **Targets weakest opponent first** (lowest life total) - critical for multiplayer strategy

## Integration Points

### In LLM Agent
- **Added to**: `src/agent/llm_agent.py`
- **Tool schema**: Included in `_get_tool_schemas()` (line ~360)
- **Available at**: `self.tools["can_i_win"]`
- **Use case**: LLM calls this during Main Phase or Combat when planning aggressive turns

### In Heuristic Decision-Making (Future)
- Can be called during combat phase decision to determine if lethal is possible
- Informs whether to attack aggressively or conservatively
- Helps with mulligan decisions early game (planning for lethal)

## Test Coverage

| Test Case | Purpose | Status |
|-----------|---------|--------|
| `test_can_i_win_with_lethal_creatures` | Verify damage calculation and lethal detection | ✅ PASS |
| `test_can_i_win_insufficient_damage` | Verify non-lethal situations | ✅ PASS |
| `test_can_i_win_with_damage_spells` | Verify spell damage extraction | ✅ PASS |
| `test_can_i_win_no_creatures` | Verify edge case: no creatures | ✅ PASS |
| `test_can_i_win_summoning_sick` | Verify summoning sick detection | ✅ PASS |
| `test_can_i_win_target_selection` | Verify weakest opponent targeting | ✅ PASS |
| `test_damage_extraction_patterns` | Verify damage pattern matching | ✅ PASS |

## Example Usage

### LLM Prompt Integration
The tool is automatically available to the LLM in its function calling schema. The LLM can call it during reasoning:

```
LLM: "Let me check if I can close out this game..."
→ Calls: can_i_win()
→ Gets: {can_win: True, damage: 21, lethal_target: "Opponent"}
LLM: "Perfect! I can deal lethal with my attack + spells. Let me attack all creatures..."
```

### Heuristic Decision (Future)
```python
# In combat decision logic
can_win_result = can_i_win_tool.execute()
if can_win_result["can_win"]:
    # Commit all creatures to attack
    attack_with_all_creatures()
else:
    # Be conservative
    attack_with_creatures(power_threshold=2)
```

## Design Decisions

### 1. Why include spell damage?
- Many decks win with creature + burn spell combinations
- Enables lethal detection in mixed strategies (tempo + burn)
- More comprehensive than just creature math

### 2. Why target weakest opponent?
- In multiplayer (4-player Commander), weakest opponent is strategic target
- Eliminates player with least resources quickly
- Prevents unnecessary calculation when multiple lethal options exist
- Political value: removes player with "least developed board"

### 3. Why check mana availability?
- Must be realistic about which spells can actually cast
- Factors in current mana pool + mana from untapped lands
- Returns consideration message if spell mana insufficient
- Prevents "theoretical" lethal that can't actually execute

## Performance Notes
- **Time complexity**: O(n) where n = creatures + spells in hand
- **Typical execution**: < 1ms
- **No state mutations**: Pure read operation

## Future Enhancements
1. **Combat math**: Account for creature abilities (flying, evasion) when they prevent blocking
2. **Combat prediction**: Simulate combat to include combat damage in lethal calc
3. **Protection analysis**: Check if opponent has instant-speed responses (counter/removal)
4. **Combo detection**: Identify and chain multiple damage sources (e.g., Doubling Season effects)

---

## Command to Run Tests
```bash
python3 -m pytest tests/test_can_i_win_tool.py -v
```

**Expected Output**: 7 passed ✅
