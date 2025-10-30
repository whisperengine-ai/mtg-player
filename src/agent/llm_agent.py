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
        verbose: bool = False
    ):
        """
        Initialize the agent.
        
        Args:
            game_state: Current game state
            rules_engine: Rules engine for validation
            llm_client: LLM client (OpenAI, Anthropic, etc.) - if None, will auto-initialize
            verbose: Whether to print reasoning
        """
        self.game_state = game_state
        self.rules_engine = rules_engine
        self.verbose = verbose
        
        # Initialize LLM client if not provided
        if llm_client is None:
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
        
        return {
            "get_game_state": get_game_state,
            "get_legal_actions": get_legal_actions,
            "execute_action": execute_action,
            "analyze_threats": analyze_threats,
            "get_stack_state": get_stack_state,
            "can_respond": can_respond
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
            }
        ]
    
    def _make_llm_decision(self) -> Optional[Dict[str, Any]]:
        """
        Make a decision using LLM with tool calling.
        Returns the action to take, or None if passing/no action.
        """
        if self.llm_client is None:
            # Fall back to simple heuristics if no LLM available
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
                if self.llm_provider in ["openai", "openrouter", "ollama"]:
                    # Build base params
                    params: Dict[str, Any] = {
                        "model": self.model,
                        "messages": self.messages,
                        "tools": self._get_tool_schemas(),
                        "tool_choice": "auto",
                        "temperature": 0.7,
                        "max_tokens": 2000,
                    }
                    # Optional: enable provider-specific thinking/reasoning
                    if self.thinking_mode:
                        if self.llm_provider == "openai" and ("o3" in (self.model or "") or "reasoning" in (self.model or "")):
                            # OpenAI reasoning models support an optional effort selector
                            params["reasoning"] = {"effort": self.reasoning_effort}

                    response = self.llm_client.chat.completions.create(**params)
                    
                    message = response.choices[0].message
                    
                    # If no tool calls, LLM is done reasoning
                    if not message.tool_calls:
                        # Add final message to history
                        self.messages.append({
                            "role": "assistant",
                            "content": message.content or ""
                        })
                        
                        if self.verbose and message.content:
                            print(f"💭 LLM: {message.content}")
                        # Parse action from content or return pass
                        return {"type": "pass", "reasoning": message.content or "No action needed"}
                    
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
                        return action_to_execute
                
                elif self.llm_provider == "anthropic":
                    # Anthropic has different API - simplified for now
                    response = self.llm_client.messages.create(
                        model=self.model,
                        max_tokens=2000,
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
        
        if step in ["declare_attackers", "declare_blockers"]:
            return COMBAT_PROMPT.format(step=step.upper())
        elif step == "main":
            return MAIN_PHASE_PROMPT
        else:
            return DECISION_PROMPT.format(phase=phase, step=step)
    
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
        Simple rule-based decision making for PoC.
        Replace this with LLM calls in full implementation.
        """
        # Get available actions
        legal_actions_tool = self.tools["get_legal_actions"]
        result = legal_actions_tool.execute()
        
        if not result.get("success"):
            return None
        
        actions = result.get("actions", [])
        if not actions:
            return None
        
        active_player = self.game_state.get_active_player()
        step = self.game_state.current_step.value
        
        # Main phase logic
        if step == "main":
            # 1. Play a land if possible
            land_actions = [a for a in actions if a["type"] == "play_land"]
            if land_actions and not active_player.has_played_land_this_turn:
                action = land_actions[0]
                self._execute_action(action)
                return {
                    "type": action["type"],
                    "reasoning": "Playing a land to increase mana availability"
                }
            
            # 2. Cast a cheap spell
            spell_actions = [a for a in actions if a["type"] == "cast_spell"]
            if spell_actions:
                # Sort by cost, cast cheapest
                spell_actions.sort(key=lambda x: x.get("cost", "{99}"))
                action = spell_actions[0]
                
                # First tap lands for mana
                available_mana = active_player.available_mana().total()
                required = len([c for c in action.get("cost", "") if c.isdigit()])
                
                if available_mana >= required:
                    self._execute_action(action)
                    return {
                        "type": action["type"],
                        "reasoning": f"Casting {action.get('card_name')} to develop board"
                    }
            
            # 3. Pass if nothing else to do
            pass_action = [a for a in actions if a["type"] == "pass"][0]
            self._execute_action(pass_action)
            return {
                "type": "pass",
                "reasoning": "No profitable actions, passing priority"
            }
        
        # Combat: Declare attackers
        elif step == "declare_attackers":
            attack_actions = [a for a in actions if a["type"] == "declare_attacker"]
            
            if attack_actions:
                # Simple: attack with all creatures
                for action in attack_actions:
                    self._execute_action(action)
                
                if attack_actions:
                    return {
                        "type": "declare_attacker",
                        "reasoning": f"Attacking with {len(attack_actions)} creatures to apply pressure"
                    }
            
            # Pass if no attackers
            pass_action = [a for a in actions if a["type"] == "pass"][0]
            self._execute_action(pass_action)
            return {
                "type": "pass",
                "reasoning": "No creatures able to attack"
            }
        
        # Combat: Declare blockers
        elif step == "declare_blockers":
            block_actions = [a for a in actions if a["type"] == "declare_blocker"]
            
            if block_actions:
                # Simple: block with first available blocker
                action = block_actions[0]
                self._execute_action(action)
                return {
                    "type": "declare_blocker",
                    "reasoning": f"Blocking to prevent damage"
                }
            
            # Pass if no blocks needed
            pass_action = [a for a in actions if a["type"] == "pass"][0]
            self._execute_action(pass_action)
            return {
                "type": "pass",
                "reasoning": "No blocks needed or no blockers available"
            }
        
        # Default: pass
        else:
            pass_action = [a for a in actions if a["type"] == "pass"][0]
            self._execute_action(pass_action)
            return {
                "type": "pass",
                "reasoning": "Passing through non-interactive phase"
            }
    
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
