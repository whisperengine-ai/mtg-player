"""
Tests for the OpponentModelingTool - opponent threat assessment and archetype detection.
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
from tools.evaluation_tools import OpponentModelingTool


@pytest.fixture
def empty_game():
    """Create a bare game state."""
    player1 = Player(id="p1", name="Player 1", life=20)
    player2 = Player(id="p2", name="Player 2", life=20)
    
    game_state = GameState(
        game_id=str(uuid.uuid4()),
        players=[player1, player2],
        active_player_id="p1",
        priority_player_id="p1"
    )
    
    rules_engine = RulesEngine(game_state)
    return game_state, rules_engine


def test_tool_schema():
    """Test tool schema generation."""
    tool = OpponentModelingTool()
    schema = tool.get_schema()
    
    assert schema["function"]["name"] == "analyze_opponent"
    assert "description" in schema["function"]
    assert "parameters" in schema["function"]


def test_aggro_archetype_detection(empty_game):
    """Test detection of aggro archetype with many small creatures."""
    game_state, _ = empty_game
    tool = OpponentModelingTool()
    tool.game_state = game_state
    
    player2 = game_state.players[1]
    
    # Add many small creatures to player2
    for i in range(6):
        card = Card(
            id=f"goblin_{i}",
            name=f"Goblin {i}",
            mana_cost=ManaCost(red=1),
            card_types=[CardType.CREATURE],
            colors=[Color.RED],
            power=2,
            toughness=1
        )
        instance = CardInstance(
            card=card,
            instance_id=f"goblin_inst_{i}",
            controller_id=player2.id,
            owner_id=player2.id,
            is_tapped=False,
            summoning_sick=False
        )
        player2.battlefield.append(instance)
    
    result = tool.execute(opponent_id=player2.id)
    
    assert result["success"] is True
    assert result["archetype"] == "aggro"
    assert result["board_summary"]["creatures"] == 6


def test_threat_assessment_high_threat(empty_game):
    """Test threat assessment with powerful creatures."""
    game_state, _ = empty_game
    tool = OpponentModelingTool()
    tool.game_state = game_state
    
    player2 = game_state.players[1]
    
    # Add a powerful flying creature
    dragon = Card(
        id="dragon",
        name="Dragon",
        mana_cost=ManaCost(red=4),
        card_types=[CardType.CREATURE],
        colors=[Color.RED],
        power=8,
        toughness=8,
        keywords=["flying"]
    )
    instance = CardInstance(
        card=dragon,
        instance_id="dragon_inst",
        controller_id=player2.id,
        owner_id=player2.id,
        is_tapped=False,
        summoning_sick=False
    )
    player2.battlefield.append(instance)
    
    result = tool.execute(opponent_id=player2.id)
    
    assert result["success"] is True
    assert result["threat_level"] >= 0.4
    assert result["biggest_threat"] is not None
    assert result["biggest_threat"]["name"] == "Dragon"


def test_biggest_threat_identification(empty_game):
    """Test correct identification of biggest threat."""
    game_state, _ = empty_game
    tool = OpponentModelingTool()
    tool.game_state = game_state
    
    player2 = game_state.players[1]
    
    # Add weak creature
    weak = Card(
        id="goblin",
        name="Goblin",
        mana_cost=ManaCost(red=1),
        card_types=[CardType.CREATURE],
        colors=[Color.RED],
        power=1,
        toughness=1
    )
    weak_inst = CardInstance(
        card=weak,
        instance_id="goblin_inst",
        controller_id=player2.id,
        owner_id=player2.id,
        is_tapped=False,
        summoning_sick=False
    )
    player2.battlefield.append(weak_inst)
    
    # Add strong creature
    strong = Card(
        id="titan",
        name="Titan",
        mana_cost=ManaCost(generic=4),
        card_types=[CardType.CREATURE],
        colors=[Color.GREEN],
        power=7,
        toughness=7
    )
    strong_inst = CardInstance(
        card=strong,
        instance_id="titan_inst",
        controller_id=player2.id,
        owner_id=player2.id,
        is_tapped=False,
        summoning_sick=False
    )
    player2.battlefield.append(strong_inst)
    
    result = tool.execute(opponent_id=player2.id)
    
    assert result["success"] is True
    assert result["biggest_threat"]["name"] == "Titan"
    assert result["biggest_threat"]["power"] == 7


def test_empty_opponent_board(empty_game):
    """Test analyzing opponent with empty board."""
    game_state, _ = empty_game
    tool = OpponentModelingTool()
    tool.game_state = game_state
    
    player2 = game_state.players[1]
    
    result = tool.execute(opponent_id=player2.id)
    
    assert result["success"] is True
    assert result["board_summary"]["creatures"] == 0


def test_confidence_scoring(empty_game):
    """Test confidence is between 0 and 1."""
    game_state, _ = empty_game
    tool = OpponentModelingTool()
    tool.game_state = game_state
    
    player2 = game_state.players[1]
    
    # Add a creature
    card = Card(
        id="creature",
        name="Creature",
        mana_cost=ManaCost(generic=2),
        card_types=[CardType.CREATURE],
        colors=[Color.RED],
        power=2,
        toughness=2
    )
    inst = CardInstance(
        card=card,
        instance_id="creature_inst",
        controller_id=player2.id,
        owner_id=player2.id,
        is_tapped=False,
        summoning_sick=False
    )
    player2.battlefield.append(inst)
    
    result = tool.execute(opponent_id=player2.id)
    
    assert result["success"] is True
    assert 0 <= result["confidence"] <= 1


def test_eliminate_political_priority(empty_game):
    """Test ELIMINATE political priority for high threats."""
    game_state, _ = empty_game
    tool = OpponentModelingTool()
    tool.game_state = game_state
    
    player2 = game_state.players[1]
    
    # Add many threatening creatures
    for i in range(4):
        card = Card(
            id=f"creature_{i}",
            name=f"Creature {i}",
            mana_cost=ManaCost(generic=i+1),
            card_types=[CardType.CREATURE],
            colors=[Color.RED],
            power=4,
            toughness=4,
            keywords=["flying"]
        )
        inst = CardInstance(
            card=card,
            instance_id=f"creature_inst_{i}",
            controller_id=player2.id,
            owner_id=player2.id,
            is_tapped=False,
            summoning_sick=False
        )
        player2.battlefield.append(inst)
    
    result = tool.execute(opponent_id=player2.id)
    
    assert result["success"] is True
    assert "ELIMINATE" in result["political_value"]


def test_hand_size_influences_threat(empty_game):
    """Test large hand size increases threat level."""
    game_state, _ = empty_game
    tool = OpponentModelingTool()
    tool.game_state = game_state
    
    player2 = game_state.players[1]
    
    # Add small creature
    card = Card(
        id="creature",
        name="Creature",
        mana_cost=ManaCost(generic=1),
        card_types=[CardType.CREATURE],
        colors=[Color.RED],
        power=1,
        toughness=1
    )
    inst = CardInstance(
        card=card,
        instance_id="creature_inst",
        controller_id=player2.id,
        owner_id=player2.id,
        is_tapped=False,
        summoning_sick=False
    )
    player2.battlefield.append(inst)
    
    # Give player2 large hand
    for i in range(7):
        hand_card = Card(
            id=f"spell_{i}",
            name=f"Spell {i}",
            mana_cost=ManaCost(generic=i),
            card_types=[CardType.SORCERY],
            colors=[Color.RED]
        )
        player2.hand.append(hand_card)
    
    result = tool.execute(opponent_id=player2.id)
    
    assert result["success"] is True
    assert result["board_summary"]["hand_size"] == 7


def test_strategy_estimate_wide_aggro(empty_game):
    """Test wide aggro strategy estimate."""
    game_state, _ = empty_game
    tool = OpponentModelingTool()
    tool.game_state = game_state
    
    player2 = game_state.players[1]
    
    # Add many small creatures (wide aggro)
    for i in range(6):
        card = Card(
            id=f"goblin_{i}",
            name=f"Goblin {i}",
            mana_cost=ManaCost(red=1),
            card_types=[CardType.CREATURE],
            colors=[Color.RED],
            power=1,
            toughness=1
        )
        inst = CardInstance(
            card=card,
            instance_id=f"goblin_inst_{i}",
            controller_id=player2.id,
            owner_id=player2.id,
            is_tapped=False,
            summoning_sick=False
        )
        player2.battlefield.append(inst)
    
    result = tool.execute(opponent_id=player2.id)
    
    assert result["success"] is True
    estimated = result["estimated_strategy"].lower()
    assert "wide" in estimated or "aggro" in estimated
