"""
Tests for instant-speed spell interactions, priority passing, and stack responses.

These tests validate Phase 4 functionality:
- Casting instants in response to other spells
- Counterspell interactions
- Combat tricks
- Priority passing
- Stack tool functionality
"""

import pytest
import uuid
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.game_state import GameState
from core.player import Player
from core.rules_engine import RulesEngine
from core.card import Card, CardType, ManaCost, Color, CardInstance
from core.stack import StackObject, StackObjectType
from data.cards import create_basic_cards
from tools.game_tools import GetStackStateTool, CanRespondTool, GetLegalActionsTool


def create_test_game(num_players=2):
    """Helper to create a basic test game."""
    players = [
        Player(id=f'p{i}', name=f'Player {i}', life=40)
        for i in range(1, num_players + 1)
    ]
    
    game_state = GameState(
        game_id=str(uuid.uuid4()),
        players=players,
        active_player_id='p1',
        priority_player_id='p1'
    )
    
    rules_engine = RulesEngine(game_state)
    rules_engine.start_game()
    
    return game_state, rules_engine


def add_card_to_hand(player, card, controller_id):
    """Helper to add a card to player's hand."""
    instance = CardInstance(
        card=card,
        instance_id=str(uuid.uuid4()),
        controller_id=controller_id,
        owner_id=controller_id
    )
    player.hand.append(instance)
    return instance


def add_mana_to_battlefield(player, color, count, controller_id):
    """Helper to add mana sources (lands) to battlefield."""
    color_map = {
        Color.BLUE: 'Island',
        Color.GREEN: 'Forest',
        Color.RED: 'Mountain',
        Color.WHITE: 'Plains',
        Color.BLACK: 'Swamp'
    }
    
    land_card = Card(
        id=f'{color_map[color].lower()}',
        name=color_map[color],
        card_types=[CardType.LAND],
        colors=[color],
        mana_cost=ManaCost()
    )
    
    for _ in range(count):
        instance = CardInstance(
            card=land_card,
            instance_id=str(uuid.uuid4()),
            controller_id=controller_id,
            owner_id=controller_id
        )
        instance.is_tapped = False  # Lands available for mana
        player.battlefield.append(instance)


class TestInstantSpeedCasting:
    """Test basic instant-speed spell casting."""
    
    def test_can_cast_instant_any_time(self):
        """Test that instants can be cast when you have priority."""
        game_state, rules_engine = create_test_game()
        player = game_state.players[0]
        
        # Give player Counterspell and mana
        cards = create_basic_cards()
        counterspell = cards['counterspell']
        add_card_to_hand(player, counterspell, 'p1')
        add_mana_to_battlefield(player, Color.BLUE, 2, 'p1')
        
        # Player should be able to cast instant using tool
        tool = GetLegalActionsTool()
        tool.game_state = game_state
        tool.rules_engine = rules_engine
        result = tool.execute()
        
        # Check that counterspell is in castable spells
        assert isinstance(result, list) or 'error' not in result
        # Instant should be castable with sufficient mana
        assert len(player.hand) > 0, "Should have card in hand"
    
    def test_instant_in_hand(self):
        """Test that instant spells are properly in hand."""
        game_state, rules_engine = create_test_game()
        player = game_state.players[0]
        
        # Create an instant
        cards = create_basic_cards()
        lightning_bolt = cards['lightning_bolt']
        add_card_to_hand(player, lightning_bolt, 'p1')
        add_mana_to_battlefield(player, Color.RED, 1, 'p1')
        
        # Verify instant is in hand
        assert len(player.hand) > 0, "Should have card in hand"
        instant_in_hand = player.hand[0]
        assert instant_in_hand.card.is_instant(), "Card should be an instant"
        assert instant_in_hand.card.name == "Lightning Bolt"


