"""
LLM Agent for playing MTG.
Uses Chain-of-Thought reasoning and tool calling.
"""
import json
import os
from typing import List, Dict, Any, Optional
from core.game_state import GameState
from core.rules_engine import RulesEngine
from tools.game_tools import (
    GetGameStateTool,
    GetLegalActionsTool,
    ExecuteActionTool,
    AnalyzeThreatsTool,
    GetStackStateTool,
    CanRespondTool
)
from tools.evaluation_tools import EvaluatePositionTool
from agent.prompts import SYSTEM_PROMPT, DECISION_PROMPT, MAIN_PHASE_PROMPT, COMBAT_PROMPT

# LLM client imports
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


class MTGAgent:
    """AI Agent that plays Magic: The Gathering."""
    
    def __init__(
        self,
        game_state: GameState,
        rules_engine: RulesEngine,
        llm_client: Any = None,
        verbose: bool = False,
        llm_logger: Any = None,
        use_llm: bool = True,
        aggression: str = "balanced"
    ):
        """
        Initialize the agent.
        
        Args:
            game_state: Current game state
            rules_engine: Rules engine for validation
            llm_client: LLM client (OpenAI, Anthropic, etc.) - if None, will auto-initialize
            verbose: Whether to print reasoning
            llm_logger: LLM logger for recording prompts/responses
            use_llm: Whether to use LLM for decisions (if False, uses rule-based heuristics)
            aggression: Combat aggression level - "conservative", "balanced", or "aggressive"
                       conservative: Only attack with power 3+ or when behind
                       balanced: Attack with power 2+ or when at 30 life or below
                       aggressive: Attack with all creatures every turn
        """
        self.game_state = game_state
        self.rules_engine = rules_engine
        self.verbose = verbose
        self.llm_logger = llm_logger
        self.use_llm = use_llm
        self.aggression = aggression.lower()
        
        # Validate aggression level
        if self.aggression not in ["conservative", "balanced", "aggressive"]:
            print(f"⚠️  Warning: Invalid aggression '{aggression}', defaulting to 'balanced'")
            self.aggression = "balanced"
        
        # Initialize LLM client if not provided (and if we're using LLM)
        if llm_client is None and use_llm:
            self.llm_client = self._initialize_llm_client()
        else:
            self.llm_client = llm_client
        
        # Store provider info
        self.llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.model = self._get_model_name()
        # Thinking mode controls (optional)
        self.thinking_mode = os.getenv("LLM_THINKING", "false").lower() in ("1", "true", "yes", "on")
        self.reasoning_effort = os.getenv("LLM_REASONING_EFFORT", "medium")
        
        # Initialize tools
        self.tools = self._setup_tools()
        
        # Conversation history
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    
    def _initialize_llm_client(self) -> Optional[Any]:
        """Initialize LLM client based on environment configuration."""
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
        
        try:
            if provider == "openrouter":
                if OpenAI is None:
                    raise ImportError("openai package not installed. Run: pip install openai")
                
                api_key = os.getenv("OPENROUTER_API_KEY")
                if not api_key:
                    print("⚠️  Warning: OPENROUTER_API_KEY not set. Using fallback heuristics.")
                    return None
                # Optional thinking mode header for OpenRouter
                default_headers = {
                    "HTTP-Referer": "https://github.com/mtg-player",
                    "X-Title": "MTG AI Player"
                }
                if os.getenv("LLM_THINKING", "false").lower() in ("1", "true", "yes", "on"):
                    # Ask OpenRouter to include provider-specific hidden reasoning when available
                    # This may be ignored for models that don't support it
                    default_headers["X-OpenRouter-Reasoning"] = "true"

                return OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key,
                    default_headers=default_headers
                )
            
            elif provider == "openai":
                if OpenAI is None:
                    raise ImportError("openai package not installed. Run: pip install openai")
                
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    print("⚠️  Warning: OPENAI_API_KEY not set. Using fallback heuristics.")
                    return None
                
                return OpenAI(api_key=api_key)
            
            elif provider == "anthropic":
                if Anthropic is None:
                    raise ImportError("anthropic package not installed. Run: pip install anthropic")
                
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    print("⚠️  Warning: ANTHROPIC_API_KEY not set. Using fallback heuristics.")
                    return None
                
                return Anthropic(api_key=api_key)
            
            elif provider == "ollama":
                if OpenAI is None:
                    raise ImportError("openai package not installed. Run: pip install openai")
                
                base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
                return OpenAI(
                    base_url=base_url,
                    api_key="ollama"  # Ollama doesn't need real key
                )
            
            elif provider == "lmstudio":
                if OpenAI is None:
                    raise ImportError("openai package not installed. Run: pip install openai")
                
                base_url = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
                return OpenAI(
                    base_url=base_url,
                    api_key="lm-studio"  # LM Studio doesn't need real key
                )
            
            else:
                print(f"⚠️  Warning: Unknown LLM provider '{provider}'. Using fallback heuristics.")
                return None
        
        except ImportError as e:
            print(f"⚠️  Warning: {e}. Using fallback heuristics.")
            return None
        except Exception as e:
            print(f"⚠️  Warning: Failed to initialize LLM client: {e}. Using fallback heuristics.")
            return None
    
    def _get_model_name(self) -> str:
        """Get model name based on provider."""
        provider = self.llm_provider
        
        if provider == "openrouter":
            return os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
        elif provider == "openai":
            return os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        elif provider == "anthropic":
            return os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        elif provider == "ollama":
            return os.getenv("OLLAMA_MODEL", "llama3.1")
        elif provider == "lmstudio":
            return os.getenv("LMSTUDIO_MODEL", "local-model")
        else:
            return "unknown"
    
    def _setup_tools(self) -> Dict[str, Any]:
        """Set up available tools."""
        get_game_state = GetGameStateTool()
        get_game_state.game_state = self.game_state
        
        get_legal_actions = GetLegalActionsTool()
        get_legal_actions.game_state = self.game_state
        get_legal_actions.rules_engine = self.rules_engine
        
        execute_action = ExecuteActionTool()
        execute_action.game_state = self.game_state
        execute_action.rules_engine = self.rules_engine
        
        analyze_threats = AnalyzeThreatsTool()
        analyze_threats.game_state = self.game_state
        
        get_stack_state = GetStackStateTool()
        get_stack_state.game_state = self.game_state
        get_stack_state.rules_engine = self.rules_engine
        
        can_respond = CanRespondTool()
        can_respond.game_state = self.game_state
        can_respond.rules_engine = self.rules_engine
        
        evaluate_position = EvaluatePositionTool()
        evaluate_position.game_state = self.game_state
        
        return {
            "get_game_state": get_game_state,
            "get_legal_actions": get_legal_actions,
            "execute_action": execute_action,
            "analyze_threats": analyze_threats,
            "get_stack_state": get_stack_state,
            "can_respond": can_respond,
            "evaluate_position": evaluate_position
        }
    
    def _get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Convert tools to OpenAI function calling format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_game_state",
                    "description": "Get the current game state including turn, phase, players' life totals, cards, and board state.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_legal_actions",
                    "description": "Get all legal actions available to the active player in the current game state.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_action",
                    "description": "Execute a game action. Use this to play lands, cast spells, attack, block, or pass priority.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "object",
                                "description": "The action to execute",
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "enum": ["play_land", "cast_spell", "declare_attackers", "declare_blockers", "pass"],
                                        "description": "Type of action to take"
                                    },
                                    "card_id": {
                                        "type": "string",
                                        "description": "ID of card to play/cast (for play_land, cast_spell)"
                                    },
                                    "attackers": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "List of creature IDs to attack with (for declare_attackers)"
                                    },
                                    "blockers": {
                                        "type": "object",
                                        "description": "Map of blocker_id to attacker_id (for declare_blockers)"
                                    },
                                    "reasoning": {
                                        "type": "string",
                                        "description": "Your reasoning for this action"
                                    }
                                },
                                "required": ["type"]
                            }
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_threats",
                    "description": "Analyze threats and opportunities on the battlefield.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_stack_state",
                    "description": "Get the current state of the stack. Shows all spells on the stack, who has priority, and whether you can respond.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "can_respond",
                    "description": "Check if you can respond to spells on the stack by casting an instant. Returns available instants and recommendations.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "evaluate_position",
                    "description": "Evaluate the current game position and get a strategic assessment. Returns a score (0.0-1.0), position status (winning/losing/even), and detailed breakdown of life totals, board state, mana, card advantage, and threats. Use this to make strategic decisions and assess whether you're ahead or behind.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]
    
    def _make_llm_decision(self) -> Optional[Dict[str, Any]]:
        """
        Make a decision using LLM with tool calling.
        Returns the action to take, or None if passing/no action.
        """
        # If LLM is disabled, use heuristics
        if not self.use_llm or self.llm_client is None:
            if self.verbose:
                print("🎲 Using rule-based AI (no LLM)")
            return self._make_simple_decision()
        
        # Reset conversation for this decision (keep only system prompt)
        self.messages = [self.messages[0]]
        
        # Add phase-specific prompt to messages
        phase_prompt = self._get_phase_specific_prompt()
        self.messages.append({"role": "user", "content": phase_prompt})
        
        try:
            max_iterations = 5
            for iteration in range(max_iterations):
                if self.verbose:
                    print(f"🤖 LLM Iteration {iteration + 1}/{max_iterations}")
                
                # Call LLM based on provider
                if self.llm_provider in ["openai", "openrouter", "ollama", "lmstudio"]:
                    # Build base params
                    # Use higher max_tokens for reasoning models that output long chain-of-thought
                    # Standard models: 2000 tokens is usually enough
                    # Reasoning models (DeepSeek-R1, Qwen3-thinking, o1/o3): need 4000-8000 tokens
                    max_tokens = int(os.getenv("LLM_MAX_TOKENS", "4000"))
                    
                    params: Dict[str, Any] = {
                        "model": self.model,
                        "messages": self.messages,
                        "tools": self._get_tool_schemas(),
                        "tool_choice": "auto",
                        "temperature": 0.7,
                        "max_tokens": max_tokens,
                    }
                    # Optional: enable provider-specific thinking/reasoning
                    if self.thinking_mode:
                        if self.llm_provider == "openai" and ("o3" in (self.model or "") or "reasoning" in (self.model or "")):
                            # OpenAI reasoning models support an optional effort selector
                            params["reasoning"] = {"effort": self.reasoning_effort}

                    # Log LLM call
                    if self.llm_logger:
                        active_player = self.game_state.get_active_player()
                        player_name = active_player.name if active_player else "Unknown"
                        phase_str = f"{self.game_state.current_phase.value}/{self.game_state.current_step.value}"
                        self.llm_logger.log_llm_call(
                            player_name=player_name,
                            turn=self.game_state.turn_number,
                            phase=phase_str,
                            model=self.model,
                            messages=self.messages,
                            tools=self._get_tool_schemas()
                        )

                    response = self.llm_client.chat.completions.create(**params)
                    
                    message = response.choices[0].message
                    
                    # Extract any reasoning/thinking content if present
                    # Different providers/models use different field names for extended reasoning
                    reasoning_content = None
                    thinking_content = None
                    
                    # Check multiple possible reasoning field names (order matters - most specific first)
                    reasoning_fields = [
                        'reasoning_content',  # LM Studio Qwen3-thinking, Ollama reasoning models
                        'reasoning',          # OpenAI o1/o3 series
                        'thinking',           # DeepSeek-R1, some reasoning models
                        'thoughts',           # Some custom models
                        'inner_thoughts',     # Some agent-based models
                        'scratchpad',         # Some fine-tuned reasoning models
                    ]
                    
                    for field in reasoning_fields:
                        if hasattr(message, field):
                            value = getattr(message, field, None)
                            if value:  # Only use non-empty values
                                reasoning_content = value
                                break  # Use first matching field
                    
                    # Check for extended response data (some providers include thinking in metadata)
                    if hasattr(response, 'usage') and hasattr(response.usage, 'completion_tokens_details'):
                        # Some models provide reasoning token counts
                        details = response.usage.completion_tokens_details
                        if hasattr(details, 'reasoning_tokens') and details.reasoning_tokens > 0:
                            thinking_content = f"[Model used {details.reasoning_tokens} reasoning tokens]"
                    
                    # Log response with all available content
                    if self.llm_logger:
                        self.llm_logger.log_llm_response(
                            response_content=message.content,
                            tool_calls=message.tool_calls,
                            finish_reason=response.choices[0].finish_reason,
                            reasoning_content=reasoning_content,
                            thinking_content=thinking_content,
                            usage=response.usage if hasattr(response, 'usage') else None
                        )
                    
                    # If no tool calls, LLM is done reasoning
                    if not message.tool_calls:
                        # Add final message to history
                        self.messages.append({
                            "role": "assistant",
                            "content": message.content or ""
                        })
                        
                        if self.verbose and message.content:
                            print(f"💭 LLM: {message.content}")
                        
                        # Include reasoning in decision if available
                        decision_reasoning = message.content or "No action needed"
                        if reasoning_content:
                            decision_reasoning = f"{decision_reasoning}\n[Reasoning: {reasoning_content[:200]}...]"
                        
                        # Log decision
                        decision = {"type": "pass", "reasoning": decision_reasoning}
                        if self.llm_logger:
                            active_player = self.game_state.get_active_player()
                            player_name = active_player.name if active_player else "Unknown"
                            self.llm_logger.log_decision(player_name, decision)
                        
                        # Parse action from content or return pass
                        return decision
                    
                    # Add assistant message with tool calls to history
                    self.messages.append({
                        "role": "assistant",
                        "content": message.content or "",
                        "tool_calls": [tc.model_dump() for tc in message.tool_calls]
                    })
                    
                    # Collect all tool results before adding to messages
                    tool_results = []
                    action_to_execute = None
                    
                    # Execute tool calls
                    for tool_call in message.tool_calls:
                        function_name = tool_call.function.name
                        try:
                            function_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                        except json.JSONDecodeError:
                            function_args = {}
                        
                        if self.verbose:
                            print(f"🔧 Calling tool: {function_name}({list(function_args.keys())})")
                        
                        # Execute the tool
                        tool = self.tools.get(function_name)
                        if tool:
                            try:
                                result = tool.execute(**function_args)
                                
                                # Log tool execution
                                if self.llm_logger:
                                    self.llm_logger.log_tool_execution(function_name, function_args, result)
                                
                                # Special case: if execute_action was called, save it to return
                                if function_name == "execute_action":
                                    action_to_execute = function_args.get("action", {})
                                    if self.verbose:
                                        print(f"✅ Will execute action: {action_to_execute.get('type')}")
                                
                                # Add tool result
                                tool_results.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": json.dumps(result)
                                })
                            except Exception as e:
                                if self.verbose:
                                    print(f"⚠️  Tool execution error: {e}")
                                tool_results.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": json.dumps({"error": f"Tool execution failed: {str(e)}"})
                                })
                        else:
                            tool_results.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps({"error": f"Unknown tool: {function_name}"})
                            })
                    
                    # Add all tool results to messages
                    self.messages.extend(tool_results)
                    
                    # If execute_action was called, return that action
                    if action_to_execute:
                        if self.llm_logger:
                            active_player = self.game_state.get_active_player()
                            player_name = active_player.name if active_player else "Unknown"
                            self.llm_logger.log_decision(player_name, action_to_execute)
                        return action_to_execute
                
                elif self.llm_provider == "anthropic":
                    # Anthropic has different API - simplified for now
                    # Use configurable max_tokens (same as above)
                    max_tokens = int(os.getenv("LLM_MAX_TOKENS", "4000"))
                    
                    response = self.llm_client.messages.create(
                        model=self.model,
                        max_tokens=max_tokens,
                        messages=self.messages,
                        temperature=0.7
                    )
                    
                    content = response.content[0].text if response.content else ""
                    if self.verbose:
                        print(f"💭 LLM: {content}")
                    
                    return {"type": "pass", "reasoning": content}
        
        except Exception as e:
            print(f"❌ Error calling LLM: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            # Fall back to simple heuristics
            return self._make_simple_decision()
        
        # If we exhausted iterations without a decision, pass
        return {"type": "pass", "reasoning": "Max iterations reached"}
    
    def _get_phase_specific_prompt(self) -> str:
        """Get prompt specific to current game phase."""
        step = self.game_state.current_step.value
        phase = self.game_state.current_phase.value
        
        # Add aggression guidance to the prompt
        aggression_guidance = {
            "aggressive": "\n**AGGRESSION LEVEL: AGGRESSIVE** - Attack with ALL creatures every turn. Maximum pressure!",
            "balanced": "\n**AGGRESSION LEVEL: BALANCED** - Attack when advantageous (power 2+) or when behind on life.",
            "conservative": "\n**AGGRESSION LEVEL: CONSERVATIVE** - Only attack with strong creatures (power 3+) or when desperate."
        }
        
        base_prompt = ""
        if step in ["declare_attackers", "declare_blockers"]:
            base_prompt = COMBAT_PROMPT.format(step=step.upper())
        elif step == "main":
            base_prompt = MAIN_PHASE_PROMPT
        else:
            base_prompt = DECISION_PROMPT.format(phase=phase, step=step)
        
        # Append aggression guidance
        return base_prompt + aggression_guidance.get(self.aggression, "")
    
    def take_turn_action(self) -> bool:
        """
        Take a single action during the turn.
        Returns True if the turn should continue, False if done.
        """
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Agent Decision Point: {self.game_state.current_phase.value}/{self.game_state.current_step.value}")
            print(f"{'='*60}")
        
        # Use LLM to make decision (falls back to heuristics if no LLM)
        action = self._make_llm_decision()
        
        if self.verbose and action:
            print(f"\n🤔 Decision: {action.get('type', 'unknown')}")
            if action.get('reasoning'):
                print(f"💭 Reasoning: {action['reasoning']}")
        
        return action is not None
    
    def _make_simple_decision(self) -> Optional[Dict[str, Any]]:
        """
        Enhanced rule-based decision making that demonstrates agentic flow.
        Uses the same tools as LLM would use, showing the architecture works.
        """
        if self.verbose:
            print("\n🔍 Analyzing game state...")
        
        # Step 1: Get game state (like LLM would)
        game_state_tool = self.tools["get_game_state"]
        state_result = game_state_tool.execute()
        
        if not state_result.get("success"):
            return {"type": "pass", "reasoning": "Could not read game state"}
        
        # Step 2: Check stack state (instant-speed awareness)
        stack_tool = self.tools["get_stack_state"]
        stack_result = stack_tool.execute()
        stack_empty = stack_result.get("is_empty", True)
        
        # Step 3: Analyze threats (strategic awareness)
        threats_tool = self.tools["analyze_threats"]
        threats_result = threats_tool.execute()
        threats = threats_result.get("threats", [])
        
        if self.verbose and threats:
            print(f"⚠️  Identified {len(threats)} threats")
        
        # Step 3.5: Evaluate overall position (new tool)
        position_score = None
        try:
            eval_tool = self.tools.get("evaluate_position")
            if eval_tool:
                eval_result = eval_tool.execute()
                self._position_eval = eval_result  # cache for visibility/debugging
                position_score = eval_result.get("score")
                position_status = eval_result.get("position")
                if self.verbose and position_score is not None:
                    print(f"📊 Position: {position_status or 'unknown'} ({position_score:.2f})")
        except Exception:
            # Do not block heuristic flow if evaluation fails
            position_score = None
        
        # Step 4: Get legal actions
        legal_actions_tool = self.tools["get_legal_actions"]
        actions_result = legal_actions_tool.execute()
        
        if not actions_result.get("success"):
            return {"type": "pass", "reasoning": "No legal actions available"}
        
        actions = actions_result.get("actions", [])
        if not actions:
            return {"type": "pass", "reasoning": "No actions available"}
        
        active_player = self.game_state.get_active_player()
        step = self.game_state.current_step.value
        phase = self.game_state.current_phase.value
        
        if self.verbose:
            print(f"📋 Found {len(actions)} legal actions in {phase}/{step}")
        
        # Step 5: Make intelligent decisions based on phase/step
        decision = None
        
        # Only make decisions during interactive steps
        if step == "main":
            decision = self._decide_main_phase(actions, active_player, threats, position_score)
        elif step == "declare_attackers":
            decision = self._decide_attackers(actions, active_player, threats, position_score)
        elif step == "declare_blockers":
            decision = self._decide_blockers(actions, active_player, threats, position_score)
        else:
            # For non-interactive steps (untap, upkeep, draw, end step, cleanup, etc.)
            # Check if we can respond with instants
            can_respond_tool = self.tools.get("can_respond")
            if can_respond_tool:
                respond_result = can_respond_tool.execute()
                
                if respond_result.get("can_respond") and respond_result.get("available_instants"):
                    decision = self._decide_instant_response(actions, respond_result)
            
            # If no instant response or can't respond, just pass to advance
            if not decision:
                pass_action = next((a for a in actions if a["type"] == "pass"), None)
                if pass_action:
                    self._execute_action(pass_action)
                    if self.verbose:
                        print(f"⏭️  Passing priority in {phase}/{step}")
                    decision = {"type": "pass", "reasoning": f"Passing through {phase}/{step}"}
        
        return decision
    
    def _decide_main_phase(self, actions: list, active_player, threats: list, position_score: float | None = None) -> Dict[str, Any]:
        """Decide what to do during main phase - demonstrates strategic thinking."""
        # Priority 1: Play a land if we haven't yet
        land_actions = [a for a in actions if a["type"] == "play_land"]
        if land_actions and not active_player.has_played_land_this_turn:
            action = land_actions[0]
            self._execute_action(action)
            if self.verbose:
                print(f"🌲 Playing land: {action.get('card_name', 'Land')}")
            return {
                "type": action["type"],
                "card": action.get("card_name"),
                "reasoning": "Ramping: Playing land for mana development"
            }
        
        # Priority 2: Cast removal if there's a threat
        removal_keywords = ["destroy", "exile", "counter", "bounce", "removal"]
        spell_actions = [a for a in actions if a["type"] == "cast_spell"]
        
        if threats and spell_actions:
            # Look for removal spells
            removal_spells = [
                a for a in spell_actions 
                if any(keyword in a.get("card_name", "").lower() for keyword in removal_keywords)
                or any(keyword in a.get("oracle_text", "").lower() for keyword in removal_keywords)
            ]
            
            if removal_spells:
                # Cast cheapest removal
                removal_spells.sort(key=lambda x: self._mana_cost_value(x.get("cost", "")))
                action = removal_spells[0]
                
                if self._can_afford(action, active_player):
                    self._execute_action(action)
                    if self.verbose:
                        print(f"🎯 Casting removal: {action.get('card_name')}")
                    return {
                        "type": action["type"],
                        "card": action.get("card_name"),
                        "reasoning": f"Answering threat with {action.get('card_name')}"
                    }
        
        # Priority 3: Cast creatures (board development)
        creature_actions = [
            a for a in spell_actions 
            if "creature" in a.get("card_types", []) or "Creature" in str(a.get("card_types", []))
        ]
        
        if creature_actions:
            # Cast cheapest creature we can afford
            affordable = [a for a in creature_actions if self._can_afford(a, active_player)]
            if affordable:
                affordable.sort(key=lambda x: self._mana_cost_value(x.get("cost", "")))
                action = affordable[0]
                self._execute_action(action)
                if self.verbose:
                    print(f"🦁 Casting creature: {action.get('card_name')}")
                return {
                    "type": action["type"],
                    "card": action.get("card_name"),
                    "reasoning": f"Building board with {action.get('card_name')}"
                }
        
        # Priority 4: Cast other spells (ramp, draw, etc.)
        if spell_actions:
            affordable = [a for a in spell_actions if self._can_afford(a, active_player)]
            if affordable:
                # Prefer cheaper spells
                affordable.sort(key=lambda x: self._mana_cost_value(x.get("cost", "")))
                action = affordable[0]
                self._execute_action(action)
                if self.verbose:
                    print(f"✨ Casting spell: {action.get('card_name')}")
                return {
                    "type": action["type"],
                    "card": action.get("card_name"),
                    "reasoning": f"Casting {action.get('card_name')} for value"
                }
        
        # Nothing else to do - pass
        pass_action = next((a for a in actions if a["type"] == "pass"), None)
        if pass_action:
            self._execute_action(pass_action)
            if self.verbose:
                print("⏭️  Passing priority - no profitable plays")
            return {
                "type": "pass",
                "reasoning": "No profitable actions available, passing priority"
            }
        
        return {"type": "pass", "reasoning": "End of main phase"}
    
    def _decide_attackers(self, actions: list, active_player, threats: list, position_score: float | None = None) -> Dict[str, Any]:
        """Decide which creatures to attack with - demonstrates combat logic."""
        attack_actions = [a for a in actions if a["type"] == "declare_attacker"]
        
        if not attack_actions:
            pass_action = next((a for a in actions if a["type"] == "pass"), None)
            if pass_action:
                self._execute_action(pass_action)
            return {"type": "pass", "reasoning": "No creatures available to attack"}
        
        # Apply aggression strategy to determine which creatures should attack
        attackers_declared = []
        
        # Adjust aggression based on evaluated position if available
        local_aggression = self.aggression
        if position_score is not None:
            if position_score >= 0.6:
                local_aggression = "aggressive"
            elif position_score <= 0.4:
                local_aggression = "conservative"
            else:
                local_aggression = "balanced"

        for action in attack_actions:
            attacker_power = action.get("power", 0)
            
            # Determine if we should attack based on aggression level
            should_attack = False
            
            if local_aggression == "aggressive":
                # Always attack with everything
                should_attack = True
            elif local_aggression == "balanced":
                # Attack with power 2+ or when at/below 30 life
                should_attack = attacker_power >= 2 or active_player.life <= 30
            else:  # conservative
                # Only attack with strong creatures (3+) or when desperate (20 life or below)
                should_attack = attacker_power >= 3 or active_player.life <= 20
            
            if should_attack:
                self._execute_action(action)
                attackers_declared.append(action.get("creature_name", "creature"))
        
        if attackers_declared:
            if self.verbose:
                aggression_msg = {
                    "aggressive": "ALL-OUT ATTACK",
                    "balanced": "Attacking",
                    "conservative": "Carefully attacking"
                }
                print(f"⚔️  {aggression_msg.get(local_aggression, 'Attacking')} with {len(attackers_declared)} creatures")
            return {
                "type": "declare_attacker",
                "count": len(attackers_declared),
                "reasoning": f"{local_aggression.capitalize()} strategy: attacking with {len(attackers_declared)} creatures"
            }
        else:
            # Decided not to attack - pass
            pass_action = next((a for a in actions if a["type"] == "pass"), None)
            if pass_action:
                self._execute_action(pass_action)
            if self.verbose:
                print("🛡️  Holding back - too risky to attack")
            return {
                "type": "pass",
                "reasoning": "Holding creatures back - attack too risky"
            }
    
    def _decide_blockers(self, actions: list, active_player, threats: list, position_score: float | None = None) -> Dict[str, Any]:
        """Decide how to block - demonstrates defensive logic."""
        block_actions = [a for a in actions if a["type"] == "declare_blocker"]
        
        if not block_actions:
            pass_action = next((a for a in actions if a["type"] == "pass"), None)
            if pass_action:
                self._execute_action(pass_action)
            return {"type": "pass", "reasoning": "No blockers available"}
        
        # Simple blocking strategy: block the biggest attacker we can handle
        # Sort by attacker power (highest first)
        block_actions.sort(key=lambda x: x.get("attacker_power", 0), reverse=True)
        
        blockers_declared = []
        for action in block_actions:
            attacker_power = action.get("attacker_power", 0)
            blocker_toughness = action.get("blocker_toughness", 0)
            
            # Block if we can survive (our toughness >= their power)
            # or if we're desperate (low life)
            should_block = blocker_toughness >= attacker_power or active_player.life <= 15
            
            if should_block:
                self._execute_action(action)
                blockers_declared.append(action.get("blocker_name", "creature"))
                # Only block one attacker per blocker in this simple strategy
                break
        
        if blockers_declared:
            if self.verbose:
                print(f"🛡️  Blocking with {len(blockers_declared)} creatures")
            return {
                "type": "declare_blocker",
                "count": len(blockers_declared),
                "reasoning": f"Blocking {len(blockers_declared)} attacker(s) to prevent damage"
            }
        else:
            # No good blocks - take the damage
            pass_action = next((a for a in actions if a["type"] == "pass"), None)
            if pass_action:
                self._execute_action(pass_action)
            if self.verbose:
                print("💔 No favorable blocks - taking damage")
            return {
                "type": "pass",
                "reasoning": "No favorable blocks available - accepting damage"
            }
    
    def _decide_instant_response(self, actions: list, respond_result: dict) -> Dict[str, Any]:
        """Decide whether to cast instant-speed spells - demonstrates instant interaction."""
        instants = respond_result.get("available_instants", [])
        
        if not instants:
            pass_action = next((a for a in actions if a["type"] == "pass"), None)
            if pass_action:
                self._execute_action(pass_action)
            return {"type": "pass", "reasoning": "No instant-speed responses available"}
        
        # Simple heuristic: cast instant if it's a counterspell or removal
        priority_keywords = ["counter", "destroy", "exile", "return"]
        
        for instant in instants:
            card_name = instant.get("name", "").lower()
            oracle_text = instant.get("oracle_text", "").lower()
            
            # Check if it's a high-priority instant
            if any(keyword in card_name or keyword in oracle_text for keyword in priority_keywords):
                # Try to cast it
                cast_actions = [a for a in actions if a["type"] == "cast_spell" and a.get("card_name") == instant.get("name")]
                if cast_actions:
                    action = cast_actions[0]
                    self._execute_action(action)
                    if self.verbose:
                        print(f"⚡ Responding with instant: {instant.get('name')}")
                    return {
                        "type": "cast_spell",
                        "card": instant.get("name"),
                        "reasoning": f"Responding with instant-speed {instant.get('name')}"
                    }
        
        # No good instants to cast - pass
        pass_action = next((a for a in actions if a["type"] == "pass"), None)
        if pass_action:
            self._execute_action(pass_action)
        return {"type": "pass", "reasoning": "Holding instant-speed spells"}
    
    def _can_afford(self, action: Dict[str, Any], player) -> bool:
        """Check if player can afford to cast this spell with proper color requirements."""
        cost_str = action.get("cost", "")
        if not cost_str:
            return True
        
        # Parse cost string like "{2}{W}{U}" → 2 generic, 1 white, 1 blue
        import re
        
        # Extract numbers (generic mana)
        generic_cost = sum(int(n) for n in re.findall(r'\d+', cost_str))
        
        # Extract colored mana symbols
        white_cost = cost_str.count('{W}') + cost_str.count('W')
        blue_cost = cost_str.count('{U}') + cost_str.count('U')
        black_cost = cost_str.count('{B}') + cost_str.count('B')
        red_cost = cost_str.count('{R}') + cost_str.count('R')
        green_cost = cost_str.count('{G}') + cost_str.count('G')
        
        # Get available mana
        available = player.available_mana()
        
        # Check colored requirements
        if white_cost > available.white:
            return False
        if blue_cost > available.blue:
            return False
        if black_cost > available.black:
            return False
        if red_cost > available.red:
            return False
        if green_cost > available.green:
            return False
        
        # Check total mana (generic can be paid with any color)
        total_colored = white_cost + blue_cost + black_cost + red_cost + green_cost
        total_cost = generic_cost + total_colored
        
        return available.total() >= total_cost
    
    def _mana_cost_value(self, cost_str: str) -> int:
        """Convert mana cost string to numeric value for comparison."""
        if not cost_str:
            return 0
        
        generic = sum(int(c) for c in cost_str if c.isdigit())
        colored = sum(1 for c in cost_str if c.isalpha())
        return generic + colored
    
    def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action using the tool."""
        execute_tool = self.tools["execute_action"]
        
        # Execute with the action dict (matches ExecuteActionTool.execute signature)
        result = execute_tool.execute(action=action)
        
        if self.verbose:
            if result.get("success"):
                print(f"✅ {result.get('message', 'Action succeeded')}")
            else:
                print(f"❌ {result.get('error', 'Action failed')}")
        
        return result
    
    def analyze_position(self) -> Dict[str, Any]:
        """Analyze current position using tools."""
        game_state_tool = self.tools["get_game_state"]
        threats_tool = self.tools["analyze_threats"]
        
        game_state = game_state_tool.execute()
        threats = threats_tool.execute()
        
        return {
            "game_state": game_state,
            "threats": threats
        }
