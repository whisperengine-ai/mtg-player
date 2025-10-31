"""
Tests for triggered abilities: ETB and dies.
"""
import sys
from pathlib import Path
import uuid

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
from core.game_state import GameState
from core.player import Player
from core.rules_engine import RulesEngine
from core.card import CardInstance
from data.cards import create_basic_cards


def create_game_state():
    """Helper to create a basic two-player game state."""
    p1 = Player(id="p1", name="Alice", life=40)
    p2 = Player(id="p2", name="Bob", life=40)
    return GameState(
        game_id=str(uuid.uuid4()),
        players=[p1, p2],
        active_player_id="p1",
        priority_player_id="p1",
    )


def add_basic_lands(rules: RulesEngine, player: Player, count: int, name: str = "Forest"):
    """Add some basic lands to battlefield untapped for paying costs."""
    from core.card import Card, CardType
    for i in range(count):
        land = Card(id=f"{name.lower()}_{i}", name=name, card_types=[CardType.LAND])
        inst = rules.create_card_instance(land, owner_id=player.id)
        inst.is_tapped = False
        inst.summoning_sick = False
        player.battlefield.append(inst)


class TestTriggers:
    def test_etb_draw_resolves(self):
        """Casting an ETB draw creature should draw a card when the trigger resolves."""
        game_state = create_game_state()
        rules = RulesEngine(game_state)
        p1 = game_state.get_player("p1")

        cards = create_basic_cards()
        visionary = cards["elvish_visionary"]

        # Prepare library with enough cards
        # Add 5 generic cards to the top of library so draws succeed
        filler = cards["grizzly_bears"]
        for _ in range(5):
            p1.library.append(rules.create_card_instance(filler, owner_id=p1.id))

        # Give player lands to pay cost and the creature in hand
        add_basic_lands(rules, p1, count=2, name="Forest")
        creature_inst = rules.create_card_instance(visionary, owner_id=p1.id)
        p1.hand.append(creature_inst)

        # Track initial hand size
        initial_hand = len(p1.hand)

        # Cast spell (goes to stack), then pass priority around to resolve spell and trigger
        assert rules.cast_spell(p1, creature_inst)

        # Resolve spell (players pass priority in succession)
        # We loop a few times to ensure both spell and ETB ability resolve
        for _ in range(4):
            rules.pass_priority()

        # After resolution: creature on battlefield, and hand increased by 1 due to ETB draw
        assert creature_inst in p1.battlefield
        assert len(p1.hand) == initial_hand  # spell left hand then draw +1 => net 0
        # To ensure the draw actually happened, check library decreased by 1
        assert len(p1.library) == 5 - 1

    def test_dies_draw_resolves(self):
        """A dies trigger like Solemn Simulacrum should draw a card on death."""
        game_state = create_game_state()
        rules = RulesEngine(game_state)
        p1 = game_state.get_player("p1")

        cards = create_basic_cards()
        solemn = cards["solemn_simulacrum"]

        # Put Solemn on battlefield under p1 control
        solemn_inst = rules.create_card_instance(solemn, owner_id=p1.id)
        solemn_inst.summoning_sick = False
        p1.battlefield.append(solemn_inst)

        # Prepare library with enough cards to draw
        filler = cards["grizzly_bears"]
        for _ in range(3):
            p1.library.append(rules.create_card_instance(filler, owner_id=p1.id))

        # Track initial hand size
        initial_hand = len(p1.hand)

        # Mark lethal damage and invoke combat damage cleanup to move it to graveyard
        solemn_inst.damage_marked = 999
        rules.resolve_combat_damage()

        # Pass priority to allow dies trigger to resolve
        for _ in range(3):
            rules.pass_priority()

        # Solemn should be in graveyard, and hand increased by 1 from dies draw
        assert solemn_inst in p1.graveyard or solemn_inst in p1.command_zone
        assert len(p1.hand) == initial_hand + 1

    def test_etb_ramp_resolves(self):
        """Casting Wood Elves should put a land from library onto battlefield tapped."""
        game_state = create_game_state()
        rules = RulesEngine(game_state)
        p1 = game_state.get_player("p1")

        cards = create_basic_cards()
        wood_elves = cards["wood_elves"]
        forest_card = cards["forest_1"]

        # Put a Forest into library (as a CardInstance)
        forest_inst = rules.create_card_instance(forest_card, owner_id=p1.id)
        p1.library.append(forest_inst)

        # Give player lands to pay cost and the creature in hand
        add_basic_lands(rules, p1, count=3, name="Forest")
        elves_inst = rules.create_card_instance(wood_elves, owner_id=p1.id)
        p1.hand.append(elves_inst)

        # Cast Wood Elves
        assert rules.cast_spell(p1, elves_inst)

        # Resolve spell and trigger
        for _ in range(4):
            rules.pass_priority()

        # Forest should be moved from library to battlefield tapped
        assert forest_inst in p1.battlefield
        assert forest_inst.is_tapped is True
        assert forest_inst not in p1.library


if __name__ == "__main__":
    pytest.main([__file__, "-q"]) 
