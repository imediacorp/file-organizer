#!/usr/bin/env python3
"""
Command-line interface for file organizer.
"""

import argparse
import sys
from pathlib import Path
from file_organizer.core.organizer import FileOrganizer
from file_organizer.config.loader import ConfigManager
from file_organizer.utils.index import IndexGenerator
from file_organizer.utils.duplicates import DuplicateFinder
from file_organizer.utils.mounts import get_path_info, is_network_path

# Try to import AI utilities (may not be available)
try:
    from file_organizer.utils.ai_advisory import (
        suggest_organization_structure,
        classify_document,
        extract_metadata,
        suggest_filename,
    )
    AI_AVAILABLE = True
except Exception:
    AI_AVAILABLE = False


def organize_command(args):
    """Handle organize command."""
    root_path = Path(args.path).resolve()
    if not root_path.exists():
        print(f"Error: Path does not exist: {root_path}")
        print("\nTip: For network drives, make sure:")
        print("  - The drive is mounted and accessible")
        print("  - You have proper authentication credentials")
        print("  - The path is accessible from your current system")
        sys.exit(1)
    
    # Check if it's a network path and provide info
    if is_network_path(root_path):
        path_info = get_path_info(root_path)
        print(f"Detected network path: {root_path}")
        if path_info.get('is_readonly', False):
            print("Warning: Path appears to be read-only. Organization may fail.")
    
    # Load configuration if provided
    config = ConfigManager()
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Error: Configuration file does not exist: {config_path}")
            sys.exit(1)
        config.load(config_path)
    
    # Create organizer
    organizer = FileOrganizer(
        root_path,
        config=config,
        dry_run=args.dry_run,
        log_file=Path(args.log_file) if args.log_file else None
    )
    
    # Run organization
    try:
        result = organizer.organize(
            args.strategy,
            target_folder=Path(args.target_folder) if args.target_folder else None
        )
        
        print("\n" + "=" * 60)
        print("Organization complete!")
        stats = result.get('statistics', {})
        print(f"Total operations: {stats.get('total_operations', 0)}")
        print(f"File moves: {stats.get('file_moves', 0)}")
        print(f"Folder moves: {stats.get('folder_moves', 0)}")
        print(f"Errors: {stats.get('errors', 0)}")
        if 'transaction_log' in result:
            print(f"Transaction log: {result['transaction_log']}")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def preview_command(args):
    """Handle preview command."""
    root_path = Path(args.path).resolve()
    if not root_path.exists():
        print(f"Error: Path does not exist: {root_path}")
        sys.exit(1)
    
    # Load configuration if provided
    config = ConfigManager()
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            config.load(config_path)
    
    # Create organizer
    organizer = FileOrganizer(
        root_path,
        config=config,
        dry_run=True  # Always dry run for preview
    )
    
    # Get preview
    try:
        preview_moves = organizer.preview(
            args.strategy,
            target_folder=Path(args.target_folder) if args.target_folder else None
        )
        
        print(f"\nPreview: {len(preview_moves)} operations would be performed\n")
        print("=" * 80)
        
        # Show confidence and reasoning for AI strategy
        show_details = args.strategy == 'ai_suggested'
        
        for i, move in enumerate(preview_moves[:50], 1):
            if show_details and 'confidence' in move:
                print(f"{i}. {move['source']} -> {move['destination']}")
                print(f"   Confidence: {move.get('confidence', 0):.2f}")
                if move.get('reasoning'):
                    print(f"   Reasoning: {move.get('reasoning', '')[:100]}")
            else:
                print(f"{i}. {move['source']} -> {move['destination']}")
        
        if len(preview_moves) > 50:
            print(f"\n... and {len(preview_moves) - 50} more operations")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def index_command(args):
    """Handle index command."""
    root_path = Path(args.path).resolve()
    if not root_path.exists():
        print(f"Error: Path does not exist: {root_path}")
        sys.exit(1)
    
    generator = IndexGenerator(
        root_path,
        index_dir=Path(args.output_dir) if args.output_dir else None
    )
    
    try:
        result = generator.generate(
            output_markdown=Path(args.markdown) if args.markdown else None,
            output_html=Path(args.html) if args.html else None
        )
        
        print("\nIndex generation complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def duplicates_command(args):
    """Handle duplicates command."""
    root_path = Path(args.path).resolve()
    if not root_path.exists():
        print(f"Error: Path does not exist: {root_path}")
        sys.exit(1)
    
    finder = DuplicateFinder(
        root_path,
        hash_large_files=args.hash_large,
        max_file_size_mb=args.max_size
    )
    
    output_json = Path(args.json) if args.json else (root_path / "file_version_analysis.json")
    output_report = Path(args.report) if args.report else (root_path / "file_version_report.txt")
    
    try:
        result = finder.analyze(output_json=output_json, output_report=output_report)
        
        # Print summary
        summary = result.get('summary', {})
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("-" * 80)
        print(f"Exact Duplicates: {summary.get('total_exact_duplicates', 0)} groups")
        print(f"Name Duplicates: {summary.get('total_name_duplicates', 0)} groups")
        print(f"Similar Names: {summary.get('total_similar_names', 0)} pairs")
        print(f"Version Files: {summary.get('total_version_files', 0)}")
        print(f"Large Files: {summary.get('total_large_files', 0)}")
        print(f"Old Files: {summary.get('total_old_files', 0)}")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def rollback_command(args):
    """Handle rollback command."""
    log_file = Path(args.log_file)
    if not log_file.exists():
        print(f"Error: Transaction log does not exist: {log_file}")
        sys.exit(1)
    
    # Determine root path from log file
    import json
    with open(log_file, 'r') as f:
        log_data = json.load(f)
        root_path = Path(log_data.get('root_path', '.'))
    
    organizer = FileOrganizer(root_path, dry_run=args.dry_run)
    
    try:
        success = organizer.rollback(log_file)
        if success:
            print("\nRollback complete!")
        else:
            print("\nRollback completed with errors. Check logs.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def suggest_command(args):
    """Handle suggest command (AI advisory mode)."""
    if not AI_AVAILABLE:
        print("Error: AI features not available. Install AI dependencies.")
        sys.exit(1)
    
    root_path = Path(args.path).resolve()
    if not root_path.exists():
        print(f"Error: Path does not exist: {root_path}")
        sys.exit(1)
    
    try:
        result = suggest_organization_structure(
            root_path,
            provider=args.provider,
            max_files=args.max_files,
        )
        
        if result.get("success"):
            print("\n" + "=" * 80)
            print("ORGANIZATION SUGGESTIONS")
            print("=" * 80)
            print(result.get("suggestions", ""))
            if "files_analyzed" in result:
                print(f"\nFiles analyzed: {result['files_analyzed']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def classify_command(args):
    """Handle classify command."""
    if not AI_AVAILABLE:
        print("Error: AI features not available. Install AI dependencies.")
        sys.exit(1)
    
    file_path = Path(args.file).resolve()
    if not file_path.exists():
        print(f"Error: File does not exist: {file_path}")
        sys.exit(1)
    
    try:
        result = classify_document(file_path, provider=args.provider)
        
        if result.get("success"):
            print("\n" + "=" * 80)
            print("DOCUMENT CLASSIFICATION")
            print("=" * 80)
            classification = result.get("classification", {})
            for key, value in classification.items():
                if key != "raw_response":
                    print(f"{key}: {value}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def extract_metadata_command(args):
    """Handle extract-metadata command."""
    if not AI_AVAILABLE:
        print("Error: AI features not available. Install AI dependencies.")
        sys.exit(1)
    
    file_path = Path(args.file).resolve()
    if not file_path.exists():
        print(f"Error: File does not exist: {file_path}")
        sys.exit(1)
    
    try:
        result = extract_metadata(file_path, provider=args.provider)
        
        if result.get("success"):
            print("\n" + "=" * 80)
            print("EXTRACTED METADATA")
            print("=" * 80)
            metadata = result.get("metadata", {})
            for key, value in metadata.items():
                if key != "raw_response":
                    print(f"{key}: {value}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='File Organizer - Organize large content trees using various strategies'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Organize command
    organize_parser = subparsers.add_parser('organize', help='Organize files using a strategy')
    organize_parser.add_argument('strategy', help='Strategy name (filetype, rule_based)')
    organize_parser.add_argument('path', help='Path to organize')
    organize_parser.add_argument('--target-folder', help='Specific folder to organize')
    organize_parser.add_argument('--config', help='Configuration file path')
    organize_parser.add_argument('--dry-run', action='store_true', help='Preview changes without moving files')
    organize_parser.add_argument('--log-file', help='Log file path')
    
    # Preview command
    preview_parser = subparsers.add_parser('preview', help='Preview what changes would be made')
    preview_parser.add_argument('strategy', help='Strategy name')
    preview_parser.add_argument('path', help='Path to analyze')
    preview_parser.add_argument('--target-folder', help='Specific folder to analyze')
    preview_parser.add_argument('--config', help='Configuration file path')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Generate index files')
    index_parser.add_argument('path', help='Path to index')
    index_parser.add_argument('--output-dir', help='Output directory for index files')
    index_parser.add_argument('--markdown', help='Markdown output file path')
    index_parser.add_argument('--html', help='HTML output file path')
    
    # Duplicates command
    duplicates_parser = subparsers.add_parser('duplicates', help='Find duplicate files')
    duplicates_parser.add_argument('path', help='Path to analyze')
    duplicates_parser.add_argument('--json', help='JSON output file path')
    duplicates_parser.add_argument('--report', help='Text report output file path')
    duplicates_parser.add_argument('--hash-large', action='store_true', help='Hash large files')
    duplicates_parser.add_argument('--max-size', type=int, default=50, help='Max file size in MB for hashing (default: 50)')
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback previous organization')
    rollback_parser.add_argument('log_file', help='Transaction log file path')
    rollback_parser.add_argument('--dry-run', action='store_true', help='Preview rollback without executing')
    
    # Suggest command (AI advisory)
    if AI_AVAILABLE:
        suggest_parser = subparsers.add_parser('suggest', help='Get AI suggestions for organization structure')
        suggest_parser.add_argument('path', help='Path to analyze')
        suggest_parser.add_argument('--provider', default='auto', help='AI provider (auto, ollama, openai, gemini, anthropic)')
        suggest_parser.add_argument('--max-files', type=int, default=50, help='Maximum number of files to analyze')
    
    # Classify command
    if AI_AVAILABLE:
        classify_parser = subparsers.add_parser('classify', help='Classify a document using AI')
        classify_parser.add_argument('file', help='File to classify')
        classify_parser.add_argument('--provider', default='auto', help='AI provider (auto, ollama, openai, gemini, anthropic)')
    
    # Extract metadata command
    if AI_AVAILABLE:
        metadata_parser = subparsers.add_parser('extract-metadata', help='Extract metadata from a file using AI')
        metadata_parser.add_argument('file', help='File to extract metadata from')
        metadata_parser.add_argument('--provider', default='auto', help='AI provider (auto, ollama, openai, gemini, anthropic)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Route to appropriate command handler
    if args.command == 'organize':
        organize_command(args)
    elif args.command == 'preview':
        preview_command(args)
    elif args.command == 'index':
        index_command(args)
    elif args.command == 'duplicates':
        duplicates_command(args)
    elif args.command == 'rollback':
        rollback_command(args)
    elif args.command == 'suggest':
        if AI_AVAILABLE:
            suggest_command(args)
        else:
            print("Error: AI features not available. Install AI dependencies.")
            sys.exit(1)
    elif args.command == 'classify':
        if AI_AVAILABLE:
            classify_command(args)
        else:
            print("Error: AI features not available. Install AI dependencies.")
            sys.exit(1)
    elif args.command == 'extract-metadata':
        if AI_AVAILABLE:
            extract_metadata_command(args)
        else:
            print("Error: AI features not available. Install AI dependencies.")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()

