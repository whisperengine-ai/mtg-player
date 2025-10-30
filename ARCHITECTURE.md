# MTG Commander AI - System Architecture

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      GAME STARTS                            │
│  • Initialize 2-4 players with 100-card decks               │
│  • Each player draws 7 cards                                │
│  • Set first active player                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   TURN BEGINS                               │
│  Phase: Beginning → Main → Combat → Main → End             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              LLM AGENT ACTIVATES                            │
│                                                              │
│  1. 🧠 Analyze: What's happening?                           │
│     ├─ Call get_game_state()                                │
│     ├─ Call analyze_threats()                               │
│     └─ Review: Life totals, board state, resources          │
│                                                              │
│  2. 🎯 Plan: What's my goal?                                │
│     ├─ Win condition assessment                             │
│     ├─ Resource management                                  │
│     └─ Threat prioritization                                │
│                                                              │
│  3. 🔍 Explore: What can I do?                              │
│     └─ Call get_legal_actions()                             │
│                                                              │
│  4. 🤔 Evaluate: Chain-of-Thought Reasoning                 │
│     ├─ "If I play this land..."                             │
│     ├─ "If I attack with this creature..."                  │
│     ├─ "What are the risks?"                                │
│     └─ "What's the expected value?"                         │
│                                                              │
│  5. ✅ Decide: Choose best action                           │
│     └─ Call execute_action(...)                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              RULES ENGINE VALIDATES                          │
│                                                              │
│  • Is this action legal?                                     │
│  • Does player have resources?                               │
│  • Correct phase/step?                                       │
│  • Valid targets?                                            │
│                                                              │
│  ✅ If valid → Execute                                       │
│  ❌ If invalid → Reject (agent tries again)                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               ACTION EXECUTES                                │
│                                                              │
│  • Update game state                                         │
│  • Move cards between zones                                 │
│  • Adjust life totals                                        │
│  • Resolve combat damage                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            CHECK WIN CONDITIONS                              │
│                                                              │
│  • Any player at 0 life?                                     │
│  • 21 commander damage?                                      │
│  • Only one player left?                                     │
│                                                              │
│  If yes → GAME OVER                                          │
│  If no → Continue to next action/phase                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Making a Decision

```
┌──────────────┐
│  LLM Agent   │
└──────┬───────┘
       │
       │ 1. Request game state
       ▼
┌──────────────────────┐
│  get_game_state()    │────────┐
│  Tool                │        │
└──────┬───────────────┘        │ 2. Reads from
       │                        │
       │ Returns JSON           │
       ▼                        ▼
┌──────────────┐         ┌─────────────┐
│  LLM Agent   │         │ Game State  │
│  (Reasoning) │◄────────┤  Object     │
└──────┬───────┘         └─────────────┘
       │
       │ 3. "I should play a land"
       │
       │ 4. Request legal actions
       ▼
┌──────────────────────┐
│ get_legal_actions()  │
│  Tool                │
└──────┬───────────────┘
       │
       │ 5. Returns available moves
       ▼
┌──────────────┐
│  LLM Agent   │
│  (Decision)  │
└──────┬───────┘
       │
       │ 6. execute_action("play_land", card_id="...")
       ▼
┌──────────────────────┐
│ execute_action()     │
│  Tool                │
└──────┬───────────────┘
       │
       │ 7. Forwards to rules engine
       ▼
┌──────────────────────┐
│  Rules Engine        │
│  • Validates         │────► ❌ Invalid → Return error
│  • Executes          │
│  • Updates state     │
└──────┬───────────────┘
       │
       │ ✅ Success
       ▼
┌──────────────┐
│  LLM Agent   │
│  (Continue)  │
└──────────────┘
```

---

## Component Interactions

```
┌─────────────────────────────────────────────────────────────┐
│                        MTG Agent                            │
│                                                              │
│  Properties:                                                 │
│  • game_state: GameState                                     │
│  • rules_engine: RulesEngine                                 │
│  • llm_client: OpenAI/Anthropic/Ollama                       │
│  • tools: Dict[str, Tool]                                    │
│  • messages: List[Message]  # conversation history          │
│                                                              │
│  Methods:                                                    │
│  • take_turn_action() → bool                                 │
│  • analyze_position() → Dict                                 │
│  • _make_decision() → Action                                 │
└────┬──────────────┬──────────────┬────────────────┬─────────┘
     │              │              │                │
     │ Uses         │ Uses         │ Uses           │ Uses
     ▼              ▼              ▼                ▼
┌─────────┐  ┌──────────┐  ┌─────────────┐  ┌────────────┐
│  Game   │  │  Rules   │  │   Tools     │  │    LLM     │
│  State  │  │  Engine  │  │   Layer     │  │   Client   │
└─────────┘  └──────────┘  └─────────────┘  └────────────┘
     │              │              │                │
     │              │              │                │
     ├─ Players[]   ├─ play_land() ├─ get_game_    │
     ├─ Turn info   ├─ cast_spell()│    state()     │
     ├─ Phase/Step  ├─ combat()    ├─ get_legal_   │
     ├─ Stack[]     ├─ validate()  │    actions()   │
     └─ Winner      └─ advance()   ├─ execute_     │
                                   │    action()    │
                                   └─ analyze_     │
                                       threats()    │
```

---

## Example Decision Tree: Combat Phase

