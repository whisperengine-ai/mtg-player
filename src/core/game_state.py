"""
Game state and turn structure for MTG.
"""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from core.player import Player
from core.card import CardInstance


class Phase(str, Enum):
    """Game phases."""
    BEGINNING = "beginning"
    PRECOMBAT_MAIN = "precombat_main"
    COMBAT = "combat"
    POSTCOMBAT_MAIN = "postcombat_main"
    ENDING = "ending"


class Step(str, Enum):
    """Game steps."""
    # Beginning phase
    UNTAP = "untap"
    UPKEEP = "upkeep"
    DRAW = "draw"
    
    # Main phase
    MAIN = "main"
    
    # Combat phase
    BEGIN_COMBAT = "begin_combat"
    DECLARE_ATTACKERS = "declare_attackers"
    DECLARE_BLOCKERS = "declare_blockers"
    COMBAT_DAMAGE = "combat_damage"
    END_COMBAT = "end_combat"
    
    # Ending phase
    END = "end"
    CLEANUP = "cleanup"


class GameState(BaseModel):
    """Represents the complete game state."""
    model_config = {"arbitrary_types_allowed": True}
    
    game_id: str
    players: List[Player]
    turn_number: int = 1
    active_player_id: str
    priority_player_id: str
    
    # Turn structure
    current_phase: Phase = Phase.BEGINNING
    current_step: Step = Step.UNTAP
    
    # Stack (managed externally by RulesEngine, but serialized here)
    stack: List[dict] = Field(default_factory=list)
    
    # Game state
    is_game_over: bool = False
    winner_id: Optional[str] = None

    def get_player(self, player_id: str) -> Optional[Player]:
        """Get player by ID."""
        for player in self.players:
            if player.id == player_id:
                return player
        return None

    def get_active_player(self) -> Optional[Player]:
        """Get the active player."""
        return self.get_player(self.active_player_id)

    def get_priority_player(self) -> Optional[Player]:
        """Get the player with priority."""
        return self.get_player(self.priority_player_id)

    def get_opponents(self, player_id: str) -> List[Player]:
        """Get all opponents of a player."""
        return [p for p in self.players if p.id != player_id and not p.is_dead()]

    def get_alive_players(self) -> List[Player]:
        """Get all players still in the game."""
        return [p for p in self.players if not p.is_dead()]

    def check_win_condition(self):
        """Check if the game is over."""
        alive_players = self.get_alive_players()
        if len(alive_players) == 1:
            self.is_game_over = True
            self.winner_id = alive_players[0].id
        elif len(alive_players) == 0:
            self.is_game_over = True
            # Draw game

    def get_next_player_id(self, current_player_id: str) -> str:
        """Get the next player in turn order."""
        current_idx = None
        for i, player in enumerate(self.players):
            if player.id == current_player_id:
                current_idx = i
                break
        
        if current_idx is None:
            return self.players[0].id
        
        # Find next alive player
        for i in range(1, len(self.players) + 1):
            next_idx = (current_idx + i) % len(self.players)
            if not self.players[next_idx].is_dead():
                return self.players[next_idx].id
        
        return current_player_id

    def to_dict(self) -> dict:
        """Convert to dictionary for LLM consumption."""
        return {
            "game_id": self.game_id,
            "turn_number": self.turn_number,
            "current_phase": self.current_phase.value,
            "current_step": self.current_step.value,
            "active_player": self.active_player_id,
            "priority_player": self.priority_player_id,
            "players": [
                {
                    "id": p.id,
                    "name": p.name,
                    "life": p.life,
                    "hand_size": len(p.hand),
                    "battlefield": [str(card) for card in p.battlefield],
                    "creatures": [str(card) for card in p.creatures_in_play()],
                    "available_mana": str(p.available_mana()),
                    "is_active": p.id == self.active_player_id,
                    "has_priority": p.id == self.priority_player_id,
                }
                for p in self.players
            ],
            "stack": self.stack,
            "is_game_over": self.is_game_over,
            "winner_id": self.winner_id,
        }

    def __str__(self) -> str:
        """String representation."""
        active = self.get_active_player()
        return (
            f"Turn {self.turn_number} - {self.current_phase.value}/{self.current_step.value}\n"
            f"Active: {active.name if active else 'None'}\n"
            f"Players: {', '.join(f'{p.name} ({p.life} life)' for p in self.get_alive_players())}"
        )
