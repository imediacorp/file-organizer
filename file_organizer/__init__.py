"""
File Organizer - A flexible, extensible tool for organizing large content trees.

This package provides both a library and CLI interface for organizing files
using various strategies (file type, rules, dates, etc.).
"""

__version__ = "1.0.0"

from file_organizer.core.organizer import FileOrganizer
from file_organizer.core.operations import FileOperations
from file_organizer.core.strategy import Strategy

# Try to import AI features (may not be available if dependencies missing)
try:
    from file_organizer.ai import get_ai_suggestion, AIProvider, get_provider_status
    __all__ = ['FileOrganizer', 'FileOperations', 'Strategy', 'get_ai_suggestion', 'AIProvider', 'get_provider_status']
except Exception:
__all__ = ['FileOrganizer', 'FileOperations', 'Strategy']

