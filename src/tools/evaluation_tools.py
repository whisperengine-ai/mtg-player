"""
Position evaluation tools for MTG Commander AI.

Provides scoring functions to evaluate game state quality.
"""
from typing import Dict, Any, Optional, List


class EvaluatePositionTool:
    """Evaluate the current position and return a score from 0.0 (losing badly) to 1.0 (winning)."""
    
    def __init__(self):
        self.game_state: Optional[Any] = None  # Will be set by agent
    
    def get_schema(self) -> Dict[str, Any]:
        """Return tool schema for LLM."""
        return {
            "type": "function",
            "function": {
                "name": "evaluate_position",
                "description": "Evaluate the current game position and return a score from 0.0 (losing badly) to 1.0 (winning strongly). Considers life totals, board state, mana, and card advantage. Use this to compare potential moves and make strategic decisions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "player_id": {
                            "type": "string",
                            "description": "ID of the player to evaluate position for (optional, defaults to active player)"
                        }
                    },
                    "required": []
                }
            }
        }
    
    def execute(self, player_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate position for a player.
        
        Args:
            player_id: ID of player to evaluate (defaults to active player)
            
        Returns:
            Dictionary with:
            - score: 0.0-1.0 (0.0 = losing badly, 0.5 = even, 1.0 = winning)
            - breakdown: component scores
            - summary: text explanation
        """
        if not self.game_state:
            return {"error": "Game state not available"}
        
        # Get player to evaluate
        if player_id:
            player = next((p for p in self.game_state.players if p.id == player_id), None)
            if not player:
                return {"error": f"Player {player_id} not found"}
        else:
            player = self.game_state.get_active_player()
            if not player:
                return {"error": "No active player"}
        
        # Calculate component scores
        life_score = self._evaluate_life(player)
        board_score = self._evaluate_board(player)
        mana_score = self._evaluate_mana(player)
        card_advantage_score = self._evaluate_card_advantage(player)
        threat_score = self._evaluate_threats(player)
        
        # Weighted average (adjust weights based on game phase)
        weights = {
            "life": 0.25,
            "board": 0.30,
            "mana": 0.15,
            "cards": 0.15,
            "threats": 0.15
        }
        
        overall_score = (
            life_score * weights["life"] +
            board_score * weights["board"] +
            mana_score * weights["mana"] +
            card_advantage_score * weights["cards"] +
            threat_score * weights["threats"]
        )
        
        # Clamp to 0.0-1.0
        overall_score = max(0.0, min(1.0, overall_score))
        
        # Generate summary
        if overall_score >= 0.7:
            position = "winning strongly"
        elif overall_score >= 0.55:
            position = "slightly ahead"
        elif overall_score >= 0.45:
            position = "roughly even"
        elif overall_score >= 0.3:
            position = "slightly behind"
        else:
            position = "losing badly"
        
        return {
            "success": True,
            "player_id": player.id,
            "player_name": player.name,
            "score": round(overall_score, 3),
            "position": position,
            "breakdown": {
                "life": round(life_score, 3),
                "board": round(board_score, 3),
                "mana": round(mana_score, 3),
                "card_advantage": round(card_advantage_score, 3),
                "threats": round(threat_score, 3)
            },
            "summary": self._generate_summary(player, overall_score, {
                "life": life_score,
                "board": board_score,
                "mana": mana_score,
                "cards": card_advantage_score,
                "threats": threat_score
            })
        }
    
    def _evaluate_life(self, player: Any) -> float:
        """
        Evaluate life total position.
        
        In Commander, life matters less until you're low.
        Score based on relative life compared to average.
        """
        # Get average opponent life
        opponents = [p for p in self.game_state.players if p.id != player.id and p.life > 0]
        if not opponents:
            return 1.0  # Only player alive
        
        avg_opponent_life = sum(p.life for p in opponents) / len(opponents)
        
        # Score based on relative position
        if player.life <= 0:
            return 0.0
        elif player.life <= 10:
            return 0.2  # Critical danger
        elif player.life <= 20:
            return 0.4  # Danger zone
        elif player.life <= 30:
            return 0.5 + (player.life - 20) / 20 * 0.2  # 0.5-0.7
        else:
            # Compare to average
            if player.life >= avg_opponent_life:
                return 0.7 + min(0.3, (player.life - avg_opponent_life) / 40)
            else:
                return 0.5 + (player.life - avg_opponent_life) / 40 * 0.2
    
    def _evaluate_board(self, player: Any) -> float:
        """
        Evaluate board presence.
        
        Considers creatures, power/toughness, and permanents.
        """
        # Get player's creatures
        creatures = player.creatures_in_play()
        
        # Get opponent creatures
        opponent_creatures = []
        for p in self.game_state.players:
            if p.id != player.id and p.life > 0:
                opponent_creatures.extend(p.creatures_in_play())
        
        # No creatures on either side
        if not creatures and not opponent_creatures:
            return 0.5
        
        # Calculate power/toughness
        player_power = sum(c.card.power or 0 for c in creatures)
        player_toughness = sum(c.card.toughness or 0 for c in creatures)
        
        opponent_power = sum(c.card.power or 0 for c in opponent_creatures)
        opponent_toughness = sum(c.card.toughness or 0 for c in opponent_creatures)
        
        # Calculate board score
        creature_count_ratio = len(creatures) / max(1, len(creatures) + len(opponent_creatures))
        power_ratio = player_power / max(1, player_power + opponent_power)
        
        # Weight towards having creatures
        board_score = 0.5 + (creature_count_ratio - 0.5) * 0.6 + (power_ratio - 0.5) * 0.4
        
        return max(0.0, min(1.0, board_score))
    
    def _evaluate_mana(self, player: Any) -> float:
        """
        Evaluate mana position.
        
        More lands = more options. Critical in early game.
        """
        # Count lands on battlefield
        lands = [p for p in player.battlefield if any(ct.value == 'land' for ct in p.card.card_types)]
        land_count = len(lands)
        
        # Get average opponent lands
        opponent_lands = []
        for p in self.game_state.players:
            if p.id != player.id and p.life > 0:
                opp_lands = [perm for perm in p.battlefield if any(ct.value == 'land' for ct in perm.card.card_types)]
                opponent_lands.append(len(opp_lands))
        
        avg_opponent_lands = sum(opponent_lands) / max(1, len(opponent_lands))
        
        # Score based on land count and relative position
        if land_count == 0:
            return 0.1  # Very bad
        elif land_count <= 2:
            return 0.3
        elif land_count <= 4:
            return 0.5
        else:
            # Compare to opponents
            if land_count >= avg_opponent_lands:
                return 0.7 + min(0.3, (land_count - avg_opponent_lands) / 10)
            else:
                return 0.5 + (land_count - avg_opponent_lands) / 10 * 0.2
    
    def _evaluate_card_advantage(self, player: Any) -> float:
        """
        Evaluate card advantage.
        
        Hand size matters - more cards = more options.
        """
        hand_size = len(player.hand)
        
        # Get average opponent hand size
        opponent_hand_sizes = [len(p.hand) for p in self.game_state.players if p.id != player.id and p.life > 0]
        avg_opponent_hand = sum(opponent_hand_sizes) / max(1, len(opponent_hand_sizes))
        
        # Score based on hand size
        if hand_size == 0:
            return 0.2  # Topdecking is bad
        elif hand_size <= 2:
            return 0.4
        elif hand_size >= 7:
            return 0.8  # Good position
        else:
            # Compare to opponents
            if hand_size >= avg_opponent_hand:
                return 0.6 + min(0.4, (hand_size - avg_opponent_hand) / 5)
            else:
                return 0.5 + (hand_size - avg_opponent_hand) / 5 * 0.2
    
    def _evaluate_threats(self, player: Any) -> float:
        """
        Evaluate immediate threats from opponents.
        
        Lower score = more threats to worry about.
        """
        max_opponent_power = 0
        opponent_creature_count = 0
        
        for p in self.game_state.players:
            if p.id != player.id and p.life > 0:
                creatures = p.creatures_in_play()
                opponent_creature_count += len(creatures)
                total_power = sum(c.card.power or 0 for c in creatures)
                max_opponent_power = max(max_opponent_power, total_power)
        
        # If opponent can kill us next turn, score low
        if max_opponent_power >= player.life:
            return 0.1  # Lethal threat
        elif max_opponent_power >= player.life * 0.5:
            return 0.3  # Serious threat
        elif opponent_creature_count == 0:
            return 0.9  # No immediate threats
        else:
            # Scale based on threat level
            threat_ratio = max_opponent_power / max(1, player.life)
            return max(0.5, 1.0 - threat_ratio)
    
    def _generate_summary(self, player: Any, overall_score: float, breakdown: Dict[str, float]) -> str:
        """Generate human-readable summary of position."""
        strengths = []
        weaknesses = []
        
        if breakdown["life"] >= 0.7:
            strengths.append("healthy life total")
        elif breakdown["life"] <= 0.3:
            weaknesses.append("low life")
        
        if breakdown["board"] >= 0.7:
            strengths.append("strong board presence")
        elif breakdown["board"] <= 0.3:
            weaknesses.append("weak board")
        
        if breakdown["mana"] >= 0.7:
            strengths.append("good mana base")
        elif breakdown["mana"] <= 0.3:
            weaknesses.append("mana-screwed")
        
        if breakdown["cards"] >= 0.7:
            strengths.append("card advantage")
        elif breakdown["cards"] <= 0.3:
            weaknesses.append("low cards")
        
        if breakdown["threats"] <= 0.3:
            weaknesses.append("facing lethal threats")
        
        summary_parts = []
        
        if overall_score >= 0.7:
            summary_parts.append(f"You are in a strong position (score: {overall_score:.2f}).")
        elif overall_score >= 0.55:
            summary_parts.append(f"You are slightly ahead (score: {overall_score:.2f}).")
        elif overall_score >= 0.45:
            summary_parts.append(f"The game is roughly even (score: {overall_score:.2f}).")
        elif overall_score >= 0.3:
            summary_parts.append(f"You are slightly behind (score: {overall_score:.2f}).")
        else:
            summary_parts.append(f"You are in a difficult position (score: {overall_score:.2f}).")
        
        if strengths:
            summary_parts.append(f"Strengths: {', '.join(strengths)}.")
        
        if weaknesses:
            summary_parts.append(f"Weaknesses: {', '.join(weaknesses)}.")
        
        return " ".join(summary_parts)


class CanIWinTool:
    """Analyze if the active player can achieve lethal this turn."""
    
    def __init__(self):
        self.game_state: Optional[Any] = None  # Will be set by agent
    
    def get_schema(self) -> Dict[str, Any]:
        """Return tool schema for LLM."""
        return {
            "type": "function",
            "function": {
                "name": "can_i_win",
                "description": "Analyze if you can deal lethal damage this turn. Calculates total damage from attacking creatures and instant-speed spells in hand. Returns whether lethal is possible, total damage potential, and the attack line.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "player_id": {
                            "type": "string",
                            "description": "ID of the player to check (optional, defaults to active player)"
                        }
                    },
                    "required": []
                }
            }
        }
    
    def execute(self, player_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if player can deal lethal damage this turn.
        
        Args:
            player_id: ID of player to evaluate (defaults to active player)
            
        Returns:
            Dictionary with:
            - can_win: True/False
            - damage: Total damage potential
            - life_needed: Opponent life to reach lethal
            - line: Attack/spell sequence to reach lethal
            - considerations: Warnings or notes
        """
        if not self.game_state:
            return {"error": "Game state not available"}
        
        # Get player to evaluate
        if player_id:
            player = next((p for p in self.game_state.players if p.id == player_id), None)
            if not player:
                return {"error": f"Player {player_id} not found"}
        else:
            player = self.game_state.get_active_player()
            if not player:
                return {"error": "No active player"}
        
        # Get all opponents
        opponents = [p for p in self.game_state.players if p.id != player.id and p.life > 0]
        if not opponents:
            return {
                "success": True,
                "can_win": False,
                "damage": 0,
                "reason": "No opponents to attack"
            }
        
        # Calculate damage sources
        creature_damage = self._calculate_creature_damage(player)
        spell_damage = self._calculate_spell_damage(player)
        total_damage = creature_damage["damage"] + spell_damage["damage"]
        
        # Check each opponent for lethal
        # Find all possible lethal targets, then pick the one that makes most sense
        # (weakest opponent = highest priority target in multiplayer)
        lethal_targets = []
        for opponent in opponents:
            if total_damage >= opponent.life:
                lethal_targets.append(opponent)
        
        # Sort by life total (lowest life = weakest opponent = best target)
        lethal_targets.sort(key=lambda p: p.life)
        lethal_target = lethal_targets[0] if lethal_targets else None
        
        # Build line description
        line_parts = []
        if creature_damage["damage"] > 0:
            line_parts.append(f"Attack with {creature_damage['count']} creatures ({creature_damage['damage']} damage)")
        if spell_damage["damage"] > 0:
            line_parts.append(f"Cast {spell_damage['count']} spells ({spell_damage['damage']} damage)")
        
        line = " + ".join(line_parts) if line_parts else "No damage sources available"
        
        # Generate considerations
        considerations = []
        if not self._are_all_creatures_ready(player):
            considerations.append("Not all creatures are ready to attack (check summoning sickness)")
        
        if spell_damage["damage"] > 0:
            available_mana = player.available_mana().total()
            if spell_damage["min_mana_needed"] > available_mana:
                considerations.append(f"Not enough mana for all damage spells (need {spell_damage['min_mana_needed']}, have {available_mana})")
        
        return {
            "success": True,
            "player_id": player.id,
            "player_name": player.name,
            "can_win": lethal_target is not None,
            "lethal_target": lethal_target.name if lethal_target else None,
            "damage": total_damage,
            "damage_breakdown": {
                "creatures": creature_damage["damage"],
                "spells": spell_damage["damage"]
            },
            "line": line,
            "creatures_attacking": creature_damage["count"],
            "spells_to_cast": spell_damage["count"],
            "considerations": considerations,
            "summary": self._generate_summary(lethal_target, total_damage, line)
        }
    
    def _calculate_creature_damage(self, player: Any) -> Dict[str, Any]:
        """
        Calculate maximum damage from creatures that can attack.
        
        Returns:
            dict with 'damage', 'count', and 'creatures' list
        """
        total_damage = 0
        count = 0
        creatures = []
        
        for creature in player.creatures_in_play():
            # Check if creature can attack
            if not creature.can_attack():
                continue
            
            power = creature.current_power()
            if power > 0:
                total_damage += power
                count += 1
                creatures.append({
                    "name": creature.card.name,
                    "power": power
                })
        
        return {
            "damage": total_damage,
            "count": count,
            "creatures": creatures
        }
    
    def _calculate_spell_damage(self, player: Any) -> Dict[str, Any]:
        """
        Calculate maximum damage from spells in hand.
        
        Looks for damage spells that can be cast instantly or are sorceries.
        Returns damage from direct damage spells.
        
        Returns:
            dict with 'damage', 'count', 'min_mana_needed', and 'spells' list
        """
        total_damage = 0
        count = 0
        min_mana_needed = 0
        spells = []
        
        available_mana = player.available_mana().total()
        
        for spell in player.hand:
            card = spell.card
            
            # Skip lands
            if card.is_land():
                continue
            
            # Look for damage-dealing spells
            damage = self._extract_damage_from_card(card)
            
            if damage > 0:
                mana_cost = card.mana_cost.total()
                
                # Only include if we might be able to afford it
                if mana_cost <= available_mana:
                    total_damage += damage
                    min_mana_needed += mana_cost
                    count += 1
                    spells.append({
                        "name": card.name,
                        "damage": damage,
                        "cost": mana_cost
                    })
        
        return {
            "damage": total_damage,
            "count": count,
            "min_mana_needed": min_mana_needed,
            "spells": spells
        }
    
    def _extract_damage_from_card(self, card: Any) -> int:
        """
        Extract direct damage value from card text.
        
        Looks for common damage patterns:
        - "Lightning Bolt" → 3
        - "deals 5 damage" → 5
        - "target opponent loses X life" → X (approximate)
        """
        oracle_text = card.oracle_text.lower()
        
        # Common damage spells
        if "lightning bolt" in card.name.lower():
            return 3
        if "shock" in card.name.lower():
            return 2
        if "fireball" in card.name.lower():
            return 5  # Variable, assume 5 for lethal check
        
        # Look for "deals X damage" pattern
        import re
        
        # Match "deals X damage"
        match = re.search(r'deals (\d+) damage', oracle_text)
        if match:
            return int(match.group(1))
        
        # Match "target opponent loses X life"
        match = re.search(r'target opponent loses (\d+) life', oracle_text)
        if match:
            return int(match.group(1))
        
        # Match variable damage (X in the cost)
        if "damage to" in oracle_text or "damage equal to" in oracle_text:
            # Conservative estimate - these need analysis
            return 0
        
        return 0
    
    def _are_all_creatures_ready(self, player: Any) -> bool:
        """Check if all attacking creatures are ready (not summoning sick, not tapped)."""
        for creature in player.creatures_in_play():
            if creature.can_attack():
                return True
        return False
    
    def _generate_summary(self, lethal_target: Any, damage: int, line: str) -> str:
        """Generate human-readable summary."""
        if lethal_target:
            return (
                f"YES! You can win this turn! Deal {damage} damage to {lethal_target.name} "
                f"(they have {lethal_target.life} life). {line}"
            )
        else:
            return (
                f"You cannot reach lethal this turn. Maximum damage available: {damage}. "
                f"{line}"
            )


class StrategyRecommendationTool:
    """Recommend strategic approach based on game position."""
    
    def __init__(self):
        self.game_state: Optional[Any] = None  # Will be set by agent
    
    def get_schema(self) -> Dict[str, Any]:
        """Return tool schema for LLM."""
        return {
            "type": "function",
            "function": {
                "name": "recommend_strategy",
                "description": "Analyze the current game state and recommend a strategic approach. Returns one of: RAMP (accelerate resources), DEFEND (stabilize board), ATTACK (aggressive creatures), or CLOSE (finish game). Includes reasoning and action priorities.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "player_id": {
                            "type": "string",
                            "description": "ID of the player to recommend strategy for (optional, defaults to active player)"
                        }
                    },
                    "required": []
                }
            }
        }
    
    def execute(self, player_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Recommend a strategic approach.
        
        Args:
            player_id: ID of player to recommend for (defaults to active player)
            
        Returns:
            Dictionary with:
            - strategy: RAMP, DEFEND, ATTACK, or CLOSE
            - confidence: 0.0-1.0 confidence in this recommendation
            - reasoning: Explanation of why this strategy
            - priorities: List of action priorities for this turn
            - game_phase: Current phase analysis
        """
        if not self.game_state:
            return {"error": "Game state not available"}
        
        # Get player to evaluate
        if player_id:
            player = next((p for p in self.game_state.players if p.id == player_id), None)
            if not player:
                return {"error": f"Player {player_id} not found"}
        else:
            player = self.game_state.get_active_player()
            if not player:
                return {"error": "No active player"}
        
        # Evaluate position
        position_score = self._evaluate_position(player)
        board_presence = self._evaluate_board_presence(player)
        mana_resources = self._evaluate_resources(player)
        threats = self._evaluate_threats(player)
        card_advantage = self._evaluate_hand_size(player)
        
        # Determine strategy
        strategy, confidence = self._determine_strategy(
            position_score,
            board_presence,
            mana_resources,
            threats,
            card_advantage
        )
        
        # Get priorities for this strategy
        priorities = self._get_priorities(strategy, threats)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            strategy,
            position_score,
            board_presence,
            mana_resources,
            threats
        )
        
        return {
            "success": True,
            "player_id": player.id,
            "player_name": player.name,
            "strategy": strategy,
            "confidence": round(confidence, 2),
            "reasoning": reasoning,
            "priorities": priorities,
            "game_phase": f"{self.game_state.current_phase.value}",
            "position_score": round(position_score, 2),
            "board_presence": board_presence,
            "resources": mana_resources,
            "threats_detected": threats,
            "hand_size": len(player.hand),
            "summary": self._generate_summary(strategy, reasoning)
        }
    
    def _evaluate_position(self, player: Any) -> float:
        """Evaluate relative game position (0.0-1.0)."""
        opponents = [p for p in self.game_state.players if p.id != player.id and p.life > 0]
        if not opponents:
            return 1.0
        
        if player.life <= 0:
            return 0.0
        elif player.life <= 10:
            return 0.2
        elif player.life <= 20:
            return 0.4
        else:
            avg_opponent_life = sum(p.life for p in opponents) / len(opponents)
            if player.life >= avg_opponent_life:
                return 0.7
            else:
                return 0.5
    
    def _evaluate_board_presence(self, player: Any) -> Dict[str, int]:
        """Evaluate board state."""
        creatures = player.creatures_in_play()
        lands = player.lands_in_play()
        total_power = sum(c.current_power() for c in creatures if c.current_power() > 0)
        
        return {
            "creatures": len(creatures),
            "total_power": total_power,
            "lands": len(lands),
            "untapped_lands": len(player.untapped_lands())
        }
    
    def _evaluate_resources(self, player: Any) -> Dict[str, int]:
        """Evaluate available mana resources."""
        available_mana = player.available_mana()
        
        return {
            "total_mana": available_mana.total(),
            "mana_colors": {
                "white": available_mana.white,
                "blue": available_mana.blue,
                "black": available_mana.black,
                "red": available_mana.red,
                "green": available_mana.green,
                "colorless": available_mana.colorless
            }
        }
    
    def _evaluate_threats(self, player: Any) -> int:
        """Count threatening opponent creatures."""
        opponents = [p for p in self.game_state.players if p.id != player.id and p.life > 0]
        
        threat_count = 0
        for opponent in opponents:
            for creature in opponent.creatures_in_play():
                # Consider creature threatening if power >= 2 or has evasion
                power = creature.current_power()
                if power >= 2 or "flying" in creature.card.keywords or "unblockable" in creature.card.keywords:
                    threat_count += 1
        
        return threat_count
    
    def _evaluate_hand_size(self, player: Any) -> int:
        """Evaluate card advantage."""
        return len(player.hand)
    
    def _determine_strategy(
        self,
        position_score: float,
        board_presence: Dict[str, int],
        mana_resources: Dict[str, Any],
        threats: int,
        card_advantage: int = 0  # Currently unused, for future enhancement
    ) -> tuple:
        """
        Determine best strategy based on game state.
        
        Returns: (strategy_name, confidence)
        """
        position = position_score
        creatures = board_presence["creatures"]
        total_power = board_presence["total_power"]
        lands = board_presence["lands"]
        mana_available = mana_resources["total_mana"]
        
        # Winning position + have power → CLOSE
        if position >= 0.7 and total_power >= 6:
            return ("CLOSE", 0.9)
        
        # Have lethal threat on board + good position → ATTACK
        if position >= 0.6 and total_power >= 8 and creatures >= 2:
            return ("ATTACK", 0.85)
        
        # Under threat, need stabilization → DEFEND
        if position <= 0.3 and threats >= 3:
            return ("DEFEND", 0.9)
        
        if position <= 0.4 and threats >= 2:
            return ("DEFEND", 0.8)
        
        # Behind on board but have resources → RAMP
        if creatures <= 1 and mana_available <= 3 and lands <= 2:
            return ("RAMP", 0.85)
        
        # Low resources despite board → RAMP
        if mana_available <= 2:
            return ("RAMP", 0.75)
        
        # Balanced position with reasonable board → ATTACK
        if position >= 0.45 and creatures >= 2 and total_power >= 4:
            return ("ATTACK", 0.7)
        
        # Default based on position
        if position >= 0.6:
            return ("ATTACK", 0.65)
        elif position >= 0.45:
            return ("RAMP", 0.6)
        elif position >= 0.3:
            return ("DEFEND", 0.65)
        else:
            return ("DEFEND", 0.7)
    
    def _get_priorities(self, strategy: str, threats: int) -> List[str]:
        """Get prioritized actions for this turn."""
        priorities = []
        
        if strategy == "RAMP":
            priorities.extend([
                "Play land to accelerate mana",
                "Cast mana dorks or ramp spells",
                "Build toward key spells",
                "Avoid unnecessary trades"
            ])
        
        elif strategy == "DEFEND":
            priorities.extend([
                "Remove or block the biggest threat",
                "Trade creatures favorably if possible",
                "Gain life if available",
                "Hold interaction (removal/instants) in hand"
            ])
            if threats > 3:
                priorities.insert(0, "Stabilize the board immediately")
        
        elif strategy == "ATTACK":
            priorities.extend([
                "Attack with all creatures that can deal damage",
                "Play creatures to increase board presence",
                "Deal damage and put pressure on opponents",
                "Look for opening to close game"
            ])
        
        elif strategy == "CLOSE":
            priorities.extend([
                "Execute the plan for lethal",
                "Use remaining spells to protect creatures",
                "Attack to deal final damage",
                "Hold responses for opponent interaction"
            ])
        
        return priorities
    
    def _generate_reasoning(
        self,
        strategy: str,
        position: float,
        board: Dict[str, int],
        resources: Dict[str, Any],
        threats: int
    ) -> str:
        """Generate explanation for strategy recommendation."""
        parts = []
        
        # Position assessment
        if position >= 0.7:
            parts.append("You have a winning position")
        elif position >= 0.55:
            parts.append("You're slightly ahead")
        elif position >= 0.45:
            parts.append("The game is roughly even")
        elif position >= 0.3:
            parts.append("You're slightly behind")
        else:
            parts.append("You're in danger - need to stabilize")
        
        # Board assessment
        if board["creatures"] == 0:
            parts.append("with no creatures on board")
        elif board["total_power"] >= 10:
            parts.append(f"with a strong board ({board['creatures']} creatures, {board['total_power']} power)")
        elif board["creatures"] >= 3:
            parts.append(f"with a decent board ({board['creatures']} creatures, {board['total_power']} power)")
        
        # Threat assessment
        if threats >= 3:
            parts.append(f"while facing {threats} threats")
        elif threats >= 1:
            parts.append("while facing some threats")
        
        # Resource assessment
        mana = resources["total_mana"]
        if mana <= 2:
            parts.append("with limited mana available")
        elif mana >= 6:
            parts.append("with abundant resources")
        
        # Strategy specific
        if strategy == "CLOSE":
            parts.append(". You should finish the game this turn.")
        elif strategy == "ATTACK":
            parts.append(". Press your advantage with creatures.")
        elif strategy == "DEFEND":
            parts.append(". Stabilize and survive.")
        elif strategy == "RAMP":
            parts.append(". Build resources for future turns.")
        
        return " ".join(parts)
    
    def _generate_summary(self, strategy: str, reasoning: str) -> str:
        """Generate concise summary."""
        strategy_emoji = {
            "RAMP": "📈",
            "DEFEND": "🛡️",
            "ATTACK": "⚔️",
            "CLOSE": "🏁"
        }
        emoji = strategy_emoji.get(strategy, "🎯")
        
        return f"{emoji} **{strategy}** - {reasoning}"


class OpponentModelingTool:
    """Model opponent deck archetype and identify threats."""
    
    def __init__(self):
        self.game_state: Optional[Any] = None  # Will be set by agent
    
    def get_schema(self) -> Dict[str, Any]:
        """Return tool schema for LLM."""
        return {
            "type": "function",
            "function": {
                "name": "analyze_opponent",
                "description": "Analyze opponent deck composition and identify threats. Returns archetype (aggro/control/combo/midrange), threat level (0.0-1.0), and biggest threat card. Use to understand opponent strategy and plan accordingly.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "opponent_id": {
                            "type": "string",
                            "description": "ID of opponent to analyze (optional, analyzes all if not specified)"
                        }
                    },
                    "required": []
                }
            }
        }
    
    def execute(self, opponent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze opponent(s) deck composition and identify threats.
        
        Args:
            opponent_id: ID of specific opponent (analyzes all if not specified)
            
        Returns:
            Dictionary with archetype analysis and threats
        """
        if not self.game_state:
            return {"error": "Game state not available"}
        
        active_player = self.game_state.get_active_player()
        if not active_player:
            return {"error": "No active player"}
        
        # Get opponents to analyze
        if opponent_id:
            opponent = next((p for p in self.game_state.players if p.id == opponent_id), None)
            if not opponent:
                return {"error": f"Opponent {opponent_id} not found"}
            opponents = [opponent]
        else:
            opponents = [p for p in self.game_state.players if p.id != active_player.id and p.life > 0]
        
        if not opponents:
            return {
                "success": True,
                "message": "No opponents to analyze"
            }
        
        # Analyze each opponent
        analyses = []
        for opponent in opponents:
            analysis = self._analyze_opponent(opponent, active_player)
            analyses.append(analysis)
        
        # If single opponent, return detailed analysis
        if len(analyses) == 1:
            return {
                "success": True,
                "opponent_id": analyses[0]["opponent_id"],
                "opponent_name": analyses[0]["opponent_name"],
                "archetype": analyses[0]["archetype"],
                "confidence": round(analyses[0]["archetype_confidence"], 2),
                "threat_level": round(analyses[0]["threat_level"], 2),
                "biggest_threat": analyses[0]["biggest_threat"],
                "board_summary": analyses[0]["board_summary"],
                "card_types": analyses[0]["card_types"],
                "estimated_strategy": analyses[0]["estimated_strategy"],
                "political_value": analyses[0]["political_value"],
                "summary": analyses[0]["summary"]
            }
        
        # If multiple opponents, return summary
        return {
            "success": True,
            "opponent_count": len(analyses),
            "opponents": [
                {
                    "id": a["opponent_id"],
                    "name": a["opponent_name"],
                    "archetype": a["archetype"],
                    "threat_level": round(a["threat_level"], 2),
                    "biggest_threat": a["biggest_threat"]["name"] if a["biggest_threat"] else "None"
                }
                for a in analyses
            ],
            "most_threatening": max(analyses, key=lambda x: x["threat_level"]),
            "archetypes_present": list(set(a["archetype"] for a in analyses))
        }
    
    def _analyze_opponent(self, opponent: Any, active_player: Any) -> Dict[str, Any]:
        """Analyze a single opponent."""
        board_creatures = opponent.creatures_in_play()
        board_lands = opponent.lands_in_play()
        
        # Categorize board creatures
        aggro_creatures = self._count_aggro_creatures(board_creatures)
        control_creatures = self._count_control_creatures(board_creatures)
        combo_creatures = self._count_combo_creatures(board_creatures)
        ramp_artifacts = self._count_ramp_artifacts(opponent.battlefield)
        
        # Determine archetype
        archetype, confidence = self._determine_archetype(
            len(board_creatures),
            aggro_creatures,
            control_creatures,
            combo_creatures,
            ramp_artifacts,
            len(board_lands),
            len(opponent.hand)
        )
        
        # Find biggest threat
        biggest_threat = self._identify_biggest_threat(board_creatures)
        
        # Calculate threat level
        threat_level = self._calculate_threat_level(
            board_creatures,
            opponent.life,
            active_player.life,
            aggro_creatures,
            len(opponent.hand)
        )
        
        # Board summary
        total_power = sum(c.current_power() for c in board_creatures if c.current_power() > 0)
        
        # Estimate strategy from board
        estimated_strategy = self._estimate_strategy(archetype, len(board_creatures), total_power)
        
        # Political value (threat to eliminate vs threat to keep)
        political_value = self._assess_political_value(threat_level, opponent.life)
        
        return {
            "opponent_id": opponent.id,
            "opponent_name": opponent.name,
            "archetype": archetype,
            "archetype_confidence": confidence,
            "threat_level": threat_level,
            "biggest_threat": biggest_threat,
            "board_summary": {
                "creatures": len(board_creatures),
                "total_power": total_power,
                "lands": len(board_lands),
                "hand_size": len(opponent.hand)
            },
            "card_types": {
                "aggro_creatures": aggro_creatures,
                "control_creatures": control_creatures,
                "combo_creatures": combo_creatures,
                "ramp_artifacts": ramp_artifacts
            },
            "estimated_strategy": estimated_strategy,
            "political_value": political_value,
            "summary": self._generate_summary(opponent.name, archetype, threat_level, biggest_threat)
        }
    
    def _count_aggro_creatures(self, creatures: List[Any]) -> int:
        """Count creatures with power >= 3 or haste."""
        count = 0
        for creature in creatures:
            power = creature.current_power()
            has_haste = "haste" in creature.card.keywords
            if power >= 3 or has_haste:
                count += 1
        return count
    
    def _count_control_creatures(self, creatures: List[Any]) -> int:
        """Count creatures with defensive abilities or high toughness."""
        count = 0
        for creature in creatures:
            toughness = creature.current_toughness()
            keywords = creature.card.keywords
            # Control creatures have flying, reach, or high toughness
            if toughness >= 4 or "flying" in keywords or "reach" in keywords:
                count += 1
        return count
    
    def _count_combo_creatures(self, creatures: List[Any]) -> int:
        """Count creatures that might be part of combos."""
        # Creatures with special abilities are combo pieces
        count = 0
        for creature in creatures:
            if creature.card.oracle_text and ("tap" in creature.card.oracle_text.lower() or "draw" in creature.card.oracle_text.lower()):
                count += 1
        return count
    
    def _count_ramp_artifacts(self, battlefield: List[Any]) -> int:
        """Count mana ramp artifacts."""
        count = 0
        for card in battlefield:
            if card.card.card_types and "artifact" in [t.value for t in card.card.card_types]:
                card_name = card.card.name.lower()
                # Common ramp artifacts
                if any(x in card_name for x in ["ring", "signet", "sphere", "stone", "vault", "crank"]):
                    count += 1
        return count
    
    def _determine_archetype(
        self,
        creature_count: int,
        aggro_creatures: int,
        control_creatures: int,
        combo_creatures: int,
        ramp_artifacts: int,
        land_count: int,
        hand_size: int
    ) -> tuple:
        """
        Determine opponent archetype.
        
        Returns: (archetype_name, confidence)
        """
        # Score each archetype
        aggro_score = aggro_creatures * 2
        control_score = (control_creatures * 1.5) + (land_count * 0.5)
        combo_score = combo_creatures * 2
        ramp_score = ramp_artifacts * 1.5
        midrange_score = (creature_count * 0.8) + (control_creatures * 0.5)
        
        # Adjust scores based on card counts
        if creature_count >= 5:
            # Many creatures strongly suggest aggro
            aggro_score += 5
        if creature_count >= 6:
            # 6+ creatures almost certainly aggro
            aggro_score += 3
        if creature_count <= 2:
            control_score += 2  # Few creatures suggest control
        if hand_size >= 5:
            combo_score += 1  # Large hand suggests combo setup
        if ramp_artifacts >= 3:
            ramp_score += 3  # Many ramps suggest ramp deck
        
        scores = {
            "aggro": aggro_score,
            "control": control_score,
            "combo": combo_score,
            "ramp": ramp_score,
            "midrange": midrange_score
        }
        
        # Determine archetype
        archetype = max(scores, key=lambda x: scores[x])
        total_score = sum(scores.values())
        confidence = scores[archetype] / max(total_score, 1)
        
        return (archetype, confidence)
    
    def _identify_biggest_threat(self, creatures: List[Any]) -> Optional[Dict[str, Any]]:
        """Identify the most threatening creature on board."""
        if not creatures:
            return None
        
        biggest = None
        biggest_score = 0
        
        for creature in creatures:
            # Threat score: power + toughness + evasion bonus
            power = creature.current_power()
            toughness = creature.current_toughness()
            score = power + (toughness * 0.5)
            
            # Bonus for evasion
            if "flying" in creature.card.keywords:
                score += 3
            if "unblockable" in creature.card.keywords or "cant_be_blocked" in creature.card.keywords:
                score += 4
            if "trample" in creature.card.keywords:
                score += 1
            
            if score > biggest_score:
                biggest_score = score
                biggest = creature
        
        if biggest:
            return {
                "name": biggest.card.name,
                "power": biggest.current_power(),
                "toughness": biggest.current_toughness(),
                "threat_score": biggest_score
            }
        
        return None
    
    def _calculate_threat_level(
        self,
        creatures: List[Any],
        opponent_life: int,
        player_life: int,
        aggro_creatures: int,
        hand_size: int
    ) -> float:
        """
        Calculate threat level 0.0-1.0.
        
        Factors: creature count, total power, life totals, hand size
        """
        if opponent_life <= 0:
            return 0.0
        
        # Power calculation
        total_power = sum(c.current_power() for c in creatures if c.current_power() > 0)
        
        # Base threat from power
        threat = min(1.0, total_power / 20.0)  # 20 power = max threat
        
        # Modifier for aggro creatures
        threat += (aggro_creatures * 0.1)
        
        # Modifier for hand size (more cards = more options)
        threat += (hand_size * 0.05)
        
        # Modifier for relative life totals
        if player_life < opponent_life:
            threat += 0.2  # Opponent ahead in life
        
        # Clamp to 0.0-1.0
        return min(1.0, threat)
    
    def _estimate_strategy(self, archetype: str, creature_count: int, _total_power: int) -> str:
        """Estimate what strategy opponent is executing."""
        if archetype == "aggro":
            if creature_count >= 5:
                return "Wide aggro (many small creatures)"
            else:
                return "Tall aggro (few powerful creatures)"
        
        elif archetype == "control":
            return "Control (stabilizing board, disruption)"
        
        elif archetype == "combo":
            return "Combo (setting up combination)"
        
        elif archetype == "ramp":
            return "Ramp (building mana for big plays)"
        
        else:  # midrange
            return "Midrange (balanced creatures and removal)"
    
    def _assess_political_value(self, threat_level: float, opponent_life: int) -> str:
        """Assess political priority for this opponent."""
        if threat_level >= 0.8:
            return "ELIMINATE (highest priority threat)"
        elif threat_level >= 0.6:
            return "CONTAIN (watch closely, respond to)"
        elif threat_level >= 0.4:
            return "MONITOR (keep eye on board)"
        elif opponent_life <= 15:
            return "VULNERABLE (focus damage)"
        else:
            return "SAFE (lower priority)"
    
    def _generate_summary(
        self,
        opponent_name: str,
        archetype: str,
        threat_level: float,
        biggest_threat: Optional[Dict[str, Any]]
    ) -> str:
        """Generate human-readable summary."""
        threat_emoji = "🔴" if threat_level >= 0.8 else "🟡" if threat_level >= 0.5 else "🟢"
        
        summary = f"{threat_emoji} **{opponent_name}** plays {archetype} (threat: {threat_level:.0%})"
        
        if biggest_threat:
            summary += f". Biggest threat: {biggest_threat['name']} ({biggest_threat['power']}/{biggest_threat['toughness']})"
        
        return summary
