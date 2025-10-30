"""
Logging utilities for MTG Commander AI.

Provides structured logging for:
- Game state transitions and actions
- LLM prompts and responses
- Tool calls and results
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional


class GameLogger:
    """Logger for game events and state transitions."""
    
    def __init__(self, log_dir: Path, game_id: str):
        """Initialize game logger."""
        self.log_dir = log_dir
        self.game_id = game_id
        self.log_file = log_dir / f"game_{game_id}.log"
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up file logger
        self.logger = logging.getLogger(f"game_{game_id}")
        self.logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # File handler only (no console output)
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        
        self.logger.info("Game started: %s", game_id)
    
    def log_turn_start(self, turn: int, player_name: str, phase: str, step: str):
        """Log turn start."""
        self.logger.info("TURN %s | %s | %s/%s", turn, player_name, phase, step)
    
    def log_action(self, player_name: str, action_type: str, details: str = ""):
        """Log player action."""
        if details:
            self.logger.info("ACTION | %s | %s | %s", player_name, action_type, details)
        else:
            self.logger.info("ACTION | %s | %s", player_name, action_type)
    
    def log_phase_change(self, old_phase: str, old_step: str, new_phase: str, new_step: str):
        """Log phase transition."""
        self.logger.info("PHASE CHANGE | %s/%s → %s/%s", old_phase, old_step, new_phase, new_step)
    
    def log_game_state(self, state_dict: Dict[str, Any]):
        """Log full game state snapshot."""
        self.logger.info("STATE | %s", json.dumps(state_dict, indent=2))
    
    def log_win_condition(self, winner_name: Optional[str], reason: str):
        """Log game end."""
        if winner_name:
            self.logger.info("GAME END | Winner: %s | Reason: %s", winner_name, reason)
        else:
            self.logger.info("GAME END | Draw | Reason: %s", reason)
    
    def log_error(self, error_msg: str):
        """Log error."""
        self.logger.error("ERROR | %s", error_msg)

    def log_draw(self, player_name: str, new_hand_size: int):
        """Log a card draw event."""
        self.logger.info("DRAW | %s | Hand: %d", player_name, new_hand_size)

    def log_life_change(self, player_name: str, delta: int, new_life: int, reason: Optional[str] = None):
        """Log a life total change.

        Args:
            player_name: Name of the player whose life changed
            delta: Positive for life gain, negative for damage/loss
            new_life: New life total after the change
            reason: Optional context (e.g., "combat damage from Goblin Raider")
        """
        if reason:
            self.logger.info("LIFE | %s | %+d -> %d | %s", player_name, delta, new_life, reason)
        else:
            self.logger.info("LIFE | %s | %+d -> %d", player_name, delta, new_life)

    def log_stack_push(self, controller_name: str, card_name: str, targets: Optional[list] = None):
        """Log when a spell or ability is put on the stack."""
        if targets:
            try:
                targets_str = ", ".join(str(t) for t in targets)
            except (TypeError, ValueError):
                targets_str = str(targets)
            self.logger.info("STACK | PUSH | %s | %s | targets: %s", controller_name, card_name, targets_str)
        else:
            self.logger.info("STACK | PUSH | %s | %s", controller_name, card_name)

    def log_stack_resolve(self, controller_name: str, card_name: str, outcome: str):
        """Log resolution of the top object on the stack."""
        self.logger.info("STACK | RESOLVE | %s | %s | %s", controller_name, card_name, outcome)

    def log_priority_pass(self, player_name: str):
        """Log a single player's pass of priority."""
        self.logger.info("PRIORITY | pass | %s", player_name)

    def log_priority_next(self, next_player_name: str):
        """Log the next player to get priority."""
        self.logger.info("PRIORITY | to | %s", next_player_name)

    def log_all_passed(self, action: str):
        """Log when all players have passed priority and the resulting action.

        action values may include: 'resolve_top', 'empty_stack', 'advance_phase'.
        """
        self.logger.info("PRIORITY | all passed | action: %s", action)


