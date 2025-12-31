# Eratosthenes - Acting on AI Recommendations

## Overview

Eratosthenes can both **suggest** organization improvements (advisory mode) and **execute** organization based on AI analysis (action mode).

## Recommended Workflow

**Best Practice: Two-Stage Organization**

1. **Stage 1: Initial Organization** (Fast, rule-based)
   - Use `filetype` or `rule_based` strategies for bulk organization
   - These are fast and handle the majority of files quickly
   - Example: `file-organizer organize filetype "04-Financial"`

2. **Stage 2: AI Refinement** (Slower, intelligent)
   - Use `ai_suggested` strategy to refine and improve
   - AI can suggest better naming, metadata extraction, and fine-tuned organization
   - Example: `file-organizer organize ai_suggested "04-Financial"`

**Why this approach?**
- Initial organization is fast and handles obvious cases
- AI refinement focuses on optimization rather than bulk work
- More efficient use of AI resources
- Better user experience with faster initial results

## Two Modes of Operation

### 1. Advisory Mode (Suggestions Only)
Get recommendations without making changes:
```bash
file-organizer suggest "04-Financial" --max-files 10
```

### 2. Action Mode (Execute AI Recommendations)
Actually organize files based on AI analysis:
```bash
# Preview what AI would do
file-organizer preview ai_suggested "04-Financial"

# Execute AI organization
file-organizer organize ai_suggested "04-Financial"
```

## Step-by-Step: Acting on Recommendations

### Recommended: Two-Stage Workflow

**Stage 1: Fast Initial Organization**
```bash
# Organize by file type first (fast)
file-organizer organize filetype "04-Financial"

# Or use rule-based organization
file-organizer organize rule_based "04-Financial" --config config.yaml
```

**Stage 2: AI Refinement**
```bash
# Then use AI to refine and optimize
file-organizer preview ai_suggested "04-Financial"
file-organizer organize ai_suggested "04-Financial"
```

### Step 1: Preview AI Suggestions (Recommended First!)

Always preview before executing:

```bash
file-organizer preview ai_suggested "04-Financial"
```

**Note:** AI analysis takes time. You'll see progress indicators:
- Batch processing status
- Number of files analyzed
- Suggestions generated
- Confidence filtering results

This shows you:
- Which files will be moved
- Where they'll be moved to
- Confidence scores for each suggestion
- Reasoning for each move

**Example output:**
```
Preview: 10 operations would be performed

1. 04-Financial/Invoices & Receipts/Amazon Invoice.pdf 
   -> 04-Financial/Invoices & Receipts/2024/2024-01-15_Invoice_Amazon.pdf
   Confidence: 0.9
   Reasoning: Invoice should be organized chronologically with descriptive filename

2. 04-Financial/Taxes/2024_Tax_Return.pdf
   -> 04-Financial/Taxes/2024/2024_Tax_Return.pdf
   Confidence: 0.85
   ...
```

### Step 2: Review and Adjust Confidence Threshold

The AI strategy uses a confidence threshold (default: 0.6). Only suggestions with confidence >= threshold are executed.

**Check current threshold:**
```bash
# Default is 0.6 - see config file
```

**To be more conservative (only high-confidence moves):**
Create or edit `ai_config.yaml`:
```yaml
strategies:
  ai_suggested:
    enabled: true
    provider: "ollama"
    confidence_threshold: 0.8  # Only execute 80%+ confidence
    batch_size: 10
    use_cache: true
```

**To be more aggressive (include lower-confidence moves):**
```yaml
strategies:
  ai_suggested:
    confidence_threshold: 0.5  # Execute 50%+ confidence
```

### Step 3: Execute with Dry-Run First (Safety!)

Always test with `--dry-run` first:

```bash
file-organizer organize ai_suggested "04-Financial" --dry-run
```

This shows what would happen without actually moving files.

### Step 4: Execute AI Organization

Once you're satisfied with the preview:

```bash
file-organizer organize ai_suggested "04-Financial"
```

