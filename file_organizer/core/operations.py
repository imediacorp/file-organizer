"""
Core file operations with safety features: dry-run, transaction logging, rollback support.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Callable
from collections import defaultdict


class FileOperations:
    """
    Safe file operations with transaction logging and rollback support.
    """
    
    def __init__(self, root_path: Path, dry_run: bool = False, log_file: Optional[Path] = None):
        """
        Initialize file operations.
        
        Args:
            root_path: Root directory for operations (used for relative paths in logs)
            dry_run: If True, don't actually move files
            log_file: Optional log file path for transaction log
        """
        self.root_path = Path(root_path).resolve()
        self.dry_run = dry_run
        self.log_file = log_file
        self.transactions: List[Dict] = []
        self.errors: List[str] = []
        self.duplicates = defaultdict(int)
        self._current_transaction_id: Optional[str] = None
        
    def log(self, message: str):
        """Log a message."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        if self.log_file and not self.dry_run:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + "\n")
    
    def start_transaction(self, transaction_id: Optional[str] = None) -> str:
        """
        Start a new transaction for grouping operations.
        
        Args:
            transaction_id: Optional transaction ID, auto-generated if not provided
            
        Returns:
            Transaction ID
        """
        if transaction_id is None:
            transaction_id = datetime.now().isoformat()
        self._current_transaction_id = transaction_id
        return transaction_id
    
    def get_unique_filename(self, target_path: Path) -> Path:
        """
        Get a unique filename if target already exists.
        
        Args:
            target_path: Desired target path
            
        Returns:
            Unique path (may be the same as target_path if no conflict)
        """
        if not target_path.exists():
            return target_path
        
        base = target_path.stem
        suffix = target_path.suffix
        parent = target_path.parent
        counter = self.duplicates[str(target_path)]
        self.duplicates[str(target_path)] += 1
        
        new_name = f"{base}_duplicate_{counter}{suffix}"
        return parent / new_name
    
    def move_file(self, source: Path, destination: Path, preserve_timestamps: bool = True) -> bool:
        """
        Move a file to destination, handling duplicates.
        
        Args:
            source: Source file path
            destination: Destination file path
            preserve_timestamps: If True, preserve file timestamps
            
        Returns:
            True if successful, False otherwise
        """
        try:
            source_path = Path(source).resolve()
            dest_path = Path(destination)
            
            if not source_path.exists():
                self.log(f"Warning: Source does not exist: {source_path}")
                return False
            
            if not source_path.is_file():
                self.log(f"Warning: Source is not a file: {source_path}")
                return False
            
            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Handle duplicates
            if dest_path.exists():
                dest_path = self.get_unique_filename(dest_path)
                self.log(f"Duplicate detected, using: {dest_path.name}")
            
            # Record transaction
            # Try to get relative paths, fall back to absolute if not subpath
            try:
                rel_source = str(source_path.relative_to(self.root_path))
            except ValueError:
                rel_source = str(source_path)
            
            try:
                rel_dest = str(dest_path.relative_to(self.root_path))
            except ValueError:
                rel_dest = str(dest_path)
            
            transaction = {
                'type': 'move_file',
                'source': rel_source,
                'destination': rel_dest,
                'absolute_source': str(source_path),
                'absolute_destination': str(dest_path),
                'timestamp': datetime.now().isoformat(),
                'transaction_id': self._current_transaction_id,
            }
            
            if not self.dry_run:
                # Preserve timestamps
                stat = source_path.stat()
                shutil.move(str(source_path), str(dest_path))
                if preserve_timestamps:
                    os.utime(dest_path, (stat.st_atime, stat.st_mtime))
                
                transaction['size'] = stat.st_size
                transaction['atime'] = stat.st_atime
                transaction['mtime'] = stat.st_mtime
            
            self.transactions.append(transaction)
            try:
                log_dest = dest_path.relative_to(self.root_path)
            except ValueError:
                log_dest = dest_path
            self.log(f"Moved: {source_path.name} -> {log_dest}")
            return True
            
        except Exception as e:
            error_msg = f"Error moving {source} to {destination}: {str(e)}"
            self.log(f"ERROR: {error_msg}")
            self.errors.append(error_msg)
            return False
    
    def move_folder(self, source: Path, destination: Path, merge: bool = True) -> bool:
        """
        Move an entire folder to destination.
        
        Args:
            source: Source folder path
            destination: Destination folder path
            merge: If True and destination exists, merge contents instead of overwriting
            
        Returns:
            True if successful, False otherwise
        """
        try:
            source_path = Path(source).resolve()
            dest_path = Path(destination)
            
            if not source_path.exists() or not source_path.is_dir():
                self.log(f"Warning: Source folder does not exist: {source_path}")
                return False
            
            # If destination exists and merge is True, merge contents
            if dest_path.exists() and merge:
                self.log(f"Destination exists, merging: {dest_path}")
                # Move contents instead of folder
                for item in source_path.iterdir():
                    if item.name.startswith('.'):
                        continue
                    dest_item = dest_path / item.name
                    if item.is_file():
                        self.move_file(item, dest_item)
                    elif item.is_dir():
                        self.move_folder(item, dest_item, merge=True)
                # Remove empty source folder
                if not self.dry_run:
                    try:
                        source_path.rmdir()
                    except OSError:
                        pass  # Folder not empty, leave it
            else:
                # Move entire folder
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Try to get relative paths, fall back to absolute if not subpath
                try:
                    rel_source = str(source_path.relative_to(self.root_path))
                except ValueError:
                    rel_source = str(source_path)
                
                try:
                    rel_dest = str(dest_path.relative_to(self.root_path))
                except ValueError:
                    rel_dest = str(dest_path)
                
                transaction = {
                    'type': 'move_folder',
                    'source': rel_source,
                    'destination': rel_dest,
                    'absolute_source': str(source_path),
                    'absolute_destination': str(dest_path),
                    'timestamp': datetime.now().isoformat(),
                    'transaction_id': self._current_transaction_id,
                }
                
                if not self.dry_run:
                    shutil.move(str(source_path), str(dest_path))
                
                self.transactions.append(transaction)
                try:
                    log_dest = dest_path.relative_to(self.root_path)
                except ValueError:
                    log_dest = dest_path
                self.log(f"Moved folder: {source_path.name} -> {log_dest}")
            
            return True
            
        except Exception as e:
            error_msg = f"Error moving folder {source} to {destination}: {str(e)}"
            self.log(f"ERROR: {error_msg}")
            self.errors.append(error_msg)
            return False
    
    def copy_file(self, source: Path, destination: Path, preserve_timestamps: bool = True) -> bool:
        """
        Copy a file to destination.
        
        Args:
            source: Source file path
            destination: Destination file path
            preserve_timestamps: If True, preserve file timestamps
            
        Returns:
            True if successful, False otherwise
        """
        try:
            source_path = Path(source).resolve()
            dest_path = Path(destination)
            
            if not source_path.exists():
                self.log(f"Warning: Source does not exist: {source_path}")
                return False
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if dest_path.exists():
                dest_path = self.get_unique_filename(dest_path)
            
            # Try to get relative paths, fall back to absolute if not subpath
            try:
                rel_source = str(source_path.relative_to(self.root_path))
            except ValueError:
                rel_source = str(source_path)
            
            try:
                rel_dest = str(dest_path.relative_to(self.root_path))
            except ValueError:
                rel_dest = str(dest_path)
            
            transaction = {
                'type': 'copy_file',
                'source': rel_source,
                'destination': rel_dest,
                'absolute_source': str(source_path),
                'absolute_destination': str(dest_path),
                'timestamp': datetime.now().isoformat(),
                'transaction_id': self._current_transaction_id,
            }
            
            if not self.dry_run:
                stat = source_path.stat()
                shutil.copy2(str(source_path), str(dest_path))
                if preserve_timestamps:
                    os.utime(dest_path, (stat.st_atime, stat.st_mtime))
                
                transaction['size'] = stat.st_size
            
            self.transactions.append(transaction)
            try:
                log_dest = dest_path.relative_to(self.root_path)
            except ValueError:
                log_dest = dest_path
            self.log(f"Copied: {source_path.name} -> {log_dest}")
            return True
            
        except Exception as e:
            error_msg = f"Error copying {source} to {destination}: {str(e)}"
            self.log(f"ERROR: {error_msg}")
            self.errors.append(error_msg)
            return False
    
    def create_directory(self, path: Path) -> bool:
        """
        Create a directory if it doesn't exist.
        
        Args:
            path: Directory path to create
            
        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(path)
            if not path.exists():
                if not self.dry_run:
                    path.mkdir(parents=True, exist_ok=True)
                try:
                    log_path = path.relative_to(self.root_path)
                except ValueError:
                    log_path = path
                self.log(f"Created directory: {log_path}")
                return True
            return True
        except Exception as e:
            error_msg = f"Error creating directory {path}: {str(e)}"
            self.log(f"ERROR: {error_msg}")
            self.errors.append(error_msg)
            return False
    
    def save_transaction_log(self, output_file: Path):
        """
        Save transaction log to JSON file for rollback.
        
        Args:
            output_file: Path to save transaction log
        """
        log_data = {
            'root_path': str(self.root_path),
            'dry_run': self.dry_run,
            'timestamp': datetime.now().isoformat(),
            'transactions': self.transactions,
            'errors': self.errors,
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2)
    
    def load_transaction_log(self, log_file: Path) -> List[Dict]:
        """
        Load transaction log from JSON file.
        
        Args:
            log_file: Path to transaction log file
            
        Returns:
            List of transactions
        """
        with open(log_file, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        return log_data.get('transactions', [])
    
    def rollback(self, log_file: Path, confirm: bool = True) -> bool:
        """
        Rollback operations from a transaction log.
        
        Args:
            log_file: Path to transaction log file
            confirm: If True, prompt for confirmation (not implemented, always proceeds)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            transactions = self.load_transaction_log(log_file)
            # Reverse transactions to rollback in reverse order
            transactions.reverse()
            
            self.log(f"Rolling back {len(transactions)} operations...")
            
            for transaction in transactions:
                op_type = transaction.get('type')
                source = transaction.get('absolute_destination')
                destination = transaction.get('absolute_source')
                
                if op_type in ('move_file', 'move_folder'):
                    source_path = Path(source)
                    dest_path = Path(destination)
                    
                    if source_path.exists():
                        if op_type == 'move_file':
                            if not self.dry_run:
                                stat = source_path.stat()
                                shutil.move(str(source_path), str(dest_path))
                                # Restore timestamps if available
                                if 'atime' in transaction and 'mtime' in transaction:
                                    os.utime(dest_path, (transaction['atime'], transaction['mtime']))
                        else:  # move_folder
                            if not self.dry_run:
                                shutil.move(str(source_path), str(dest_path))
                        
                        try:
                            log_dest = dest_path.relative_to(self.root_path)
                        except ValueError:
                            log_dest = dest_path
                        self.log(f"Rolled back: {source_path.name} -> {log_dest}")
                elif op_type == 'copy_file':
                    # For copy operations, just delete the copied file
                    source_path = Path(source)
                    if source_path.exists() and not self.dry_run:
                        source_path.unlink()
                        try:
                            log_path = source_path.relative_to(self.root_path)
                        except ValueError:
                            log_path = source_path
                        self.log(f"Removed copied file: {log_path}")
            
            self.log("Rollback complete!")
            return True
            
        except Exception as e:
            error_msg = f"Error during rollback: {str(e)}"
            self.log(f"ERROR: {error_msg}")
            self.errors.append(error_msg)
            return False
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about operations performed.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_operations': len(self.transactions),
            'file_moves': len([t for t in self.transactions if t.get('type') == 'move_file']),
            'folder_moves': len([t for t in self.transactions if t.get('type') == 'move_folder']),
            'file_copies': len([t for t in self.transactions if t.get('type') == 'copy_file']),
            'errors': len(self.errors),
            'duplicates_handled': sum(self.duplicates.values()),
        }