class LLMLogger:
    """Logger for LLM interactions and prompts."""
    
    def __init__(self, log_dir: Path, game_id: str):
        """Initialize LLM logger."""
        self.log_dir = log_dir
        self.game_id = game_id
        self.log_file = log_dir / f"llm_{game_id}.log"
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up file logger
        self.logger = logging.getLogger(f"llm_{game_id}")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # File handler only (no console output)
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        
        self.logger.info("LLM Logger initialized for game: %s", game_id)
        
        # Track call count
        self.call_count = 0
    
    def log_llm_call(
        self,
        player_name: str,
        turn: int,
        phase: str,
        model: str,
        messages: list,
        tools: Optional[list] = None
    ):
        """Log LLM API call with full prompt."""
        self.call_count += 1
        
        self.logger.info("=" * 80)
        self.logger.info("LLM CALL #%d | %s | Turn %d | %s", self.call_count, player_name, turn, phase)
        self.logger.info("Model: %s", model)
        self.logger.info("-" * 80)
        
        # Log messages (full content, no truncation)
        self.logger.info("MESSAGES:")
        for i, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            # Log full content without truncation
            self.logger.info("  [%d] %s:", i, role.upper())
            for line in content.split('\n'):
                self.logger.info("    %s", line)
        
        # Log tool schemas if present
        if tools:
            self.logger.info("-" * 80)
            self.logger.info("TOOLS: %d available", len(tools))
            for tool in tools:
                tool_name = tool.get("function", {}).get("name", "unknown")
                self.logger.debug("  - %s", tool_name)
    
    def log_llm_response(
        self,
        response_content: Optional[str],
        tool_calls: Optional[list] = None,
        finish_reason: str = "unknown",
        reasoning_content: Optional[str] = None,
        thinking_content: Optional[str] = None,
        usage: Optional[Any] = None
    ):
        """Log LLM response with reasoning and thinking content."""
        self.logger.info("-" * 80)
        self.logger.info("LLM RESPONSE:")
        
        if response_content:
            self.logger.info("Content: %s", response_content)
        
        # Log reasoning content if available (e.g., from o-series models)
        if reasoning_content:
            self.logger.info("=" * 80)
            self.logger.info("REASONING (Extended Thinking):")
            self.logger.info(reasoning_content)
            self.logger.info("=" * 80)
        
        # Log thinking metadata if available
        if thinking_content:
            self.logger.info("Thinking: %s", thinking_content)
        
        if tool_calls:
            self.logger.info("Tool Calls: %d", len(tool_calls))
            for tc in tool_calls:
                if hasattr(tc, 'function'):
                    func_name = tc.function.name
                    # Log full arguments without truncation
                    func_args = tc.function.arguments
                    self.logger.info("  - %s(%s)", func_name, func_args)
                else:
                    self.logger.info("  - %s", tc)
        
        # Log token usage if available
        if usage:
            self.logger.info("Token Usage:")
            if hasattr(usage, 'prompt_tokens'):
                self.logger.info("  Prompt: %s", usage.prompt_tokens)
            if hasattr(usage, 'completion_tokens'):
                self.logger.info("  Completion: %s", usage.completion_tokens)
            if hasattr(usage, 'total_tokens'):
                self.logger.info("  Total: %s", usage.total_tokens)
            
            # Log reasoning token usage if available (o-series models)
            if hasattr(usage, 'completion_tokens_details'):
                details = usage.completion_tokens_details
                if hasattr(details, 'reasoning_tokens'):
                    self.logger.info("  Reasoning: %s", details.reasoning_tokens)
        
        self.logger.info("Finish Reason: %s", finish_reason)
        self.logger.info("=" * 80)
    
    def log_tool_execution(self, tool_name: str, args: Dict[str, Any], result: Dict[str, Any]):
        """Log tool execution with full results (no truncation)."""
        self.logger.info("TOOL EXEC | %s", tool_name)
        self.logger.debug("  Args: %s", json.dumps(args, indent=2))
        # Log full result without truncation
        result_json = json.dumps(result, indent=2)
        self.logger.info("  Result:")
        for line in result_json.split('\n'):
            self.logger.info("    %s", line)
    
    def log_decision(self, player_name: str, decision: Dict[str, Any]):
        """Log final decision made."""
        self.logger.info("-" * 80)
        self.logger.info("DECISION | %s", player_name)
        self.logger.info("  Action: %s", decision.get('type', 'unknown'))
        if decision.get('reasoning'):
            self.logger.info("  Reasoning: %s", decision['reasoning'])
        self.logger.info("-" * 80)


