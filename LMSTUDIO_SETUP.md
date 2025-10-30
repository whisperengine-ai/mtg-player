# LM Studio Configuration Guide

## What is LM Studio?

[LM Studio](https://lmstudio.ai) is a desktop application that lets you run large language models (LLMs) locally on your computer. It provides an OpenAI-compatible API server, making it a drop-in replacement for cloud LLM providers - perfect for:
- 🔒 **Privacy**: All computation happens on your machine
- 💰 **Zero API costs**: No per-token charges
- 🚀 **Low latency**: No network round-trips
- 🔌 **Offline use**: Works without internet
- 🎛️ **Full control**: Adjust parameters, use quantized models

## Prerequisites

- **Hardware**: 
  - Minimum: 16GB RAM for 7B models
  - Recommended: 32GB+ RAM for 13B models
  - Ideal: 64GB+ RAM or GPU with 8GB+ VRAM for larger models
- **Storage**: 5-20GB per model (depends on quantization)
- **OS**: Windows, macOS, or Linux

## Setup

### 1. Install LM Studio

1. Download from [https://lmstudio.ai](https://lmstudio.ai)
2. Install and launch the application
3. Browse and download a model (see recommendations below)

### 2. Start the Local Server

1. In LM Studio, click the **"Local Server"** tab (left sidebar)
2. Select your downloaded model from the dropdown
3. Click **"Start Server"**
4. Server will start on `http://localhost:1234` by default
5. Keep LM Studio running while using the MTG AI

### 3. Configure `.env`

```bash
# Use LM Studio as provider
LLM_PROVIDER=lmstudio

# Local server URL (default: http://localhost:1234/v1)
LMSTUDIO_BASE_URL=http://localhost:1234/v1

# Model name (use the model identifier shown in LM Studio)
# Common examples: "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF"
# Or just use a simple name like "local-model"
LMSTUDIO_MODEL=local-model

# Game settings
MAX_TURNS=20
VERBOSE=true
```

### 4. Run the Game

```bash
# Make sure LM Studio server is running first!
python run.py --verbose
```

## Recommended Models for MTG AI

LM Studio uses GGUF quantized models for efficiency. Look for models with **"Instruct"** in the name (fine-tuned for following instructions).

### Best for MTG Strategy (13B+ parameters)

**Meta Llama 3.1 13B Instruct** (Recommended)
- Model: `lmstudio-community/Meta-Llama-3.1-13B-Instruct-GGUF`
- Quant: `Q4_K_M` (8GB RAM) or `Q6_K` (10GB RAM)
- Excellent reasoning and game strategy
- Good tool calling support

**Qwen 2.5 14B Instruct**
- Model: `lmstudio-community/Qwen2.5-14B-Instruct-GGUF`
- Quant: `Q4_K_M` (9GB RAM)
- Strong logical reasoning
- Great at complex decision making

### Good for Testing (7B-8B parameters)

**Meta Llama 3.1 8B Instruct** (Budget-friendly)
- Model: `lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF`
- Quant: `Q4_K_M` (5GB RAM) or `Q8_0` (8GB RAM)
- Fast inference, lower resource usage
- Decent for simpler game states

**Mistral 7B Instruct**
- Model: `TheBloke/Mistral-7B-Instruct-v0.2-GGUF`
- Quant: `Q4_K_M` (5GB RAM)
- Fast and efficient
- Good instruction following

### Budget Option (3B-4B parameters)

**Phi-3 Mini 3.8B Instruct**
- Model: `microsoft/Phi-3-mini-4k-instruct-gguf`
- Quant: `Q4_K_M` (3GB RAM)
- Surprisingly capable for its size
- Great for testing on limited hardware

## Quantization Guide

GGUF models come in different quantization levels (compression):

| Quant | Quality | RAM Usage | Speed | Recommendation |
|-------|---------|-----------|-------|----------------|
| Q4_K_M | Good | ~5-8GB | Fast | ⭐ Best balance |
| Q5_K_M | Better | ~6-9GB | Medium | Good if you have RAM |
| Q6_K | Great | ~7-10GB | Slower | High quality |
| Q8_0 | Excellent | ~8-12GB | Slow | Maximum quality |
| Q3_K_M | Fair | ~4-6GB | Very fast | Budget option |

**Recommendation**: Start with `Q4_K_M` for best speed/quality balance.

## Performance Tips

### 1. Model Selection
- **7B models**: 2-5 seconds per decision (good for testing)
- **13B models**: 5-15 seconds per decision (better strategy)
- **30B+ models**: 20-60+ seconds per decision (requires powerful hardware)

### 2. LM Studio Settings

In LM Studio's "Local Server" settings, adjust:
- **Context Length**: 4096-8192 (longer for complex games)
- **GPU Offload**: Max layers if you have a GPU
- **Threads**: Match your CPU core count
- **Temperature**: 0.7-0.8 (balance creativity and consistency)

### 3. MTG Game Settings

```bash
# Shorter games for faster testing
python run.py --max-turns=5 --players=2 --verbose

# Use heuristic mode for comparison
python run.py --no-llm --verbose
```

## Troubleshooting

### "Connection refused" error
- ✅ Make sure LM Studio is running
- ✅ Check server is started in LM Studio
- ✅ Verify URL in `.env` matches LM Studio's server URL

### Slow responses
- Try a smaller model (7B instead of 13B)
- Use a more aggressive quantization (Q4_K_M instead of Q6_K)
- Enable GPU offloading in LM Studio settings
- Reduce game complexity (fewer players, shorter turns)

### Out of memory
- Use a smaller model
- Use more aggressive quantization (Q3_K_M or Q4_K_M)
- Close other applications
- Reduce context length in LM Studio settings

### Model not following instructions
- Make sure you're using an **"Instruct"** model variant
- Try a different model (Llama 3.1 is generally reliable)
- Increase temperature slightly (0.7-0.9)
- Check LM Studio's system prompt settings

## Comparison: LM Studio vs Cloud LLMs

### LM Studio Advantages ✅
- 🔒 Complete privacy (data never leaves your machine)
- 💰 Zero ongoing costs (no API fees)
- 🚀 Low latency (no network delays)
- 🔌 Works offline
- 🎛️ Full control over model parameters

### LM Studio Limitations ⚠️
- 🖥️ Requires decent hardware (16GB+ RAM recommended)
- ⏱️ Slower inference than cloud GPUs (especially for large models)
- 📦 Models take up significant disk space (5-20GB each)
- 🎯 Generally less capable than GPT-4/Claude 3.5 (but still very good!)

### Performance Comparison (MTG AI)

| Provider | Quality | Speed | Cost | Privacy |
|----------|---------|-------|------|---------|
| GPT-4 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | $$$$$ | ❌ |
| Claude 3.5 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | $$$$ | ❌ |
| LM Studio (13B) | ⭐⭐⭐⭐ | ⭐⭐⭐ | Free | ✅ |
| LM Studio (7B) | ⭐⭐⭐ | ⭐⭐⭐⭐ | Free | ✅ |
| Heuristic Mode | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Free | ✅ |

## Example Workflow

```bash
# 1. Download and start Llama 3.1 8B in LM Studio
# 2. Configure .env
cat > .env << EOF
LLM_PROVIDER=lmstudio
LMSTUDIO_BASE_URL=http://localhost:1234/v1
LMSTUDIO_MODEL=local-model
EOF

# 3. Test with a quick game
python run.py --players=2 --max-turns=5 --verbose

# 4. Run a full game
python run.py --players=4 --max-turns=50 --verbose --aggression=balanced
```

## Additional Resources

- [LM Studio Documentation](https://lmstudio.ai/docs)
- [GGUF Model Hub](https://huggingface.co/models?library=gguf)
- [Llama 3.1 Model Card](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct)
- [Quantization Explained](https://huggingface.co/docs/optimum/concept_guides/quantization)

## Next Steps

1. Try running a game with LM Studio
2. Experiment with different models and quantizations
3. Compare performance with heuristic mode (`--no-llm`)
4. See [ARCHITECTURE.md](ARCHITECTURE.md) for more on the agentic AI design
5. Check [ROADMAP.md](ROADMAP.md) for future improvements

---

**Pro Tip**: Start with Llama 3.1 8B Q4_K_M for the best first experience - it's fast, capable, and runs on most modern computers! 🚀
