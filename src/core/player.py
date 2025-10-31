"""
Player state representation.
"""
from typing import List, Dict
from pydantic import BaseModel, Field
from core.card import CardInstance, Color


class ManaPool(BaseModel):
    """Represents available mana."""
    white: int = 0
    blue: int = 0
    black: int = 0
    red: int = 0
    green: int = 0
    colorless: int = 0

    def total(self) -> int:
        """Total mana available."""
        return (
            self.white +
            self.blue +
            self.black +
            self.red +
            self.green +
            self.colorless
        )

    def add(self, color: str, amount: int = 1):
        """Add mana of a color."""
        color = color.lower()
        if hasattr(self, color):
            setattr(self, color, getattr(self, color) + amount)

    def clear(self):
        """Empty the mana pool."""
        self.white = 0
        self.blue = 0
        self.black = 0
        self.red = 0
        self.green = 0
        self.colorless = 0

    def __str__(self) -> str:
        """String representation."""
        parts = []
        if self.white > 0:
            parts.append(f"{self.white}W")
        if self.blue > 0:
            parts.append(f"{self.blue}U")
        if self.black > 0:
            parts.append(f"{self.black}B")
        if self.red > 0:
            parts.append(f"{self.red}R")
        if self.green > 0:
            parts.append(f"{self.green}G")
        if self.colorless > 0:
            parts.append(f"{self.colorless}C")
        return ", ".join(parts) if parts else "0"


class Player(BaseModel):
    """Represents a player in the game."""
    id: str
    name: str
    life: int = 40  # Commander starts at 40
    
    # Commander-specific
    commander: CardInstance | None = None
    commander_damage: Dict[str, int] = Field(default_factory=dict)  # damage from each opponent's commander
    command_tax: int = 0  # additional cost to cast commander
    
    # Zones
    library: List[CardInstance] = Field(default_factory=list)
    hand: List[CardInstance] = Field(default_factory=list)
    battlefield: List[CardInstance] = Field(default_factory=list)
    graveyard: List[CardInstance] = Field(default_factory=list)
    exile: List[CardInstance] = Field(default_factory=list)
    command_zone: List[CardInstance] = Field(default_factory=list)
    
    # Resources
    mana_pool: ManaPool = Field(default_factory=ManaPool)
    
    # State
    has_played_land_this_turn: bool = False
    is_active_player: bool = False
    has_priority: bool = False
    has_lost: bool = False

    def lands_in_play(self) -> List[CardInstance]:
        """Get all lands on battlefield."""
        return [card for card in self.battlefield if card.card.is_land()]

    def creatures_in_play(self) -> List[CardInstance]:
        """Get all creatures on battlefield."""
        return [card for card in self.battlefield if card.card.is_creature()]

    def untapped_lands(self) -> List[CardInstance]:
        """Get all untapped lands."""
        return [land for land in self.lands_in_play() if not land.is_tapped]

    def available_mana(self) -> ManaPool:
        """Calculate available mana from untapped lands."""
        mana = ManaPool()
        for land in self.untapped_lands():
            # Check for basic land types by name or colors
            land_name = land.card.name.lower()
            if "plains" in land_name or Color.WHITE in land.card.colors:
                mana.white += 1
            elif "island" in land_name or Color.BLUE in land.card.colors:
                mana.blue += 1
            elif "swamp" in land_name or Color.BLACK in land.card.colors:
                mana.black += 1
            elif "mountain" in land_name or Color.RED in land.card.colors:
                mana.red += 1
            elif "forest" in land_name or Color.GREEN in land.card.colors:
                mana.green += 1
            else:
                # Non-basic lands produce colorless for now
                mana.colorless += 1
        
        # Add existing mana pool
        mana.white += self.mana_pool.white
        mana.blue += self.mana_pool.blue
        mana.black += self.mana_pool.black
        mana.red += self.mana_pool.red
        mana.green += self.mana_pool.green
        mana.colorless += self.mana_pool.colorless
        
        return mana

    def is_dead(self) -> bool:
        """Check if player has lost."""
        if self.has_lost:
            return True
        if self.life <= 0:
            return True
        # Check commander damage (21 damage from any single commander)
        for damage in self.commander_damage.values():
            if damage >= 21:
                return True
        # Check if library is empty (simplified)
        return False

    def draw_card(self) -> CardInstance | None:
        """Draw a card from library."""
        if not self.library:
            self.has_lost = True  # Lose from drawing from empty library
            return None
        card = self.library.pop(0)
        self.hand.append(card)
        return card

    def __str__(self) -> str:
        """String representation."""
        return (
            f"{self.name} - Life: {self.life}, "
            f"Hand: {len(self.hand)}, "
            f"Battlefield: {len(self.battlefield)} cards, "
            f"Creatures: {len(self.creatures_in_play())}"
        )
