#!/bin/bash
# Quick test script for heuristic mode (no LLM calls)

echo "Testing heuristic mode (no LLM API calls)..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run game in heuristic mode
python run.py --no-llm --verbose --players=2

echo ""
echo "Test complete! No API calls were made."
