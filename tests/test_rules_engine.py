"""
Tests for the rules engine.
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import uuid
from core.game_state import GameState, Phase, Step
from core.player import Player
from core.card import Card, CardType, ManaCost
from core.rules_engine import RulesEngine


@pytest.fixture
def simple_game():
    """Create a simple game for testing."""
    player1 = Player(id="p1", name="Player 1", life=40)
    player2 = Player(id="p2", name="Player 2", life=40)
    
    game_state = GameState(
        game_id=str(uuid.uuid4()),
        players=[player1, player2],
        active_player_id="p1",
        priority_player_id="p1"
    )
    
    rules_engine = RulesEngine(game_state)
    
    return game_state, rules_engine


def test_game_initialization(simple_game):
    """Test basic game initialization."""
    game_state, _ = simple_game
    
    assert len(game_state.players) == 2
    assert game_state.turn_number == 1
    assert game_state.current_phase == Phase.BEGINNING
    assert not game_state.is_game_over


def test_land_drop(simple_game):
    """Test playing a land."""
    game_state, rules_engine = simple_game
    player = game_state.get_active_player()
    
    # Create a land card
    land = Card(
        id="forest",
        name="Forest",
        card_types=[CardType.LAND]
    )
    land_instance = rules_engine.create_card_instance(land, player.id)
    player.hand.append(land_instance)
    
    # Play the land
    success = rules_engine.play_land(player, land_instance)
    
    assert success
    assert land_instance in player.battlefield
    assert land_instance not in player.hand
    assert player.has_played_land_this_turn


def test_cannot_play_two_lands(simple_game):
    """Test that you can't play more than one land per turn."""
    game_state, rules_engine = simple_game
    player = game_state.get_active_player()
    
    # Create two lands
    land1 = rules_engine.create_card_instance(
        Card(id="forest1", name="Forest", card_types=[CardType.LAND]),
        player.id
    )
    land2 = rules_engine.create_card_instance(
        Card(id="forest2", name="Forest", card_types=[CardType.LAND]),
        player.id
    )
    
    player.hand.extend([land1, land2])
    
    # Play first land
    assert rules_engine.play_land(player, land1)
    
    # Try to play second land
    assert not rules_engine.play_land(player, land2)


def test_turn_advancement(simple_game):
    """Test turn structure advancement."""
    game_state, rules_engine = simple_game
    
    initial_turn = game_state.turn_number
    initial_player = game_state.active_player_id
    
    # Advance through all phases
    for _ in range(12):  # 12 steps in a turn
        rules_engine.advance_phase()
    
    # Should be next player's turn
    assert game_state.turn_number == initial_turn + 1
    assert game_state.active_player_id != initial_player


def test_win_condition(simple_game):
    """Test win condition detection."""
    game_state, _ = simple_game
    
    # Kill player 2
    player2 = game_state.get_player("p2")
    player2.life = 0
    
    game_state.check_win_condition()
    
    assert game_state.is_game_over
    assert game_state.winner_id == "p1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
