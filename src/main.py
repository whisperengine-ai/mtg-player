"""
Main entry point for MTG Commander AI.
"""
import sys
import random
import uuid
from pathlib import Path
from datetime import datetime

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
from utils.logger import setup_loggers


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


def play_game(game_state, rules_engine, max_full_turns=10, verbose=True, use_llm=True, aggression="balanced", llm_console_summary=False):
    """Play a game of Commander with simple auto-progression through phases.

    We progress the game by ensuring each loop iteration advances at least one
    phase/step. This avoids getting stuck in the same step when the agent takes
    a non-passing action (e.g., plays a land).
    
    Args:
        game_state: The game state
        rules_engine: The rules engine
        max_full_turns: Maximum number of full turns before ending game
        verbose: Whether to print game progress
        use_llm: Whether to use LLM for AI decisions (if False, uses rule-based heuristics)
        aggression: Combat aggression level
        llm_console_summary: If True, print one-line console summaries per LLM call
    """

    # Set up loggers
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    game_id = f"{timestamp}_{game_state.game_id[:8]}"
    game_logger, llm_logger, heuristic_logger = setup_loggers(game_id, llm_console_summary=llm_console_summary)
    # Attach game logger to rules engine for internal events (draws, life changes)
    if hasattr(rules_engine, "set_game_logger"):
        rules_engine.set_game_logger(game_logger)
    
    # Log game setup
    game_logger.log_game_state({
        "game_id": game_state.game_id,
        "players": [{"id": p.id, "name": p.name, "life": p.life} for p in game_state.players],
        "turn": game_state.turn_number
    })

    # Start the game
    rules_engine.start_game()

    if verbose:
        print(f"\n{'='*60}")
        print("🎲 GAME START")
        if not use_llm:
            print("🎲 Running in HEURISTIC MODE (no LLM calls)")
        print(f"📝 Logs saved to: logs/game_{game_id}.log, logs/llm_{game_id}.log, logs/heuristic_{game_id}.log")
        print(f"{'='*60}\n")
        print(game_state)

    # Create agents for each player with logger
    agents = {p.id: MTGAgent(
        game_state=game_state, 
        rules_engine=rules_engine, 
        verbose=verbose, 
        game_logger=game_logger,
        llm_logger=llm_logger,
        heuristic_logger=heuristic_logger,
        use_llm=use_llm,
        aggression=aggression
    ) for p in game_state.players}

    # Drive the game by steps, but cap by full-turns to avoid infinite loops
    starting_turn = game_state.turn_number
    max_steps = max_full_turns * 20  # generous upper bound of steps per turn
    steps_executed = 0

    while not game_state.is_game_over and (game_state.turn_number - starting_turn) < max_full_turns and steps_executed < max_steps:
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
        
        # Log turn start
        game_logger.log_turn_start(
            turn=game_state.turn_number,
            player_name=active_player.name,
            phase=game_state.current_phase.value,
            step=game_state.current_step.value
        )

        # Snapshot to detect whether the agent advanced the phase
        prev_snapshot = (
            game_state.current_phase,
            game_state.current_step,
            game_state.active_player_id,
            game_state.turn_number,
        )

        # Get agent and let them take actions until phase changes or they pass
        agent = agents[active_player.id]
        max_actions_per_phase = 10  # Prevent infinite loops (lowered from 20 for debugging)
        actions_taken = 0
        
        try:
            while actions_taken < max_actions_per_phase:
                # Take one action
                agent.take_turn_action()
                actions_taken += 1
                
                # Check if phase/step changed
                post_snapshot = (
                    game_state.current_phase,
                    game_state.current_step,
                    game_state.active_player_id,
                    game_state.turn_number,
                )
                
                # If phase changed, break out of action loop
                if post_snapshot != prev_snapshot:
                    game_logger.log_phase_change(
                        old_phase=prev_snapshot[0].value,
                        old_step=prev_snapshot[1].value,
                        new_phase=post_snapshot[0].value,
                        new_step=post_snapshot[1].value
                    )
                    break
                    
        except Exception as e:
            if verbose:
                print(f"❌ Error during turn: {e}")
            game_logger.log_error(f"Turn error for {active_player.name}: {e}")
        
        # If too many actions without advancing, force advance to prevent infinite loop
        if actions_taken >= max_actions_per_phase:
            if verbose:
                print(f"⚠️  Warning: Forcing phase advance after {actions_taken} actions")
            game_logger.log_phase_change(
                old_phase=game_state.current_phase.value,
                old_step=game_state.current_step.value,
                new_phase="advancing",
                new_step="forced"
            )
            rules_engine.advance_phase()

        # Check win conditions after each step
        game_state.check_win_condition()
        steps_executed += 1

    # Game finished (win, draw, or loop cap)
    if verbose:
        print(f"\n{'='*60}")
        print("🏁 GAME OVER")
        print(f"{'='*60}")

        if game_state.winner_id:
            winner = game_state.get_player(game_state.winner_id)
            print(f"\n🎉 Winner: {winner.name}!")
            print(f"Final life total: {winner.life}")
            game_logger.log_win_condition(winner.name, "Life total or commander damage")
        else:
            reason = "turn limit" if (game_state.turn_number - starting_turn) >= max_full_turns or steps_executed >= max_steps else "no winner"
            print(f"\n🤝 Game ended in a draw ({reason})")
            game_logger.log_win_condition(None, reason)

        print("\nFinal standings:")
        for player in game_state.players:
            status = "💀 Eliminated" if player.is_dead() else f"❤️ {player.life} life"
            print(f"  {player.name}: {status}")
        
        print(f"\n📝 Game log: logs/game_{game_id}.log")
        print(f"📝 LLM log: logs/llm_{game_id}.log")


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
    no_llm = "--no-llm" in sys.argv or "--heuristic" in sys.argv
    
    # Support aggression level
    aggression = "balanced"  # Default
    for arg in sys.argv:
        if arg.startswith("--aggression="):
            aggression = arg.split("=")[1].lower()
            if aggression not in ["conservative", "balanced", "aggressive"]:
                print(f"⚠️  Invalid aggression level '{aggression}', using 'balanced'")
                aggression = "balanced"
    
    # Support custom player count
    num_players = 4  # Default to 4-player Commander
    for arg in sys.argv:
        if arg.startswith("--players="):
            try:
                num_players = int(arg.split("=")[1])
                num_players = max(2, min(4, num_players))  # Clamp between 2-4
            except ValueError:
                pass
    
    # Support custom max turns
    max_turns = 10  # Default to 10 full turns
    for arg in sys.argv:
        if arg.startswith("--max-turns="):
            try:
                max_turns = int(arg.split("=")[1])
                max_turns = max(1, max_turns)  # At least 1 turn
            except ValueError:
                pass

    # Optional RNG seed for reproducible runs
    seed = None
    for arg in sys.argv:
        if arg.startswith("--seed="):
            try:
                seed = int(arg.split("=")[1])
            except ValueError:
                seed = None
    if seed is not None:
        try:
            random.seed(seed)
            print(f"🔁 RNG seeded with {seed}")
        except Exception:
            print("⚠️  Failed to set RNG seed; continuing without seeding.")

    # Turn summary logging flag (default: enabled)
    turn_summaries = True
    if "--no-turn-summaries" in sys.argv:
        turn_summaries = False
    if "--turn-summaries" in sys.argv:
        turn_summaries = True

    # LLM console summary flag (default: disabled)
    llm_console_summary = False
    if "--llm-console" in sys.argv:
        llm_console_summary = True
    
    # Show help if requested
    if "--help" in sys.argv or "-h" in sys.argv:
        print("""
Usage: python run.py [OPTIONS]

Options:
  --verbose, -v             Show detailed turn-by-turn output (logs always saved to files)
  --no-llm, --heuristic     Use rule-based AI instead of LLM (no API costs)
  --players=N               Number of players (2-4, default: 4)
  --max-turns=N             Maximum number of full turns before ending (default: 10)
  --aggression=LEVEL        Combat aggression level (default: balanced)
                            conservative: Only attack with power 3+ or when desperate
                            balanced: Attack with power 2+ or when at 30 life or below
                            aggressive: Attack with ALL creatures every turn
  --seed=N                  Seed Python RNG for reproducible shuffles and decisions
  --no-turn-summaries       Disable end-of-turn summaries in game log
  --turn-summaries          Enable end-of-turn summaries in game log (default)
  --llm-console             Print one-line console summaries per LLM call
  --help, -h                Show this help message

Examples:
  python run.py                           # 4 players, 10 turns, balanced aggression
  python run.py --verbose                 # Show output to console
  python run.py --no-llm --aggressive     # Heuristic AI with aggressive attacks
  python run.py --max-turns=50            # Longer game (more likely to see a winner)
  python run.py --players=2 --verbose     # 2-player game with output
  python run.py --no-llm --verbose        # Heuristic mode (no API costs)
  python run.py --max-turns=5 --verbose   # Short 5-turn game
  python run.py --llm-console --verbose   # Show LLM call summaries in console

For more information, see README.md and QUICKSTART.md
        """)
        return
    
    # Set up and play game
    game_state, rules_engine = setup_game(num_players=num_players, verbose=verbose)
    # Configure end-of-turn summaries
    if hasattr(rules_engine, "set_turn_summary_enabled"):
        rules_engine.set_turn_summary_enabled(turn_summaries)
    play_game(
        game_state,
        rules_engine,
        max_full_turns=max_turns,
        verbose=verbose,
        use_llm=not no_llm,
        aggression=aggression,
        llm_console_summary=llm_console_summary
    )
    
    print("\n✨ Thanks for playing! ✨\n")


if __name__ == "__main__":
    main()
