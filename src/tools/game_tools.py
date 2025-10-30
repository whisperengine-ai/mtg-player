"""
Tools for the LLM agent to interact with the game.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class Tool(BaseModel):
    """Base class for a tool."""
    model_config = ConfigDict(arbitrary_types_allowed=True, extra='allow')
    
    name: str
    description: str
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool."""
        raise NotImplementedError


class GetGameStateTool(Tool):
    """Get the current game state."""
    game_state: Optional[Any] = None  # Will be set by agent
    
    def __init__(self, **data):
        super().__init__(
            name="get_game_state",
            description=(
                "Get the current game state including all players, life totals, "
                "battlefield state, turn number, and phase. Use this to understand "
                "the current situation before making decisions."
            ),
            **data
        )
    
    def execute(self) -> Dict[str, Any]:
        """Return game state as dictionary."""
        if not self.game_state:
            return {"error": "Game state not initialized"}
        
        return {
            "success": True,
            "game_state": self.game_state.to_dict()
        }


class GetLegalActionsTool(Tool):
    """Get all legal actions for the active player."""
    game_state: Optional[Any] = None
    rules_engine: Optional[Any] = None
    
    def __init__(self, **data):
        super().__init__(
            name="get_legal_actions",
            description=(
                "Get all legal actions the active player can take right now. "
                "Returns available actions like: play_land, cast_spell, "
                "declare_attackers, activate_ability, pass_priority."
            ),
            **data
        )
    
    def execute(self) -> Dict[str, Any]:
        """Return available actions."""
        if not self.game_state or not self.rules_engine:
            return {"error": "Game not initialized"}
        
        active_player = self.game_state.get_active_player()
        if not active_player:
            return {"error": "No active player"}
        
        actions = []
        step = self.game_state.current_step.value
        
        # Always can pass priority
        actions.append({
            "type": "pass",
            "description": "Pass priority (move to next phase/step)"
        })
        
        # Main phase actions
        if step == "main":
            # Can play lands
            if not active_player.has_played_land_this_turn:
                lands_in_hand = [c for c in active_player.hand if c.card.is_land()]
                for land in lands_in_hand:
                    actions.append({
                        "type": "play_land",
                        "card_id": land.instance_id,
                        "card_name": land.card.name,
                        "description": f"Play land: {land.card.name}"
                    })
            
            # Can cast spells
            available_mana = active_player.available_mana().total()
            castable_spells = [
                c for c in active_player.hand 
                if not c.card.is_land() and c.card.cmc() <= available_mana
            ]
            for spell in castable_spells:
                actions.append({
                    "type": "cast_spell",
                    "card_id": spell.instance_id,
                    "card_name": spell.card.name,
                    "cost": str(spell.card.mana_cost),
                    "card_types": [ct.value for ct in spell.card.card_types],  # Include card types for AI
                    "oracle_text": spell.card.oracle_text or "",  # Include text for AI analysis
                    "power": spell.card.power,  # Include P/T for creatures
                    "toughness": spell.card.toughness,
                    "description": f"Cast {spell.card.name} (cost: {spell.card.mana_cost})"
                })
            
            # Can tap lands for mana
            for land in active_player.untapped_lands():
                actions.append({
                    "type": "tap_land",
                    "card_id": land.instance_id,
                    "card_name": land.card.name,
                    "description": f"Tap {land.card.name} for mana"
                })
        
        # Declare attackers
        if step == "declare_attackers":
            attackers = [c for c in active_player.creatures_in_play() if c.can_attack()]
            if attackers:
                opponents = self.game_state.get_opponents(active_player.id)
                for creature in attackers:
                    for opponent in opponents:
                        actions.append({
                            "type": "declare_attacker",
                            "creature_id": creature.instance_id,
                            "creature_name": creature.card.name,
                            "target_id": opponent.id,
                            "target_name": opponent.name,
                            "power": creature.card.power or 0,  # Include for heuristic
                            "toughness": creature.card.toughness or 0,
                            "description": f"Attack {opponent.name} with {creature.card.name} ({creature.card.power}/{creature.card.toughness})"
                        })
        
        # Declare blockers
        if step == "declare_blockers":
            # Find attacking creatures
            attackers = []
            for opponent in self.game_state.get_opponents(active_player.id):
                attackers.extend([c for c in opponent.creatures_in_play() if c.is_attacking])
            
            blockers = [c for c in active_player.creatures_in_play() if c.can_block()]
            
            for blocker in blockers:
                for attacker in attackers:
                    actions.append({
                        "type": "declare_blocker",
                        "blocker_id": blocker.instance_id,
                        "blocker_name": blocker.card.name,
                        "blocker_power": blocker.card.power or 0,  # Include for heuristic
                        "blocker_toughness": blocker.card.toughness or 0,
                        "attacker_id": attacker.instance_id,
                        "attacker_name": attacker.card.name,
                        "attacker_power": attacker.card.power or 0,
                        "attacker_toughness": attacker.card.toughness or 0,
                        "description": f"Block {attacker.card.name} ({attacker.card.power}/{attacker.card.toughness}) with {blocker.card.name} ({blocker.card.power}/{blocker.card.toughness})"
                    })
        
        return {
            "success": True,
            "actions": actions,
            "count": len(actions)
        }


