# File Organizer - Best Practices Workflow

## Recommended Two-Stage Organization Approach

### Why Two Stages?

1. **Speed**: Initial organization is fast (rule-based)
2. **Efficiency**: AI focuses on refinement, not bulk work
3. **Cost-Effective**: Less AI processing time
4. **Better UX**: Faster initial results, then intelligent refinement

## Stage 1: Initial Organization (Fast)

Use rule-based strategies for bulk organization:

### Option A: File Type Organization
```bash
# Organize by file extension (very fast)
file-organizer organize filetype "04-Financial"
```

**Best for:**
- Large directories with mixed file types
- Initial cleanup
- Quick organization by extension

### Option B: Rule-Based Organization
```bash
# Organize using custom rules
file-organizer organize rule_based "04-Financial" --config config.yaml
```

**Best for:**
- Known patterns (e.g., "all invoices go to Invoices/")
- Consistent naming conventions
- Predictable file types

## Stage 2: AI Refinement (Intelligent)

After initial organization, use Eratosthenes to refine:

### Step 1: Preview AI Suggestions
```bash
file-organizer preview ai_suggested "04-Financial"
```

**What you'll see:**
- Progress indicators (batch processing)
- Files being analyzed
- Suggestions with confidence scores
- Reasoning for each suggestion

**Note:** This takes time - be patient. Progress is shown.

### Step 2: Execute AI Refinement
```bash
# Test first
file-organizer organize ai_suggested "04-Financial" --dry-run

# Then execute
file-organizer organize ai_suggested "04-Financial"
```

**What AI does:**
- Suggests better filenames
- Recommends metadata extraction
- Optimizes folder structure
- Identifies duplicates and versions
- Applies library science principles

## Complete Workflow Example

```bash
# 1. Initial fast organization
file-organizer organize filetype "04-Financial"
# Result: Files organized by type (PDFs, Images, Documents, etc.)

# 2. Preview AI refinements
file-organizer preview ai_suggested "04-Financial"
# Result: See what AI would improve

# 3. Execute AI refinements
file-organizer organize ai_suggested "04-Financial"
# Result: Better naming, metadata, optimized structure
```

## When to Use Each Strategy

### Use `filetype` when:
- ✅ You have many files of different types
- ✅ You want quick bulk organization
- ✅ File extension is sufficient for organization
- ✅ You need fast results

### Use `rule_based` when:
- ✅ You have specific patterns to match
- ✅ You know where files should go
- ✅ You want consistent rule-based organization
- ✅ You have a configuration file ready

### Use `ai_suggested` when:
- ✅ You want intelligent naming suggestions
- ✅ You need metadata extraction
- ✅ You want optimization after initial organization
- ✅ You have time for AI processing
- ✅ You want library science principles applied

## Performance Tips

### For Large Directories:

1. **Start Small**: Test on a subdirectory first
   ```bash
   file-organizer organize filetype "04-Financial/Invoices & Receipts"
   ```

2. **Use Target Folder**: Organize specific folders
   ```bash
   file-organizer organize filetype "04-Financial" --target-folder "04-Financial/Invoices & Receipts"
   ```

3. **Reduce AI Batch Size**: For faster AI processing
   ```yaml
   strategies:
     ai_suggested:
       batch_size: 5  # Smaller batches = faster per batch
   ```

4. **Increase Confidence Threshold**: Fewer suggestions = faster
   ```yaml
   strategies:
     ai_suggested:
       confidence_threshold: 0.8  # Only high-confidence moves
   ```

## Progress Indicators

When using AI strategies, you'll see:
```
📊 Eratosthenes analyzing 50 files...
   Using batch size: 10
   Confidence threshold: 0.6
   Processing batch 1/5 (10 files)... ✓ (8 suggestions)
   Processing batch 2/5 (10 files)... ✓ (9 suggestions)
   ...
✅ Analysis complete: 42 suggestions generated

📋 Filtering suggestions by confidence threshold (0.6)...
   Total suggestions: 42
   Approved (≥0.6): 35
   Filtered out: 7

🚀 Executing 35 approved moves...
```

## Safety First

Always use this sequence:

1. **Preview** → See what will happen
2. **Dry-Run** → Test without changes
3. **Execute** → Make the changes
4. **Review** → Check transaction log
5. **Rollback** → If needed

## Example: Complete Financial Folder Organization

```bash
# Stage 1: Fast initial organization
file-organizer organize filetype "04-Financial"
# Takes: ~30 seconds for 1000 files
# Result: Files organized by type

# Stage 2: AI refinement
file-organizer preview ai_suggested "04-Financial" --max-files 20
# Takes: ~2-3 minutes for 20 files
# Result: See refinement suggestions

file-organizer organize ai_suggested "04-Financial"
# Takes: ~5-10 minutes for 100 files
# Result: Optimized naming, metadata, structure
```

## Summary

**Fast First, Smart Second:**
1. Use `filetype` or `rule_based` for bulk organization
2. Use `ai_suggested` for refinement and optimization
3. Always preview before executing
4. Use dry-run for safety
5. Review transaction logs

This approach gives you the best of both worlds: speed and intelligence!

