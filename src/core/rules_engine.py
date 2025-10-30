"""
Core rules engine for MTG.
Handles game logic, turn structure, and action validation.
"""
from typing import Optional, List
import uuid
from core.game_state import GameState, Phase, Step
from core.player import Player
from core.card import CardInstance, Card
from core.stack import Stack, StackObject, StackObjectType


class RulesEngine:
    """Manages game rules and state transitions."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.stack = Stack()  # Create stack manager
        self._pending_cards: dict = {}  # Store cards pending resolution

    def start_game(self):
        """Initialize the game."""
        # Each player draws opening hand (7 cards)
        for player in self.game_state.players:
            for _ in range(7):
                player.draw_card()
        
        # Set first player as active
        first_player = self.game_state.players[0]
        first_player.is_active_player = True
        first_player.has_priority = True
        
        # Initialize stack priority order
        player_ids = [p.id for p in self.game_state.players]
        self.stack.set_priority_order(player_ids, self.game_state.active_player_id)

    def advance_phase(self):
        """Move to the next phase."""
        phase_order = [
            (Phase.BEGINNING, Step.UNTAP),
            (Phase.BEGINNING, Step.UPKEEP),
            (Phase.BEGINNING, Step.DRAW),
            (Phase.PRECOMBAT_MAIN, Step.MAIN),
            (Phase.COMBAT, Step.BEGIN_COMBAT),
            (Phase.COMBAT, Step.DECLARE_ATTACKERS),
            (Phase.COMBAT, Step.DECLARE_BLOCKERS),
            (Phase.COMBAT, Step.COMBAT_DAMAGE),
            (Phase.COMBAT, Step.END_COMBAT),
            (Phase.POSTCOMBAT_MAIN, Step.MAIN),
            (Phase.ENDING, Step.END),
            (Phase.ENDING, Step.CLEANUP),
        ]
        
        # Find current phase/step in order
        current = (self.game_state.current_phase, self.game_state.current_step)
        try:
            current_idx = phase_order.index(current)
            next_idx = current_idx + 1
            
            if next_idx >= len(phase_order):
                # End of turn, move to next player
                self.advance_turn()
            else:
                # Move to next phase/step
                self.game_state.current_phase, self.game_state.current_step = phase_order[next_idx]
                self.execute_phase_actions()
        except ValueError:
            # Invalid phase, reset to beginning
            self.game_state.current_phase = Phase.BEGINNING
            self.game_state.current_step = Step.UNTAP

    def advance_turn(self):
        """Move to the next player's turn."""
        # Get next player
        next_player_id = self.game_state.get_next_player_id(self.game_state.active_player_id)
        
        # Update active player
        current_active = self.game_state.get_active_player()
        if current_active:
            current_active.is_active_player = False
            current_active.has_priority = False
        
        next_player = self.game_state.get_player(next_player_id)
        if next_player:
            next_player.is_active_player = True
            next_player.has_priority = True
            
        self.game_state.active_player_id = next_player_id
        self.game_state.priority_player_id = next_player_id
        self.game_state.turn_number += 1
        
        # Reset to beginning phase
        self.game_state.current_phase = Phase.BEGINNING
        self.game_state.current_step = Step.UNTAP
        
        self.execute_phase_actions()

    def execute_phase_actions(self):
        """Execute automatic actions for the current phase."""
        active_player = self.game_state.get_active_player()
        if not active_player:
            return
        
        step = self.game_state.current_step
        
        if step == Step.UNTAP:
            self.untap_step(active_player)
        elif step == Step.DRAW:
            self.draw_step(active_player)
        elif step == Step.CLEANUP:
            self.cleanup_step(active_player)

    def untap_step(self, player: Player):
        """Untap all permanents."""
        for card in player.battlefield:
            card.is_tapped = False
            card.summoning_sick = False
        
        # Clear mana pool
        player.mana_pool.clear()

    def draw_step(self, player: Player):
        """Draw a card."""
        player.draw_card()

    def cleanup_step(self, player: Player):
        """Cleanup step actions."""
        # Remove temporary effects
        for card in player.battlefield:
            card.temp_power_bonus = 0
            card.temp_toughness_bonus = 0
            card.damage_marked = 0
        
        # Clear mana pool
        player.mana_pool.clear()
        
        # Reset land drop
        player.has_played_land_this_turn = False
        
        # Discard to hand size (7)
        # Simplified: assume hand size is 7
        while len(player.hand) > 7:
            # In a full implementation, player would choose
            card = player.hand.pop()
            player.graveyard.append(card)

    def play_land(self, player: Player, card_instance: CardInstance) -> bool:
        """Play a land from hand."""
        # Validation
        if player.has_played_land_this_turn:
            return False
        
        if card_instance not in player.hand:
            return False
        
        if not card_instance.card.is_land():
            return False
        
        # Execute
        player.hand.remove(card_instance)
        player.battlefield.append(card_instance)
        player.has_played_land_this_turn = True
        
        return True

    def tap_land_for_mana(self, player: Player, land: CardInstance) -> bool:
        """Tap a land to add mana to pool."""
        if land not in player.battlefield:
            return False
        
        if not land.card.is_land():
            return False
        
        if land.is_tapped:
            return False
        
        # Tap the land
        land.is_tapped = True
        
        # Add mana (simplified: 1 colorless for all lands)
        # In a full implementation, would check land type
        player.mana_pool.colorless += 1
        
        return True

    def cast_spell(self, player: Player, card_instance: CardInstance, targets: Optional[List[str]] = None) -> bool:
        """Cast a spell from hand - puts it on the stack."""
        # Validation
        if card_instance not in player.hand:
            return False
        
        if card_instance.card.is_land():
            return False
        
        # Check mana (simplified)
        available_mana = player.available_mana()
        required_mana = card_instance.card.mana_cost.total()
        
        if available_mana.total() < required_mana:
            return False
        
        # Pay mana (simplified: just remove from pool/tap lands)
        mana_to_pay = required_mana
        for land in player.untapped_lands():
            if mana_to_pay <= 0:
                break
            land.is_tapped = True
            mana_to_pay -= 1
        
        # Move card from hand and put on stack
        player.hand.remove(card_instance)
        
        # Create stack object
        stack_obj = StackObject(
            object_id=str(uuid.uuid4()),
            object_type=StackObjectType.SPELL,
            controller_id=player.id,
            card_instance_id=card_instance.instance_id,
            card_name=card_instance.card.name,
            targets=targets or [],
            is_instant_speed=False  # Simplified for now
        )
        
        # Push to stack
        self.stack.push(stack_obj)
        
        # Update game state stack representation
        self.game_state.stack = [obj.model_dump() for obj in self.stack.get_all()]
        
        # Store card instance for resolution
        self._pending_cards[card_instance.instance_id] = card_instance
        
        # Priority returns to active player
        self.stack.reset_priority_after_resolution(self.game_state.active_player_id)
        
        return True
    
    def resolve_top_of_stack(self) -> bool:
        """Resolve the top object on the stack."""
        if self.stack.is_empty():
            return False
        
        stack_obj = self.stack.pop()
        if not stack_obj:
            return False
        
        # Update game state
        self.game_state.stack = [obj.model_dump() for obj in self.stack.get_all()]
        
        if stack_obj.object_type == StackObjectType.SPELL:
            # Resolve spell
            card_instance = self._pending_cards.get(stack_obj.card_instance_id)
            if not card_instance:
                return False
            
            # Get controller
            controller = self.game_state.get_player(stack_obj.controller_id)
            if not controller:
                return False
            
            # Resolve based on card type
            if card_instance.card.is_creature():
                # Creature goes to battlefield
                card_instance.summoning_sick = True
                controller.battlefield.append(card_instance)
            else:
                # Other spells resolve and go to graveyard
                controller.graveyard.append(card_instance)
            
            # Clean up pending cards
            self._pending_cards.pop(stack_obj.card_instance_id, None)
        
        # Priority returns to active player after resolution
        self.stack.reset_priority_after_resolution(self.game_state.active_player_id)
        
        return True
    
    def pass_priority(self) -> bool:
        """
        Current priority player passes priority.
        Returns True if stack should resolve (all players passed).
        """
        all_passed = self.stack.pass_priority()
        
        if all_passed and not self.stack.is_empty():
            # All players passed with objects on stack - resolve top
            self.resolve_top_of_stack()
            return True
        elif all_passed and self.stack.is_empty():
            # All passed with empty stack - move to next phase/step
            return True
        
        # Update priority player in game state
        priority_player_id = self.stack.get_priority_player()
        if priority_player_id:
            self.game_state.priority_player_id = priority_player_id
        
        return False

    def declare_attackers(self, player: Player, attackers: List[tuple[CardInstance, str]]) -> bool:
        """Declare attacking creatures.
        
        Args:
            player: Attacking player
            attackers: List of (creature, target_player_id) tuples
        """
        # Validation
        for creature, target_id in attackers:
            if creature not in player.battlefield:
                return False
            
            if not creature.can_attack():
                return False
            
            target_player = self.game_state.get_player(target_id)
            if not target_player or target_player.id == player.id:
                return False
        
        # Execute
        for creature, target_id in attackers:
            creature.is_attacking = True
            creature.is_tapped = True
        
        return True

    def declare_blockers(self, player: Player, blockers: List[tuple[CardInstance, str]]) -> bool:
        """Declare blocking creatures.
        
        Args:
            player: Blocking player
            blockers: List of (blocker, attacker_instance_id) tuples
        """
        # Validation
        for blocker, attacker_id in blockers:
            if blocker not in player.battlefield:
                return False
            
            if not blocker.can_block():
                return False
        
        # Execute
        for blocker, attacker_id in blockers:
            blocker.is_blocking = True
            blocker.blocking_target = attacker_id
        
        return True

    def resolve_combat_damage(self):
        """Resolve combat damage."""
        active_player = self.game_state.get_active_player()
        if not active_player:
            return
        
        # Find all attacking creatures
        attackers = [c for c in active_player.battlefield if c.is_attacking]
        
        for attacker in attackers:
            # Find blockers
            blockers = []
            for opponent in self.game_state.get_opponents(active_player.id):
                for creature in opponent.creatures_in_play():
                    if creature.blocking_target == attacker.instance_id:
                        blockers.append(creature)
            
            if blockers:
                # Attacker deals damage to blockers
                for blocker in blockers:
                    blocker.damage_marked += attacker.current_power()
                    attacker.damage_marked += blocker.current_power()
            else:
                # Attacker deals damage to defending player
                # Find which player was being attacked (simplified: first opponent)
                opponents = self.game_state.get_opponents(active_player.id)
                if opponents:
                    target = opponents[0]
                    damage = attacker.current_power()
                    target.life -= damage
                    
                    # Track commander damage
                    if attacker.card.is_commander:
                        if active_player.id not in target.commander_damage:
                            target.commander_damage[active_player.id] = 0
                        target.commander_damage[active_player.id] += damage
                        
                        # Check for commander damage win condition (21 damage)
                        if target.commander_damage[active_player.id] >= 21:
                            target.has_lost = True
        
        # Check for dead creatures (including commanders)
        for player in self.game_state.players:
            dead_creatures = [c for c in player.battlefield if c.is_dead()]
            for creature in dead_creatures:
                player.battlefield.remove(creature)
                
                # If it's a commander, owner can choose to move to command zone
                if creature.card.is_commander:
                    # Simplified: always move commander to command zone
                    player.command_zone.append(creature)
                    player.command_tax += 2  # Increment command tax by {2}
                else:
                    player.graveyard.append(creature)
        
        # Clear combat state
        for player in self.game_state.players:
            for creature in player.creatures_in_play():
                creature.is_attacking = False
                creature.is_blocking = False
                creature.blocking_target = None
        
        # Check win conditions (including commander damage)
        self.check_win_conditions()

    def cast_commander(self, player: Player) -> bool:
        """Cast commander from command zone."""
        if not player.commander:
            return False
        
        commander = player.commander
        
        # Check if commander is in command zone
        if commander not in player.command_zone:
            return False
        
        # Calculate total mana cost (including command tax)
        base_cost = commander.card.mana_cost.total()
        total_cost = base_cost + player.command_tax
        
        # Check mana availability
        available_mana = player.available_mana()
        if available_mana.total() < total_cost:
            return False
        
        # Pay mana (simplified: tap lands)
        mana_to_pay = total_cost
        for land in player.untapped_lands():
            if mana_to_pay <= 0:
                break
            land.is_tapped = True
            mana_to_pay -= 1
        
        # Move commander from command zone to battlefield
        player.command_zone.remove(commander)
        commander.summoning_sick = True
        player.battlefield.append(commander)
        
        return True

    def check_win_conditions(self):
        """Check all win conditions including commander damage."""
        for player in self.game_state.players:
            # Check life total
            if player.life <= 0:
                player.has_lost = True
            
            # Check commander damage (21 from any single commander)
            for _, damage in player.commander_damage.items():
                if damage >= 21:
                    player.has_lost = True
                    break
        
        # Update game state
        self.game_state.check_win_condition()

    def create_card_instance(self, card: Card, owner_id: str) -> CardInstance:
        """Create a new instance of a card."""
        return CardInstance(
            card=card,
            instance_id=str(uuid.uuid4()),
            controller_id=owner_id,
            owner_id=owner_id
        )
