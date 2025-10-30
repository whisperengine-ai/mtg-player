# Opponent Modeling Tool

## Overview

The **Opponent Modeling Tool** (`OpponentModelingTool`) analyzes opponents' board composition and hand to detect their deck archetype, identify threats, and assess relative danger levels. This enables intelligent political targeting and threat prioritization in multi-player games.

## API

### Function Call
```
analyze_opponent(opponent_id: Optional[str] = None)
```

### Parameters
- **opponent_id** (optional): Specific opponent to analyze. If omitted, analyzes all opponents.

### Returns

#### Single Opponent Response
```json
{
  "success": true,
  "opponent_id": "p2",
  "opponent_name": "Player 2",
  "archetype": "aggro",
  "confidence": 0.85,
  "threat_level": 0.72,
  "biggest_threat": {
    "name": "Dragon",
    "power": 8,
    "toughness": 8,
    "threat_score": 24.0
  },
  "board_summary": {
    "creatures": 6,
    "total_power": 24,
    "lands": 3,
    "hand_size": 4
  },
  "card_types": {
    "aggro_creatures": 4,
    "control_creatures": 0,
    "combo_creatures": 0,
    "ramp_artifacts": 0
  },
  "estimated_strategy": "Wide aggro (many small creatures)",
  "political_value": "ELIMINATE (highest priority threat)",
  "summary": "🔴 **Player 2** plays aggro (threat: 72%). Biggest threat: Dragon (8/8)"
}
```

#### Multiple Opponents Response
```json
{
  "success": true,
  "opponent_count": 2,
  "opponents": [
    {
      "id": "p2",
      "name": "Player 2",
      "archetype": "aggro",
      "threat_level": 0.72,
      "biggest_threat": "Dragon"
    },
    {
      "id": "p3",
      "name": "Player 3",
      "archetype": "control",
      "threat_level": 0.45,
      "biggest_threat": "None"
    }
  ],
  "most_threatening": { ... },
  "archetypes_present": ["aggro", "control"]
}
```

## Archetype Detection

### Supported Archetypes

| Archetype | Characteristics | Detection | Strategy |
|-----------|-----------------|-----------|----------|
| **Aggro** | Many creatures, high power/toughness or haste | 5+ creatures, high power creatures | Apply pressure, remove threats |
| **Control** | High toughness creatures, many lands, defensive abilities (flying, reach) | Few creatures but high defenses, many lands | Break through defenses |
| **Combo** | Creatures/spells with tap abilities or synergy engines | Cards with special text, large hand | Disrupt before combo triggers |
| **Ramp** | Mana acceleration artifacts (Sol Ring, Arcane Signet, etc.) | 3+ ramp artifacts | Race before they accelerate |
| **Midrange** | Balanced creature/removal mix | Moderate creatures + defensive creatures | Evaluate case-by-case |

### Scoring Logic

```
aggro_score = (creatures with power >= 3 or haste) * 2
            + bonus(5-8) if creature_count >= 5

control_score = (high-toughness or evasion creatures) * 1.5
              + land_count * 0.5
              + bonus(2) if creature_count <= 2

combo_score = (creatures with tap/draw abilities) * 2
            + bonus(1) if hand_size >= 5

ramp_score = ramp_artifact_count * 1.5
           + bonus(3) if ramp_artifact_count >= 3

midrange_score = creature_count * 0.8 
               + control_creatures * 0.5
```

## Threat Assessment

### Threat Level (0.0 - 1.0)

Combines multiple factors:
- **Board Power**: Sum of all creature power (20+ = 1.0)
- **Aggro Creatures**: Each adds +0.1
- **Hand Size**: Each card adds +0.05
- **Life Total Advantage**: +0.2 if opponent ahead in life
- **Result**: Clamped to [0.0, 1.0]

### Political Value Classifications

| Classification | Threat Level | Recommendation |
|---|---|---|
| **ELIMINATE** | ≥ 0.8 | Top priority - remove immediately |
| **CONTAIN** | 0.6-0.79 | Watch carefully, respond to threats |
| **MONITOR** | 0.4-0.59 | Keep eye on board state |
| **VULNERABLE** | < 0.4 + life ≤ 15 | Focus damage here |
| **SAFE** | < 0.4 + life > 15 | Lower priority |

