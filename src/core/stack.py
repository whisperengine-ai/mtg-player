"""
Stack implementation for MTG.
Handles spell and ability resolution with priority passing.
"""
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class StackObjectType(str, Enum):
    """Type of object on the stack."""
    SPELL = "spell"
    ABILITY = "ability"


class StackObject(BaseModel):
    """Represents an object on the stack."""
    object_id: str
    object_type: StackObjectType
    controller_id: str
    
    # For spells
    card_instance_id: Optional[str] = None
    card_name: Optional[str] = None
    
    # For abilities
    ability_source_id: Optional[str] = None
    ability_text: Optional[str] = None
    
    # Targeting
    targets: List[str] = Field(default_factory=list)
    
    # Metadata
    can_be_countered: bool = True
    is_instant_speed: bool = False
    
    def __str__(self) -> str:
        """String representation."""
        if self.object_type == StackObjectType.SPELL:
            return f"{self.card_name} (spell)"
        else:
            return f"{self.ability_text} (ability)"


class Stack:
    """Manages the stack and priority passing."""
    
    def __init__(self):
        self.objects: List[StackObject] = []
        self.priority_order: List[str] = []  # Player IDs in priority order
        self.current_priority_player_idx: int = 0
        self.passes_in_succession: int = 0
        
    def is_empty(self) -> bool:
        """Check if stack is empty."""
        return len(self.objects) == 0
    
    def size(self) -> int:
        """Get number of objects on stack."""
        return len(self.objects)
    
    def push(self, stack_object: StackObject):
        """Add an object to the stack."""
        self.objects.append(stack_object)
        # Reset priority passes when something is added
        self.passes_in_succession = 0
    
    def pop(self) -> Optional[StackObject]:
        """Remove and return the top object from the stack."""
        if self.is_empty():
            return None
        return self.objects.pop()
    
    def peek(self) -> Optional[StackObject]:
        """Look at the top object without removing it."""
        if self.is_empty():
            return None
        return self.objects[-1]
    
    def get_all(self) -> List[StackObject]:
        """Get all objects on the stack (bottom to top)."""
        return self.objects.copy()
    
    def set_priority_order(self, player_ids: List[str], active_player_id: str):
        """
        Set the priority order starting with the active player.
        In MTG, priority starts with the active player and goes clockwise.
        """
        # Find active player index
        active_idx = player_ids.index(active_player_id)
        
        # Rotate list so active player is first
        self.priority_order = player_ids[active_idx:] + player_ids[:active_idx]
        self.current_priority_player_idx = 0
        self.passes_in_succession = 0
    
    def get_priority_player(self) -> Optional[str]:
        """Get the player who currently has priority."""
        if not self.priority_order:
            return None
        return self.priority_order[self.current_priority_player_idx]
    
    def pass_priority(self) -> bool:
        """
        Pass priority to the next player.
        Returns True if all players have passed and stack should resolve.
        """
        self.passes_in_succession += 1
        self.current_priority_player_idx = (
            (self.current_priority_player_idx + 1) % len(self.priority_order)
        )
        
        # If all players have passed in succession, stack can resolve
        return self.passes_in_succession >= len(self.priority_order)
    
    def reset_priority_after_resolution(self, active_player_id: str):
        """Reset priority to active player after resolving a stack object."""
        if active_player_id in self.priority_order:
            self.current_priority_player_idx = self.priority_order.index(active_player_id)
        self.passes_in_succession = 0
    
    def clear(self):
        """Clear the stack (for cleanup or game reset)."""
        self.objects.clear()
        self.passes_in_succession = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "objects": [
                {
                    "object_id": obj.object_id,
                    "type": obj.object_type.value,
                    "controller": obj.controller_id,
                    "name": obj.card_name or obj.ability_text,
                    "targets": obj.targets
                }
                for obj in self.objects
            ],
            "size": self.size(),
            "priority_player": self.get_priority_player(),
            "passes_in_succession": self.passes_in_succession
        }
    
    def __str__(self) -> str:
        """String representation."""
        if self.is_empty():
            return "Stack: (empty)"
        
        lines = ["Stack (top to bottom):"]
        for i, obj in enumerate(reversed(self.objects)):
            lines.append(f"  {len(self.objects) - i}. {obj}")
        return "\n".join(lines)
