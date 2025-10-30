#!/usr/bin/env python
"""Quick test of logging functionality without LLM calls."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.logger import setup_loggers

# Test loggers
game_id = "test_20241030_123456"
loggers = setup_loggers(game_id, log_base_dir="logs")
try:
    game_logger, llm_logger, heuristic_logger = loggers
except ValueError:
    # Backward compatibility if setup_loggers returns only two
    game_logger, llm_logger = loggers
    heuristic_logger = None

print(f"✅ Loggers initialized")
print(f"📝 Game log: logs/game_{game_id}.log")
print(f"📝 LLM log: logs/llm_{game_id}.log")
if heuristic_logger:
    print(f"📝 Heuristic log: logs/heuristic_{game_id}.log")

# Test game logger
game_logger.log_turn_start(1, "Player 1", "beginning", "untap")
game_logger.log_action("Player 1", "play_land", "Forest")
game_logger.log_phase_change("beginning", "untap", "beginning", "upkeep")
game_logger.log_win_condition("Player 1", "opponent eliminated")

print("✅ Game log entries written")

# Test LLM logger
llm_logger.log_llm_call(
    player_name="Player 1",
    turn=1,
    phase="beginning/main",
    model="test-model",
    messages=[
        {"role": "system", "content": "You are a test AI"},
        {"role": "user", "content": "What should I do?"}
    ],
    tools=[{"function": {"name": "test_tool"}}]
)

llm_logger.log_llm_response(
    response_content="I will pass priority.",
    tool_calls=None,
    finish_reason="stop",
    reasoning_content="After analyzing the board, there are no good plays available.",
    thinking_content="[Used 50 reasoning tokens]"
)

llm_logger.log_decision("Player 1", {"type": "pass", "reasoning": "No good plays"})

print("✅ LLM log entries written")
if heuristic_logger:
    heuristic_logger.log_context("Player 1", 1, "beginning", "main", threats_count=0, actions_count=3)
    heuristic_logger.log_position({"score": 0.55, "position": "even", "breakdown": {"life": 0.8}})
    heuristic_logger.log_decision("Player 1", {"type": "pass", "reasoning": "Testing heuristic log"})
    print("✅ Heuristic log entries written")
print("\n📖 Check the log files to verify content")
