"""
Base class for organization strategies.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional
from file_organizer.core.operations import FileOperations


class Strategy(ABC):
    """
    Base class for file organization strategies.
    
    All strategies must implement the organize() method, which takes a root path
    and file operations object, and organizes files according to the strategy.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the strategy.
        
        Args:
            config: Configuration dictionary for the strategy
        """
        self.config = config or {}
        self.name = self.__class__.__name__
    
    @abstractmethod
    def organize(self, root_path: Path, operations: FileOperations, **kwargs) -> Dict:
        """
        Organize files according to this strategy.
        
        Args:
            root_path: Root directory to organize
            operations: FileOperations instance for safe file operations
            **kwargs: Additional strategy-specific arguments
            
        Returns:
            Dictionary with organization results (stats, errors, etc.)
        """
        pass
    
    @abstractmethod
    def preview(self, root_path: Path, **kwargs) -> List[Dict]:
        """
        Preview what changes would be made without actually moving files.
        
        Args:
            root_path: Root directory to analyze
            **kwargs: Additional strategy-specific arguments
            
        Returns:
            List of dictionaries describing proposed moves, each with 'source' and 'destination'
        """
        pass
    
    def get_config(self, key: str, default=None):
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'categories.Documents')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value
    
    def validate_config(self) -> List[str]:
        """
        Validate strategy configuration.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        return []  # Override in subclasses for custom validation

