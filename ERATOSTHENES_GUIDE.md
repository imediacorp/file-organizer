# Eratosthenes - AI-Powered File Organization Guide

## Overview

**Eratosthenes** is the Knowledge/Content Management agent integrated into File Organizer. Named after the ancient Greek librarian who organized knowledge at the Library of Alexandria, Eratosthenes provides intelligent file organization assistance.

## Quick Start

### 1. Check AI Provider Status

```bash
python3 -c "from file_organizer.ai import get_provider_status; import json; print(json.dumps(get_provider_status(), indent=2))"
```

**Current Status:**
- ✅ **Ollama**: Available (local, recommended for privacy)
- ❌ OpenAI: Not configured
- ❌ Gemini: Not configured  
- ❌ Anthropic: Not configured

### 2. Available Models

Your Ollama installation has:
- `llama3.1:latest` - Recommended for best results
- `minimax-m2:cloud` - Alternative option
- `gemma3:4b` - Lightweight option

**Set default model:**
```bash
export OLLAMA_MODEL=llama3.1:latest
```

## CLI Commands

### Get Organization Suggestions

Analyze a directory and get AI-powered organization recommendations:

```bash
file-organizer suggest /path/to/documents --max-files 20
```

**Example:**
```bash
file-organizer suggest "04-Financial" --max-files 10
```

### Classify a Document

Get AI classification for a single file:

```bash
file-organizer classify /path/to/document.pdf
```

**Example:**
```bash
file-organizer classify "04-Financial/Invoices & Receipts/Amazon Invoice.pdf"
```

**Output includes:**
- Document type (Invoice, Contract, Report, etc.)
- Category (Financial, Legal, Business, etc.)
- Suggested folder location
- Confidence score
- Reasoning

### Extract Metadata

Extract metadata from a file:

```bash
file-organizer extract-metadata /path/to/file.pdf
```

**Extracted fields:**
- Title
- Date
- Author/Creator
- Subject/Topic
- Type
- Keywords

### AI-Powered Organization

Organize files using AI suggestions:

```bash
# Preview AI suggestions
file-organizer preview ai_suggested /path/to/documents

# Execute AI organization
file-organizer organize ai_suggested /path/to/documents
```

## Python API Usage

### Basic Classification

```python
from pathlib import Path
from file_organizer.utils.ai_advisory import classify_document

result = classify_document(
    Path("04-Financial/Invoices & Receipts/Amazon Invoice.pdf"),
    provider="ollama"
)

if result.get("success"):
    classification = result.get("classification", {})
    print(f"Type: {classification.get('type')}")
    print(f"Category: {classification.get('category')}")
```

### Metadata Extraction

```python
from file_organizer.utils.ai_advisory import extract_metadata

result = extract_metadata(
    Path("document.pdf"),
    provider="ollama"
)

if result.get("success"):
    metadata = result.get("metadata", {})
    print(f"Title: {metadata.get('title')}")
    print(f"Date: {metadata.get('date')}")
```

### Filename Suggestions

```python
from file_organizer.utils.ai_advisory import suggest_filename

result = suggest_filename(
    Path("invoice.pdf"),
    content_hint="Invoice from Amazon dated January 15, 2024",
    provider="ollama"
)

if result.get("success"):
    suggestion = result.get("suggestion", {})
    print(f"Suggested: {suggestion.get('suggested_filename')}")
```

### Direct AI Calls with Eratosthenes

```python
from file_organizer.ai import get_ai_suggestion, AIProvider

payload = {
    "request": "suggest_organization",
    "domain": "library_science",  # Activates Eratosthenes skill
    "context": {
        "files": [
            {"name": "contract.pdf", "extension": ".pdf"},
            {"name": "invoice.pdf", "extension": ".pdf"},
        ]
    },
    "instructions": "Suggest organization structure for these files"
}

result = get_ai_suggestion(
    payload,
    provider=AIProvider.OLLAMA,
    use_skills=True  # Enable Eratosthenes skill enhancement
)

if result.get("ok"):
    print(result.get("text"))
```