**What happens:**
1. Eratosthenes analyzes files in the directory
2. Generates organization suggestions with confidence scores
3. Filters suggestions by confidence threshold
4. Executes moves for approved suggestions
5. Creates transaction log for rollback

### Step 5: Review Results

After execution, you'll see:
```
Organization complete!
Total operations: 15
File moves: 15
Folder moves: 0
Errors: 0
Transaction log: /path/to/organization_transaction_log.json
```

### Step 6: Rollback if Needed

If something went wrong, you can rollback:

```bash
file-organizer rollback /path/to/organization_transaction_log.json
```

## Configuration for AI Organization

Create `ai_config.yaml`:

```yaml
ai:
  enabled: true
  provider: "auto"  # or "ollama" to force local
  use_cache: true
  use_skills: true

strategies:
  ai_suggested:
    enabled: true
    provider: "ollama"
    confidence_threshold: 0.7  # Adjust based on your comfort level
    batch_size: 10  # Files analyzed per AI request
    use_cache: true
```

## Examples

### Example 1: Organize Financial Documents

```bash
# 1. Get suggestions
file-organizer suggest "04-Financial" --max-files 10

# 2. Preview what AI would do
file-organizer preview ai_suggested "04-Financial"

# 3. Test with dry-run
file-organizer organize ai_suggested "04-Financial" --dry-run

# 4. Execute
file-organizer organize ai_suggested "04-Financial"
```

### Example 2: Organize Specific Folder

```bash
# Organize just the Invoices folder
file-organizer organize ai_suggested "04-Financial" --target-folder "04-Financial/Invoices & Receipts"
```

### Example 3: Use Custom Config

```bash
file-organizer organize ai_suggested "04-Financial" --config ai_config.yaml
```

## Understanding Confidence Scores

- **0.9-1.0**: Very high confidence - AI is very sure about the suggestion
- **0.7-0.9**: High confidence - AI is confident, likely good suggestion
- **0.6-0.7**: Medium confidence - AI thinks it's right, but review recommended
- **< 0.6**: Low confidence - Not executed by default (adjust threshold if needed)

## Best Practices

1. **Always Preview First**: Use `preview` to see what will happen
2. **Start with Dry-Run**: Test with `--dry-run` before executing
3. **Start Conservative**: Use higher confidence threshold (0.7-0.8) initially
4. **Review Transaction Log**: Check the log file to see what was done
5. **Test on Small Folders**: Try on a small folder first before large directories
6. **Keep Backups**: The transaction log allows rollback, but backups are always good

## Troubleshooting

### AI suggestions seem wrong?

1. Check the confidence scores - low confidence suggestions might be filtered out
2. Review the reasoning in the preview
3. Adjust confidence threshold if needed
4. Try with fewer files first (`--max-files 3`)

### Too slow?

1. Reduce `batch_size` in config (default: 10)
2. Use fewer files: `--max-files 5`
3. Enable caching (already enabled by default)
4. Use `quick=True` mode (if implemented)

### Want to undo?

```bash
file-organizer rollback organization_transaction_log.json
```

## Advanced: Programmatic Usage

```python
from pathlib import Path
from file_organizer import FileOrganizer
from file_organizer.config import ConfigManager

# Load config
config = ConfigManager()
config.load('ai_config.yaml')

# Create organizer
organizer = FileOrganizer(
    Path('/path/to/documents'),
    config=config,
    dry_run=False  # Set to True for testing
)

# Preview AI suggestions
preview = organizer.preview('ai_suggested', target_folder=Path('04-Financial'))
for move in preview:
    print(f"{move['source']} -> {move['destination']}")
    print(f"  Confidence: {move.get('confidence', 0)}")
    print(f"  Reasoning: {move.get('reasoning', '')}")

# Execute AI organization
result = organizer.organize('ai_suggested', target_folder=Path('04-Financial'))
print(f"Organized {result['statistics']['total_operations']} files")
```

---

**Remember**: Eratosthenes is powerful but always review before executing, especially on important directories!