## Biggest Threat Identification

### Threat Score Calculation

```
threat_score = power + (toughness * 0.5)
             + flying_bonus(3)
             + unblockable_bonus(4)
             + trample_bonus(1)
```

Returns card with highest threat score, considering:
- **Power/Toughness**: Core damage potential
- **Flying**: Hard to block, typically +3
- **Unblockable**: Can't be stopped, +4
- **Trample**: Gets through blockers, +1

## Usage Examples

### Single Opponent Analysis
```python
# Analyze specific opponent's threats
result = tool.execute(opponent_id="p2")
print(f"{result['opponent_name']} plays {result['archetype']}")
print(f"Threat level: {result['threat_level']:.0%}")
print(f"Biggest threat: {result['biggest_threat']['name']}")
print(f"Action: {result['political_value']}")
```

### Multi-Opponent Political Analysis
```python
# Analyze all opponents to decide who to target
result = tool.execute()
threats = result["opponents"]
threats.sort(key=lambda x: x["threat_level"], reverse=True)

print(f"Most threatening: {threats[0]['name']} ({threats[0]['threat_level']:.0%})")
print(f"Archetypes: {', '.join(result['archetypes_present'])}")
```

### Strategic Decision Making
```python
# Use archetype to choose strategy
result = tool.execute(opponent_id="p3")

if result["archetype"] == "aggro":
    # Board wipe or evasion
    strategy = "defensive"
elif result["archetype"] == "control":
    # Break through with evasion
    strategy = "aggressive"
elif result["archetype"] == "ramp":
    # Race before they cast big spells
    strategy = "tempo"
else:
    strategy = "balanced"
```

## Integration with LLM Agent

The tool is automatically available to the LLM agent through function calling:

```
LLM can call: analyze_opponent(opponent_id=None)
Returns: archetype, threat_level, biggest_threat, political_value
LLM uses this to inform: target selection, defense priorities, mulligan decisions
```

## Implementation Details

### Key Methods

- **execute(opponent_id)**: Main entry point, delegates to _analyze_opponent()
- **_analyze_opponent(opponent)**: Core analysis logic for single opponent
- **_determine_archetype()**: Scores board composition against archetype patterns
- **_identify_biggest_threat()**: Finds most dangerous creature on board
- **_calculate_threat_level()**: Combines metrics into 0.0-1.0 threat score
- **_assess_political_value()**: Maps threat level to political priority
- **_generate_summary()**: Creates human-readable threat description

### Data Dependencies

Reads from opponent state:
- `opponent.battlefield`: List of CardInstance on board
- `opponent.hand`: List of Card in hand
- `opponent.life`: Current life total
- Card properties: `name`, `power`, `toughness`, `keywords`, `oracle_text`

## Test Coverage

| Test | Coverage |
|---|---|
| `test_tool_schema()` | Schema generation |
| `test_aggro_archetype_detection()` | Aggro detection with 6 creatures |
| `test_threat_assessment_high_threat()` | Flying creature threat bonus |
| `test_biggest_threat_identification()` | Correct threat ranking |
| `test_empty_opponent_board()` | Empty board handling |
| `test_confidence_scoring()` | Confidence in [0, 1] |
| `test_eliminate_political_priority()` | High threat political classification |
| `test_hand_size_influences_threat()` | Hand size increases threat |
| `test_strategy_estimate_wide_aggro()` | Wide aggro strategy estimate |

**Result**: 9/9 tests passing ✅

## Future Enhancements

1. **Archetype Refinement**: Track archetype changes across turns (e.g., aggro → control pivot)
2. **Synergy Detection**: Identify card combinations (e.g., Craterhoof + Blightsteel)
3. **Probability Weighting**: Estimate likelihood of opponent having key cards in hand
4. **Historical Patterns**: Remember previous decks/archetypes from same opponent
5. **Mana Analysis**: Assess color requirements to predict future plays
6. **Removal Tracking**: Identify opponents that can remove specific threats

## Related Tools

- **Strategy Recommendation Tool**: Uses opponent model to inform strategic recommendations
- **Can I Win Tool**: Evaluates damage potential against threats identified by opponent modeling
- **Analyze Threats Tool**: Lower-level threat assessment for current board state
