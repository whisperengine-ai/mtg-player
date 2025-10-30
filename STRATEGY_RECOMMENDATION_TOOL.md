# Strategy Recommendation Tool - Phase 2.2 Strategic Enhancement

## Overview

The **`StrategyRecommendationTool`** analyzes the current game state and recommends one of four strategic approaches:
- **RAMP** 📈 - Accelerate resources and build toward key spells
- **DEFEND** 🛡️ - Stabilize the board and survive threats
- **ATTACK** ⚔️ - Press advantage with creatures
- **CLOSE** 🏁 - Execute the win condition

## Location
- **Implementation**: `src/tools/evaluation_tools.py` (class `StrategyRecommendationTool`)
- **Tests**: `tests/test_strategy_recommendation_tool.py` (8 test cases, all passing ✅)

## Tool Behavior

### Input
```python
tool.execute(player_id: Optional[str] = None)
```
- `player_id`: (Optional) Specific player to recommend for. Defaults to active player.

### Output
```python
{
    "success": True,
    "player_id": "p1",
    "player_name": "Alice",
    "strategy": "ATTACK",                         # RAMP, DEFEND, ATTACK, or CLOSE
    "confidence": 0.85,                           # 0.0-1.0 confidence in recommendation
    "reasoning": "You have a good board (3 creatures, 6 power) while being slightly ahead...",
    "priorities": [
        "Attack with all creatures that can deal damage",
        "Play creatures to increase board presence",
        "Deal damage and put pressure on opponents",
        "Look for opening to close game"
    ],
    "game_phase": "precombat_main",
    "position_score": 0.65,                       # Relative position (0.0-1.0)
    "board_presence": {
        "creatures": 3,
        "total_power": 6,
        "lands": 3,
        "untapped_lands": 2
    },
    "resources": {
        "total_mana": 5,
        "mana_colors": {
            "white": 0, "blue": 0, "black": 0, "red": 0,
            "green": 5, "colorless": 0
        }
    },
    "threats_detected": 2,                        # Opponent threatening creatures
    "hand_size": 6,
    "summary": "⚔️ **ATTACK** - You have a good board (3 creatures, 6 power)..."
}
```

## Strategy Decision Logic

### Decision Tree

```
if position >= 0.7 AND total_power >= 6
  → CLOSE (confidence 0.9)
    
else if position >= 0.6 AND total_power >= 8 AND creatures >= 2
  → ATTACK (confidence 0.85)
    
else if position <= 0.3 AND threats >= 3
  → DEFEND (confidence 0.9)
    
else if position <= 0.4 AND threats >= 2
  → DEFEND (confidence 0.8)
    
else if creatures <= 1 AND mana <= 3 AND lands <= 2
  → RAMP (confidence 0.85)
    
else if mana <= 2
  → RAMP (confidence 0.75)
    
else if position >= 0.45 AND creatures >= 2 AND total_power >= 4
  → ATTACK (confidence 0.7)
    
else
  → Default based on position score
```

## Evaluation Components

### Position Score (0.0-1.0)
- **0.0-0.2**: Critical danger (life ≤ 10)
- **0.2-0.4**: Danger zone (life ≤ 20)
- **0.4-0.7**: Moderate position (based on relative life totals)
- **0.7-1.0**: Winning position

### Board Presence
- `creatures`: Count of creatures on battlefield
- `total_power`: Sum of creature power
- `lands`: Count of lands on battlefield
- `untapped_lands`: Available mana producers

### Threat Assessment
- Counts opponent creatures with power ≥ 2 or evasion abilities (flying, unblockable)
- Higher threat count → more likely to recommend DEFEND

### Resource Evaluation
- Total mana available (from lands + mana pool)
- Mana breakdown by color
- Lower resources → more likely to recommend RAMP

## Action Priorities

### RAMP Strategy
1. Play land to accelerate mana
2. Cast mana dorks or ramp spells
3. Build toward key spells
4. Avoid unnecessary trades

### DEFEND Strategy
1. *(If threats > 3)*: Stabilize the board immediately
2. Remove or block the biggest threat
3. Trade creatures favorably if possible
4. Gain life if available
5. Hold interaction (removal/instants) in hand

