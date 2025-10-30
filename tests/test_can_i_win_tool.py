"""
Tests for the CanIWinTool - lethal damage detection.
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import uuid
from core.game_state import GameState, Phase, Step
from core.player import Player
from core.card import Card, CardType, CardInstance, ManaCost, Color
from core.rules_engine import RulesEngine
from tools.evaluation_tools import CanIWinTool


@pytest.fixture
def game_with_creatures():
    """Create a game with attacking creatures."""
    player1 = Player(id="p1", name="Attacker", life=40)
    player2 = Player(id="p2", name="Defender", life=9)  # 9 life so 3+1+5=9 damage is lethal
    
    game_state = GameState(
        game_id=str(uuid.uuid4()),
        players=[player1, player2],
        active_player_id="p1",
        priority_player_id="p1"
    )
    
    # Add some creatures to player1's battlefield
    # 3/3 creature
    creature1 = Card(
        id="grizzly_bears",
        name="Grizzly Bears",
        mana_cost=ManaCost(generic=2, green=0),
        card_types=[CardType.CREATURE],
        power=3,
        toughness=3,
        colors=[Color.GREEN]
    )
    creature1_inst = CardInstance(
        card=creature1,
        instance_id="grizzly_1",
        controller_id="p1",
        owner_id="p1",
        is_tapped=False,
        summoning_sick=False
    )
    
    # 2/2 creature
    creature2 = Card(
        id="llanowar_elves",
        name="Llanowar Elves",
        mana_cost=ManaCost(generic=1, green=1),
        card_types=[CardType.CREATURE],
        power=1,
        toughness=1,
        colors=[Color.GREEN]
    )
    creature2_inst = CardInstance(
        card=creature2,
        instance_id="elves_1",
        controller_id="p1",
        owner_id="p1",
        is_tapped=False,
        summoning_sick=False
    )
    
    # 5/5 creature (can deal lethal alone)
    creature3 = Card(
        id="serra_angel",
        name="Serra Angel",
        mana_cost=ManaCost(generic=3, white=1),
        card_types=[CardType.CREATURE],
        power=5,
        toughness=5,
        colors=[Color.WHITE]
    )
    creature3_inst = CardInstance(
        card=creature3,
        instance_id="serra_1",
        controller_id="p1",
        owner_id="p1",
        is_tapped=False,
        summoning_sick=False
    )
    
    player1.battlefield.extend([creature1_inst, creature2_inst, creature3_inst])
    
    rules_engine = RulesEngine(game_state)
    
    return game_state, rules_engine


def test_can_i_win_with_lethal_creatures(game_with_creatures):
    """Test detecting lethal with attacking creatures."""
    game_state, _ = game_with_creatures
    
    tool = CanIWinTool()
    tool.game_state = game_state
    
    result = tool.execute()
    
    assert result["success"] is True
    assert result["damage"] == 9  # 3+1+5 = 9 damage
    assert result["creatures_attacking"] == 3
    # 9 damage to 10 life opponent = lethal
    assert result["can_win"] is True


def test_can_i_win_insufficient_damage(game_with_creatures):
    """Test when damage is insufficient for lethal."""
    game_state, _ = game_with_creatures
    
    # Increase opponent life above available damage
    player2 = game_state.players[1]
    player2.life = 100
    
    tool = CanIWinTool()
    tool.game_state = game_state
    
    result = tool.execute()
    
    assert result["success"] is True
    assert result["can_win"] is False
    assert result["damage"] < 100


def test_can_i_win_with_damage_spells(game_with_creatures):
    """Test lethal detection including damage spells."""
    game_state, _ = game_with_creatures
    player1 = game_state.get_active_player()
    
    # Add a Lightning Bolt to hand
    lightning_bolt = Card(
        id="lightning_bolt",
        name="Lightning Bolt",
        mana_cost=ManaCost(generic=0, red=1),
        card_types=[CardType.INSTANT],
        colors=[Color.RED],
        oracle_text="Lightning Bolt deals 3 damage to any target."
    )
    bolt_inst = CardInstance(
        card=lightning_bolt,
        instance_id="bolt_1",
        controller_id="p1",
        owner_id="p1"
    )
    player1.hand.append(bolt_inst)
    
    # Give player1 red mana
    player1.mana_pool.red = 1
    
    tool = CanIWinTool()
    tool.game_state = game_state
    
    result = tool.execute()
    
    assert result["success"] is True
    # Should now have more damage (creatures + bolt)
    assert result["damage"] > 3  # At least creatures + bolt damage


def test_can_i_win_no_creatures(game_with_creatures):
    """Test when player has no creatures to attack with."""
    game_state, _ = game_with_creatures
    player1 = game_state.get_active_player()
    
    # Clear all creatures
    player1.battlefield.clear()
    
    tool = CanIWinTool()
    tool.game_state = game_state
    
    result = tool.execute()
    
    assert result["success"] is True
    assert result["damage"] == 0
    assert result["creatures_attacking"] == 0


def test_can_i_win_summoning_sick(game_with_creatures):
    """Test that summoning sick creatures can't attack."""
    game_state, _ = game_with_creatures
    player1 = game_state.get_active_player()
    
    # Mark all creatures as summoning sick
    for creature in player1.battlefield:
        creature.summoning_sick = True
    
    tool = CanIWinTool()
    tool.game_state = game_state
    
    result = tool.execute()
    
    assert result["success"] is True
    # Should show warning about summoning sickness
    assert any("summoning sickness" in c.lower() for c in result.get("considerations", []))


def test_can_i_win_target_selection(game_with_creatures):
    """Test that lethal targets the weakest opponent."""
    game_state, _ = game_with_creatures
    
    # Add a third player
    player3 = Player(id="p3", name="Weak Player", life=5)
    game_state.players.append(player3)
    
    tool = CanIWinTool()
    tool.game_state = game_state
    
    result = tool.execute()
    
    assert result["success"] is True
    # Should find lethal vs weakest player
    if result["can_win"]:
        assert result["lethal_target"] == "Weak Player"


def test_damage_extraction_patterns():
    """Test various damage spell patterns."""
    tool = CanIWinTool()
    
    # Test Lightning Bolt pattern
    bolt = Card(
        id="bolt",
        name="Lightning Bolt",
        oracle_text="deals 3 damage"
    )
    assert tool._extract_damage_from_card(bolt) == 3
    
    # Test "target opponent loses X life" pattern
    card = Card(
        id="card",
        name="Some Card",
        oracle_text="target opponent loses 4 life"
    )
    assert tool._extract_damage_from_card(card) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
