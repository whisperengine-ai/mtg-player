"""
Main entry point for MTG Commander AI.
"""
import sys
import random
import uuid
import os
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try loading from current directory
    load_dotenv()

from core.game_state import GameState, Phase, Step
from core.player import Player
from core.rules_engine import RulesEngine
from core.card import Card, CardType, ManaCost, Color, CardInstance
from agent.llm_agent import MTGAgent
from data.cards import create_simple_deck


def create_simple_commander():
    """Create a simple commander for testing."""
    return Card(
        id="commander_1",
        name="Commander Bear",
        mana_cost=ManaCost(generic=2, green=2),
        card_types=[CardType.CREATURE],
        colors=[Color.GREEN],
        power=4,
        toughness=4,
        is_commander=True,
        oracle_text="Legendary Creature - Bear Commander"
    )


def setup_game(num_players=4, verbose=True, archetypes=None):
    """
    Set up a new game.
    
    Args:
        num_players: Number of players (default 4)
        verbose: Whether to print setup messages
        archetypes: List of archetypes for each player (e.g., ["ramp", "control", "midrange", "ramp"])
                   If None, assigns archetypes: [ramp, control, midrange, midrange]
    """
    if verbose:
        print(f"🎮 Setting up {num_players}-player Magic: The Gathering Commander game...")
    
    # Default archetype assignment for variety
    if archetypes is None:
        archetypes = ["ramp", "control", "midrange", "midrange"][:num_players]
    
    # Create players
    players = []
    for i in range(num_players):
        player_id = f"player_{i+1}"
        archetype = archetypes[i] if i < len(archetypes) else "midrange"
        
        player = Player(
            id=player_id,
            name=f"Player {i+1} ({archetype.title()})",
            life=40
        )
        
        # Create deck with archetype
        commander = create_simple_commander()
        deck_cards = create_simple_deck(commander, archetype=archetype)
        
        if verbose:
            print(f"  📦 Built {archetype} deck for Player {i+1} ({len(deck_cards)} cards)")
        
        # Shuffle deck
        random.shuffle(deck_cards)
        
        # Create card instances (without rules engine for now)
        library = []
        for card in deck_cards:
            instance = CardInstance(
                card=card,
                instance_id=str(uuid.uuid4()),
                controller_id=player_id,
                owner_id=player_id
            )
            library.append(instance)
        
        player.library = library
        
        # Set commander
        if commander:
            commander_instance = CardInstance(
                card=commander,
                instance_id=str(uuid.uuid4()),
                controller_id=player_id,
                owner_id=player_id
            )
            commander_instance.card.is_commander = True
            player.commander = commander_instance
            player.command_zone.append(commander_instance)
        
        players.append(player)
        
        if verbose:
            print(f"  ✓ Created {player.name} with {len(player.library)} card deck")
    
    # Create game state
    game_state = GameState(
        game_id=str(uuid.uuid4()),
        players=players,
        active_player_id=players[0].id,
        priority_player_id=players[0].id,
        current_phase=Phase.BEGINNING,
        current_step=Step.UNTAP
    )
    
    # Create rules engine
    rules_engine = RulesEngine(game_state)
    
    if verbose:
        print(f"✓ Game initialized with {num_players} players")
    
    return game_state, rules_engine


def play_game(game_state, rules_engine, max_turns=20, verbose=True):
    """Play a game of Commander."""
    
    # Start the game
    rules_engine.start_game()
    
    if verbose:
        print(f"\n{'='*60}")
        print("🎲 GAME START")
        print(f"{'='*60}\n")
        print(game_state)
    
    # Create agents for each player
    agents = {}
    for player in game_state.players:
        agents[player.id] = MTGAgent(
            game_state=game_state,
            rules_engine=rules_engine,
            verbose=verbose
        )
    
    # Game loop
    turn_count = 0
    while not game_state.is_game_over and turn_count < max_turns:
        active_player = game_state.get_active_player()
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Turn {game_state.turn_number} - {active_player.name}'s turn")
            print(f"Phase: {game_state.current_phase.value}/{game_state.current_step.value}")
            print(f"{'='*60}")
            print(f"Life: {active_player.life}")
            print(f"Hand: {len(active_player.hand)} cards")
            print(f"Battlefield: {len(active_player.battlefield)} permanents")
            print(f"Creatures: {len(active_player.creatures_in_play())}")
        
        # Get the agent for this player
        agent = agents[active_player.id]
        
        # Take actions for this phase
        try:
            agent.take_turn_action()
        except Exception as e:
            if verbose:
                print(f"❌ Error during turn: {e}")
            # Skip to next phase
            rules_engine.advance_phase()
        
        # Check for game over
        game_state.check_win_condition()
        
        turn_count += 1
        
        # Safety: limit turns
        if turn_count >= max_turns:
            if verbose:
                print(f"\n⏱️ Game ended due to turn limit ({max_turns} turns)")
            break
    
    # Game over
    if verbose:
        print(f"\n{'='*60}")
        print("🏁 GAME OVER")
        print(f"{'='*60}")
        
        if game_state.winner_id:
            winner = game_state.get_player(game_state.winner_id)
            print(f"\n🎉 Winner: {winner.name}!")
            print(f"Final life total: {winner.life}")
        else:
            print("\n🤝 Game ended in a draw")
        
        print(f"\nFinal standings:")
        for player in game_state.players:
            status = "💀 Eliminated" if player.is_dead() else f"❤️ {player.life} life"
            print(f"  {player.name}: {status}")


def main():
    """Main entry point."""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║          MTG Commander AI - Proof of Concept           ║
    ║              Agentic AI with Tool Calling               ║
    ║               Phase 3: Multiplayer Commander            ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Parse arguments
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    # Support custom player count
    num_players = 4  # Default to 4-player Commander
    for arg in sys.argv:
        if arg.startswith("--players="):
            try:
                num_players = int(arg.split("=")[1])
                num_players = max(2, min(4, num_players))  # Clamp between 2-4
            except ValueError:
                pass
    
    # Set up and play game
    game_state, rules_engine = setup_game(num_players=num_players, verbose=verbose)
    play_game(game_state, rules_engine, max_turns=10, verbose=verbose)
    
    print("\n✨ Thanks for playing! ✨\n")


if __name__ == "__main__":
    main()