```
                        Combat Phase
                             │
                             ▼
                  ┌──────────────────┐
                  │ Declare Attackers│
                  └────────┬─────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Attack   │    │ Attack   │    │  Don't   │
    │ Player A │    │ Player B │    │  Attack  │
    └─────┬────┘    └─────┬────┘    └─────┬────┘
          │               │               │
          │               │               │
    "High threat"    "Low life"      "Need to"
    "Must kill"      "Easy target"   "defend"
          │               │               │
          ▼               ▼               ▼
    ┌──────────────────────────────────────┐
    │     LLM Evaluates Each Option:       │
    │                                       │
    │  • Expected damage dealt              │
    │  • Risk of losing creatures           │
    │  • Political consequences             │
    │  • Board state after combat           │
    └────────────────┬──────────────────────┘
                     │
                     ▼
              ┌─────────────┐
              │  Best Move  │
              └──────┬──────┘
                     │
                     ▼
              execute_action()
```

---

## State Machine: Turn Structure

```
╔═══════════════════════════════════════════════════════════╗
║                    BEGINNING PHASE                        ║
╚═══════════════════════════════════════════════════════════╝
          │
          ├─► Untap Step    (Automatic: untap all)
          ├─► Upkeep Step   (Triggered abilities)
          └─► Draw Step     (Automatic: draw 1 card)
          │
          ▼
╔═══════════════════════════════════════════════════════════╗
║                 PRECOMBAT MAIN PHASE                      ║
╚═══════════════════════════════════════════════════════════╝
          │
          │ Player can:
          ├─► Play land (once per turn)
          ├─► Cast spells (creatures, sorceries, etc.)
          ├─► Activate abilities
          └─► Pass priority
          │
          ▼
╔═══════════════════════════════════════════════════════════╗
║                     COMBAT PHASE                          ║
╚═══════════════════════════════════════════════════════════╝
          │
          ├─► Begin Combat   (Last chance for instants)
          ├─► Declare Attackers (Active player chooses attackers)
          ├─► Declare Blockers  (Defenders choose blockers)
          ├─► Combat Damage     (Deal damage, creatures die)
          └─► End Combat        (Combat over)
          │
          ▼
╔═══════════════════════════════════════════════════════════╗
║                POSTCOMBAT MAIN PHASE                      ║
╚═══════════════════════════════════════════════════════════╝
          │
          │ (Same as precombat main phase)
          │
          ▼
╔═══════════════════════════════════════════════════════════╗
║                      ENDING PHASE                         ║
╚═══════════════════════════════════════════════════════════╝
          │
          ├─► End Step      (End of turn triggers)
          └─► Cleanup Step  (Discard to 7, clear damage)
          │
          ▼
╔═══════════════════════════════════════════════════════════╗
║                    NEXT PLAYER'S TURN                     ║
╚═══════════════════════════════════════════════════════════╝
```

---

## Why Agentic Architecture Works for MTG

### Traditional Approach (Fine-tuning) ❌
```
Large Dataset of Games
        │
        ▼
  Fine-tune LLM
        │
        ▼
  Generate Action
        │
        ▼
   Hope it's legal? 🤞
```

**Problems**:
- Need millions of game examples
- Model might hallucinate illegal moves
- Hard to debug when it fails
- Expensive to train and update
- Can't explain decisions

### Agentic Approach (Tool Use) ✅
```
Base LLM (GPT-4, Claude, etc.)
        │
        ▼
   Call tools to:
   • See game state
   • Get legal moves
   • Execute validated action
        │
        ▼
   Always legal! ✅
```

**Benefits**:
- No training data needed
- All moves validated by rules engine
- Easy to debug (see tool calls)
- Can explain reasoning (CoT)
- Iterate quickly without retraining

---

## Chain-of-Thought Example

```
USER: "It's your main phase. What do you do?"

LLM (Internal reasoning):
┌─────────────────────────────────────────┐
│ 1. ANALYZE                              │
│    - I have 5 life (danger!)            │
│    - Opponent has 20 life               │
│    - Opponent has 3 creatures attacking │
│    - I have 2 blockers                  │
│    - I have 4 mana available            │
│                                         │
│ 2. THREATS                              │
│    - Will die next turn if I don't act │
│    - Need blockers or removal           │
│                                         │
│ 3. OPTIONS                              │
│    - Cast Serra Angel (4/4 flying)      │
│    - Cast Lightning Bolt (3 damage)     │
│    - Play another land                  │
│                                         │
│ 4. EVALUATE                             │
│    - Serra Angel: Good blocker,         │
│      but doesn't stop all attackers     │
│    - Lightning Bolt: Removes one        │
│      creature, saves 3 life             │
│    - Land: Doesn't help immediately     │
│                                         │
│ 5. DECISION                             │
│    - Cast Lightning Bolt on biggest     │
│      creature, then cast Serra Angel    │
│      if mana allows                     │
└─────────────────────────────────────────┘

LLM (Tool calls):
1. execute_action("cast_spell", card_id="lightning_bolt", target="opponent_creature_1")
2. execute_action("cast_spell", card_id="serra_angel")
```

---

This architecture allows the AI to:
1. **Understand** the game through tools
2. **Reason** about strategy using LLM capabilities  
3. **Act** through validated, legal moves
4. **Learn** by analyzing past games (future)
5. **Explain** its decisions (transparency)
