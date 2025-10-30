"""
Position evaluation tools for MTG Commander AI.

Provides scoring functions to evaluate game state quality.
"""
from typing import Dict, Any, Optional


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
    
    def execute(self, player_id: str = None) -> Dict[str, Any]:
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