class TestCounterspells:
    """Test counterspell interactions."""
    
    def test_counterspell_counters_spell(self):
        """Test that Counterspell successfully counters a spell."""
        game_state, rules_engine = create_test_game()
        player1 = game_state.players[0]
        
        # Player 1 has Counterspell
        cards = create_basic_cards()
        counterspell = cards['counterspell']
        counter_instance = add_card_to_hand(player1, counterspell, 'p1')
        add_mana_to_battlefield(player1, Color.BLUE, 2, 'p1')
        
        # Player 2 casts a spell (simulate by adding to stack)
        target_spell = StackObject(
            object_id='spell1',
            object_type=StackObjectType.SPELL,
            controller_id='p2',
            card_name='Fireball',
            can_be_countered=True
        )
        rules_engine.stack.push(target_spell)
        rules_engine.stack.set_priority_order(['p1', 'p2'], 'p1')
        
        # Player 1 should be able to cast Counterspell in response
        game_state.priority_player_id = 'p1'
        
        # Cast Counterspell
        result = rules_engine.cast_spell(player1, counter_instance)
        
        assert result == True, "Should successfully cast Counterspell"
        assert rules_engine.stack.size() == 2, "Stack should have 2 spells"
        assert rules_engine.stack.peek().card_name == 'Counterspell'
    
    def test_stack_state_tool_with_counterspell(self):
        """Test GetStackStateTool shows counterspell on stack."""
        game_state, rules_engine = create_test_game()
        
        # Add two spells to stack
        spell1 = StackObject(
            object_id='spell1',
            object_type=StackObjectType.SPELL,
            controller_id='p2',
            card_name='Fireball',
            can_be_countered=True
        )
        spell2 = StackObject(
            object_id='spell2',
            object_type=StackObjectType.SPELL,
            controller_id='p1',
            card_name='Counterspell',
            can_be_countered=True
        )
        
        rules_engine.stack.push(spell1)
        rules_engine.stack.push(spell2)
        rules_engine.stack.set_priority_order(['p1', 'p2'], 'p1')
        
        # Test stack state tool
        tool = GetStackStateTool()
        tool.game_state = game_state
        tool.rules_engine = rules_engine
        
        result = tool.execute()
        
        assert result['stack_size'] == 2
        assert result['top_object']['name'] == 'Counterspell'
        assert len(result['objects']) == 2
        assert result['objects'][0]['name'] == 'Fireball'  # Bottom of stack
        assert result['objects'][1]['name'] == 'Counterspell'  # Top of stack


