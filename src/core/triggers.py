"""
Triggered ability system for MTG.

Handles enters-the-battlefield (ETB), dies, and other triggered abilities.
"""
from typing import List, Optional, Dict, Any, Callable
from enum import Enum
from pydantic import BaseModel, Field


class TriggerType(str, Enum):
    """Types of triggers."""
    ETB = "enters_the_battlefield"  # When permanent enters battlefield
    DIES = "dies"  # When permanent moves to graveyard from battlefield
    ATTACKS = "attacks"  # When creature attacks
    BLOCKS = "blocks"  # When creature blocks
    DEALS_DAMAGE = "deals_damage"  # When source deals damage
    CAST = "cast"  # When spell is cast
    DRAW = "draw"  # When card is drawn
    UPKEEP = "upkeep"  # At beginning of upkeep
    END_STEP = "end_step"  # At beginning of end step


class TriggerEffect(BaseModel):
    """Represents the effect of a triggered ability."""
    effect_type: str  # "draw_card", "deal_damage", "create_token", "ramp", etc.
    amount: Optional[int] = None  # Numeric value (damage, cards, etc.)
    target_type: Optional[str] = None  # "any", "opponent", "player", "creature", etc.
    text: str  # Human-readable effect description
    
    # Optional: conditions for the trigger
    conditions: Dict[str, Any] = Field(default_factory=dict)
    
    # Optional: targeting information
    requires_target: bool = False
    valid_targets: List[str] = Field(default_factory=list)  # List of valid target IDs


class TriggeredAbility(BaseModel):
    """Definition of a triggered ability on a card."""
    trigger_type: TriggerType
    effect: TriggerEffect
    
    # Optional: only trigger under certain conditions
    condition: Optional[Callable] = Field(default=None, exclude=True)
    
    def __str__(self) -> str:
        """Human-readable trigger."""
        trigger_text = {
            TriggerType.ETB: "When this enters the battlefield",
            TriggerType.DIES: "When this dies",
            TriggerType.ATTACKS: "When this attacks",
            TriggerType.BLOCKS: "When this blocks",
            TriggerType.UPKEEP: "At the beginning of your upkeep",
            TriggerType.END_STEP: "At the beginning of the end step",
        }.get(self.trigger_type, f"When {self.trigger_type.value}")
        
        return f"{trigger_text}, {self.effect.text}"


class QueuedTrigger(BaseModel):
    """A trigger that has been queued and is waiting to go on the stack."""
    ability: TriggeredAbility
    controller_id: str  # Player who controls the permanent with the trigger
    source_id: str  # Instance ID of the permanent that triggered
    source_name: str  # Name of the card for display
    
    # For ordering (APNAP - Active Player, Non-Active Player)
    is_active_player: bool = False
    
    # Targeting information (if required)
    chosen_targets: List[str] = Field(default_factory=list)
    
    def __str__(self) -> str:
        """Human-readable queued trigger."""
        return f"{self.source_name}'s triggered ability: {self.ability.effect.text}"


class TriggerQueue(BaseModel):
    """
    Queue of triggered abilities waiting to be put on the stack.
    
    Triggers are ordered by APNAP (Active Player, Non-Active Player):
    - Active player's triggers go on stack first
    - Then other players' triggers in turn order
    - Within a player's triggers, they choose the order
    """
    triggers: List[QueuedTrigger] = Field(default_factory=list)
    
    def add_trigger(self, trigger: QueuedTrigger):
        """Add a trigger to the queue."""
        self.triggers.append(trigger)
    
    def has_triggers(self) -> bool:
        """Check if there are any pending triggers."""
        return len(self.triggers) > 0
    
    def get_all(self) -> List[QueuedTrigger]:
        """Get all queued triggers in APNAP order."""
        # Sort by APNAP: active player first, then others
        active_triggers = [t for t in self.triggers if t.is_active_player]
        other_triggers = [t for t in self.triggers if not t.is_active_player]
        return active_triggers + other_triggers
    
    def clear(self):
        """Clear all triggers from the queue."""
        self.triggers.clear()
    
    def remove(self, trigger: QueuedTrigger):
        """Remove a specific trigger from the queue."""
        if trigger in self.triggers:
            self.triggers.remove(trigger)
    
    def __len__(self) -> int:
        """Number of queued triggers."""
        return len(self.triggers)


def create_etb_draw_trigger(count: int = 1) -> TriggeredAbility:
    """Helper: Create an ETB trigger that draws cards."""
    return TriggeredAbility(
        trigger_type=TriggerType.ETB,
        effect=TriggerEffect(
            effect_type="draw_card",
            amount=count,
            text=f"draw {count} card{'s' if count > 1 else ''}"
        )
    )


def create_etb_ramp_trigger() -> TriggeredAbility:
    """Helper: Create an ETB trigger that searches for a basic land."""
    return TriggeredAbility(
        trigger_type=TriggerType.ETB,
        effect=TriggerEffect(
            effect_type="ramp",
            amount=1,
            text="search your library for a basic land card, put it onto the battlefield tapped"
        )
    )


def create_dies_draw_trigger(count: int = 1) -> TriggeredAbility:
    """Helper: Create a dies trigger that draws cards."""
    return TriggeredAbility(
        trigger_type=TriggerType.DIES,
        effect=TriggerEffect(
            effect_type="draw_card",
            amount=count,
            text=f"draw {count} card{'s' if count > 1 else ''}"
        )
    )


def create_etb_damage_trigger(damage: int, target: str = "any") -> TriggeredAbility:
    """Helper: Create an ETB trigger that deals damage."""
    target_text = {
        "any": "any target",
        "opponent": "target opponent",
        "creature": "target creature",
        "player": "target player"
    }.get(target, target)
    
    return TriggeredAbility(
        trigger_type=TriggerType.ETB,
        effect=TriggerEffect(
            effect_type="deal_damage",
            amount=damage,
            target_type=target,
            text=f"deal {damage} damage to {target_text}",
            requires_target=True
        )
    )