class ExecuteActionTool(Tool):
    """Execute a game action."""
    game_state: Optional[Any] = None
    rules_engine: Optional[Any] = None
    
    def __init__(self, **data):
        super().__init__(
            name="execute_action",
            description=(
                "Execute a game action. Provide the action type and required parameters. "
                "Actions: pass, play_land, cast_spell, tap_land, declare_attacker, declare_blocker."
            ),
            **data
        )
    
    def execute(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action."""
        if not self.game_state or not self.rules_engine:
            return {"error": "Game not initialized"}
        
        active_player = self.game_state.get_active_player()
        if not active_player:
            return {"error": "No active player"}
        
        action_type = action.get("type")
        if not action_type:
            return {"error": "No action type specified"}
        
        try:
            if action_type == "pass":
                self.rules_engine.advance_phase()
                return {
                    "success": True,
                    "message": "Passed priority, advanced phase"
                }
            
            elif action_type == "play_land":
                card_id = action.get("card_id")
                card = next((c for c in active_player.hand if c.instance_id == card_id), None)
                if not card:
                    return {"error": "Card not found in hand"}
                
                success = self.rules_engine.play_land(active_player, card)
                return {
                    "success": success,
                    "message": f"Played {card.card.name}" if success else "Could not play land"
                }
            
            elif action_type == "tap_land":
                card_id = action.get("card_id")
                land = next((c for c in active_player.battlefield if c.instance_id == card_id), None)
                if not land:
                    return {"error": "Land not found on battlefield"}
                
                success = self.rules_engine.tap_land_for_mana(active_player, land)
                return {
                    "success": success,
                    "message": f"Tapped {land.card.name} for mana" if success else "Could not tap land"
                }
            
            elif action_type == "cast_spell":
                card_id = action.get("card_id")
                card = next((c for c in active_player.hand if c.instance_id == card_id), None)
                if not card:
                    return {"error": "Card not found in hand"}
                
                success = self.rules_engine.cast_spell(active_player, card)
                return {
                    "success": success,
                    "message": f"Cast {card.card.name}" if success else "Could not cast spell"
                }
            
            elif action_type == "declare_attacker":
                creature_id = action.get("creature_id")
                target_id = action.get("target_id")
                
                creature = next(
                    (c for c in active_player.creatures_in_play() if c.instance_id == creature_id),
                    None
                )
                if not creature:
                    return {"error": "Creature not found"}
                
                success = self.rules_engine.declare_attackers(active_player, [(creature, target_id)])
                return {
                    "success": success,
                    "message": f"{creature.card.name} attacks" if success else "Could not declare attacker"
                }
            
            elif action_type == "declare_blocker":
                blocker_id = action.get("blocker_id")
                attacker_id = action.get("attacker_id")
                
                blocker = next(
                    (c for c in active_player.creatures_in_play() if c.instance_id == blocker_id),
                    None
                )
                if not blocker:
                    return {"error": "Blocker not found"}
                
                success = self.rules_engine.declare_blockers(active_player, [(blocker, attacker_id)])
                return {
                    "success": success,
                    "message": f"{blocker.card.name} blocks" if success else "Could not declare blocker"
                }
            
            else:
                return {"error": f"Unknown action type: {action_type}"}
        
        except Exception as e:
            return {"error": f"Error executing action: {str(e)}"}


class AnalyzeThreatsTool(Tool):
    """Analyze threats on the board."""
    game_state: Optional[Any] = None
    
    def __init__(self, **data):
        super().__init__(
            name="analyze_threats",
            description=(
                "Analyze the current threats from opponents. Returns information about "
                "dangerous creatures, board state evaluation, and which opponents pose "
                "the biggest threat."
            ),
            **data
        )
    
    def execute(self) -> Dict[str, Any]:
        """Analyze threats."""
        if not self.game_state:
            return {"error": "Game state not initialized"}
        
        active_player = self.game_state.get_active_player()
        if not active_player:
            return {"error": "No active player"}
        
        threats = []
        opponent_scores = {}
        
        for opponent in self.game_state.get_opponents(active_player.id):
            # Calculate threat score
            score = 0
            
            # Life total (higher life = bigger threat, they're winning)
            score += opponent.life * 0.5
            
            # Creatures and board presence
            creatures = opponent.creatures_in_play()
            total_power = sum(c.current_power() for c in creatures)
            score += total_power * 3  # Combat damage potential
            score += len(creatures) * 2  # Board presence
            
            # Card advantage
            score += len(opponent.hand) * 2  # Cards in hand are resources
            score += len(opponent.battlefield) * 1.5  # Board state
            
            # Commander damage tracking
            commander_damage_to_me = 0
            if opponent.id in active_player.commander_damage:
                commander_damage_to_me = active_player.commander_damage[opponent.id]
                score += commander_damage_to_me * 5  # Approaching 21 is very dangerous
            
            # Check if opponent's commander is on battlefield
            has_commander = any(c.card.is_commander for c in creatures)
            if has_commander:
                score += 10  # Commander on field is a threat
            
            opponent_scores[opponent.id] = {
                "player_name": opponent.name,
                "player_id": opponent.id,
                "threat_score": round(score, 1),
                "life": opponent.life,
                "creatures": len(creatures),
                "total_power": total_power,
                "hand_size": len(opponent.hand),
                "battlefield_size": len(opponent.battlefield),
                "commander_damage_to_me": commander_damage_to_me,
                "has_commander_out": has_commander,
                "is_winning": opponent.life >= 35 and total_power >= 10  # Heuristic
            }
            
            # Identify specific threats
            for creature in creatures:
                threat_level = "medium"
                reason = []
                
                if creature.card.is_commander:
                    threat_level = "high"
                    reason.append("Commander")
                
                if creature.current_power() >= 5:
                    threat_level = "high"
                    reason.append(f"High power ({creature.current_power()})")
                elif creature.current_power() >= 3:
                    threat_level = "medium"
                    reason.append(f"Moderate power ({creature.current_power()})")
                
                if creature.current_toughness() >= 5:
                    reason.append("Hard to kill")
                
                if reason:
                    threats.append({
                        "type": "creature",
                        "name": creature.card.name,
                        "power": creature.current_power(),
                        "toughness": creature.current_toughness(),
                        "controller": opponent.name,
                        "controller_id": opponent.id,
                        "threat_level": threat_level,
                        "is_commander": creature.card.is_commander,
                        "reason": ", ".join(reason)
                    })
            
            # Check for commander damage threats (approaching lethal)
            if commander_damage_to_me >= 15:
                threats.append({
                    "type": "commander_damage",
                    "name": f"{opponent.name}'s Commander",
                    "controller": opponent.name,
                    "controller_id": opponent.id,
                    "threat_level": "critical",
                    "commander_damage": commander_damage_to_me,
                    "reason": f"Commander damage at {commander_damage_to_me}/21 - LETHAL RANGE!"
                })
        
        # Sort opponents by threat score
        sorted_opponents = sorted(
            opponent_scores.items(),
            key=lambda x: x[1]["threat_score"],
            reverse=True
        )
        
        # Determine political recommendations
        biggest_threat_id = sorted_opponents[0][0] if sorted_opponents else None
        political_advice = self._generate_political_advice(
            active_player,
            opponent_scores,
            biggest_threat_id
        )
        
        return {
            "success": True,
            "threats": threats,
            "opponent_analysis": dict(sorted_opponents),
            "biggest_threat": sorted_opponents[0][1]["player_name"] if sorted_opponents else None,
            "biggest_threat_id": biggest_threat_id,
            "political_advice": political_advice,
            "my_commander_damage": {
                opponent_id: damage 
                for opponent_id, damage in active_player.commander_damage.items()
            }
        }
    
    def _generate_political_advice(
        self,
        active_player: Any,
        opponent_scores: Dict[str, Dict],
        biggest_threat_id: Optional[str]
    ) -> str:
        """Generate political advice for multiplayer."""
        if not opponent_scores:
            return "No opponents remaining."
        
        if len(opponent_scores) == 1:
            return "Only one opponent left - focus on winning!"
        
        sorted_opponents = sorted(
            opponent_scores.items(),
            key=lambda x: x[1]["threat_score"],
            reverse=True
        )
        
        biggest_threat = sorted_opponents[0][1]
        weakest_player = sorted_opponents[-1][1]
        
        advice = []
        
        if biggest_threat["threat_score"] > weakest_player["threat_score"] * 2:
            advice.append(
                f"⚠️ {biggest_threat['player_name']} is pulling ahead "
                f"(threat score: {biggest_threat['threat_score']}). "
                f"Consider focusing attacks/removal on them."
            )
        
        if biggest_threat["commander_damage_to_me"] >= 15:
            advice.append(
                f"🚨 DANGER: {biggest_threat['player_name']}'s commander has dealt "
                f"{biggest_threat['commander_damage_to_me']}/21 damage to you! Priority target!"
            )
        
        if biggest_threat["is_winning"]:
            advice.append(
                f"💪 {biggest_threat['player_name']} is in a strong position. "
                f"May need to form temporary alliances to stop them."
            )
        
        if weakest_player["life"] <= 10:
            advice.append(
                f"🎯 {weakest_player['player_name']} is low on life ({weakest_player['life']}). "
                f"Could be eliminated soon, but watch for kingmaker scenarios."
            )
        
        return " ".join(advice) if advice else "Balanced board state - proceed carefully."


class GetStackStateTool(Tool):
    """Get the current state of the stack."""
    game_state: Optional[Any] = None
    rules_engine: Optional[Any] = None
    
    def __init__(self, **data):
        super().__init__(
            name="get_stack_state",
            description=(
                "Get the current state of the stack. Shows all spells and abilities "
                "on the stack (in order), who has priority, and whether you can respond. "
                "Use this when deciding whether to cast an instant or respond to an opponent's spell."
            ),
            **data
        )
    
    def execute(self) -> Dict[str, Any]:
        """Return stack state."""
        if not self.game_state or not self.rules_engine:
            return {"error": "Game not initialized"}
        
        stack = self.rules_engine.stack
        active_player = self.game_state.get_active_player()
        priority_player_id = stack.get_priority_player()
        priority_player = self.game_state.get_player(priority_player_id) if priority_player_id else None
        
        # Get stack objects
        stack_objects = []
        for obj in stack.get_all():
            stack_objects.append({
                "name": obj.card_name or obj.ability_text,
                "type": obj.object_type.value,
                "controller": self.game_state.get_player(obj.controller_id).name if obj.controller_id else "Unknown",
                "controller_id": obj.controller_id,
                "targets": obj.targets,
                "can_be_countered": obj.can_be_countered
            })
        
        return {
            "success": True,
            "stack_size": stack.size(),
            "is_empty": stack.is_empty(),
            "objects": stack_objects,  # Bottom to top
            "top_object": stack_objects[-1] if stack_objects else None,
            "priority_player": priority_player.name if priority_player else None,
            "priority_player_id": priority_player_id,
            "you_have_priority": active_player and priority_player_id == active_player.id,
            "passes_in_succession": stack.passes_in_succession
        }


class CanRespondTool(Tool):
    """Check if the active player can respond with an instant."""
    game_state: Optional[Any] = None
    rules_engine: Optional[Any] = None
    
    def __init__(self, **data):
        super().__init__(
            name="can_respond",
            description=(
                "Check if you can respond to spells on the stack by casting an instant. "
                "Returns whether you have priority, what instants you can cast, and what's on the stack. "
                "Use this before deciding to cast an instant or pass priority."
            ),
            **data
        )
    
    def execute(self) -> Dict[str, Any]:
        """Check if can respond."""
        if not self.game_state or not self.rules_engine:
            return {"error": "Game not initialized"}
        
        active_player = self.game_state.get_active_player()
        if not active_player:
            return {"error": "No active player"}
        
        stack = self.rules_engine.stack
        priority_player_id = stack.get_priority_player()
        has_priority = priority_player_id == active_player.id
        
        # Find castable instants in hand
        available_mana = active_player.available_mana().total()
        castable_instants = [
            {
                "card_id": c.instance_id,
                "card_name": c.card.name,
                "cost": str(c.card.mana_cost),
                "cmc": c.card.cmc(),
                "effect": c.card.oracle_text
            }
            for c in active_player.hand 
            if c.card.is_instant() and c.card.cmc() <= available_mana
        ]
        
        # Get top of stack
        top_spell = None
        if not stack.is_empty():
            top_obj = stack.peek()
            if top_obj:
                top_spell = {
                    "name": top_obj.card_name or top_obj.ability_text,
                    "controller": self.game_state.get_player(top_obj.controller_id).name if top_obj.controller_id else "Unknown",
                    "can_counter": top_obj.can_be_countered
                }
        
        return {
            "success": True,
            "has_priority": has_priority,
            "can_respond": has_priority and len(castable_instants) > 0,
            "castable_instants": castable_instants,
            "available_mana": available_mana,
            "stack_size": stack.size(),
            "top_of_stack": top_spell,
            "recommendation": self._generate_recommendation(
                has_priority,
                castable_instants,
                top_spell,
                stack.size()
            )
        }
    
    def _generate_recommendation(
        self,
        has_priority: bool,
        castable_instants: List[Dict],
        top_spell: Optional[Dict],
        stack_size: int
    ) -> str:
        """Generate advice about responding."""
        if not has_priority:
            return "You don't have priority. Wait for priority to pass back to you."
        
        if stack_size == 0:
            return "Stack is empty. No need to respond, but you can cast instants during your turn."
        
        if not castable_instants:
            return f"Stack has {stack_size} object(s), but you have no castable instants. Consider passing priority."
        
        if top_spell:
            if "counter" in [inst["card_name"].lower() for inst in castable_instants]:
                if top_spell.get("can_counter", True):
                    return f"⚠️ {top_spell['name']} is on the stack. You have counterspells available!"
                else:
                    return f"{top_spell['name']} cannot be countered. Consider other responses."
            
            return f"{top_spell['name']} is on the stack. You have {len(castable_instants)} instant(s) you could cast in response."
        
        return f"You have {len(castable_instants)} castable instant(s) and priority."

