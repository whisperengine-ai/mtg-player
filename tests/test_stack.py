"""
Tests for Stack implementation and stack-based spell resolution.
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.stack import Stack, StackObject, StackObjectType
from core.game_state import GameState, Phase, Step
from core.player import Player
from core.card import Card, CardType, ManaCost, Color, CardInstance
from core.rules_engine import RulesEngine
import uuid


def create_test_card(name: str, is_creature: bool = True) -> Card:
    """Helper to create a test card."""
    return Card(
        id=str(uuid.uuid4()),
        name=name,
        mana_cost=ManaCost(generic=2),
        card_types=[CardType.CREATURE if is_creature else CardType.SORCERY],
        colors=[Color.GREEN],
        power=2 if is_creature else None,
        toughness=2 if is_creature else None
    )


def create_test_game(num_players: int = 2) -> tuple[GameState, RulesEngine]:
    """Helper to create a test game."""
    players = []
    for i in range(num_players):
        player = Player(
            id=f"p{i+1}",
            name=f"Player {i+1}",
            life=40
        )
        players.append(player)
    
    game_state = GameState(
        game_id=str(uuid.uuid4()),
        players=players,
        active_player_id="p1",
        priority_player_id="p1"
    )
    
    rules_engine = RulesEngine(game_state)
    return game_state, rules_engine


def test_stack_basic_operations():
    """Test basic stack push/pop operations."""
    stack = Stack()
    
    assert stack.is_empty()
    assert stack.size() == 0
    
    # Push an object
    obj1 = StackObject(
        object_id="obj1",
        object_type=StackObjectType.SPELL,
        controller_id="p1",
        card_name="Lightning Bolt"
    )
    stack.push(obj1)
    
    assert not stack.is_empty()
    assert stack.size() == 1
    assert stack.peek() == obj1
    
    # Push another
    obj2 = StackObject(
        object_id="obj2",
        object_type=StackObjectType.SPELL,
        controller_id="p2",
        card_name="Counterspell"
    )
    stack.push(obj2)
    
    assert stack.size() == 2
    assert stack.peek() == obj2  # LIFO - last in is on top
    
    # Pop
    popped = stack.pop()
    assert popped == obj2
    assert stack.size() == 1
    assert stack.peek() == obj1


def test_stack_priority_order():
    """Test priority passing system."""
    stack = Stack()
    player_ids = ["p1", "p2", "p3", "p4"]
    
    # Set priority order starting with p1
    stack.set_priority_order(player_ids, "p1")
    assert stack.get_priority_player() == "p1"
    
    # Pass priority
    all_passed = stack.pass_priority()
    assert not all_passed  # Not everyone has passed yet
    assert stack.get_priority_player() == "p2"
    
    stack.pass_priority()
    assert stack.get_priority_player() == "p3"
    
    stack.pass_priority()
    assert stack.get_priority_player() == "p4"
    
    # Last player passes - all have passed
    all_passed = stack.pass_priority()
    assert all_passed  # Everyone passed


def test_stack_priority_with_active_player():
    """Test that priority starts with active player regardless of position."""
    stack = Stack()
    player_ids = ["p1", "p2", "p3", "p4"]
    
    # Active player is p3
    stack.set_priority_order(player_ids, "p3")
    
    # Priority should start with p3, then go p4, p1, p2
    assert stack.get_priority_player() == "p3"
    stack.pass_priority()
    assert stack.get_priority_player() == "p4"
    stack.pass_priority()
    assert stack.get_priority_player() == "p1"
    stack.pass_priority()
    assert stack.get_priority_player() == "p2"


def test_cast_spell_puts_on_stack():
    """Test that casting a spell puts it on the stack instead of resolving immediately."""
    game_state, rules_engine = create_test_game()
    player = game_state.players[0]
    
    # Give player mana and a card
    for _ in range(3):
        land_card = Card(
            id=str(uuid.uuid4()),
            name="Forest",
            mana_cost=ManaCost(),
            card_types=[CardType.LAND],
            colors=[Color.GREEN]
        )
        land_instance = rules_engine.create_card_instance(land_card, player.id)
        player.battlefield.append(land_instance)
    
    creature_card = create_test_card("Bear")
    creature_instance = rules_engine.create_card_instance(creature_card, player.id)
    player.hand.append(creature_instance)
    
    # Cast the spell
    success = rules_engine.cast_spell(player, creature_instance)
    assert success
    
    # Card should not be in hand
    assert creature_instance not in player.hand
    
    # Card should NOT be on battlefield yet (on stack instead)
    assert creature_instance not in player.battlefield
    
    # Stack should have one object
    assert rules_engine.stack.size() == 1
    assert not rules_engine.stack.is_empty()
    
    # Game state stack should be updated
    assert len(game_state.stack) == 1


def test_resolve_stack_creature():
    """Test resolving a creature spell from the stack."""
    game_state, rules_engine = create_test_game()
    player = game_state.players[0]
    
    # Setup
    for _ in range(3):
        land_card = Card(
            id=str(uuid.uuid4()),
            name="Forest",
            mana_cost=ManaCost(),
            card_types=[CardType.LAND],
            colors=[Color.GREEN]
        )
        land_instance = rules_engine.create_card_instance(land_card, player.id)
        player.battlefield.append(land_instance)
    
    creature_card = create_test_card("Bear")
    creature_instance = rules_engine.create_card_instance(creature_card, player.id)
    player.hand.append(creature_instance)
    
    # Cast spell (puts on stack)
    rules_engine.cast_spell(player, creature_instance)
    assert rules_engine.stack.size() == 1
    
    # Resolve
    success = rules_engine.resolve_top_of_stack()
    assert success
    
    # Stack should be empty
    assert rules_engine.stack.is_empty()
    assert len(game_state.stack) == 0
    
    # Creature should now be on battlefield
    assert creature_instance in player.battlefield
    assert creature_instance.summoning_sick


def test_stack_lifo_resolution():
    """Test that stack resolves in LIFO order."""
    game_state, rules_engine = create_test_game()
    player = game_state.players[0]
    
    # Setup mana
    for _ in range(10):
        land_card = Card(
            id=str(uuid.uuid4()),
            name="Forest",
            mana_cost=ManaCost(),
            card_types=[CardType.LAND],
            colors=[Color.GREEN]
        )
        land_instance = rules_engine.create_card_instance(land_card, player.id)
        player.battlefield.append(land_instance)
    
    # Create two creatures
    creature1 = create_test_card("Bear 1")
    instance1 = rules_engine.create_card_instance(creature1, player.id)
    player.hand.append(instance1)
    
    creature2 = create_test_card("Bear 2")
    instance2 = rules_engine.create_card_instance(creature2, player.id)
    player.hand.append(instance2)
    
    # Cast both spells
    rules_engine.cast_spell(player, instance1)
    rules_engine.cast_spell(player, instance2)
    
    assert rules_engine.stack.size() == 2
    
    # Resolve - should resolve Bear 2 first (LIFO)
    rules_engine.resolve_top_of_stack()
    assert instance2 in player.battlefield
    assert instance1 not in player.battlefield
    assert rules_engine.stack.size() == 1
    
    # Resolve Bear 1
    rules_engine.resolve_top_of_stack()
    assert instance1 in player.battlefield
    assert rules_engine.stack.is_empty()


def test_pass_priority_with_empty_stack():
    """Test that passing priority with empty stack moves to next phase."""
    game_state, rules_engine = create_test_game(num_players=2)
    rules_engine.start_game()
    
    # Initialize priority
    player_ids = [p.id for p in game_state.players]
    rules_engine.stack.set_priority_order(player_ids, game_state.active_player_id)
    
    # Stack is empty
    assert rules_engine.stack.is_empty()
    
    # Both players pass
    all_passed = rules_engine.pass_priority()
    assert not all_passed
    
    all_passed = rules_engine.pass_priority()
    assert all_passed  # Everyone passed with empty stack


def test_priority_resets_after_stack_addition():
    """Test that adding to stack resets priority passes."""
    game_state, rules_engine = create_test_game(num_players=2)
    player = game_state.players[0]
    
    # Setup
    player_ids = [p.id for p in game_state.players]
    rules_engine.stack.set_priority_order(player_ids, game_state.active_player_id)
    
    # Player 1 passes
    rules_engine.pass_priority()
    assert rules_engine.stack.passes_in_succession == 1
    
    # Add something to stack
    obj = StackObject(
        object_id="obj1",
        object_type=StackObjectType.SPELL,
        controller_id="p1",
        card_name="Test Spell"
    )
    rules_engine.stack.push(obj)
    
    # Passes should be reset
    assert rules_engine.stack.passes_in_succession == 0


def test_stack_to_dict():
    """Test stack serialization."""
    stack = Stack()
    
    # Empty stack
    result = stack.to_dict()
    assert result["size"] == 0
    assert result["objects"] == []
    
    # Add object
    obj = StackObject(
        object_id="obj1",
        object_type=StackObjectType.SPELL,
        controller_id="p1",
        card_name="Lightning Bolt",
        targets=["target1"]
    )
    stack.push(obj)
    
    result = stack.to_dict()
    assert result["size"] == 1
    assert len(result["objects"]) == 1
    assert result["objects"][0]["name"] == "Lightning Bolt"
    assert result["objects"][0]["type"] == "spell"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