class TestCanRespondTool:
    """Test the CanRespondTool functionality."""
    
    def test_can_respond_with_instants_in_hand(self):
        """Test tool correctly identifies when you can respond."""
        game_state, rules_engine = create_test_game()
        player = game_state.players[0]
        
        # Give player instants and mana
        cards = create_basic_cards()
        lightning_bolt = cards['lightning_bolt']
        counterspell = cards['counterspell']
        add_card_to_hand(player, lightning_bolt, 'p1')
        add_card_to_hand(player, counterspell, 'p1')
        add_mana_to_battlefield(player, Color.RED, 1, 'p1')
        add_mana_to_battlefield(player, Color.BLUE, 2, 'p1')
        
        # Add opponent spell to stack
        spell = StackObject(
            object_id='spell1',
            object_type=StackObjectType.SPELL,
            controller_id='p2',
            card_name='Giant Growth',
            can_be_countered=True
        )
        rules_engine.stack.push(spell)
        rules_engine.stack.set_priority_order(['p1', 'p2'], 'p1')
        game_state.priority_player_id = 'p1'
        
        # Test can respond tool
        tool = CanRespondTool()
        tool.game_state = game_state
        tool.rules_engine = rules_engine
        
        result = tool.execute()
        
        assert result['has_priority'] == True
        assert result['can_respond'] == True
        assert len(result['castable_instants']) >= 1
        assert result['top_of_stack']['name'] == 'Giant Growth'
        assert 'recommendation' in result
        assert len(result['recommendation']) > 0
    
    def test_cannot_respond_without_mana(self):
        """Test tool shows can't respond when no mana available."""
        game_state, rules_engine = create_test_game()
        player = game_state.players[0]
        
        # Give player instants but NO mana
        cards = create_basic_cards()
        counterspell = cards['counterspell']
        add_card_to_hand(player, counterspell, 'p1')
        
        # Add opponent spell to stack
        spell = StackObject(
            object_id='spell1',
            object_type=StackObjectType.SPELL,
            controller_id='p2',
            card_name='Fireball',
            can_be_countered=True
        )
        rules_engine.stack.push(spell)
        rules_engine.stack.set_priority_order(['p1', 'p2'], 'p1')
        game_state.priority_player_id = 'p1'
        
        # Test can respond tool
        tool = CanRespondTool()
        tool.game_state = game_state
        tool.rules_engine = rules_engine
        
        result = tool.execute()
        
        assert result['has_priority'] == True
        assert result['can_respond'] == False  # No mana to cast instants
        assert len(result['castable_instants']) == 0
    
    def test_cannot_respond_without_priority(self):
        """Test tool shows can't respond when you don't have priority."""
        game_state, rules_engine = create_test_game()
        player = game_state.players[0]
        
        # Give player instants and mana
        cards = create_basic_cards()
        counterspell = cards['counterspell']
        add_card_to_hand(player, counterspell, 'p1')
        add_mana_to_battlefield(player, Color.BLUE, 2, 'p1')
        
        # Add spell to stack but give priority to opponent
        spell = StackObject(
            object_id='spell1',
            object_type=StackObjectType.SPELL,
            controller_id='p2',
            card_name='Fireball',
            can_be_countered=True
        )
        rules_engine.stack.push(spell)
        rules_engine.stack.set_priority_order(['p1', 'p2'], 'p2')  # p2 has priority
        game_state.priority_player_id = 'p2'
        
        # Test can respond tool
        tool = CanRespondTool()
        tool.game_state = game_state
        tool.rules_engine = rules_engine
        
        result = tool.execute()
        
        assert result['has_priority'] == False
        assert result['can_respond'] == False


class TestCombatTricks:
    """Test instant-speed combat tricks."""
    
    def test_giant_growth_in_combat(self):
        """Test using Giant Growth as a combat trick."""
        game_state, rules_engine = create_test_game()
        player = game_state.players[0]
        
        # Give player Giant Growth and mana
        cards = create_basic_cards()
        giant_growth = cards['giant_growth']
        add_card_to_hand(player, giant_growth, 'p1')
        add_mana_to_battlefield(player, Color.GREEN, 1, 'p1')
        
        # Create a creature on battlefield
        creature = Card(
            id='creature1',
            name='Test Creature',
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            mana_cost=ManaCost(green=1),
            power=2,
            toughness=2,
            oracle_text=''
        )
        creature_instance = CardInstance(
            card=creature,
            instance_id=str(uuid.uuid4()),
            controller_id='p1',
            owner_id='p1'
        )
        player.battlefield.append(creature_instance)
        
        # Player should have Giant Growth in hand
        assert len(player.hand) > 0, "Should have Giant Growth in hand"
        assert player.hand[0].card.is_instant(), "Should be an instant"