### ATTACK Strategy
1. Attack with all creatures that can deal damage
2. Play creatures to increase board presence
3. Deal damage and put pressure on opponents
4. Look for opening to close game

### CLOSE Strategy
1. Execute the plan for lethal
2. Use remaining spells to protect creatures
3. Attack to deal final damage
4. Hold responses for opponent interaction

## Test Coverage

| Test Case | Purpose | Status |
|-----------|---------|--------|
| `test_strategy_close_winning` | CLOSE when winning with strong board | ✅ PASS |
| `test_strategy_attack_good_position` | ATTACK with good board | ✅ PASS |
| `test_strategy_defend_under_threat` | DEFEND when under heavy threat | ✅ PASS |
| `test_strategy_ramp_low_resources` | RAMP with few resources | ✅ PASS |
| `test_strategy_includes_priorities` | Verify action priorities returned | ✅ PASS |
| `test_strategy_board_presence_details` | Board state evaluation | ✅ PASS |
| `test_strategy_player_specified` | Recommend for specific player | ✅ PASS |
| `test_strategy_all_required_fields` | All fields present in response | ✅ PASS |

## Example Usage

### LLM Integration
```
LLM: "Let me understand the situation first..."
→ Calls: recommend_strategy()
→ Gets: {strategy: "ATTACK", confidence: 0.85, priorities: [...]}
LLM: "Great! I should attack with my creatures. Let me execute..."
→ Calls: execute_action(declare_attackers)
```

### Heuristic Agent
```python
# In combat decision phase
strategy_result = recommend_strategy_tool.execute()

if strategy_result["strategy"] == "CLOSE":
    attack_with_all_creatures()
elif strategy_result["strategy"] == "ATTACK":
    attack_aggressively()
elif strategy_result["strategy"] == "DEFEND":
    hold_defensive_position()
elif strategy_result["strategy"] == "RAMP":
    play_land_and_pass()
```

### Strategic Planning
```python
result = tool.execute()
print(f"Strategy: {result['strategy']}")
print(f"Reasoning: {result['reasoning']}")
print(f"This turn priorities:")
for i, priority in enumerate(result['priorities'], 1):
    print(f"  {i}. {priority}")
```

## Design Decisions

### 1. Why Four Strategies?
- **RAMP**: Core early-game strategy (resource accumulation)
- **DEFEND**: Essential for survival and tempo
- **ATTACK**: Core mid-game strategy (pressure + damage)
- **CLOSE**: End-game focus (finish execution)
- Four covers the full game arc without overcomplicating

### 2. Why Confidence Scores?
- Different situations have different clarity
- Winning position with strong board → high confidence (0.9)
- Borderline position → lower confidence (0.6)
- LLM can use confidence to decide whether to override recommendation

### 3. Why Include All Evaluation Details?
- Transparency: LLM/heuristic sees the reasoning
- Debugging: Easy to understand why recommendation was made
- Learning: Can track which factors drove decisions
- Adaptability: Future enhancements can reweight factors

### 4. Why Target Weakest Opponent (Implicitly)?
- In multiplayer, focus fire is strategic
- Eliminates threats systematically
- Simplifies game tree evaluation
- Can be overridden by LLM if political circumstances warrant

## Integration with Other Tools

### Works Well With:
- **`can_i_win`** - Can I Win? checks if CLOSE strategy is viable
- **`evaluate_position`** - Position score used in both
- **`analyze_threats`** - Threat detection feeds strategy

### Data Flow:
```
evaluate_position (get position score)
  ↓
recommend_strategy (incorporate all factors)
  ↓
can_i_win (if strategy is CLOSE, verify lethal)
  ↓
execute_action (act on recommendation)
```

## Future Enhancements

1. **Aggression Parameter**: Scale strategy based on risk tolerance
2. **Matchup Awareness**: Adjust for opponent deck type
3. **Long-term Planning**: Think 2-3 turns ahead, not just this turn
4. **Synergy Detection**: Recognize combos and synergies
5. **Political Strategy**: Account for multiplayer dynamics
6. **Card Advantage Weighting**: Factor hand size into strategy

---

## Command to Run Tests
```bash
python3 -m pytest tests/test_strategy_recommendation_tool.py -v
```

**Expected Output**: 8 passed ✅