## Configuration

### AI Configuration File

Create `ai_config.yaml`:

```yaml
ai:
  enabled: true
  provider: "auto"  # auto, ollama, openai, gemini, anthropic
  use_cache: true
  cache_ttl: 3600
  use_skills: true
  
  providers:
    ollama:
      endpoint: "http://localhost:11434"
      model: "llama3.1:latest"  # Use your available model
      timeout: 30

library_science:
  enabled: true
  classification_scheme: "functional"
  metadata_extraction: true
  suggest_naming: true

strategies:
  ai_suggested:
    enabled: true
    provider: "ollama"
    confidence_threshold: 0.6
    batch_size: 10
    use_cache: true
```

### Environment Variables

```bash
# Set default Ollama model
export OLLAMA_MODEL=llama3.1:latest

# For other providers (optional)
export OPENAI_API_KEY=your_key_here
export GEMINI_API_KEY=your_key_here
export ANTHROPIC_API_KEY=your_key_here
```

## Eratosthenes Capabilities

### 1. Document Classification
- Automatically categorizes documents by type and subject
- Suggests appropriate folder locations
- Provides confidence scores

### 2. Metadata Extraction
- Extracts titles, dates, authors, subjects
- Identifies document types
- Generates keywords for searchability

### 3. Organization Recommendations
- Suggests folder structures
- Recommends naming conventions
- Validates existing taxonomies

### 4. Naming Conventions
- Suggests descriptive filenames
- Follows library science best practices
- Ensures sortability and searchability

## Examples

### Example 1: Classify Financial Documents

```bash
file-organizer classify "04-Financial/Invoices & Receipts/Amazon Invoice.pdf"
```

**Expected Output:**
- Classification: Financial/Invoice
- Category: Business/Financial
- Suggested Location: Financial/Invoices/2024/
- Confidence: High

### Example 2: Get Organization Suggestions

```bash
file-organizer suggest "03-Business" --max-files 20
```

**Provides:**
- Overall structure assessment
- Suggested folder hierarchy
- Naming convention recommendations
- Metadata extraction priorities

### Example 3: AI-Powered Organization

```bash
# Preview what AI would do
file-organizer preview ai_suggested "04-Financial"

# Execute AI organization
file-organizer organize ai_suggested "04-Financial" --dry-run
```

## Troubleshooting

### Model Not Found

If you get "model not found" errors:

1. Check available models:
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. Set the model:
   ```bash
   export OLLAMA_MODEL=llama3.1:latest
   ```

3. Or update config file with correct model name

### Timeout Errors

For large requests, increase timeout:

```python
result = get_ai_suggestion(
    payload,
    provider=AIProvider.OLLAMA,
    timeout=60  # Increase timeout
)
```

### Provider Not Available

Check provider status:
```python
from file_organizer.ai import get_provider_status
status = get_provider_status()
print(status)
```

## Best Practices

1. **Start with Preview**: Always preview AI suggestions before executing
2. **Use Dry-Run**: Test with `--dry-run` flag first
3. **Set Confidence Threshold**: Only execute high-confidence suggestions
4. **Batch Processing**: Use appropriate batch sizes for large directories
5. **Cache Results**: Enable caching to avoid redundant API calls

## Next Steps

- Run the demo script: `python3 test_eratosthenes.py`
- Try classifying your documents
- Get organization suggestions for your directories
- Experiment with AI-powered organization

## Resources

- **Eratosthenes Skill**: `file_organizer/ai/skills/library_science.py`
- **AI Advisory Tools**: `file_organizer/utils/ai_advisory.py`
- **Configuration Examples**: `file_organizer/config/examples/ai_config.yaml`

---

*"Eratosthenes: Bringing systematic knowledge organization to file management"*

