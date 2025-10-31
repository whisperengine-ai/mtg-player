"""
Tests for LLM agent integration.
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import uuid
import os
from unittest.mock import Mock, MagicMock, patch
from core.game_state import GameState, Phase, Step
from core.player import Player
from core.card import Card, CardType, ManaCost, Color
from core.rules_engine import RulesEngine
from agent.llm_agent import MTGAgent


@pytest.fixture
def game_setup():
    """Create a game setup for testing."""
    player1 = Player(id="p1", name="Player 1", life=40)
    player2 = Player(id="p2", name="Player 2", life=40)
    
    game_state = GameState(
        game_id=str(uuid.uuid4()),
        players=[player1, player2],
        active_player_id="p1",
        priority_player_id="p1"
    )
    
    rules_engine = RulesEngine(game_state)
    
    return game_state, rules_engine, player1, player2


def test_agent_initialization_no_llm(game_setup):
    """Test agent initializes correctly without LLM client."""
    game_state, rules_engine, _, _ = game_setup
    
    agent = MTGAgent(game_state, rules_engine, llm_client=None, verbose=False)
    
    assert agent.game_state == game_state
    assert agent.rules_engine == rules_engine
    assert len(agent.tools) == 12  # Updated: includes get_stack_state, can_respond, get_pending_triggers, evaluate_position, can_i_win, recommend_strategy, analyze_opponent, get_turn_history
    assert "get_game_state" in agent.tools
    assert "get_legal_actions" in agent.tools
    assert "execute_action" in agent.tools
    assert "analyze_threats" in agent.tools
    assert "get_stack_state" in agent.tools
    assert "can_respond" in agent.tools
    assert "get_pending_triggers" in agent.tools
    assert "evaluate_position" in agent.tools
    assert "can_i_win" in agent.tools
    assert "recommend_strategy" in agent.tools
    assert "analyze_opponent" in agent.tools


def test_agent_tools_setup(game_setup):
    """Test that agent tools are properly configured."""
    game_state, rules_engine, _, _ = game_setup
    
    agent = MTGAgent(game_state, rules_engine, verbose=False)
    
    # Test get_game_state tool
    game_state_tool = agent.tools["get_game_state"]
    result = game_state_tool.execute()
    assert result["success"] is True
    assert "game_state" in result
    
    # Test get_legal_actions tool
    legal_actions_tool = agent.tools["get_legal_actions"]
    result = legal_actions_tool.execute()
    assert result["success"] is True
    assert "actions" in result
    
    # Test analyze_threats tool
    threats_tool = agent.tools["analyze_threats"]
    result = threats_tool.execute()
    assert result["success"] is True


def test_simple_decision_making(game_setup):
    """Test fallback heuristic decision making."""
    game_state, rules_engine, player1, _ = game_setup
    
    # Add a land to hand
    land = Card(id="forest", name="Forest", card_types=[CardType.LAND])
    land_instance = rules_engine.create_card_instance(land, player1.id)
    player1.hand.append(land_instance)
    
    # Set to main phase
    game_state.current_phase = Phase.PRECOMBAT_MAIN
    game_state.current_step = Step.MAIN
    
    agent = MTGAgent(game_state, rules_engine, llm_client=None, verbose=False)
    
    # Agent should decide to play land
    action = agent._make_simple_decision()
    
    assert action is not None
    assert action["type"] == "play_land"


def test_cot_enforcement_tracking(game_setup):
    """Test that strategic tools are tracked correctly."""
    game_state, rules_engine, _, _ = game_setup
    
    agent = MTGAgent(game_state, rules_engine, llm_client=None, verbose=False)
    
    # Reset tracking
    agent._reset_strategic_tool_tracking()
    assert len(agent._strategic_tools_called) == 0
    
    # Record some tool calls
    agent._record_strategic_tool_call("evaluate_position")
    assert "evaluate_position" in agent._strategic_tools_called
    
    agent._record_strategic_tool_call("analyze_opponent")
    assert "analyze_opponent" in agent._strategic_tools_called
    
    # Non-strategic tools should not be tracked
    agent._record_strategic_tool_call("get_game_state")
    assert "get_game_state" not in agent._strategic_tools_called
    
    assert len(agent._strategic_tools_called) == 2


def test_cot_enforcement_validation_fails(game_setup):
    """Test that validation fails when strategic tools not called."""
    game_state, rules_engine, _, _ = game_setup
    
    agent = MTGAgent(game_state, rules_engine, llm_client=None, verbose=False)
    agent._cot_enforcement_enabled = True
    agent._min_strategic_tools = 3
    
    # Reset tracking
    agent._reset_strategic_tool_tracking()
    
    # Try to validate without calling any tools
    is_valid, error_msg = agent._validate_strategic_tools_called()
    assert not is_valid
    assert "evaluate_position" in error_msg
    
    # Call evaluate_position but not enough others
    agent._record_strategic_tool_call("evaluate_position")
    is_valid, error_msg = agent._validate_strategic_tools_called()
    assert not is_valid
    assert "at least 3" in error_msg


def test_cot_enforcement_validation_passes(game_setup):
    """Test that validation passes when sufficient strategic tools called."""
    game_state, rules_engine, _, _ = game_setup
    
    agent = MTGAgent(game_state, rules_engine, llm_client=None, verbose=False)
    agent._cot_enforcement_enabled = True
    agent._min_strategic_tools = 3
    
    # Reset tracking
    agent._reset_strategic_tool_tracking()
    
    # Call required strategic tools
    agent._record_strategic_tool_call("evaluate_position")
    agent._record_strategic_tool_call("analyze_opponent")
    agent._record_strategic_tool_call("recommend_strategy")
    
    # Should pass now
    is_valid, error_msg = agent._validate_strategic_tools_called()
    assert is_valid
    assert error_msg == ""


def test_cot_enforcement_disabled(game_setup):
    """Test that validation always passes when enforcement disabled."""
    game_state, rules_engine, _, _ = game_setup
    
    agent = MTGAgent(game_state, rules_engine, llm_client=None, verbose=False)
    agent._cot_enforcement_enabled = False
    
    # Reset tracking
    agent._reset_strategic_tool_tracking()
    
    # Should pass even with no tools called
    is_valid, error_msg = agent._validate_strategic_tools_called()
    assert is_valid
    assert error_msg == ""


def test_llm_initialization_openrouter():
    """Test LLM client initialization for OpenRouter."""
    with patch.dict(os.environ, {
        "LLM_PROVIDER": "openrouter",
        "OPENROUTER_API_KEY": "test-key",
        "OPENROUTER_MODEL": "anthropic/claude-3.5-sonnet"
    }):
        game_state = Mock()
        rules_engine = Mock()
        
        with patch('agent.llm_agent.OpenAI') as mock_openai:
            agent = MTGAgent(game_state, rules_engine, verbose=False)
            
            # Check that OpenAI was called with correct parameters
            mock_openai.assert_called_once()
            call_kwargs = mock_openai.call_args[1]
            assert call_kwargs["base_url"] == "https://openrouter.ai/api/v1"
            assert call_kwargs["api_key"] == "test-key"
            assert "HTTP-Referer" in call_kwargs["default_headers"]


def test_llm_tool_schemas(game_setup):
    """Test that tool schemas are properly formatted for LLM."""
    game_state, rules_engine, _, _ = game_setup
    
    agent = MTGAgent(game_state, rules_engine, verbose=False)
    schemas = agent._get_tool_schemas()
    
    assert len(schemas) == 12  # Updated: includes get_stack_state, can_respond, get_pending_triggers, evaluate_position, can_i_win, recommend_strategy, analyze_opponent, get_turn_history
    
    # Check each schema has required fields
    for schema in schemas:
        assert schema["type"] == "function"
        assert "function" in schema
        assert "name" in schema["function"]
        assert "description" in schema["function"]
        assert "parameters" in schema["function"]
    
    # Check execute_action has proper structure
    execute_schema = next(s for s in schemas if s["function"]["name"] == "execute_action")
    params = execute_schema["function"]["parameters"]
    assert "action" in params["properties"]
    assert "type" in params["properties"]["action"]["properties"]

    # Confirm evaluate_position schema exists
    eval_schema = next(s for s in schemas if s["function"]["name"] == "evaluate_position")
    assert eval_schema["function"]["parameters"]["type"] == "object"


def test_tool_execution_with_error(game_setup):
    """Test that tool execution errors are handled gracefully."""
    game_state, rules_engine, player1, _ = game_setup
    
    agent = MTGAgent(game_state, rules_engine, verbose=False)
    
    # Try to execute invalid action
    result = agent.tools["execute_action"].execute(action={"type": "invalid_action"})
    
    assert "error" in result or result.get("success") is False


def test_agent_analyze_position(game_setup):
    """Test position analysis method."""
    game_state, rules_engine, _, _ = game_setup
    
    agent = MTGAgent(game_state, rules_engine, verbose=False)
    
    analysis = agent.analyze_position()
    
    assert "game_state" in analysis
    assert "threats" in analysis
    assert analysis["game_state"]["success"] is True
    assert analysis["threats"]["success"] is True


@patch('agent.llm_agent.OpenAI')
def test_llm_decision_with_mock(mock_openai_class, game_setup):
    """Test LLM decision making with mocked API."""
    game_state, rules_engine, player1, _ = game_setup
    
    # Setup mock LLM response
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    # Mock a simple pass action response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = "Passing priority"
    mock_response.choices[0].message.tool_calls = None
    
    mock_client.chat.completions.create.return_value = mock_response
    
    with patch.dict(os.environ, {
        "LLM_PROVIDER": "openrouter",
        "OPENROUTER_API_KEY": "test-key"
    }):
        agent = MTGAgent(game_state, rules_engine, verbose=False)
        agent.llm_client = mock_client
        
        # Make decision
        action = agent._make_llm_decision()
        
        assert action is not None
        assert action["type"] == "pass"
        assert "reasoning" in action


def test_phase_specific_prompts(game_setup):
    """Test that different phases get different prompts."""
    game_state, rules_engine, _, _ = game_setup
    
    agent = MTGAgent(game_state, rules_engine, verbose=False)
    
    # Test main phase prompt
    game_state.current_step = Step.MAIN
    main_prompt = agent._get_phase_specific_prompt()
    assert "main phase" in main_prompt.lower() or "play lands" in main_prompt.lower()
    
    # Test combat prompt
    game_state.current_step = Step.DECLARE_ATTACKERS
    combat_prompt = agent._get_phase_specific_prompt()
    assert "attack" in combat_prompt.lower() or "declare_attackers" in combat_prompt.lower()


def test_agent_with_cards_in_hand(game_setup):
    """Test agent behavior with cards in hand."""
    game_state, rules_engine, player1, _ = game_setup
    
    # Add various cards to hand
    forest = Card(id="forest", name="Forest", card_types=[CardType.LAND])
    elf = Card(
        id="elf",
        name="Llanowar Elves",
        mana_cost=ManaCost(green=1),
        card_types=[CardType.CREATURE],
        colors=[Color.GREEN],
        power=1,
        toughness=1
    )
    
    forest_instance = rules_engine.create_card_instance(forest, player1.id)
    elf_instance = rules_engine.create_card_instance(elf, player1.id)
    
    player1.hand.extend([forest_instance, elf_instance])
    
    # Set to main phase
    game_state.current_phase = Phase.PRECOMBAT_MAIN
    game_state.current_step = Step.MAIN
    
    agent = MTGAgent(game_state, rules_engine, verbose=False)
    
    # Get legal actions
    legal_actions_tool = agent.tools["get_legal_actions"]
    result = legal_actions_tool.execute()
    
    assert result["success"] is True
    actions = result["actions"]
    
    # Should have options to play land, cast spell, or pass
    action_types = {a["type"] for a in actions}
    assert "play_land" in action_types
    assert "pass" in action_types


def test_fallback_to_heuristics_on_no_api_key(game_setup):
    """Test that agent falls back to heuristics when no API key is set."""
    game_state, rules_engine, player1, _ = game_setup
    
    with patch.dict(os.environ, {"LLM_PROVIDER": "openrouter"}, clear=True):
        # No OPENROUTER_API_KEY set
        agent = MTGAgent(game_state, rules_engine, verbose=False)
        
        # Should fall back to simple decision
        assert agent.llm_client is None
        
        # Add a land
        land = Card(id="forest", name="Forest", card_types=[CardType.LAND])
        land_instance = rules_engine.create_card_instance(land, player1.id)
        player1.hand.append(land_instance)
        
        game_state.current_phase = Phase.PRECOMBAT_MAIN
        game_state.current_step = Step.MAIN
        
        # Should still make a decision using heuristics
        action = agent._make_llm_decision()
        assert action is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
