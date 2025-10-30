"""
Logging utilities for MTG Commander AI.

Provides structured logging for:
- Game state transitions and actions
- LLM prompts and responses
- Tool calls and results
"""
import json
import logging
from datetime import datetime
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
        
        self.logger.info(f"Game started: {game_id}")
    
    def log_turn_start(self, turn: int, player_name: str, phase: str, step: str):
        """Log turn start."""
        self.logger.info(f"TURN {turn} | {player_name} | {phase}/{step}")
    
    def log_action(self, player_name: str, action_type: str, details: str = ""):
        """Log player action."""
        msg = f"ACTION | {player_name} | {action_type}"
        if details:
            msg += f" | {details}"
        self.logger.info(msg)
    
    def log_phase_change(self, old_phase: str, old_step: str, new_phase: str, new_step: str):
        """Log phase transition."""
        self.logger.info(f"PHASE CHANGE | {old_phase}/{old_step} → {new_phase}/{new_step}")
    
    def log_game_state(self, state_dict: Dict[str, Any]):
        """Log full game state snapshot."""
        self.logger.info(f"STATE | {json.dumps(state_dict, indent=2)}")
    
    def log_win_condition(self, winner_name: Optional[str], reason: str):
        """Log game end."""
        if winner_name:
            self.logger.info(f"GAME END | Winner: {winner_name} | Reason: {reason}")
        else:
            self.logger.info(f"GAME END | Draw | Reason: {reason}")
    
    def log_error(self, error_msg: str):
        """Log error."""
        self.logger.error(f"ERROR | {error_msg}")


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
        
        self.logger.info(f"LLM Logger initialized for game: {game_id}")
        
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
        self.logger.info(f"LLM CALL #{self.call_count} | {player_name} | Turn {turn} | {phase}")
        self.logger.info(f"Model: {model}")
        self.logger.info("-" * 80)
        
        # Log messages (full content, no truncation)
        self.logger.info("MESSAGES:")
        for i, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            # Log full content without truncation
            self.logger.info(f"  [{i}] {role.upper()}:")
            for line in content.split('\n'):
                self.logger.info(f"    {line}")
        
        # Log tool schemas if present
        if tools:
            self.logger.info("-" * 80)
            self.logger.info(f"TOOLS: {len(tools)} available")
            for tool in tools:
                tool_name = tool.get("function", {}).get("name", "unknown")
                self.logger.debug(f"  - {tool_name}")
    
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
            self.logger.info(f"Content: {response_content}")
        
        # Log reasoning content if available (e.g., from o-series models)
        if reasoning_content:
            self.logger.info("=" * 80)
            self.logger.info("REASONING (Extended Thinking):")
            self.logger.info(reasoning_content)
            self.logger.info("=" * 80)
        
        # Log thinking metadata if available
        if thinking_content:
            self.logger.info(f"Thinking: {thinking_content}")
        
        if tool_calls:
            self.logger.info(f"Tool Calls: {len(tool_calls)}")
            for tc in tool_calls:
                if hasattr(tc, 'function'):
                    func_name = tc.function.name
                    # Log full arguments without truncation
                    func_args = tc.function.arguments
                    self.logger.info(f"  - {func_name}({func_args})")
                else:
                    self.logger.info(f"  - {tc}")
        
        # Log token usage if available
        if usage:
            self.logger.info(f"Token Usage:")
            if hasattr(usage, 'prompt_tokens'):
                self.logger.info(f"  Prompt: {usage.prompt_tokens}")
            if hasattr(usage, 'completion_tokens'):
                self.logger.info(f"  Completion: {usage.completion_tokens}")
            if hasattr(usage, 'total_tokens'):
                self.logger.info(f"  Total: {usage.total_tokens}")
            
            # Log reasoning token usage if available (o-series models)
            if hasattr(usage, 'completion_tokens_details'):
                details = usage.completion_tokens_details
                if hasattr(details, 'reasoning_tokens'):
                    self.logger.info(f"  Reasoning: {details.reasoning_tokens}")
        
        self.logger.info(f"Finish Reason: {finish_reason}")
        self.logger.info("=" * 80)
    
    def log_tool_execution(self, tool_name: str, args: Dict[str, Any], result: Dict[str, Any]):
        """Log tool execution with full results (no truncation)."""
        self.logger.info(f"TOOL EXEC | {tool_name}")
        self.logger.debug(f"  Args: {json.dumps(args, indent=2)}")
        # Log full result without truncation
        result_json = json.dumps(result, indent=2)
        self.logger.info(f"  Result:")
        for line in result_json.split('\n'):
            self.logger.info(f"    {line}")
    
    def log_decision(self, player_name: str, decision: Dict[str, Any]):
        """Log final decision made."""
        self.logger.info("-" * 80)
        self.logger.info(f"DECISION | {player_name}")
        self.logger.info(f"  Action: {decision.get('type', 'unknown')}")
        if decision.get('reasoning'):
            self.logger.info(f"  Reasoning: {decision['reasoning']}")
        self.logger.info("-" * 80)


def setup_loggers(game_id: str, log_base_dir: str = "logs") -> tuple[GameLogger, LLMLogger]:
    """
    Set up game and LLM loggers for a game session.
    
    Args:
        game_id: Unique game identifier
        log_base_dir: Base directory for logs (default: "logs")
    
    Returns:
        Tuple of (GameLogger, LLMLogger)
    """
    log_dir = Path(log_base_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    game_logger = GameLogger(log_dir, game_id)
    llm_logger = LLMLogger(log_dir, game_id)
    
    return game_logger, llm_logger
