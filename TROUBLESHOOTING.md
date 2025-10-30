# Troubleshooting Guide

Common issues and their solutions when running the MTG Commander AI.

---

## Import Errors

### Error: `ImportError: attempted relative import beyond top-level package`

**Problem**: Python can't resolve the relative imports when running the script directly.

**Solution**: Use the provided `run.py` script or set PYTHONPATH:

```bash
# Method 1: Use run.py (recommended)
python run.py --verbose

# Method 2: Set PYTHONPATH
PYTHONPATH=./src python src/main.py --verbose

# Method 3: On Windows
set PYTHONPATH=./src
python src/main.py --verbose
```

---

## Pydantic Errors

### Error: `ValueError: "Tool" object has no field "game_state"`

**Problem**: Older version of Pydantic or incorrect model configuration.

**Solution**: Make sure you have Pydantic v2+ installed:

```bash
pip install --upgrade pydantic>=2.0.0
```

---

## Module Not Found

### Error: `ModuleNotFoundError: No module named 'core'` or similar

**Problem**: Python can't find the src modules.

**Solution**: 
1. Make sure you're in the project root directory
2. Use the `run.py` script
3. Or set PYTHONPATH as shown above

```bash
# Check you're in the right directory
pwd
# Should show: /Users/yourname/git/mtg-player

# Run from project root
python run.py
```

---

## Virtual Environment Issues

### Error: `zsh: command not found: python`

**Problem**: Virtual environment not activated or Python not installed.

**Solution**:

```bash
# Activate virtual environment
source venv/bin/activate  # or .venv/bin/activate

# On Windows
venv\Scripts\activate

# Verify activation (should show venv path)
which python

# If venv doesn't exist, create it
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Dependency Errors

### Error: `ModuleNotFoundError: No module named 'pydantic'`

**Problem**: Dependencies not installed.

**Solution**:

```bash
# Install all dependencies
pip install -r requirements.txt

# Or install specific package
pip install pydantic
```

---

## Game Logic Errors

### Error: Game crashes during combat or spell casting

**Problem**: This is expected in the PoC - not all rules are implemented yet.

**Solution**: This is Phase 1. Many complex interactions aren't coded yet. Continue playing or restart the game.

---

## LLM Integration Issues

### Error: `openai.AuthenticationError: Invalid API key`

**Problem**: API key not set or incorrect.

**Solution**:

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env and add your key
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-your-actual-key-here

# 3. Verify .env file exists and has your key
cat .env | grep API_KEY
```

### Error: `No module named 'openai'`

**Problem**: LLM library not installed.

**Solution**:

```bash
# For OpenAI
pip install openai

# For Anthropic
pip install anthropic

# For OpenRouter (uses openai library)
pip install openai
```

---

## Performance Issues

### Problem: Game runs very slowly

**Cause**: LLM calls can be slow, especially with large context.

**Solution**:
1. Use faster models (e.g., `gpt-3.5-turbo` instead of `gpt-4`)
2. For OpenRouter, try `llama-3.1-8b` for testing
3. Reduce `MAX_TURNS` in `.env`
4. Use the simple heuristic AI (no LLM) for faster testing

---

## Testing Issues

### Error when running `pytest`

**Problem**: Test dependencies missing or import issues.

**Solution**:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests with PYTHONPATH set
PYTHONPATH=./src pytest

# Or run specific test
PYTHONPATH=./src pytest tests/test_rules_engine.py -v
```

---

## Type Checking (mypy) Issues

### Error: `Source file found twice under different module names: "src.core..." and "core..."`

**Cause**: src/ layout without explicit package bases.

**Solution**: Use the provided mypy.ini with `explicit_package_bases = True` and run mypy against `src`:

```bash
python -m mypy --config-file mypy.ini src
```

### Error: Missing type stubs for requests

**Solution**:

```bash
pip install types-requests
```

---

## macOS/Linux Specific

### Permission denied when running scripts

**Solution**:

```bash
# Make scripts executable
chmod +x run.py

# Then run
./run.py --verbose
```

---

## Windows Specific

### Error: `'python' is not recognized`

**Solution**:

```bash
# Use python3 or py
python3 run.py --verbose

# Or
py run.py --verbose
```

### Error: PYTHONPATH not working

**Solution**:

```cmd
# Use set instead of export
set PYTHONPATH=./src
python src/main.py --verbose

# Or use PowerShell
$env:PYTHONPATH="./src"
python src/main.py --verbose
```

---

## Still Having Issues?

### Debug Steps:

1. **Verify installation**:
```bash
python --version  # Should be 3.11+
pip list | grep pydantic  # Should show pydantic 2.x
```

2. **Check file structure**:
```bash
ls -la src/
# Should show: core/, agent/, tools/, data/, main.py
```

3. **Test imports manually**:
```bash
PYTHONPATH=./src python -c "from core.card import Card; print('OK')"
```

4. **Run with maximum verbosity**:
```bash
python run.py --verbose 2>&1 | tee output.log
# Check output.log for errors
```

5. **Fresh start**:
```bash
# Remove and recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py --verbose
```

---

## Getting Help

If you're still stuck:

1. Check the error message carefully
2. Look for similar issues in the documentation
3. Try the "Fresh start" approach above
4. Check that you're using Python 3.11 or later
5. Verify all files are present in the correct structure

Remember: This is a learning project and a proof-of-concept. Some rough edges are expected! 🎲
