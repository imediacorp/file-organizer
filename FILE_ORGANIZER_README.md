# File Organizer

> **An Open Science Initiative by [imediacorp](https://imediacorp.com)**  
> *"Innovation that matters must withstand science. Falsifiable, reproducible, transparent."*

A flexible, extensible Python tool for organizing large content trees on your computer. This tool provides both a command-line interface and a Python library for organizing files using various strategies.

## 💡 Why File Organizer?

File Organizer was born out of frustration with managing vast amounts of content across diverse file types and versions. As someone working across multiple domains—business documents, creative projects, research materials, personal files, and more—I needed a tool that could:

- **Handle the breadth**: Organize everything from PDFs and images to code, documents, and media files
- **Manage versions**: Track and identify duplicate files, similar names, and version patterns
- **Provide safety**: Never lose files with dry-run mode, transaction logging, and rollback support
- **Scale intelligently**: Use AI to understand content, not just file extensions
- **Work everywhere**: Cross-platform support for Windows, macOS, and Linux, including network drives

This tool embodies the principle of "scratching your own itch"—built to solve real problems I faced daily, and now shared as part of imediacorp's Open Science commitment to help others facing similar challenges.

## 🎨 Perfect for Content Creators & Creative Studios

File Organizer aligns with **imediacorp's Arts & Sciences philosophy** and complements our creative tools ecosystem:

- **Rhapsode** (Narrative INDE) - Brings structure to storytelling
- **Harmonia** (Music INDE) - Brings precision to music composition  
- **Production Desk** - Brings order to production workflows
- **File Organizer** - Brings scientific rigor to file organization

**For content creators**, File Organizer solves the unique challenges of managing creative projects:
- Organize scripts, drafts, and revisions (perfect for Rhapsode users)
- Manage music projects, stems, and samples (perfect for Harmonia users)
- Track production assets and deliverables (perfect for Production Desk users)
- AI-powered classification understands your creative content, not just file types

**Built for creators, by creators** - with the same Arts & Sciences approach that powers Rhapsode, Harmonia, and Production Desk.

## 🔬 Perfect for Research Institutes & CHaDD Users

File Organizer is also ideal for **research institutes and commercial organizations using CHaDD diagnostic tools**:

- **Research Data Management**: Organize datasets, research papers, documentation, and results
- **CHaDD Integration**: Manage diagnostic data, reports, compliance documents, and analysis outputs
- **Reproducibility**: Transaction logging ensures research workflows are reproducible
- **Scientific Rigor**: Aligns with Open Science principles for transparent research
- **Multi-Domain Support**: Handles diverse file types from medical, industrial, infrastructure, and geophysical diagnostics

**For CHaDD users**, File Organizer provides:
- Organized storage for diagnostic outputs and reports
- Version tracking for diagnostic configurations and results
- Metadata extraction for research documentation
- Cross-platform compatibility for research teams
- Network drive support for collaborative research

**Built with scientific rigor** - the same principles that power CHaDD's diagnostic capabilities.

## 🔬 Open Science Commitment

This tool is part of **imediacorp's commitment to Open Science**. We believe scientific tools should be as transparent and reproducible as the science they support.

**Our Open Science Principles:**
- ✅ **Reproducibility**: Every operation is logged in transaction files, enabling exact reproduction
- ✅ **Transparency**: All algorithms are documented, no black boxes
- ✅ **Falsifiability**: Dry-run mode allows validation before execution
- ✅ **Open Source**: 100% open source (MIT License)

[Learn more about imediacorp's Open Science commitment →](https://imediacorp.com/open-science)

## Features

- **Multiple Organization Strategies**: File type-based, rule-based pattern matching, AI-powered suggestions, and extensible plugin architecture
- **Eratosthenes AI Agent**: Intelligent Knowledge/Content Management agent powered by Library Science Expert for classification, metadata extraction, and organization recommendations
- **Safety First**: Dry-run mode, transaction logging, and rollback support
- **Index Generation**: Generate beautiful Markdown and HTML indexes of your file tree
- **Duplicate Detection**: Find duplicate files, similar names, and version patterns
- **Configuration-Driven**: YAML/JSON configuration files for flexible, reusable organization rules
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Network & External Drives**: Works with mounted network drives, external USB drives, and cloud storage mounts
- **Provider-Agnostic AI**: Supports Ollama (local), OpenAI, Google Gemini, and Anthropic Claude

## Installation

```bash
# Install from source (use pip3 or python3 -m pip on macOS/Linux)
pip3 install .

# Or using python3 -m pip (more universal)
python3 -m pip install .

# Or install in development mode
pip3 install -e .
# or
python3 -m pip install -e .
```

**Note:** After installation, if the `file-organizer` command is not found, you may need to:
1. Add the installation directory to your PATH (usually `~/Library/Python/3.x/bin` on macOS)
2. Or use: `python3 -m file_organizer.cli.main` instead of `file-organizer`

To add to PATH on macOS, add this to your `~/.zshrc` or `~/.bash_profile`:
```bash
export PATH="$HOME/Library/Python/3.13/bin:$PATH"
```

## Quick Start

### Command Line Usage

#### Organize files by type
```bash
# Using the installed command (if in PATH)
file-organizer organize filetype /path/to/documents

# Or using python3 -m (if not in PATH)
python3 -m file_organizer.cli.main organize filetype /path/to/documents
```

#### Preview changes before organizing
```bash
file-organizer preview filetype /path/to/documents
# or: python3 -m file_organizer.cli.main preview filetype /path/to/documents
```

#### Generate an index
```bash
file-organizer index /path/to/documents
# or: python3 -m file_organizer.cli.main index /path/to/documents
```

#### Find duplicates
```bash
file-organizer duplicates /path/to/documents
# or: python3 -m file_organizer.cli.main duplicates /path/to/documents
```

#### Organize with custom configuration
```bash
file-organizer organize rule_based /path/to/documents --config config.yaml
# or: python3 -m file_organizer.cli.main organize rule_based /path/to/documents --config config.yaml
```

#### AI-Powered Organization (Eratosthenes)
```bash
# Get AI suggestions for organization structure
file-organizer suggest /path/to/documents

# Organize using AI suggestions
file-organizer organize ai_suggested /path/to/documents

# Classify a document
file-organizer classify /path/to/document.pdf

# Extract metadata from a file
file-organizer extract-metadata /path/to/file.pdf
```

### Python Library Usage

```python
from pathlib import Path
from file_organizer import FileOrganizer
from file_organizer.config import ConfigManager

# Create organizer
config = ConfigManager()
config.load('config.yaml')

organizer = FileOrganizer(
    Path('/path/to/documents'),
    config=config,
    dry_run=False
)

# Organize using a strategy
result = organizer.organize('filetype')
print(f"Organized {result['statistics']['total_operations']} files")
```

## Organization Strategies

### AI-Powered Strategy (Eratosthenes)

Organizes files using AI-powered analysis with the Library Science Expert skill set. Named after the ancient Greek librarian and geographer who organized knowledge at the Library of Alexandria, Eratosthenes provides intelligent classification, metadata extraction, and organization recommendations.

**Features:**
- Document classification and categorization
- Metadata extraction (title, date, author, subject, keywords)
- Organization structure recommendations
- File naming suggestions
- Taxonomy management

**Configuration Example:**
```yaml
strategies:
  ai_suggested:
    enabled: true
    provider: "auto"  # auto, ollama, openai, gemini, anthropic
    confidence_threshold: 0.6
    batch_size: 10
    use_cache: true

ai:
  enabled: true
  provider: "auto"
  use_cache: true
  use_skills: true
```

**Usage:**
```bash
# Preview AI suggestions
file-organizer preview ai_suggested /path/to/documents

# Organize with AI
file-organizer organize ai_suggested /path/to/documents
```

### File Type Strategy

Organizes files by their extension into category folders (e.g., `_by_type_PDFs`, `_by_type_Images`).

**Configuration Example:**
```yaml
strategies:
  filetype:
    enabled: true
    max_depth: 3
    folder_prefix: "_by_type_"
    categories:
      Documents: [.doc, .docx, .txt]
      PDFs: [.pdf]
      Images: [.jpg, .png, .gif]
```

**Usage:**
```bash
file-organizer organize filetype /path/to/documents
```

### Rule-Based Strategy

Organizes files using pattern matching rules (exact match, glob patterns, or regex).

**Configuration Example:**
```yaml
strategies:
  rule_based:
    enabled: true
    file_rules:
      - pattern: "*.pdf"
        type: glob
        destination: "Documents/PDFs"
      - pattern: "invoice.*"
        type: regex
        destination: "Financial/Invoices"
        recursive: true
    folder_rules:
      - pattern: "Photos"
        type: exact
        destination: "Media/Photos"
```

**Usage:**
```bash
file-organizer organize rule_based /path/to/documents --config config.yaml
```

## CLI Commands

### `organize`

Organize files using a strategy.

```bash
file-organizer organize <strategy> <path> [options]

Options:
  --target-folder PATH    Specific folder to organize
  --config PATH          Configuration file path
  --dry-run              Preview changes without moving files
  --log-file PATH        Log file path
```

### `preview`

Preview what changes would be made without actually organizing.

```bash
file-organizer preview <strategy> <path> [options]

Options:
  --target-folder PATH    Specific folder to analyze
  --config PATH          Configuration file path
```

### `index`

Generate index files (Markdown and HTML) for a directory tree.

```bash
file-organizer index <path> [options]

Options:
  --output-dir PATH      Output directory for index files
  --markdown PATH        Markdown output file path
  --html PATH            HTML output file path
```

### `duplicates`

Find duplicate files, similar names, and version patterns.

```bash
file-organizer duplicates <path> [options]

Options:
  --json PATH            JSON output file path
  --report PATH          Text report output file path
  --hash-large           Hash large files (may be slow)
  --max-size SIZE        Max file size in MB for hashing (default: 50)
```

### `rollback`

Rollback previous organization operations.

```bash
file-organizer rollback <log_file> [options]

Options:
  --dry-run              Preview rollback without executing
```

## Configuration

Configuration files can be in YAML or JSON format. See `file_organizer/config/examples/` for example configurations.

### Configuration Structure

```yaml
strategies:
  filetype:
    enabled: true
    max_depth: 3
    folder_prefix: "_by_type_"
    categories:
      Documents: [.doc, .docx, .txt]
      # ... more categories
  
  rule_based:
    enabled: false
    file_rules: []
    folder_rules: []

general:
  dry_run: false
  log_file: null
  transaction_log: null
```

## Safety Features

### Dry-Run Mode

Always test your configuration with dry-run mode first:

```bash
file-organizer organize filetype /path/to/documents --dry-run
```

### Transaction Logging

All file operations are logged to a transaction file. This allows you to rollback changes if needed.

### Rollback

If something goes wrong, you can rollback:

```bash
file-organizer rollback organization_transaction_log.json
```

## Advanced Usage

### Custom Strategies

You can create custom strategies by extending the `Strategy` base class:

```python
from file_organizer.core.strategy import Strategy
from file_organizer.core.operations import FileOperations
from pathlib import Path

class MyCustomStrategy(Strategy):
    def organize(self, root_path: Path, operations: FileOperations, **kwargs):
        # Your organization logic here
        pass
    
    def preview(self, root_path: Path, **kwargs):
        # Return list of proposed moves
        pass
```

Then register it:

```python
from file_organizer.strategies import register_strategy

register_strategy('my_custom', MyCustomStrategy)
```

### Programmatic Index Generation

```python
from file_organizer.utils.index import IndexGenerator
from pathlib import Path

generator = IndexGenerator(Path('/path/to/documents'))
result = generator.generate()

print(f"Generated index: {result['markdown']}, {result['html']}")
```

### Programmatic Duplicate Detection

```python
from file_organizer.utils.duplicates import DuplicateFinder
from pathlib import Path

finder = DuplicateFinder(Path('/path/to/documents'), hash_large_files=False)
results = finder.analyze(
    output_json=Path('duplicates.json'),
    output_report=Path('duplicates_report.txt')
)

print(f"Found {results['summary']['total_exact_duplicates']} duplicate groups")
```

## Migration from Old Scripts

If you've been using the old scripts (`organize_documents.py`, `organize_by_filetype.py`, etc.), here's how to migrate:

### File Type Organization

**Old:**
```bash
python3 organize_by_filetype.py --dry-run
python3 organize_by_filetype.py "03-Business"
```

**New:**
```bash
file-organizer preview filetype .
file-organizer organize filetype . --target-folder "03-Business"
```

### Index Generation

**Old:**
```bash
python3 generate_index.py
```

**New:**
```bash
file-organizer index .
```

### Duplicate Detection

**Old:**
```bash
python3 compare_file_versions.py "04-Financial" --hash-large
```

**New:**
```bash
file-organizer duplicates "04-Financial" --hash-large
```

### Rule-Based Organization

The old `organize_documents.py` script had hardcoded rules. To migrate, create a YAML configuration file:

```yaml
strategies:
  rule_based:
    enabled: true
    file_rules:
      - pattern: "Amazon Invoice.pdf"
        type: exact
        destination: "04-Financial/Invoices & Receipts"
      # Add your other rules here
    folder_rules:
      - pattern: "Auctions"
        type: exact
        destination: "04-Financial/Invoices & Receipts/Auctions"
      # Add your other folder rules here
```

Then use:
```bash
file-organizer organize rule_based . --config config.yaml
```

## Examples

See `file_organizer/config/examples/` for example configuration files.

## Project Structure

```
file_organizer/
├── __init__.py
├── core/              # Core functionality
│   ├── organizer.py   # Main organizer class
│   ├── operations.py  # Safe file operations
│   └── strategy.py    # Base strategy class
├── strategies/        # Organization strategies
│   ├── filetype.py
│   └── rule_based.py
├── utils/             # Utilities
│   ├── index.py       # Index generation
│   ├── duplicates.py  # Duplicate detection
│   └── reporting.py   # Reporting utilities
├── config/            # Configuration management
│   ├── loader.py
│   ├── schema.py
│   └── examples/      # Example configurations
└── cli/               # Command-line interface
    └── main.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

We welcome contributions that align with our Open Science principles:
- Improvements to reproducibility features
- Documentation enhancements
- New organization strategies
- Bug fixes and performance improvements

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License

Copyright (c) 2025 imediacorp

This project is part of imediacorp's Open Science initiative. See [imediacorp.com](https://imediacorp.com) for more information.

## Network Drives and External Storage

The tool works with any mounted filesystem, including network drives, external USB drives, and cloud storage mounts. See [docs/NETWORK_DRIVES.md](docs/NETWORK_DRIVES.md) for detailed information about:

- Mounting and authenticating network drives
- Working with external storage
- Cloud storage integration (Dropbox, OneDrive, etc.)
- Troubleshooting network drive issues
- Best practices for network operations

**Quick example:**
```bash
# Organize a network drive (must be mounted first)
file-organizer organize filetype /Volumes/NetworkDrive

# Or Windows network drive
file-organizer organize filetype "\\server\share\Documents"
```

## Eratosthenes: AI-Powered Knowledge Management

Eratosthenes is the codename for the Knowledge/Content Management agent integrated into File Organizer. Named after the ancient Greek scholar who organized knowledge at the Library of Alexandria, Eratosthenes provides:

- **Intelligent Classification**: Automatically categorizes documents using library science principles
- **Metadata Extraction**: Extracts titles, dates, authors, and subjects from files
- **Organization Recommendations**: Suggests optimal folder structures based on content analysis
- **Naming Conventions**: Recommends better filenames following best practices
- **Taxonomy Management**: Helps maintain consistent classification systems

Eratosthenes supports multiple AI providers:
- **Ollama** (local, recommended for privacy)
- **OpenAI** (GPT models)
- **Google Gemini** (Gemini models)
- **Anthropic Claude** (Claude models)

The agent uses a provider-agnostic architecture with automatic fallback, ensuring reliability and flexibility.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## About imediacorp

**imediacorp** is committed to innovation without borders, where profit is the outcome of purpose. We build tools that embody scientific integrity: falsifiable, reproducible, and transparent.

### Our Tools Ecosystem

File Organizer is part of imediacorp's **Arts & Sciences** philosophy, complementing our tools:

**Creative Tools:**
- **🎭 [Rhapsode](https://imediacorp.com/rhapsode)** - Narrative INDE for writers and storytellers
- **🎵 [Harmonia](https://imediacorp.com/harmonia)** - Music INDE for composers and musicians
- **🎬 Production Desk** - Production workflow tools for filmmakers
- **📁 File Organizer** - Scientific file organization for creators

**Diagnostic & Research Tools:**
- **🔬 CHaDD** - Comprehensive Harmonic Autonomous Dual-Probe Diagnostic platform
- **📁 File Organizer** - Research data management and organization for CHaDD users

Together, these tools bring **scientific rigor to both creative and research processes**—where creativity meets precision, where research meets reproducibility, where inspiration meets structure.

- 🌐 [Website](https://imediacorp.com)
- 🔬 [Open Science Commitment](https://imediacorp.com/open-science)
- 📧 Contact: [See imediacorp.com](https://imediacorp.com/contact)

---

*"We don't just talk about Open Science—we build tools that embody it."*  
*"Arts and Sciences: Where creativity meets rigor, where inspiration meets precision."*

