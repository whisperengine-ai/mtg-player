"""
Card representation for MTG.
"""
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class CardType(str, Enum):
    """MTG card types."""
    CREATURE = "creature"
    INSTANT = "instant"
    SORCERY = "sorcery"
    ENCHANTMENT = "enchantment"
    ARTIFACT = "artifact"
    LAND = "land"
    PLANESWALKER = "planeswalker"


class Color(str, Enum):
    """MTG colors."""
    WHITE = "W"
    BLUE = "U"
    BLACK = "B"
    RED = "R"
    GREEN = "G"
    COLORLESS = "C"


class ManaCost(BaseModel):
    """Represents a mana cost."""
    generic: int = 0
    white: int = 0
    blue: int = 0
    black: int = 0
    red: int = 0
    green: int = 0
    colorless: int = 0

    def total(self) -> int:
        """Total mana value (CMC)."""
        return (
            self.generic +
            self.white +
            self.blue +
            self.black +
            self.red +
            self.green +
            self.colorless
        )

    def __str__(self) -> str:
        """String representation like {3}{W}{U}."""
        parts = []
        if self.generic > 0:
            parts.append(f"{{{self.generic}}}")
        if self.white > 0:
            parts.append("{W}" * self.white)
        if self.blue > 0:
            parts.append("{U}" * self.blue)
        if self.black > 0:
            parts.append("{B}" * self.black)
        if self.red > 0:
            parts.append("{R}" * self.red)
        if self.green > 0:
            parts.append("{G}" * self.green)
        if self.colorless > 0:
            parts.append("{C}" * self.colorless)
        return "".join(parts) if parts else "{0}"


class Card(BaseModel):
    """Represents a Magic: The Gathering card."""
    id: str = Field(description="Unique card identifier")
    name: str = Field(description="Card name")
    mana_cost: ManaCost = Field(default_factory=ManaCost)
    card_types: List[CardType] = Field(default_factory=list)
    colors: List[Color] = Field(default_factory=list)
    
    # Creature-specific
    power: Optional[int] = None
    toughness: Optional[int] = None
    
    # Abilities and text
    oracle_text: str = ""
    keywords: List[str] = Field(default_factory=list)
    
    # Metadata
    is_commander: bool = False
    is_token: bool = False

    def is_creature(self) -> bool:
        """Check if this card is a creature."""
        return CardType.CREATURE in self.card_types

    def is_land(self) -> bool:
        """Check if this card is a land."""
        return CardType.LAND in self.card_types
    
    def is_instant(self) -> bool:
        """Check if this card is an instant."""
        return CardType.INSTANT in self.card_types
    
    def is_sorcery(self) -> bool:
        """Check if this card is a sorcery."""
        return CardType.SORCERY in self.card_types

    def cmc(self) -> int:
        """Converted mana cost (mana value)."""
        return self.mana_cost.total()

    def __str__(self) -> str:
        """String representation."""
        type_line = ", ".join(t.value.title() for t in self.card_types)
        if self.is_creature() and self.power is not None:
            return f"{self.name} {self.mana_cost} - {type_line} {self.power}/{self.toughness}"
        return f"{self.name} {self.mana_cost} - {type_line}"


class CardInstance(BaseModel):
    """An instance of a card in a specific zone with game state."""
    card: Card
    instance_id: str  # Unique instance ID
    controller_id: str
    owner_id: str
    
    # State
    is_tapped: bool = False
    is_attacking: bool = False
    is_blocking: bool = False
    blocking_target: Optional[str] = None  # instance_id of creature being blocked
    
    # Counters and modifications
    damage_marked: int = 0
    plus_one_counters: int = 0
    minus_one_counters: int = 0
    
    # Temporary modifications (cleared each turn)
    temp_power_bonus: int = 0
    temp_toughness_bonus: int = 0
    summoning_sick: bool = True

    def current_power(self) -> int:
        """Calculate current power including modifications."""
        if not self.card.is_creature() or self.card.power is None:
            return 0
        return (
            self.card.power +
            self.plus_one_counters -
            self.minus_one_counters +
            self.temp_power_bonus
        )

    def current_toughness(self) -> int:
        """Calculate current toughness including modifications."""
        if not self.card.is_creature() or self.card.toughness is None:
            return 0
        return (
            self.card.toughness +
            self.plus_one_counters -
            self.minus_one_counters +
            self.temp_toughness_bonus
        )

    def is_dead(self) -> bool:
        """Check if creature should die (0 or less toughness or lethal damage)."""
        if not self.card.is_creature():
            return False
        return (
            self.current_toughness() <= 0 or
            self.damage_marked >= self.current_toughness()
        )

    def can_attack(self) -> bool:
        """Check if this creature can attack."""
        if not self.card.is_creature():
            return False
        if self.is_tapped:
            return False
        if self.summoning_sick and "haste" not in self.card.keywords:
            return False
        return True

    def can_block(self) -> bool:
        """Check if this creature can block."""
        if not self.card.is_creature():
            return False
        if self.is_tapped:
            return False
        return True

    def __str__(self) -> str:
        """String representation."""
        status = []
        if self.is_tapped:
            status.append("tapped")
        if self.is_attacking:
            status.append("attacking")
        if self.is_blocking:
            status.append("blocking")
        
        status_str = f" ({', '.join(status)})" if status else ""
        
        if self.card.is_creature():
            return f"{self.card.name} [{self.current_power()}/{self.current_toughness()}]{status_str}"
        return f"{self.card.name}{status_str}"
