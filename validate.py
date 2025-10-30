#!/usr/bin/env python
"""
Validation script to check MTG AI implementation status.
Run this to verify everything is working correctly.
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def check_imports():
    """Check that all core modules can be imported."""
    print("🔍 Checking imports...")
    try:
        from core.game_state import GameState, Phase, Step
        from core.player import Player
        from core.card import Card, CardType
        from core.rules_engine import RulesEngine
        from agent.llm_agent import MTGAgent
        from tools.game_tools import GetGameStateTool, ExecuteActionTool
        print("  ✅ All core modules import successfully")
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False


def check_environment():
    """Check environment configuration."""
    print("\n🔍 Checking environment...")
    env_file = Path(__file__).parent / '.env'
    
    if not env_file.exists():
        print("  ⚠️  .env file not found")
        print("     Run: cp .env.example .env")
        return False
    
    print("  ✅ .env file exists")
    
    # Check for API key
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    provider = os.getenv("LLM_PROVIDER", "openai")
    print(f"  📝 LLM Provider: {provider}")
    
    if provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if api_key and api_key.startswith("sk-or-v1"):
            print(f"  ✅ OpenRouter API key configured")
        else:
            print("  ⚠️  OpenRouter API key not set or invalid")
    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key.startswith("sk-"):
            print(f"  ✅ OpenAI API key configured")
        else:
            print("  ⚠️  OpenAI API key not set")
    
    return True


def check_dependencies():
    """Check that required packages are installed."""
    print("\n🔍 Checking dependencies...")
    required = {
        "pydantic": "Data validation",
        "dotenv": "Environment variables",
        "openai": "LLM integration",
        "pytest": "Testing"
    }
    
    all_installed = True
    for package, description in required.items():
        try:
            if package == "dotenv":
                __import__("dotenv")
            else:
                __import__(package)
            print(f"  ✅ {package:15} - {description}")
        except ImportError:
            print(f"  ❌ {package:15} - {description} (not installed)")
            all_installed = False
    
    return all_installed


def check_tests():
    """Check if tests can run."""
    print("\n🔍 Checking tests...")
    import subprocess
    
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/", "-v", "--co"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        # Count tests
        test_count = result.stdout.count("test_")
        print(f"  ✅ Found {test_count} tests")
        return True
    else:
        print(f"  ❌ Test discovery failed")
        return False


def check_game_engine():
    """Check basic game engine functionality."""
    print("\n🔍 Testing game engine...")
    try:
        from core.game_state import GameState
        from core.player import Player
        from core.rules_engine import RulesEngine
        import uuid
        
        # Create simple game
        player1 = Player(id="p1", name="Test Player 1", life=40)
        player2 = Player(id="p2", name="Test Player 2", life=40)
        
        game_state = GameState(
            game_id=str(uuid.uuid4()),
            players=[player1, player2],
            active_player_id="p1",
            priority_player_id="p1"
        )
        
        rules_engine = RulesEngine(game_state)
        
        print("  ✅ Game state creation works")
        print("  ✅ Rules engine initialization works")
        return True
    except Exception as e:
        print(f"  ❌ Game engine test failed: {e}")
        return False


def check_agent():
    """Check agent initialization."""
    print("\n🔍 Testing agent...")
    try:
        from agent.llm_agent import MTGAgent
        from core.game_state import GameState
        from core.player import Player
        from core.rules_engine import RulesEngine
        import uuid
        
        # Create simple game
        player1 = Player(id="p1", name="Test Player 1", life=40)
        player2 = Player(id="p2", name="Test Player 2", life=40)
        
        game_state = GameState(
            game_id=str(uuid.uuid4()),
            players=[player1, player2],
            active_player_id="p1",
            priority_player_id="p1"
        )
        
        rules_engine = RulesEngine(game_state)
        agent = MTGAgent(game_state, rules_engine, llm_client=None, verbose=False)
        
        print("  ✅ Agent initialization works")
        print(f"  ✅ Agent has {len(agent.tools)} tools")
        return True
    except Exception as e:
        print(f"  ❌ Agent test failed: {e}")
        return False


def main():
    """Run all validation checks."""
    print("="*60)
    print("MTG Commander AI - Validation Check")
    print("="*60)
    
    results = []
    
    # Run checks
    results.append(("Imports", check_imports()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("Environment", check_environment()))
    results.append(("Game Engine", check_game_engine()))
    results.append(("Agent", check_agent()))
    results.append(("Tests", check_tests()))
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:20} {status}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All validation checks passed!")
        print("\n📝 Next steps:")
        print("   1. Run tests: pytest tests/ -v")
        print("   2. Run game: python run.py --verbose")
        print("   3. Check PHASE2_COMPLETION.md for full status")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
