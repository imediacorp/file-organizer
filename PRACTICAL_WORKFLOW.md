# File Organizer - Practical Workflow Guide

## 🎯 Quick Start: From Suggestions to Execution

This guide shows you the exact steps to go from AI recommendations to organized files.

---

## Workflow Overview

```
1. Get Recommendations → 2. Preview Actions → 3. Execute → 4. Review
```

---

## Step 1: Get AI Recommendations

**Command:**
```bash
file-organizer suggest "04-Financial" --provider gemini --max-files 10
```

**What it does:**
- Analyzes your directory structure
- Provides organization recommendations
- Suggests folder structures and naming conventions
- **Does NOT move any files** (advisory only)

**Example output:**
```
## Analysis of Financial Directory Structure

### Suggested Top-Level Folder Structure:
- Income
- Expenses  
- Taxes
- Investments
- Banking
- Insurance

### Recommendations:
- Move invoices to Expenses/Shopping/
- Organize by year (2024/, 2025/)
- Use date-based naming: YYYY-MM-DD_Description.pdf
```

**Time:** ~1-2 seconds (Gemini) or ~2-3 seconds (Grok)

---

## Step 2: Preview What AI Will Do

**Command:**
```bash
# Use "." as root path and --target-folder for subdirectories (recommended)
file-organizer preview ai_suggested "." --target-folder "04-Financial/Invoices & Receipts" --config ai_config.yaml
```

**What it does:**
- Shows exactly which files will be moved
- Shows where they'll go
- Displays confidence scores
- **Does NOT move any files** (preview only)

**Important:** Use `"."` as the root path and `--target-folder` for the subdirectory to avoid path issues.

**Example output:**
```
Preview: 15 operations would be performed

1. 04-Financial/Invoices & Receipts/Amazon Invoice.pdf 
   -> 04-Financial/Expenses/Shopping/2024/2024-01-15_Invoice_Amazon.pdf
   Confidence: 0.9
   Reasoning: Invoice should be organized chronologically with descriptive filename

2. 04-Financial/Taxes/2024_Tax_Return.pdf
   -> 04-Financial/Taxes/2024/2024_Tax_Return.pdf
   Confidence: 0.85
   ...
```

**Time:** ~10-30 seconds depending on number of files

**Options:**
```bash
# Preview specific folder (recommended approach)
file-organizer preview ai_suggested "." --target-folder "04-Financial/Invoices & Receipts" --config ai_config.yaml

# Preview entire directory
file-organizer preview ai_suggested "04-Financial" --config ai_config.yaml
```

**Note:** The `ai_config.yaml` file should have `confidence_threshold: 0.5` (or lower) to catch more suggestions. Default is 0.6 which may filter out valid suggestions.

---

## Step 3: Execute the Organization

### Option A: Dry-Run First (Recommended)

**Command:**
```bash
file-organizer organize ai_suggested "04-Financial" --dry-run
```

**What it does:**
- Simulates the organization
- Shows what would happen
- **Does NOT move any files** (safe test)

### Option B: Execute for Real

**Command:**
```bash
file-organizer organize ai_suggested "04-Financial"
```

**What it does:**
- Moves files based on AI suggestions
- Only executes high-confidence moves (default: ≥0.6)
- Creates transaction log for rollback
- Shows progress and results

**Example output:**
```
📊 Eratosthenes analyzing 50 files...
   Processing batch 1/5 (10 files)... ✓
   Processing batch 2/5 (10 files)... ✓
   ...

📋 Filtering suggestions by confidence threshold (0.6)...
   Total suggestions: 42
   Approved (≥0.6): 35
   Filtered out: 7

🚀 Executing 35 approved moves...

============================================================
Organization complete!
Total operations: 35
File moves: 35
Folder moves: 0
Errors: 0
Transaction log: organization_transaction_log.json
============================================================
```

**Time:** ~1-5 minutes depending on number of files

---

## Step 4: Review Results

**Check the transaction log:**
```bash
cat organization_transaction_log.json
```

**If something went wrong, rollback:**
```bash
file-organizer rollback organization_transaction_log.json
```

---

## Complete Example Workflow

```bash
# 1. Get recommendations (advisory)
file-organizer suggest "04-Financial" --provider gemini --max-files 10

# 2. Preview what AI will do (use "." as root with --target-folder)
file-organizer preview ai_suggested "." --target-folder "04-Financial/Invoices & Receipts" --config ai_config.yaml

# 3. Test with dry-run (safe)
file-organizer organize ai_suggested "." --target-folder "04-Financial/Invoices & Receipts" --config ai_config.yaml --dry-run

# 4. Execute for real
file-organizer organize ai_suggested "." --target-folder "04-Financial/Invoices & Receipts" --config ai_config.yaml

# 5. Review results
cat organization_transaction_log.json
```