class HeuristicLogger:
    """Logger for heuristic (non-LLM) decision making runs."""

    def __init__(self, log_dir: Path, game_id: str):
        self.log_dir = log_dir
        self.game_id = game_id
        self.log_file = log_dir / f"heuristic_{game_id}.log"

        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Set up file logger
        self.logger = logging.getLogger(f"heuristic_{game_id}")
        self.logger.setLevel(logging.DEBUG)

        # Clear any existing handlers
        self.logger.handlers.clear()

        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        self.logger.info("Heuristic Logger initialized for game: %s", game_id)

    def log_context(self, player_name: str, turn: int, phase: str, step: str, threats_count: int, actions_count: int):
        self.logger.info("=" * 80)
        self.logger.info("HEURISTIC | %s | Turn %s | %s/%s", player_name, turn, phase, step)
        self.logger.info("Threats observed: %s | Legal actions: %s", threats_count, actions_count)

    def log_tool_execution(self, tool_name: str, args: Dict[str, Any], result: Dict[str, Any]):
        self.logger.info("TOOL EXEC | %s", tool_name)
        try:
            self.logger.debug("  Args: %s", json.dumps(args, indent=2))
        except (TypeError, ValueError):
            self.logger.debug("  Args: %s", args)
        try:
            result_json = json.dumps(result, indent=2)
            self.logger.info("  Result:")
            for line in result_json.split('\n'):
                self.logger.info("    %s", line)
        except (TypeError, ValueError):
            self.logger.info("  Result: %s", result)

    def log_position(self, eval_result: Dict[str, Any]):
        score = eval_result.get("score")
        status = eval_result.get("position")
        if isinstance(score, (int, float)):
            self.logger.info("POSITION | %s (%.2f)", status, score)
        else:
            self.logger.info("POSITION | %s", status)
        # Log full breakdown if available
        breakdown = eval_result.get("breakdown")
        if breakdown:
            try:
                self.logger.info("Breakdown: %s", json.dumps(breakdown, indent=2))
            except (TypeError, ValueError):
                self.logger.info("Breakdown: %s", breakdown)
        if eval_result.get("summary"):
            self.logger.info("Summary: %s", eval_result['summary'])

    def log_decision(self, player_name: str, decision: Dict[str, Any]):
        self.logger.info("-" * 80)
        self.logger.info("DECISION | %s", player_name)
        self.logger.info("  Action: %s", decision.get('type', 'unknown'))
        if decision.get('reasoning'):
            self.logger.info("  Reasoning: %s", decision['reasoning'])
        self.logger.info("-" * 80)

    def log_considered_actions(self, candidates: list, limit: int = 3):
        """Log top-N considered actions with brief reasons and scores.

        candidates: List of dicts with keys like {type, card, score, reason}
        """
        if not candidates:
            return
        # Sort by score descending when available
        try:
            sortable = [c for c in candidates if isinstance(c.get("score"), (int, float))]
            others = [c for c in candidates if c not in sortable]
            sortable.sort(key=lambda x: x.get("score", 0), reverse=True)
            ordered = sortable + others
        except (TypeError, ValueError):
            ordered = candidates

        top = ordered[:limit]
        self.logger.info("CONSIDERED ACTIONS | top %d", len(top))
        for idx, c in enumerate(top, start=1):
            score = c.get("score")
            action_type = c.get("type", "unknown")
            card = c.get("card") or c.get("card_name") or ""
            reason = c.get("reason") or c.get("summary") or ""
            if isinstance(score, (int, float)):
                if card:
                    self.logger.info("  [%d] %.2f | %s | %s", idx, float(score), action_type, card)
                else:
                    self.logger.info("  [%d] %.2f | %s", idx, float(score), action_type)
            else:
                if card:
                    self.logger.info("  [%d] %s | %s", idx, action_type, card)
                else:
                    self.logger.info("  [%d] %s", idx, action_type)
            if reason:
                self.logger.info("       - %s", reason)


def setup_loggers(game_id: str, log_base_dir: str = "logs") -> tuple[GameLogger, LLMLogger, HeuristicLogger]:
    """
    Set up game and LLM loggers for a game session.
    
    Args:
        game_id: Unique game identifier
        log_base_dir: Base directory for logs (default: "logs")
    
    Returns:
        Tuple of (GameLogger, LLMLogger, HeuristicLogger)
    """
    log_dir = Path(log_base_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    game_logger = GameLogger(log_dir, game_id)
    llm_logger = LLMLogger(log_dir, game_id)
    heuristic_logger = HeuristicLogger(log_dir, game_id)

    return game_logger, llm_logger, heuristic_logger
