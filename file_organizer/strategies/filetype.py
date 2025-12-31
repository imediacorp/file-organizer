"""
File Type Organization Strategy - Organize files by their extension/type.
"""

from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
from file_organizer.core.strategy import Strategy
from file_organizer.core.operations import FileOperations


class FileTypeStrategy(Strategy):
    """
    Organize files by their file type/extension into category folders.
    
    Files are grouped into folders like `PDFs`, `Images`, etc.
    """
    
    # Default file type categories
    DEFAULT_CATEGORIES = {
        'Documents': ['.doc', '.docx', '.txt', '.rtf', '.odt', '.pages'],
        'PDFs': ['.pdf'],
        'Spreadsheets': ['.xls', '.xlsx', '.ods', '.csv', '.numbers'],
        'Presentations': ['.ppt', '.pptx', '.key'],
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.heic', '.heif'],
        'Vector Graphics': ['.svg', '.eps', '.ai', '.cdr'],
        'Audio': ['.mp3', '.wav', '.aac', '.m4a', '.flac', '.ogg', '.wma', '.aif', '.aiff', '.aax'],
        'MIDI': ['.mid', '.midi'],
        'Video': ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
        'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.php', '.rb', '.go', '.rs', '.swift', '.kt'],
        'Data': ['.json', '.xml', '.yaml', '.yml', '.toml', '.sql', '.db', '.sqlite'],
        'Fonts': ['.ttf', '.otf', '.woff', '.woff2'],
        'Database': ['.fmp12', '.mdb', '.accdb'],
        'Other': [],  # Catch-all
    }
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize file type strategy.
        
        Config options:
            categories: Dict mapping category names to lists of file extensions
            max_depth: Maximum recursion depth (default: 3)
            folder_prefix: Prefix for type folders (default: '' - no prefix)
            skip_folders: List of folder patterns to skip
        """
        super().__init__(config)
        self.categories = self.get_config('categories', self.DEFAULT_CATEGORIES)
        self.max_depth = self.get_config('max_depth', 3)
        self.folder_prefix = self.get_config('folder_prefix', '')  # No prefix by default
        self.skip_folders = self.get_config('skip_folders', [])
    
    def get_file_category(self, file_path: Path) -> str:
        """
        Determine which category a file belongs to based on extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Category name
        """
        ext = file_path.suffix.lower()
        
        for category, extensions in self.categories.items():
            if ext in extensions:
                return category
        
        return 'Other'
    
    def should_skip_folder(self, folder_path: Path, root_path: Path) -> bool:
        """
        Check if a folder should be skipped.
        
        Args:
            folder_path: Path to folder to check
            root_path: Root path for relative path calculation
            
        Returns:
            True if folder should be skipped
        """
        rel_path = str(folder_path.relative_to(root_path))
        
        for skip_pattern in self.skip_folders:
            if rel_path.startswith(skip_pattern) or skip_pattern in rel_path:
                return True
        
        # Skip folders with the prefix to avoid re-organizing
        if self.folder_prefix and self.folder_prefix in folder_path.name:
            return True
        
        return False
    
    def organize(self, root_path: Path, operations: FileOperations, target_folder: Optional[Path] = None, **kwargs) -> Dict:
        """
        Organize files by type.
        
        Args:
            root_path: Root directory
            operations: FileOperations instance
            target_folder: Optional specific folder to organize (if None, organizes entire tree)
            **kwargs: Additional arguments
            
        Returns:
            Dictionary with results
        """
        if target_folder:
            # Resolve target_folder relative to root_path
            if isinstance(target_folder, str):
                folder_to_organize = root_path / target_folder
            else:
                folder_to_organize = root_path / target_folder
            folder_to_organize = folder_to_organize.resolve()
            # Ensure it's actually a subpath
            try:
                folder_to_organize.relative_to(root_path)
            except ValueError:
                raise ValueError(f"'{target_folder}' is not in the subpath of '{root_path}'")
        else:
            folder_to_organize = root_path
        
        stats = {
            'files_moved': 0,
            'folders_created': 0,
            'errors': 0,
        }
        
        self._organize_folder(folder_to_organize, root_path, operations, 0, stats)
        
        return {
            'stats': stats,
            'errors': operations.errors,
        }
    
    def _organize_folder(self, folder_path: Path, root_path: Path, operations: FileOperations, 
                        current_depth: int, stats: Dict):
        """
        Recursively organize files by type within a folder.
        
        Args:
            folder_path: Folder to organize
            root_path: Root path for relative calculations
            operations: FileOperations instance
            current_depth: Current recursion depth
            stats: Statistics dictionary to update
        """
        if current_depth >= self.max_depth:
            return
        
        if self.should_skip_folder(folder_path, root_path):
            return
        
        try:
            files_by_type = defaultdict(list)
            has_files = False
            
            # Collect files in this folder
            for item in folder_path.iterdir():
                if item.name.startswith('.'):
                    continue
                
                if item.is_file():
                    has_files = True
                    category = self.get_file_category(item)
                    files_by_type[category].append(item)
                elif item.is_dir():
                    # Recursively organize subdirectories
                    # Skip folders that match category names (to avoid re-organizing)
                    if not self.folder_prefix or self.folder_prefix not in item.name:
                        # Also skip if folder name matches a category (likely already organized)
                        if item.name not in self.categories:
                            self._organize_folder(item, root_path, operations, current_depth + 1, stats)
            
            # Only organize if there are files and more than one type
            if has_files and len(files_by_type) > 1:
                operations.log(f"Organizing: {folder_path.relative_to(root_path)}")
                
                # Create type folders and move files
                for category, files in files_by_type.items():
                    if len(files) == 0:
                        continue
                    
                    type_folder = folder_path / f"{self.folder_prefix}{category}"
                    operations.create_directory(type_folder)
                    stats['folders_created'] += 1
                    
                    # Move files to type folder
                    for file_path in files:
                        dest = type_folder / file_path.name
                        if operations.move_file(file_path, dest):
                            stats['files_moved'] += 1
        
        except (PermissionError, OSError) as e:
            operations.log(f"ERROR: Could not organize {folder_path}: {str(e)}")
            stats['errors'] += 1
    
    def preview(self, root_path: Path, target_folder: Optional[Path] = None, **kwargs) -> List[Dict]:
        """
        Preview what changes would be made.
        
        Args:
            root_path: Root directory
            target_folder: Optional specific folder to analyze
            **kwargs: Additional arguments
            
        Returns:
            List of proposed moves
        """
        preview_moves = []
        
        if target_folder:
            # Resolve target_folder relative to root_path
            if isinstance(target_folder, str):
                folder_to_analyze = root_path / target_folder
            else:
                folder_to_analyze = root_path / target_folder
            folder_to_analyze = folder_to_analyze.resolve()
            # Ensure it's actually a subpath
            try:
                folder_to_analyze.relative_to(root_path)
            except ValueError:
                raise ValueError(f"'{target_folder}' is not in the subpath of '{root_path}'")
        else:
            folder_to_analyze = root_path
        
        self._preview_folder(folder_to_analyze, root_path, preview_moves, 0)
        
        return preview_moves
    
    def _preview_folder(self, folder_path: Path, root_path: Path, preview_moves: List[Dict], current_depth: int):
        """
        Recursively preview organization for a folder.
        
        Args:
            folder_path: Folder to analyze
            root_path: Root path for relative calculations
            preview_moves: List to append proposed moves to
            current_depth: Current recursion depth
        """
        if current_depth >= self.max_depth:
            return
        
        if self.should_skip_folder(folder_path, root_path):
            return
        
        try:
            files_by_type = defaultdict(list)
            has_files = False
            
            for item in folder_path.iterdir():
                if item.name.startswith('.'):
                    continue
                
                if item.is_file():
                    has_files = True
                    category = self.get_file_category(item)
                    files_by_type[category].append(item)
                elif item.is_dir():
                    # Skip folders that match category names (likely already organized)
                    if not self.folder_prefix or self.folder_prefix not in item.name:
                        if item.name not in self.categories:
                            self._preview_folder(item, root_path, preview_moves, current_depth + 1)
            
            # Generate preview moves
            if has_files and len(files_by_type) > 1:
                for category, files in files_by_type.items():
                    if len(files) == 0:
                        continue
                    
                    type_folder = folder_path / f"{self.folder_prefix}{category}"
                    
                    for file_path in files:
                        dest = type_folder / file_path.name
                        preview_moves.append({
                            'source': str(file_path.relative_to(root_path)),
                            'destination': str(dest.relative_to(root_path)),
                            'category': category,
                        })
        
        except (PermissionError, OSError):
            pass  # Skip folders we can't access
    
    def validate_config(self) -> List[str]:
        """Validate configuration."""
        errors = []
        
        categories = self.get_config('categories')
        if categories and not isinstance(categories, dict):
            errors.append("'categories' must be a dictionary")
        
        max_depth = self.get_config('max_depth')
        if max_depth and not isinstance(max_depth, int) or (isinstance(max_depth, int) and max_depth < 0):
            errors.append("'max_depth' must be a non-negative integer")
        
        return errors

    def suggest_category_name(self, file_path: Path) -> Optional[str]:
        """
        Use AI to suggest a better category name for a file (optional enhancement).
        
        Args:
            file_path: File to categorize
            
        Returns:
            Suggested category name or None if AI not available
        """
        try:
            from file_organizer.ai import get_ai_suggestion, AIProvider
            
            payload = {
                "request": "suggest_file_category",
                "domain": "library_science",
                "context": {
                    "filename": file_path.name,
                    "extension": file_path.suffix,
                },
                "instructions": "Suggest a single category name for this file based on library science principles. Return only the category name.",
            }
            
            result = get_ai_suggestion(payload, provider=AIProvider.AUTO, quick=True)
            if isinstance(result, dict) and result.get("ok"):
                text = result.get("text", "").strip()
                # Extract category name (first line or first word)
                category = text.split("\n")[0].split(",")[0].strip()
                return category
        except Exception:
            pass
        
        return None
    
    def get_ai_enhanced_category(self, file_path: Path) -> str:
        """
        Get category for file, optionally enhanced with AI.
        
        Args:
            file_path: File to categorize
            
        Returns:
            Category name
        """
        # First try standard categorization
        category = self.get_file_category(file_path)
        
        # If AI enhancement is enabled and category is "Other", try AI
        if self.get_config("use_ai_enhancement", False) and category == "Other":
            ai_category = self.suggest_category_name(file_path)
            if ai_category:
                return ai_category
        
        return category