**Key Points:**
- Use `"."` as root path and `--target-folder` for subdirectories
- Use `--config ai_config.yaml` with `confidence_threshold: 0.5`
- Always preview before executing

---

## Two-Stage Workflow (Recommended for Large Directories)

### Stage 1: Fast Initial Organization

```bash
# Organize by file type (very fast, ~30 seconds for 1000 files)
file-organizer organize filetype "04-Financial"
```

**Result:** Files organized by extension (PDFs/, Images/, Documents/, etc.)

### Stage 2: AI Refinement

```bash
# Preview AI improvements
file-organizer preview ai_suggested "04-Financial"

# Execute AI refinements
file-organizer organize ai_suggested "04-Financial"
```

**Result:** Better naming, metadata extraction, optimized structure

**Why this approach?**
- ✅ Fast initial organization (30 seconds)
- ✅ Intelligent refinement (2-5 minutes)
- ✅ More efficient use of AI
- ✅ Better user experience

---

## Configuration for Better Results

Create `ai_config.yaml`:

```yaml
strategies:
  ai_suggested:
    provider: "gemini"  # or "grok", "ollama", "auto"
    confidence_threshold: 0.5  # Lower threshold to catch more suggestions (default 0.6 may be too high)
    max_files: 50  # Limit files analyzed
    batch_size: 5  # Files per AI request
    use_cache: true
```

**Use it:**
```bash
# Preview (recommended: use "." as root with --target-folder)
file-organizer preview ai_suggested "." --target-folder "04-Financial/Invoices & Receipts" --config ai_config.yaml

# Execute
file-organizer organize ai_suggested "." --target-folder "04-Financial/Invoices & Receipts" --config ai_config.yaml
```

**Why confidence_threshold: 0.5?**
- AI often generates suggestions with confidence 0.5-0.6
- Default threshold of 0.6 may filter out valid suggestions
- 0.5 catches more suggestions while still filtering very low confidence ones

---

## Provider Performance Comparison

| Provider | Simple Task | Complex Task | Best For |
|----------|-------------|--------------|----------|
| **Gemini** | 0.66s | 1.53s | ⚡ Fastest overall |
| **Grok** | 0.72s | 2.58s | ⚡ Very fast alternative |
| **Ollama** | 1.31s | 8.33s | 🔒 Privacy, offline |

**Set provider:**
```bash
# In ai_config.yaml
strategies:
  ai_suggested:
    provider: "gemini"  # Fastest
```

---

## Common Commands Reference

### Get Recommendations
```bash
file-organizer suggest <path> --provider <provider> --max-files <num>
```

### Preview Actions
```bash
# Recommended: use "." as root with --target-folder
file-organizer preview ai_suggested "." --target-folder <folder> [--config ai_config.yaml]

# Or preview entire directory
file-organizer preview ai_suggested <path> [--config ai_config.yaml]
```

### Execute Organization
```bash
# Test first (recommended: use "." as root with --target-folder)
file-organizer organize ai_suggested "." --target-folder <folder> --config ai_config.yaml --dry-run

# Execute
file-organizer organize ai_suggested "." --target-folder <folder> --config ai_config.yaml
```

### Rollback
```bash
file-organizer rollback <transaction_log.json>
```

---

## Safety Checklist

Before executing:
- ✅ Previewed the suggestions
- ✅ Reviewed confidence scores
- ✅ Tested with dry-run
- ✅ Have backup or transaction log
- ✅ Understand what will happen

---

## Troubleshooting

### No suggestions generated?
- Check confidence threshold (try lowering to 0.5)
- Verify files exist in the path
- Check AI provider is configured

### Too slow?
- Reduce `max_files` in config
- Use faster provider (Gemini or Grok)
- Organize smaller subfolders first

### Want to undo?
```bash
file-organizer rollback organization_transaction_log.json
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Get recommendations | `file-organizer suggest <path>` |
| Preview moves | `file-organizer preview ai_suggested <path>` |
| Test execution | `file-organizer organize ai_suggested <path> --dry-run` |
| Execute | `file-organizer organize ai_suggested <path>` |
| Rollback | `file-organizer rollback <log.json>` |

---

**Remember:** Always preview before executing, especially on important directories!

