"""
Configuration loader for file organizer.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Optional, Any
from file_organizer.config.schema import validate_config_schema


class ConfigManager:
    """
    Manages configuration loading and validation.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
    
    def load(self, config_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file (YAML or JSON)
                          If None, uses self.config_path
            
        Returns:
            Configuration dictionary
        """
        if config_path is None:
            config_path = self.config_path
        
        if config_path is None or not config_path.exists():
            return self.get_default_config()
        
        config_path = Path(config_path)
        
        if config_path.suffix.lower() in ('.yaml', '.yml'):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
        elif config_path.suffix.lower() == '.json':
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
        
        # Validate configuration
        errors = validate_config_schema(self.config)
        if errors:
            raise ValueError(f"Configuration validation errors: {', '.join(errors)}")
        
        return self.config
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration.
        
        Returns:
            Default configuration dictionary
        """
        # Import default categories
        from file_organizer.strategies.filetype import FileTypeStrategy
        
        return {
            'strategies': {
                'filetype': {
                    'enabled': True,
                    'categories': FileTypeStrategy.DEFAULT_CATEGORIES,
                    'max_depth': 3,
                    'folder_prefix': '_by_type_',
                    'skip_folders': [],
                },
                'rule_based': {
                    'enabled': False,
                    'file_rules': [],
                    'folder_rules': [],
                    'merge_folders': True,
                },
            },
            'general': {
                'dry_run': False,
                'log_file': None,
                'transaction_log': None,
            },
        }
    
    def get_strategy_config(self, strategy_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific strategy.
        
        Args:
            strategy_name: Name of the strategy
            
        Returns:
            Strategy configuration dictionary or None
        """
        strategies = self.config.get('strategies', {})
        return strategies.get(strategy_name)
    
    def is_strategy_enabled(self, strategy_name: str) -> bool:
        """
        Check if a strategy is enabled.
        
        Args:
            strategy_name: Name of the strategy
            
        Returns:
            True if strategy is enabled
        """
        strategy_config = self.get_strategy_config(strategy_name)
        if strategy_config is None:
            return False
        return strategy_config.get('enabled', False)
    
    def save(self, config_path: Path, format: str = 'yaml'):
        """
        Save configuration to file.
        
        Args:
            config_path: Path to save configuration
            format: Format to save ('yaml' or 'json')
        """
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == 'yaml':
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
        elif format.lower() == 'json':
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def merge(self, other_config: Dict[str, Any]):
        """
        Merge another configuration dictionary into this one.
        
        Args:
            other_config: Configuration dictionary to merge
        """
        def deep_merge(base: Dict, update: Dict):
            """Recursively merge dictionaries."""
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
        
        deep_merge(self.config, other_config)



