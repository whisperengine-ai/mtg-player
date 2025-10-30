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

## 2. Run the Game

```bash
# Option 1: Use the run script (recommended)
python run.py --verbose

# Option 2: Set PYTHONPATH and run directly
PYTHONPATH=./src python src/main.py --verbose
```

That's it! The game will run with simple rule-based AI.

## 3. Optional: Add Real LLM

To use GPT-4, Claude, or OpenRouter for decision-making:

```bash
# Copy environment file
cp .env.example .env

# Edit .env and add your API key
# For OpenAI:
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-your-key-here

# For OpenRouter (access multiple models):
# LLM_PROVIDER=openrouter
# OPENROUTER_API_KEY=sk-or-v1-your-key-here
# OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# For Anthropic:
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Note**: LLM integration is planned for Phase 2. Current PoC uses heuristics.

**For OpenRouter setup**: See [OPENROUTER_SETUP.md](OPENROUTER_SETUP.md) for detailed configuration.

## What You'll See

```
🎮 Setting up Magic: The Gathering Commander game...
  ✓ Created Player 1 with 100 card deck
  ✓ Created Player 2 with 100 card deck

============================================================
Turn 1 - Player 1's turn
============================================================
🤔 Decision: play_land
💭 Reasoning: Playing a land to increase mana availability
✅ Played Forest
```

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
