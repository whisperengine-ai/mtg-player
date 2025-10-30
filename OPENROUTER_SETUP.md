# OpenRouter Configuration Example

## What is OpenRouter?

[OpenRouter](https://openrouter.ai) is a unified API that provides access to multiple LLM providers (OpenAI, Anthropic, Meta, Google, etc.) through a single OpenAI-compatible API. Perfect for:
- Cost optimization (choose cheaper models)
- Fallback options (if one model is down)
- Easy model comparison
- Access to open-source models

## Setup

### 1. Get API Key
1. Sign up at [https://openrouter.ai](https://openrouter.ai)
2. Go to [Keys](https://openrouter.ai/keys)
3. Create a new API key (starts with `sk-or-v1-...`)
4. Add credits to your account

### 2. Configure `.env`

```bash
# Use OpenRouter as provider
LLM_PROVIDER=openrouter

# Your OpenRouter API key
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx

# Choose your model (see options below)
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Optional: for usage tracking on OpenRouter dashboard
OPENROUTER_SITE_URL=https://github.com/yourusername/mtg-player
OPENROUTER_APP_NAME=MTG-Commander-AI

# Game settings
MAX_TURNS=20
VERBOSE=true
```

## Recommended Models for MTG AI

### Best Quality (Higher Cost)
- `anthropic/claude-3.5-sonnet` - Best reasoning, great for strategy (~$3/M tokens)
- `openai/gpt-4-turbo` - Strong all-around performance (~$10/M tokens)
- `openai/gpt-4o` - Latest GPT-4 model (~$5/M tokens)

### Great Value (Medium Cost)
- `meta-llama/llama-3.1-70b-instruct` - Excellent open-source model (~$0.80/M tokens)
- `qwen/qwen-2.5-72b-instruct` - Great for complex reasoning (~$0.80/M tokens)
- `google/gemini-pro-1.5` - Large context, good reasoning (~$1.25/M tokens)

### Budget Options (Low Cost)
- `meta-llama/llama-3.1-8b-instruct` - Fast, cheap, decent quality (~$0.10/M tokens)
- `mistralai/mistral-7b-instruct` - Good for simpler decisions (~$0.10/M tokens)
- `qwen/qwen-2.5-7b-instruct` - Solid budget option (~$0.10/M tokens)

### Extended Thinking (For Complex Games)
- `anthropic/claude-3.5-sonnet:beta` - Extended thinking mode
- `openai/o1-preview` - Long reasoning chains (more expensive)

## Example Code Integration

### In `src/agent/llm_agent.py`:

```python
import os
from openai import OpenAI

class MTGAgent:
    def __init__(self, game_state, rules_engine, llm_provider="openrouter", verbose=False):
        self.game_state = game_state
        self.rules_engine = rules_engine
        self.verbose = verbose
        
        # Initialize LLM client based on provider
        if llm_provider == "openrouter":
            self.llm_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY"),
                default_headers={
                    "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", ""),
                    "X-Title": os.getenv("OPENROUTER_APP_NAME", "MTG-AI"),
                }
            )
            self.model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
        elif llm_provider == "openai":
            self.llm_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        # ... other providers ...
        
        self.tools = self._setup_tools()
    
    def _call_llm(self, messages, tools=None):
        """Call the LLM with optional tool use."""
        params = {
            "model": self.model,
            "messages": messages,
        }
        
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        
        response = self.llm_client.chat.completions.create(**params)
        return response
```

## Cost Estimates

For a typical game (10-20 turns):
- **Input tokens**: ~5,000-10,000 (game state + history)
- **Output tokens**: ~2,000-5,000 (reasoning + actions)

### Example costs per game:
- Claude 3.5 Sonnet: ~$0.05-0.10 per game
- Llama 3.1 70B: ~$0.01-0.02 per game
- Llama 3.1 8B: ~$0.001-0.002 per game

**Testing tip**: Start with cheaper models (Llama 8B) for development, then upgrade to Claude/GPT-4 for final testing.

## Testing Your Setup

```python
# test_openrouter.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

response = client.chat.completions.create(
    model="anthropic/claude-3.5-sonnet",
    messages=[
        {"role": "user", "content": "Say 'OpenRouter is working!' in exactly those words."}
    ]
)

print(response.choices[0].message.content)
```

Run with:
```bash
python test_openrouter.py
```

## Monitoring Usage

1. Visit [OpenRouter Dashboard](https://openrouter.ai/activity)
2. View your requests, costs, and model performance
3. Track which models work best for your use case

## Troubleshooting

### Error: "Invalid API Key"
- Check your API key in `.env`
- Make sure it starts with `sk-or-v1-`
- Verify you have credits in your account

### Error: "Model not found"
- Check model name at [OpenRouter Models](https://openrouter.ai/models)
- Some models require special access
- Try a different model

### Slow responses
- Some models are slower (especially extended thinking)
- Try a faster model like `llama-3.1-70b`
- Consider model-specific timeout settings

## Advanced: Model Routing

OpenRouter supports automatic routing to find the best model:

```python
# Let OpenRouter choose the best model
OPENROUTER_MODEL=openrouter/auto

# Or choose based on budget
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet:beta?fallbacks=meta-llama/llama-3.1-70b
```

## Resources

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [Model List & Pricing](https://openrouter.ai/models)
- [OpenRouter Discord](https://discord.gg/openrouter)
- [API Reference](https://openrouter.ai/docs/api-reference)

---

**Pro Tip**: Use OpenRouter's model rankings to see which models perform best for reasoning tasks similar to MTG strategy!