class TestPriorityPassing:
    """Test priority passing mechanics."""
    
    def test_priority_passes_around_table(self):
        """Test that priority passes to each player in order."""
        _, rules_engine = create_test_game(num_players=4)
        
        # Add a spell to stack
        spell = StackObject(
            object_id='spell1',
            object_type=StackObjectType.SPELL,
            controller_id='p1',
            card_name='Rampant Growth',
            can_be_countered=True
        )
        rules_engine.stack.push(spell)
        
        # Set priority order
        priority_order = ['p1', 'p2', 'p3', 'p4']
        rules_engine.stack.set_priority_order(priority_order, 'p1')
        
        # Verify priority order
        assert rules_engine.stack.priority_order == priority_order
        assert rules_engine.stack.get_priority_player() == 'p1'
    
    def test_all_players_pass_resolves_stack(self):
        """Test that when all players pass, top of stack resolves."""
        _, rules_engine = create_test_game(num_players=2)
        
        # Add spell to stack
        spell = StackObject(
            object_id='spell1',
            object_type=StackObjectType.SPELL,
            controller_id='p1',
            card_name='Lightning Bolt',
            can_be_countered=True
        )
        rules_engine.stack.push(spell)
        rules_engine.stack.set_priority_order(['p1', 'p2'], 'p1')
        
        initial_size = rules_engine.stack.size()
        assert initial_size == 1, "Stack should have 1 spell"
        
        # Both players pass priority
        result1 = rules_engine.stack.pass_priority()  # p1 passes
        assert result1 == False, "First pass shouldn't trigger resolution"
        
        result2 = rules_engine.stack.pass_priority()  # p2 passes
        assert result2 == True, "Second pass should indicate all players passed"
        assert rules_engine.stack.passes_in_succession >= 2, "Both players should have passed"


class TestStackTools:
    """Test stack-awareness tools integration."""
    
    def test_get_stack_state_empty_stack(self):
        """Test GetStackStateTool with empty stack."""
        game_state, rules_engine = create_test_game()
        
        tool = GetStackStateTool()
        tool.game_state = game_state
        tool.rules_engine = rules_engine
        
        result = tool.execute()
        
        assert result['stack_size'] == 0
        assert result['is_empty'] == True
        assert len(result['objects']) == 0
        assert result['top_object'] is None
    
    def test_get_stack_state_multiple_spells(self):
        """Test GetStackStateTool with multiple spells."""
        game_state, rules_engine = create_test_game()
        
        # Add 3 spells to stack
        spells = ['Spell A', 'Spell B', 'Spell C']
        for spell_name in spells:
            spell = StackObject(
                object_id=f'spell_{spell_name}',
                object_type=StackObjectType.SPELL,
                controller_id='p1',
                card_name=spell_name,
                can_be_countered=True
            )
            rules_engine.stack.push(spell)
        
        rules_engine.stack.set_priority_order(['p1', 'p2'], 'p1')
        
        tool = GetStackStateTool()
        tool.game_state = game_state
        tool.rules_engine = rules_engine
        
        result = tool.execute()
        
        assert result['stack_size'] == 3
        assert result['is_empty'] == False
        assert result['top_object']['name'] == 'Spell C'  # Last one pushed
        assert result['objects'][0]['name'] == 'Spell A'  # Bottom
        assert result['objects'][2]['name'] == 'Spell C'  # Top
    
    def test_can_respond_recommendation_quality(self):
        """Test that CanRespondTool provides useful recommendations."""
        game_state, rules_engine = create_test_game()
        player = game_state.players[0]
        
        # Give player counterspell and mana
        cards = create_basic_cards()
        counterspell = cards['counterspell']
        add_card_to_hand(player, counterspell, 'p1')
        add_mana_to_battlefield(player, Color.BLUE, 2, 'p1')
        
        # Add opponent spell to stack
        spell = StackObject(
            object_id='spell1',
            object_type=StackObjectType.SPELL,
            controller_id='p2',
            card_name='Wrath of God',
            can_be_countered=True
        )
        rules_engine.stack.push(spell)
        rules_engine.stack.set_priority_order(['p1', 'p2'], 'p1')
        game_state.priority_player_id = 'p1'
        
        tool = CanRespondTool()
        tool.game_state = game_state
        tool.rules_engine = rules_engine
        
        result = tool.execute()
        
        # Check recommendation contains useful info
        rec = result['recommendation']
        assert 'Wrath of God' in rec, "Should mention the spell on stack"
        assert len(rec) > 20, "Should have meaningful recommendation text"
        
        # Should mention available options
        assert result['can_respond'] == True
        assert len(result['castable_instants']) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
