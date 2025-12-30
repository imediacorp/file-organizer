# Migration Guide from Old Scripts

This guide helps you migrate from the old standalone scripts to the new unified `file-organizer` tool.

## Overview

The old scripts have been refactored into a unified, extensible tool. All functionality is preserved, but the interface has changed to be more consistent and powerful.

## Script Mappings

### `organize_by_filetype.py` → `file-organizer organize filetype`

**Old Usage:**
```bash
python3 organize_by_filetype.py --dry-run
python3 organize_by_filetype.py "03-Business"
python3 organize_by_filetype.py "03-Business/imediaCorp" --dry-run
```

**New Usage:**
```bash
file-organizer preview filetype .
file-organizer organize filetype . --target-folder "03-Business"
file-organizer organize filetype . --target-folder "03-Business/imediaCorp" --dry-run
```

**Key Differences:**
- Use `preview` instead of `--dry-run` for preview-only mode
- Use `--target-folder` to specify a specific folder (equivalent to the old positional argument)
- The strategy name (`filetype`) is now explicit

### `generate_index.py` → `file-organizer index`

**Old Usage:**
```bash
python3 generate_index.py
```

**New Usage:**
```bash
file-organizer index .
```

**Key Differences:**
- Path is now explicit (use `.` for current directory)
- Output paths can be customized with `--markdown` and `--html` options

### `compare_file_versions.py` → `file-organizer duplicates`

**Old Usage:**
```bash
python3 compare_file_versions.py
python3 compare_file_versions.py "04-Financial"
python3 compare_file_versions.py "05-Music" --hash-large --max-size 200
```

**New Usage:**
```bash
file-organizer duplicates .
file-organizer duplicates "04-Financial"
file-organizer duplicates "05-Music" --hash-large --max-size 200
```

**Key Differences:**
- Command name changed from `compare_file_versions` to `duplicates`
- Same options available (`--hash-large`, `--max-size`)
- Output paths can be customized with `--json` and `--report` options

### `organize_documents.py` → `file-organizer organize rule_based`

This is the biggest change, as the old script had hardcoded rules. You'll need to create a configuration file.

**Old Usage:**
```bash
python3 organize_documents.py --dry-run
python3 organize_documents.py
```

**Migration Steps:**

1. Create a configuration file (`config.yaml`) based on the old rules:

```yaml
strategies:
  rule_based:
    enabled: true
    merge_folders: true
    file_rules:
      - pattern: "Amazon Invoice.pdf"
        type: exact
        destination: "04-Financial/Invoices & Receipts"
      - pattern: "Apartment Purchase Contract and Title Deeds.pdf"
        type: exact
        destination: "01-Properties/General"
      # Add all your file mappings here
    folder_rules:
      - pattern: "Auctions"
        type: exact
        destination: "04-Financial/Invoices & Receipts/Auctions"
      - pattern: "Belek Properties"
        type: exact
        destination: "01-Properties/Belek Properties"
      # Add all your folder mappings here
```

2. Use the new command:

```bash
file-organizer preview rule_based . --config config.yaml
file-organizer organize rule_based . --config config.yaml
```

**Key Differences:**
- Rules are now in a configuration file instead of hardcoded
- Much more flexible - can use glob patterns and regex
- Can be reused and shared

## Configuration Files

The new tool uses YAML or JSON configuration files instead of hardcoded rules. Example configurations are available in `file_organizer/config/examples/`.

### Creating a Configuration File

1. Start with an example:
   ```bash
   cp file_organizer/config/examples/filetype.yaml my_config.yaml
   ```

2. Customize it for your needs

3. Use it:
   ```bash
   file-organizer organize filetype . --config my_config.yaml
   ```

## Transaction Logs

The old scripts saved move information to JSON files, but didn't have a rollback feature. The new tool includes transaction logging with rollback support.

**Rollback Usage:**
```bash
# If something goes wrong, rollback
file-organizer rollback organization_transaction_log.json
```

## Benefits of Migration

1. **Unified Interface**: All commands use the same CLI structure
2. **Configuration-Driven**: Rules are in files, not hardcoded
3. **Extensible**: Easy to add custom strategies
4. **Safety**: Transaction logging and rollback support
5. **Library**: Can be used as a Python library, not just CLI
6. **Better Error Handling**: More informative error messages
7. **Consistent Logging**: All operations use the same logging format

## Backward Compatibility

The old scripts are preserved in your directory and can still be used. However, we recommend migrating to the new tool for:
- Better maintainability
- More features
- Configuration reusability
- Better safety features

## Getting Help

If you encounter issues during migration:

1. Check the main README for usage examples
2. Look at example configurations in `file_organizer/config/examples/`
3. Use `--dry-run` or `preview` to test before making changes
4. Start with a small test directory
5. Check transaction logs if something goes wrong

