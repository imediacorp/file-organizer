"""
Main file organizer class that orchestrates strategies and operations.
"""

from pathlib import Path
from typing import Dict, List, Optional
from file_organizer.core.operations import FileOperations
from file_organizer.core.strategy import Strategy
from file_organizer.strategies import get_strategy
from file_organizer.config.loader import ConfigManager
from file_organizer.utils.mounts import validate_path_for_operations, is_network_path


class FileOrganizer:
    """
    Main orchestrator for file organization.
    
    Manages strategies, operations, and configuration.
    """
    
    def __init__(self, root_path: Path, config: Optional[ConfigManager] = None, 
                 dry_run: bool = False, log_file: Optional[Path] = None,
                 validate_path: bool = True):
        """
        Initialize file organizer.
        
        Args:
            root_path: Root directory to organize (can be external or network drive)
            config: Optional ConfigManager instance
            dry_run: If True, don't actually move files
            log_file: Optional log file path
            validate_path: If True, validate path accessibility (default: True)
        """
        self.root_path = Path(root_path).resolve()
        self.config = config or ConfigManager()
        self.dry_run = dry_run
        self.log_file = log_file
        self.is_network = is_network_path(self.root_path)
        
        # Validate path if requested
        if validate_path and not dry_run:
            is_valid, error = validate_path_for_operations(self.root_path, require_write=True)
            if not is_valid:
                raise ValueError(f"Cannot organize path: {error}")
        
        self.operations = FileOperations(self.root_path, dry_run=dry_run, log_file=log_file)
        self.strategies: Dict[str, Strategy] = {}
    
    def load_config(self, config_path: Path):
        """Load configuration from file."""
        self.config.load(config_path)
    
    def register_strategy(self, name: str, strategy: Strategy):
        """
        Register a strategy instance.
        
        Args:
            name: Strategy name
            strategy: Strategy instance
        """
        self.strategies[name] = strategy
    
    def get_strategy(self, name: str, config: Optional[Dict] = None) -> Optional[Strategy]:
        """
        Get a strategy instance by name.
        
        Args:
            name: Strategy name
            config: Optional configuration dictionary for the strategy
            
        Returns:
            Strategy instance or None if not found
        """
        if name in self.strategies:
            return self.strategies[name]
        
        strategy_class = get_strategy(name)
        if strategy_class is None:
            return None
        
        # Get strategy config from main config if not provided
        if config is None:
            config = self.config.get_strategy_config(name)
        
        strategy = strategy_class(config=config)
        self.strategies[name] = strategy
        return strategy
    
    def organize(self, strategy_name: str, target_folder: Optional[Path] = None, 
                 strategy_config: Optional[Dict] = None, **kwargs) -> Dict:
        """
        Organize files using a specific strategy.
        
        Args:
            strategy_name: Name of the strategy to use
            target_folder: Optional specific folder to organize (if None, organizes entire tree)
            strategy_config: Optional strategy-specific configuration
            **kwargs: Additional strategy-specific arguments
            
        Returns:
            Dictionary with organization results
        """
        strategy = self.get_strategy(strategy_name, strategy_config)
        if strategy is None:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        # Validate strategy configuration
        errors = strategy.validate_config()
        if errors:
            raise ValueError(f"Strategy configuration errors: {', '.join(errors)}")
        
        # Start transaction
        transaction_id = self.operations.start_transaction()
        
        # Run organization
        result = strategy.organize(
            self.root_path,
            self.operations,
            target_folder=target_folder,
            **kwargs
        )
        
        # Save transaction log if not dry run
        if not self.dry_run and self.operations.transactions:
            log_file = self.log_file or (self.root_path / "organization_transaction_log.json")
            self.operations.save_transaction_log(log_file)
            result['transaction_log'] = str(log_file)
        
        result['transaction_id'] = transaction_id
        result['statistics'] = self.operations.get_statistics()
        
        return result
    
    def preview(self, strategy_name: str, target_folder: Optional[Path] = None,
                strategy_config: Optional[Dict] = None, **kwargs) -> List[Dict]:
        """
        Preview what changes would be made by a strategy.
        
        Args:
            strategy_name: Name of the strategy to preview
            target_folder: Optional specific folder to analyze
            strategy_config: Optional strategy-specific configuration
            **kwargs: Additional strategy-specific arguments
            
        Returns:
            List of proposed moves
        """
        strategy = self.get_strategy(strategy_name, strategy_config)
        if strategy is None:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        return strategy.preview(self.root_path, target_folder=target_folder, **kwargs)
    
    def rollback(self, log_file: Path) -> bool:
        """
        Rollback operations from a transaction log.
        
        Args:
            log_file: Path to transaction log file
            
        Returns:
            True if successful
        """
        return self.operations.rollback(log_file)
    
    def get_statistics(self) -> Dict:
        """Get statistics about operations performed."""
        return self.operations.get_statistics()

