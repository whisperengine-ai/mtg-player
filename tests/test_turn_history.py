"""
Tests for Phase 5a.3: Turn History & Memory
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
from core.game_state import GameState, Phase, Step
from core.player import Player
from core.card import Card, CardType, Color, ManaCost, CardInstance
from core.rules_engine import RulesEngine
from tools.evaluation_tools import GetTurnHistoryTool


@pytest.fixture
def game_state():
    """Create a basic 2-player game state for testing."""
    player1 = Player(id="p1", name="Player 1", life=40)
    player2 = Player(id="p2", name="Player 2", life=40)
    
    state = GameState(
        game_id="test-game",
        players=[player1, player2],
        active_player_id="p1",
        priority_player_id="p1",
        current_phase=Phase.PRECOMBAT_MAIN,
        current_step=Step.MAIN
    )
    
    return state


@pytest.fixture
def rules_engine(game_state):
    """Create a rules engine."""
    return RulesEngine(game_state=game_state)


def test_record_turn_event(game_state):
    """Test that turn events are recorded correctly."""
    # Record a land play event
    game_state.record_turn_event(
        event_type="land_played",
        player_id="p1",
        details={"card_name": "Forest"}
    )
    
    # Check event was recorded
    assert len(game_state.turn_history) == 1
    event = game_state.turn_history[0]
    
    assert event["turn"] == 1
    assert event["event_type"] == "land_played"
    assert event["player_id"] == "p1"
    assert event["player_name"] == "Player 1"
    assert event["details"]["card_name"] == "Forest"


def test_record_multiple_events(game_state):
    """Test recording multiple events."""
    # Record several events
    game_state.record_turn_event("land_played", "p1", {"card_name": "Forest"})
    game_state.record_turn_event("creature_played", "p1", {"card_name": "Llanowar Elves", "power": 1, "toughness": 1})
    game_state.record_turn_event("spell_cast", "p2", {"card_name": "Lightning Bolt", "is_removal": True})
    
    assert len(game_state.turn_history) == 3


def test_get_recent_history(game_state):
    """Test retrieving recent turn history."""
    # Create events across multiple turns
    game_state.turn_number = 1
    game_state.record_turn_event("land_played", "p1", {"card_name": "Forest"})
    
    game_state.turn_number = 2
    game_state.record_turn_event("creature_played", "p1", {"card_name": "Grizzly Bears", "power": 2, "toughness": 2})
    
    game_state.turn_number = 5
    game_state.record_turn_event("attack", "p1", {"attacker_count": 1, "total_power": 2})
    
    game_state.turn_number = 10
    game_state.record_turn_event("spell_cast", "p2", {"card_name": "Wrath of God"})
    
    # Get recent 5 turns (should include turns 6-10)
    recent = game_state.get_recent_history(last_n_turns=5)
    
    # Should get events from turn 5 and turn 10 (both within 5 turns of turn 10: min_turn = max(1, 10-5) = 5)
    assert len(recent) == 2
    assert recent[0]["turn"] == 5
    assert recent[1]["turn"] == 10


def test_turn_history_tool(game_state):
    """Test the GetTurnHistoryTool."""
    tool = GetTurnHistoryTool()
    tool.game_state = game_state
    
    # Add some history
    game_state.record_turn_event("land_played", "p1", {"card_name": "Forest"})
    game_state.record_turn_event("creature_played", "p1", {"card_name": "Llanowar Elves", "power": 1, "toughness": 1})
    
    # Execute tool
    result = tool.execute(last_n_turns=5)
    
    assert result["success"] is True
    assert result["event_count"] == 2
    assert len(result["events"]) == 2
    assert "summary" in result
    assert "patterns" in result


def test_turn_history_tool_filters(game_state):
    """Test turn history tool with filters."""
    tool = GetTurnHistoryTool()
    tool.game_state = game_state
    
    # Add events for both players
    game_state.record_turn_event("land_played", "p1", {"card_name": "Forest"})
    game_state.record_turn_event("creature_played", "p1", {"card_name": "Llanowar Elves", "power": 1, "toughness": 1})
    game_state.record_turn_event("spell_cast", "p2", {"card_name": "Lightning Bolt", "is_removal": True})
    
    # Filter by player
    result = tool.execute(player_filter="p1")
    assert result["event_count"] == 2
    assert all(e["player_id"] == "p1" for e in result["events"])
    
    # Filter by event type
    result = tool.execute(event_filter="spell_cast")
    assert result["event_count"] == 1
    assert result["events"][0]["event_type"] == "spell_cast"


def test_pattern_detection_aggressive(game_state):
    """Test that aggressive player patterns are detected."""
    tool = GetTurnHistoryTool()
    tool.game_state = game_state
    
    # Player 1 attacks multiple times
    for _ in range(3):
        game_state.record_turn_event("attack", "p1", {"attacker_count": 2, "total_power": 4})
    
    result = tool.execute()
    
    # Should detect aggressive pattern
    assert len(result["patterns"]["aggressive_players"]) == 1
    assert result["patterns"]["aggressive_players"][0]["player_id"] == "p1"
    assert result["patterns"]["aggressive_players"][0]["attack_count"] == 3


def test_pattern_detection_control(game_state):
    """Test that control player patterns are detected."""
    tool = GetTurnHistoryTool()
    tool.game_state = game_state
    
    # Player 2 casts removal spells
    game_state.record_turn_event("spell_cast", "p2", {"card_name": "Doom Blade", "is_removal": True})
    game_state.record_turn_event("spell_cast", "p2", {"card_name": "Path to Exile", "is_removal": True})
    
    result = tool.execute()
    
    # Should detect controlling pattern
    assert len(result["patterns"]["controlling_players"]) == 1
    assert result["patterns"]["controlling_players"][0]["player_id"] == "p2"
    assert result["patterns"]["controlling_players"][0]["removal_count"] == 2


def test_pattern_detection_ramp(game_state):
    """Test that ramp player patterns are detected."""
    tool = GetTurnHistoryTool()
    tool.game_state = game_state
    
    # Player 1 casts ramp spells
    game_state.record_turn_event("spell_cast", "p1", {"card_name": "Cultivate", "is_ramp": True})
    game_state.record_turn_event("spell_cast", "p1", {"card_name": "Kodama's Reach", "is_ramp": True})
    
    result = tool.execute()
    
    # Should detect ramping pattern
    assert len(result["patterns"]["ramping_players"]) == 1
    assert result["patterns"]["ramping_players"][0]["player_id"] == "p1"
    assert result["patterns"]["ramping_players"][0]["ramp_count"] == 2


def test_rules_engine_records_land_play(game_state, rules_engine):
    """Test that rules engine records land plays."""
    player = game_state.get_player("p1")
    
    # Create a land and add to hand
    forest = Card(id="forest", name="Forest", card_types=[CardType.LAND], mana_cost=ManaCost(), colors=[Color.GREEN])
    forest_instance = CardInstance(card=forest, instance_id="forest-1", controller_id="p1", owner_id="p1")
    player.hand.append(forest_instance)
    
    # Play the land
    rules_engine.play_land(player, forest_instance)
    
    # Check event was recorded
    assert len(game_state.turn_history) == 1
    assert game_state.turn_history[0]["event_type"] == "land_played"
    assert game_state.turn_history[0]["details"]["card_name"] == "Forest"


def test_rules_engine_records_attacks(game_state, rules_engine):
    """Test that rules engine records attacks."""
    player = game_state.get_player("p1")
    
    # Create a creature on battlefield
    bear = Card(id="bear", name="Grizzly Bears", card_types=[CardType.CREATURE], mana_cost=ManaCost(generic=2), power=2, toughness=2)
    bear_instance = CardInstance(card=bear, instance_id="bear-1", controller_id="p1", owner_id="p1")
    bear_instance.summoning_sick = False
    player.battlefield.append(bear_instance)
    
    # Declare attack
    rules_engine.declare_attackers(player, [(bear_instance, "p2")])
    
    # Check event was recorded
    assert len(game_state.turn_history) == 1
    assert game_state.turn_history[0]["event_type"] == "attack"
    assert game_state.turn_history[0]["details"]["attacker_count"] == 1
    assert game_state.turn_history[0]["details"]["total_power"] == 2


def test_empty_history(game_state):
    """Test tool with no history."""
    tool = GetTurnHistoryTool()
    tool.game_state = game_state
    
    result = tool.execute()
    
    assert result["success"] is True
    assert result["event_count"] == 0
    assert len(result["events"]) == 0
    assert "No events" in result["summary"]


def test_turn_history_summary_generation(game_state):
    """Test that summary is generated correctly."""
    tool = GetTurnHistoryTool()
    tool.game_state = game_state
    
    # Add variety of events
    game_state.record_turn_event("land_played", "p1", {"card_name": "Forest"})
    game_state.record_turn_event("land_played", "p1", {"card_name": "Mountain"})
    game_state.record_turn_event("creature_played", "p1", {"card_name": "Llanowar Elves", "power": 1, "toughness": 1})
    game_state.record_turn_event("spell_cast", "p2", {"card_name": "Lightning Bolt", "is_removal": True})
    
    result = tool.execute()
    
    assert "4 events recorded" in result["summary"]
    assert "Most common" in result["summary"]
    assert "land_played" in result["summary"] or "2x land_played" in result["summary"]
