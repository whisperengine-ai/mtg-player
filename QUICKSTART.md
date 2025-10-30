# Quick Start Guide

Get the MTG Commander AI running in 5 minutes!

## 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

## 2. Set Up API Key

```bash
# Copy environment file
cp .env.example .env

# Edit .env and add your API key
# For OpenRouter (recommended - access to multiple models):
# LLM_PROVIDER=openrouter
# OPENROUTER_API_KEY=sk-or-v1-your-key-here
# OPENROUTER_MODEL=openai/gpt-4o-mini  # or any other model

# For OpenAI:
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-your-key-here

# For Anthropic:
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**For OpenRouter setup**: See [OPENROUTER_SETUP.md](OPENROUTER_SETUP.md) for detailed configuration.

## 3. Run the Game

```bash
# View all options
python run.py --help

# Run with console output (recommended for learning)
python run.py --verbose

# Quiet mode (logs to files only)
python run.py

# Customize your game
python run.py --players=2 --verbose           # 2-player game
python run.py --max-turns=5 --verbose         # Short 5-turn game
python run.py --players=2 --max-turns=3       # 2-player, 3-turn game

# Aggression levels (control combat strategy)
python run.py --aggression=aggressive --max-turns=50 --verbose   # Attack with ALL creatures
python run.py --aggression=balanced --verbose                    # Balanced attacks (default)
python run.py --aggression=conservative --verbose                # Defensive play

# Heuristic mode (no LLM calls - free, fast testing)
python run.py --no-llm --verbose
python run.py --no-llm --aggression=aggressive --verbose  # Aggressive heuristic AI

# Combine options
python run.py --players=2 --max-turns=5 --no-llm --verbose
python run.py --aggression=aggressive --max-turns=100 --verbose

# Alternative entry (without run.py)
PYTHONPATH=./src python src/main.py --verbose
```

**Available Options:**
- `--verbose` / `-v` - Show detailed output to console (logs always saved to files)
- `--no-llm` / `--heuristic` - Use rule-based AI (no API costs)
- `--players=N` - Number of players (2-4, default: 4)
- `--max-turns=N` - Maximum full turns (default: 10)
- `--aggression=LEVEL` - Combat aggression: `aggressive`, `balanced` (default), or `conservative`
- `--help` / `-h` - Show help message

**Aggression Levels:**
- 🔴 **aggressive**: Attack with ALL creatures (fast, risky)
- ⚖️ **balanced**: Attack with power 2+ (strategic, default)
- 🛡️ **conservative**: Only attack with power 3+ (defensive)

That's it! The AI will play a game using LLM reasoning.

**💡 Tip**: Use `--no-llm` flag to test without making API calls. This runs an **enhanced rule-based AI** that:
- Uses the same tool-calling architecture as the LLM version
- Analyzes game state, evaluates threats, makes strategic decisions
- Respects aggression level settings for combat strategy
- Demonstrates the agentic design pattern without LLM dependency
- Perfect for rapid testing, demos, and understanding the architecture

## What You'll See

**Console output** (with `--verbose`):
```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║          MTG Commander AI - Proof of Concept           ║
║              Agentic AI with Tool Calling               ║
║               Phase 3: Multiplayer Commander            ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

🎮 Setting up 4-player Magic: The Gathering Commander game...
  📦 Built ramp deck for Player 1 (99 cards)
  📦 Built control deck for Player 2 (99 cards)
  📦 Built midrange deck for Player 3 (99 cards)
  📦 Built midrange deck for Player 4 (99 cards)

============================================================
🎲 GAME START
📝 Logs saved to: logs/game_20251030_054257.log and logs/llm_20251030_054257.log
============================================================

Turn 1 - Player 1 (Ramp)'s turn
Phase: beginning/untap
============================================================
Life: 40
Hand: 7 cards
Battlefield: 0 permanents
Creatures: 0
```

**Log files** (in `logs/` directory):
- `game_YYYYMMDD_HHMMSS_gameid.log` - Turn progression, actions, phase changes
- `llm_YYYYMMDD_HHMMSS_gameid.log` - Complete LLM prompts, responses, reasoning, tool calls

## Next Steps

- Read [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for details
- Check [ROADMAP.md](ROADMAP.md) for development plan
- Run tests: `pytest`
- Add more cards in `src/data/cards.py`

## Troubleshooting

**Import errors or other issues?**

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions to common problems.

Quick fix:
```bash
# Use the run.py script
python run.py --verbose
```

**Need help?** Check the [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
