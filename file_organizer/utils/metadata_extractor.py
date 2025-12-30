"""AI-powered metadata extraction utilities."""

from pathlib import Path
from typing import Dict, Any, Optional

from file_organizer.utils.ai_advisory import extract_metadata


def extract_file_metadata(
    file_path: Path,
    provider: str = "auto",
) -> Dict[str, Any]:
    """Extract metadata from a file.
    
    This is a convenience wrapper around extract_metadata from ai_advisory.
    
    Args:
        file_path: File to extract metadata from
        provider: AI provider to use
        
    Returns:
        Dict with extracted metadata
    """
    return extract_metadata(file_path, provider=provider)


def batch_extract_metadata(
    files: list[Path],
    provider: str = "auto",
) -> Dict[Path, Dict[str, Any]]:
    """Extract metadata from multiple files.
    
    Args:
        files: List of file paths
        provider: AI provider to use
        
    Returns:
        Dict mapping file paths to their metadata
    """
    results = {}
    for file_path in files:
        if file_path.exists() and file_path.is_file():
            results[file_path] = extract_metadata(file_path, provider=provider)
    return results

