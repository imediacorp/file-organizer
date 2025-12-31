# Performance Tips for Eratosthenes AI

## Ollama Performance Issues

If Ollama is sluggish, here are ways to optimize:

## 1. Use a Faster Model

**Current models available:**
- `llama3.1:latest` - Good quality but slower
- `gemma3:4b` - Faster, lighter model
- `minimax-m2:cloud` - Cloud model (may be faster)

**Switch to a faster model:**
```bash
export OLLAMA_MODEL=gemma3:4b
file-organizer preview ai_suggested "04-Financial"
```

## 2. Reduce Batch Size

Smaller batches = faster per-batch processing:

**Create `ai_config.yaml`:**
```yaml
strategies:
  ai_suggested:
    batch_size: 3  # Smaller = faster per batch (default: 5)
    max_files: 20  # Limit total files analyzed (default: 50)
    confidence_threshold: 0.7  # Higher = fewer suggestions = faster
```

## 3. Limit Files Analyzed

Use `--target-folder` to analyze specific subdirectories:

```bash
# Analyze just one folder instead of entire directory
file-organizer preview ai_suggested "04-Financial" --target-folder "04-Financial/Invoices & Receipts"
```

## 4. Use Two-Stage Approach (Recommended)

**Stage 1: Fast bulk organization**
```bash
file-organizer organize filetype "04-Financial"
# Takes: ~30 seconds for 1000 files
```

**Stage 2: AI refinement on smaller subset**
```bash
# Only refine specific folders
file-organizer preview ai_suggested "04-Financial" --target-folder "04-Financial/Invoices & Receipts"
# Takes: ~2-3 minutes for 20 files
```

## 5. Increase Timeout

If requests are timing out, increase timeout in config:

```yaml
ai:
  providers:
    ollama:
      timeout: 60  # Increase from default 30
      timeout_quick: 30
```

## 6. Check Ollama Performance

**Test Ollama speed:**
```bash
time ollama run llama3.1:latest "Say hello"
```

**If slow, try:**
- Restart Ollama: `pkill ollama && ollama serve`
- Use smaller model: `gemma3:4b` or `llama3.1:8b` (if available)
- Check system resources: `top` or Activity Monitor

## 7. Use Caching

Caching is enabled by default. First run is slow, subsequent runs are fast:

```bash
# First run (slow - analyzes)
file-organizer preview ai_suggested "04-Financial"

# Second run (fast - uses cache)
file-organizer preview ai_suggested "04-Financial"
```

## 8. Quick Mode for Testing

For quick testing, use smaller batches and fewer files:

```python
# In Python
from file_organizer import FileOrganizer
from pathlib import Path

organizer = FileOrganizer(Path('04-Financial'))
# Use custom config with small batch size
config = {
    'strategies': {
        'ai_suggested': {
            'batch_size': 2,
            'max_files': 10,
        }
    }
}
preview = organizer.preview('ai_suggested', strategy_config=config)
```

## Recommended Settings for Speed

**Fast but less accurate:**
```yaml
strategies:
  ai_suggested:
    batch_size: 2
    max_files: 10
    confidence_threshold: 0.8  # Only high-confidence moves
```

**Balanced:**
```yaml
strategies:
  ai_suggested:
    batch_size: 5
    max_files: 30
    confidence_threshold: 0.7
```

**Thorough (slower):**
```yaml
strategies:
  ai_suggested:
    batch_size: 10
    max_files: 100
    confidence_threshold: 0.6
```

## Alternative: Use Cloud Providers

If local Ollama is too slow, consider cloud providers (faster but requires API keys):

```yaml
ai:
  provider: "gemini"  # or "openai", "anthropic"
  providers:
    gemini:
      api_key: "${GEMINI_API_KEY}"
      model: "gemini-1.5-flash"  # Very fast
```

## Summary

**For best performance:**
1. Use faster model (`gemma3:4b`)
2. Reduce batch size (2-3 files)
3. Limit total files (10-20)
4. Use two-stage approach (bulk first, then AI refinement)
5. Analyze specific folders, not entire directory
6. Enable caching (already on by default)

