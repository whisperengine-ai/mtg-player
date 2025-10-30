"""
Tests for the StrategyRecommendationTool - strategic recommendations.
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import uuid
from core.game_state import GameState
from core.player import Player
from core.card import Card, CardType, CardInstance, ManaCost, Color
from core.rules_engine import RulesEngine
from tools.evaluation_tools import StrategyRecommendationTool


@pytest.fixture
def empty_game():
    """Create a bare game state."""
    player1 = Player(id="p1", name="Player 1", life=30)
    player2 = Player(id="p2", name="Player 2", life=30)
    
    game_state = GameState(
        game_id=str(uuid.uuid4()),
        players=[player1, player2],
        active_player_id="p1",
        priority_player_id="p1"
    )
    
    rules_engine = RulesEngine(game_state)
    return game_state, rules_engine


def test_strategy_close_winning():
    """Test CLOSE strategy when winning with strong board."""
    player1 = Player(id="p1", name="Strong Player", life=35)
    player2 = Player(id="p2", name="Weak Player", life=5)
    
    game_state = GameState(
        game_id=str(uuid.uuid4()),
        players=[player1, player2],
        active_player_id="p1",
        priority_player_id="p1"
    )
    
    # Add powerful creatures
    for i in range(2):
        creature = Card(
            id=f"creature_{i}",
            name=f"Big Creature {i}",
            mana_cost=ManaCost(generic=5),
            card_types=[CardType.CREATURE],
            power=6,
            toughness=6
        )
        creature_inst = CardInstance(
            card=creature,
            instance_id=f"creature_{i}_inst",
            controller_id="p1",
            owner_id="p1",
            is_tapped=False,
            summoning_sick=False
        )
        player1.battlefield.append(creature_inst)
    
    tool = StrategyRecommendationTool()
    tool.game_state = game_state
    
    result = tool.execute()
    
    assert result["success"] is True
    assert result["strategy"] == "CLOSE"
    assert result["confidence"] >= 0.8
    assert "lethal" in result["reasoning"].lower() or "finish" in result["reasoning"].lower()


def test_strategy_attack_good_position():
    """Test ATTACK strategy with good board."""
    player1 = Player(id="p1", name="Attacker", life=30)
    player2 = Player(id="p2", name="Defender", life=25)
    
    game_state = GameState(
        game_id=str(uuid.uuid4()),
        players=[player1, player2],
        active_player_id="p1",
        priority_player_id="p1"
    )
    
    # Add moderate creatures
    for i in range(3):
        creature = Card(
            id=f"creature_{i}",
            name=f"Creature {i}",
            mana_cost=ManaCost(generic=2),
            card_types=[CardType.CREATURE],
            power=2,
            toughness=2
        )
        creature_inst = CardInstance(
            card=creature,
            instance_id=f"creature_{i}_inst",
            controller_id="p1",
            owner_id="p1",
            is_tapped=False,
            summoning_sick=False
        )
        player1.battlefield.append(creature_inst)
    
    tool = StrategyRecommendationTool()
    tool.game_state = game_state
    
    result = tool.execute()
    
    assert result["success"] is True
    assert result["strategy"] in ["ATTACK", "CLOSE"]  # Could be either depending on life totals
    if result["strategy"] == "ATTACK":
        assert "attack" in result["reasoning"].lower() or "pressure" in result["reasoning"].lower()


def test_strategy_defend_under_threat():
    """Test DEFEND strategy when under heavy threat."""
    player1 = Player(id="p1", name="Defender", life=8)
    player2 = Player(id="p2", name="Aggressor", life=30)
    
    game_state = GameState(
        game_id=str(uuid.uuid4()),
        players=[player1, player2],
        active_player_id="p1",
        priority_player_id="p1"
    )
    
    # Opponent has strong creatures
    for i in range(4):
        creature = Card(
            id=f"attacker_{i}",
            name=f"Attacker {i}",
            mana_cost=ManaCost(generic=2),
            card_types=[CardType.CREATURE],
            power=3,
            toughness=2
        )
        creature_inst = CardInstance(
            card=creature,
            instance_id=f"attacker_{i}_inst",
            controller_id="p2",
            owner_id="p2",
            is_tapped=False,
            summoning_sick=False
        )
        player2.battlefield.append(creature_inst)
    
    tool = StrategyRecommendationTool()
    tool.game_state = game_state
    
    result = tool.execute()
    
    assert result["success"] is True
    assert result["strategy"] == "DEFEND"
    assert result["confidence"] >= 0.8
    assert "stabilize" in result["reasoning"].lower() or "survive" in result["reasoning"].lower()
    # Priority is to stabilize immediately when under heavy threat
    assert "stabilize" in result["priorities"][0].lower()


def test_strategy_ramp_low_resources():
    """Test RAMP strategy with few resources."""
    player1 = Player(id="p1", name="Ramper", life=25)
    player2 = Player(id="p2", name="Opponent", life=30)
    
    game_state = GameState(
        game_id=str(uuid.uuid4()),
        players=[player1, player2],
        active_player_id="p1",
        priority_player_id="p1"
    )
    
    # Minimal board setup - just 1 land
    land = Card(
        id="forest",
        name="Forest",
        card_types=[CardType.LAND],
        colors=[Color.GREEN]
    )
    land_inst = CardInstance(
        card=land,
        instance_id="forest_1",
        controller_id="p1",
        owner_id="p1",
        is_tapped=False
    )
    player1.battlefield.append(land_inst)
    
    tool = StrategyRecommendationTool()
    tool.game_state = game_state
    
    result = tool.execute()
    
    assert result["success"] is True
    assert result["strategy"] == "RAMP"
    assert "accelerate" in result["reasoning"].lower() or "resources" in result["reasoning"].lower()
    assert "mana" in result["priorities"][0].lower()


def test_strategy_includes_priorities():
    """Test that recommendations include action priorities."""
    player1 = Player(id="p1", name="Player", life=25)
    player2 = Player(id="p2", name="Opponent", life=30)
    
    game_state = GameState(
        game_id=str(uuid.uuid4()),
        players=[player1, player2],
        active_player_id="p1",
        priority_player_id="p1"
    )
    
    tool = StrategyRecommendationTool()
    tool.game_state = game_state
    
    result = tool.execute()
    
    assert result["success"] is True
    assert "priorities" in result
    assert isinstance(result["priorities"], list)
    assert len(result["priorities"]) > 0
    assert all(isinstance(p, str) for p in result["priorities"])


def test_strategy_board_presence_details():
    """Test that board presence is properly evaluated."""
    player1 = Player(id="p1", name="Player", life=25)
    player2 = Player(id="p2", name="Opponent", life=30)
    
    game_state = GameState(
        game_id=str(uuid.uuid4()),
        players=[player1, player2],
        active_player_id="p1",
        priority_player_id="p1"
    )
    
    # Add 2 creatures with power 3 each
    for i in range(2):
        creature = Card(
            id=f"creature_{i}",
            name=f"Creature {i}",
            mana_cost=ManaCost(generic=2),
            card_types=[CardType.CREATURE],
            power=3,
            toughness=2
        )
        creature_inst = CardInstance(
            card=creature,
            instance_id=f"creature_{i}_inst",
            controller_id="p1",
            owner_id="p1"
        )
        player1.battlefield.append(creature_inst)
    
    # Add 3 lands
    for i in range(3):
        land = Card(
            id=f"land_{i}",
            name=f"Land {i}",
            card_types=[CardType.LAND]
        )
        land_inst = CardInstance(
            card=land,
            instance_id=f"land_{i}_inst",
            controller_id="p1",
            owner_id="p1"
        )
        player1.battlefield.append(land_inst)
    
    tool = StrategyRecommendationTool()
    tool.game_state = game_state
    
    result = tool.execute()
    
    assert result["success"] is True
    assert result["board_presence"]["creatures"] == 2
    assert result["board_presence"]["total_power"] == 6
    assert result["board_presence"]["lands"] == 3


def test_strategy_player_specified():
    """Test strategy recommendation for specified player."""
    player1 = Player(id="p1", name="Player 1", life=30)
    player2 = Player(id="p2", name="Player 2", life=10)
    
    game_state = GameState(
        game_id=str(uuid.uuid4()),
        players=[player1, player2],
        active_player_id="p1",
        priority_player_id="p1"
    )
    
    # Add a threatening creature to force DEFEND
    creature = Card(
        id="threat",
        name="Threat",
        mana_cost=ManaCost(generic=2),
        card_types=[CardType.CREATURE],
        power=4,
        toughness=4
    )
    creature_inst = CardInstance(
        card=creature,
        instance_id="threat_inst",
        controller_id="p1",
        owner_id="p1",
        is_tapped=False
    )
    player2.battlefield.append(creature_inst)
    
    tool = StrategyRecommendationTool()
    tool.game_state = game_state
    
    # Get recommendation for player 2 (low life)
    result = tool.execute(player_id="p2")
    
    assert result["success"] is True
    assert result["player_id"] == "p2"
    # With low life and facing threats, should be DEFEND
    assert result["strategy"] in ["DEFEND", "RAMP"]  # Could be either depending on specifics


def test_strategy_all_required_fields():
    """Test that all expected fields are in response."""
    player1 = Player(id="p1", name="Player 1", life=25)
    player2 = Player(id="p2", name="Player 2", life=30)
    
    game_state = GameState(
        game_id=str(uuid.uuid4()),
        players=[player1, player2],
        active_player_id="p1",
        priority_player_id="p1"
    )
    
    tool = StrategyRecommendationTool()
    tool.game_state = game_state
    
    result = tool.execute()
    
    required_fields = [
        "success", "player_id", "player_name", "strategy", "confidence",
        "reasoning", "priorities", "game_phase", "position_score",
        "board_presence", "resources", "threats_detected", "hand_size", "summary"
    ]
    
    for field in required_fields:
        assert field in result, f"Missing field: {field}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
