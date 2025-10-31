"""
Phase 2 Integration Tests - Regression Test Suite

Tests multi-tool chains, tool interactions, and full gameplay scenarios.
"""
import sys
from pathlib import Path
import uuid

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.game_state import GameState
from core.player import Player
from core.card import Card, CardType, CardInstance, ManaCost, Color
from core.rules_engine import RulesEngine
from agent.llm_agent import MTGAgent
from tools.evaluation_tools import CanIWinTool, StrategyRecommendationTool, OpponentModelingTool


def create_game_state():
    """Helper to create a basic game state."""
    player1 = Player(id="p1", name="Alice", life=40)
    player2 = Player(id="p2", name="Bob", life=40)
    
    game_state = GameState(
        game_id=str(uuid.uuid4()),
        players=[player1, player2],
        active_player_id="p1",
        priority_player_id="p1"
    )
    return game_state


def make_creature_instance(card_id: str, name: str, power: int, toughness: int, controller_id: str = "p1") -> CardInstance:
    """Helper to create a ready-to-attack creature instance."""
    card = Card(
        id=card_id,
        name=name,
        mana_cost=ManaCost(),
        card_types=[CardType.CREATURE],
        power=power,
        toughness=toughness,
        colors=[]
    )
    return CardInstance(
        card=card,
        instance_id=f"{card_id}_inst",
        controller_id=controller_id,
        owner_id=controller_id,
        is_tapped=False,
        summoning_sick=False
    )


class TestHeuristicIntegration:
    """Test heuristic agent using all Phase 2 tools."""
    
    def test_heuristic_uses_all_tools(self):
        """Verify heuristic agent has all Phase 2 tools."""
        game_state = create_game_state()
        rules_engine = RulesEngine(game_state)
        
        # Create heuristic agent (no LLM)
        agent = MTGAgent(
            game_state=game_state,
            rules_engine=rules_engine,
            use_llm=False,
            verbose=False
        )
        
        # Verify all tools are available (updated: Phase 5a.4 adds combat intelligence)
        assert len(agent.tools) == 13
        assert "can_i_win" in agent.tools
        assert "recommend_strategy" in agent.tools
        assert "analyze_opponent" in agent.tools


class TestToolChains:
    """Test multi-tool decision chains."""
    
    def test_lethal_detection_chain(self):
        """Test can_i_win with sufficient creatures."""
        game_state = create_game_state()
        player1 = game_state.players[0]
        player2 = game_state.players[1]
        
        # Set opponent to low life
        player2.life = 10
        
        # Give Alice lethal creatures (ready to attack)
        creature1 = make_creature_instance("dragon", "Dragon", power=6, toughness=6, controller_id="p1")
        creature2 = make_creature_instance("knight", "Knight", power=4, toughness=2, controller_id="p1")
        player1.battlefield.extend([creature1, creature2])
        
        # Create tools
        win_tool = CanIWinTool()
        win_tool.game_state = game_state
        strategy_tool = StrategyRecommendationTool()
        strategy_tool.game_state = game_state
        
        # Execute chain
        win_result = win_tool.execute()
        strategy_result = strategy_tool.execute(player_id="p1")
        
        # Verify lethal detected
        assert win_result.get("success")
        assert win_result.get("can_win") is True
        assert win_result.get("damage") >= 10
        
        # Verify strategy recommends CLOSE
        assert strategy_result.get("success")
        assert strategy_result.get("strategy") == "CLOSE"


class TestToolAccuracy:
    """Test accuracy of Phase 2 tool predictions."""
    
    def test_lethal_detection_simple(self):
        """Test can_i_win with exactly lethal damage."""
        game_state = create_game_state()
        player1 = game_state.players[0]
        player2 = game_state.players[1]
        
        player2.life = 15
        
        # Three 5/5 creatures = exactly 15 damage (ready to attack)
        for i in range(3):
            creature = make_creature_instance(card_id=f"creature{i}", name=f"Creature {i}", power=5, toughness=5, controller_id="p1")
            player1.battlefield.append(creature)
        
        win_tool = CanIWinTool()
        win_tool.game_state = game_state
        result = win_tool.execute()
        
        assert result.get("success")
        assert result.get("can_win") is True
        assert result.get("damage") == 15
    
    def test_opponent_archetype_aggro(self):
        """Test analyze_opponent detects aggro archetype."""
        game_state = create_game_state()
        player2 = game_state.players[1]
        
        # Give opponent aggressive creatures (high power, low toughness)
        specs = [(3, 1), (3, 1), (2, 2), (4, 2)]
        for i, (power, toughness) in enumerate(specs):
            creature = make_creature_instance(card_id=f"creature{i}", name=f"Creature {i}", power=power, toughness=toughness, controller_id="p2")
            player2.battlefield.append(creature)
        
        opp_tool = OpponentModelingTool()
        opp_tool.game_state = game_state
        result = opp_tool.execute(opponent_id="p2")
        
        assert result.get("success")
        assert result.get("archetype") == "aggro"
