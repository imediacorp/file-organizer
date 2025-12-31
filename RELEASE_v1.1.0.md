# File Organizer v1.1.0 - Eratosthenes AI Integration

## 🎉 Major Feature Release

This release introduces **Eratosthenes**, our AI-powered Knowledge/Content Management agent, bringing intelligent file organization to File Organizer.

### 🚀 What's New

#### Eratosthenes: Library Science Expert AI Agent

Eratosthenes is a specialized AI skill set that brings library science expertise to file organization:

- **Intelligent Classification**: Understands document content, not just file extensions
- **Metadata Extraction**: Automatically extracts key information from documents
- **Smart Organization Suggestions**: AI-powered recommendations for file structure
- **Filename Optimization**: Suggests better, more descriptive filenames

#### Provider-Agnostic AI Architecture

- **Multiple AI Providers**: Support for Ollama (local), OpenAI, Google Gemini, and Anthropic Claude
- **Auto-Fallback**: Automatically switches providers if one is unavailable
- **Unified Interface**: Same API works with any provider
- **Local-First**: Use Ollama for privacy-sensitive operations

#### New CLI Commands

- `file-organizer suggest` - Get AI-powered organization suggestions
- `file-organizer classify` - Classify documents using AI
- `file-organizer extract-metadata` - Extract metadata from files
- `file-organizer organize ai_suggested` - Organize using AI recommendations
- `file-organizer preview ai_suggested` - Preview AI suggestions before organizing

#### Performance Optimizations

- **Batch Processing**: Process multiple files efficiently
- **Progress Indicators**: Real-time feedback during AI analysis
- **Configurable Limits**: Control batch size and file limits for performance
- **Two-Stage Workflow**: Fast bulk organization + AI refinement

### 📚 New Documentation

- **[ERATOSTHENES_GUIDE.md](ERATOSTHENES_GUIDE.md)** - Quick reference for Eratosthenes features
- **[ERATOSTHENES_ACTION_GUIDE.md](ERATOSTHENES_ACTION_GUIDE.md)** - How to act on AI recommendations
- **[PERFORMANCE_TIPS.md](PERFORMANCE_TIPS.md)** - Optimizing AI performance
- **[WORKFLOW_BEST_PRACTICES.md](WORKFLOW_BEST_PRACTICES.md)** - Recommended workflows

### 🔧 Technical Improvements

- **Path Resolution Fix**: Fixed `--target-folder` parameter handling
- **Better Error Handling**: More specific error messages from AI providers
- **Response Parsing**: Robust JSON and text parsing for AI responses
- **Caching**: AI response caching for improved performance
- **Metrics**: Track AI usage and performance

### 📦 Installation

Install from source:

```bash
git clone https://github.com/imediacorp/file-organizer.git
cd file-organizer
git checkout v1.1.0
pip install .
```

Or install directly:

```bash
pip install git+https://github.com/imediacorp/file-organizer.git@v1.1.0
```

### 🎯 Quick Start with Eratosthenes

1. **Set up Ollama** (for local AI):
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull llama3.1:latest
   # Or use a faster model:
   ollama pull gemma3:4b
   ```

2. **Try AI suggestions**:
   ```bash
   # Preview AI suggestions
   file-organizer preview ai_suggested /path/to/files
   
   # Get organization suggestions
   file-organizer suggest /path/to/files
   
   # Classify a document
   file-organizer classify document.pdf
   ```

3. **Two-stage workflow** (recommended):
   ```bash
   # Stage 1: Fast bulk organization
   file-organizer organize filetype /path/to/files
   
   # Stage 2: AI refinement on specific folders
   file-organizer preview ai_suggested /path/to/files --target-folder "Invoices"
   ```

### 🔄 Migration from v1.0.0

This release is **fully backward compatible**. Existing strategies (`filetype`, `rule_based`) work exactly as before. AI features are opt-in.

### 📝 Configuration

Create `ai_config.yaml` to customize AI behavior:

```yaml
ai:
  default_provider: ollama
  default_model: llama3.1:latest
  timeout: 45

strategies:
  ai_suggested:
    batch_size: 5
    max_files_to_analyze: 50
    confidence_threshold: 0.7
```

### 🐛 Bug Fixes

- Fixed path resolution for `--target-folder` parameter
- Improved error messages for AI provider failures
- Better handling of AI response parsing (JSON and text formats)

### 🙏 Acknowledgments

Eratosthenes is named after the ancient Greek scholar who calculated the Earth's circumference and created the first library cataloging system—fitting for a tool that brings scientific rigor to file organization.

---

**Full Changelog**: See [git log](https://github.com/imediacorp/file-organizer/compare/v1.0.0...v1.1.0)

*"Innovation that matters must withstand science. Falsifiable, reproducible, transparent."*

