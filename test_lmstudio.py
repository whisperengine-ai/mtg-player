#!/usr/bin/env python3
"""
Test LM Studio integration with MTG game tools
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Import game components
from core.game_state import GameState, Phase, Step
from core.player import Player
from tools.game_tools import GetGameStateTool, GetLegalActionsTool

# Initialize LM Studio client
base_url = os.getenv('LMSTUDIO_BASE_URL', 'http://localhost:1234/v1')
model = os.getenv('LMSTUDIO_MODEL', 'local-model')

print("=" * 60)
print("LM Studio + MTG AI Integration Test")
print("=" * 60)
print(f"Base URL: {base_url}")
print(f"Model: {model}")
print()

client = OpenAI(base_url=base_url, api_key='lm-studio')

# Create minimal game state
player1 = Player(id="p1", name="Player 1", life=40)
player2 = Player(id="p2", name="Player 2", life=40)
game_state = GameState(
    players=[player1, player2],
    starting_player_id="p1",
    game_id="test-game",
    active_player_id="p1",
    priority_player_id="p1"
)

# Create tools
get_game_state_tool = GetGameStateTool()
get_game_state_tool.game_state = game_state

# Tool schemas
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_game_state",
            "description": "Get current game state",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

# Test API call
messages = [
    {
        "role": "system",
        "content": "You are an AI playing Magic: The Gathering. Use the available tools to query game state."
    },
    {
        "role": "user",
        "content": "What is the current game state? Use the get_game_state tool."
    }
]

print("Sending request to LM Studio...")
print()

try:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.7,
        max_tokens=500
    )
    
    print("✅ Response received!")
    print()
    print("Response details:")
    print(f"  Finish reason: {response.choices[0].finish_reason}")
    print(f"  Content: {response.choices[0].message.content}")
    print(f"  Tool calls: {response.choices[0].message.tool_calls}")
    print()
    
    if response.choices[0].message.tool_calls:
        print("✅ Model is calling tools!")
        for tool_call in response.choices[0].message.tool_calls:
            print(f"  - Tool: {tool_call.function.name}")
            print(f"    Args: {tool_call.function.arguments}")
    else:
        print("⚠️  Model did not call any tools")
        print("This might be a model limitation or prompt issue")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
