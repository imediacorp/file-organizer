"""
Rule-Based Organization Strategy - Organize files using pattern matching rules.
"""

import re
import fnmatch
from pathlib import Path
from typing import Any, Dict, List, Optional
from file_organizer.core.strategy import Strategy
from file_organizer.core.operations import FileOperations


class RuleBasedStrategy(Strategy):
    """
    Organize files using pattern matching rules (exact match, glob, regex).
    
    Rules can match file names or folder names and move them to specified destinations.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize rule-based strategy.
        
        Config options:
            file_rules: List of rules for files, each with:
                - pattern: Pattern to match (exact, glob, or regex)
                - type: 'exact', 'glob', or 'regex' (default: 'glob')
                - destination: Destination folder path (relative to root)
                - recursive: If True, search recursively (default: False)
            folder_rules: List of rules for folders, same format as file_rules
            merge_folders: If True, merge folder contents when destination exists (default: True)
        """
        super().__init__(config)
        self.file_rules = self.get_config('file_rules', [])
        self.folder_rules = self.get_config('folder_rules', [])
        self.merge_folders = self.get_config('merge_folders', True)
    
    def match_pattern(self, text: str, pattern: str, pattern_type: str = 'glob') -> bool:
        """
        Match text against a pattern.
        
        Args:
            text: Text to match
            pattern: Pattern to match against
            pattern_type: Type of pattern ('exact', 'glob', or 'regex')
            
        Returns:
            True if pattern matches
        """
        if pattern_type == 'exact':
            return text == pattern
        elif pattern_type == 'glob':
            return fnmatch.fnmatch(text, pattern)
        elif pattern_type == 'regex':
            try:
                return bool(re.search(pattern, text, re.IGNORECASE))
            except re.error:
                return False
        else:
            return False
    
    def find_matching_rule(self, name: str, rules: List[Dict]) -> Optional[Dict]:
        """
        Find the first matching rule for a name.
        
        Args:
            name: Name to match
            rules: List of rule dictionaries
            
        Returns:
            Matching rule dictionary or None
        """
        for rule in rules:
            pattern = rule.get('pattern', '')
            pattern_type = rule.get('type', 'glob')
            if self.match_pattern(name, pattern, pattern_type):
                return rule
        return None
    
    def organize(self, root_path: Path, operations: FileOperations, **kwargs) -> Dict:
        """
        Organize files and folders according to rules.
        
        Args:
            root_path: Root directory
            operations: FileOperations instance
            **kwargs: Additional arguments
            
        Returns:
            Dictionary with results
        """
        stats = {
            'files_moved': 0,
            'folders_moved': 0,
            'errors': 0,
        }
        
        # Process folder rules first (to avoid moving files that are in folders being moved)
        if self.folder_rules:
            self._organize_folders(root_path, root_path, operations, stats)
        
        # Process file rules
        if self.file_rules:
            self._organize_files(root_path, root_path, operations, stats)
        
        return {
            'stats': stats,
            'errors': operations.errors,
        }
    
    def _organize_folders(self, current_path: Path, root_path: Path, 
                         operations: FileOperations, stats: Dict):
        """
        Recursively organize folders according to rules.
        
        Args:
            current_path: Current directory to process
            root_path: Root path for relative calculations
            operations: FileOperations instance
            stats: Statistics dictionary to update
        """
        try:
            items = list(current_path.iterdir())
            
            for item in items:
                if item.name.startswith('.'):
                    continue
                
                if item.is_dir():
                    # Check if folder matches a rule
                    rule = self.find_matching_rule(item.name, self.folder_rules)
                    if rule:
                        destination = Path(root_path) / rule['destination']
                        destination.mkdir(parents=True, exist_ok=True)
                        
                        dest_path = destination / item.name
                        if operations.move_folder(item, dest_path, merge=self.merge_folders):
                            stats['folders_moved'] += 1
                    else:
                        # Recursively process subdirectories
                        self._organize_folders(item, root_path, operations, stats)
        
        except (PermissionError, OSError) as e:
            operations.log(f"ERROR: Could not process folder {current_path}: {str(e)}")
            stats['errors'] += 1
    
    def _organize_files(self, current_path: Path, root_path: Path, 
                       operations: FileOperations, stats: Dict, 
                       recursive: bool = False):
        """
        Organize files according to rules.
        
        Args:
            current_path: Current directory to process
            root_path: Root path for relative calculations
            operations: FileOperations instance
            stats: Statistics dictionary to update
            recursive: If True, search recursively (default: False)
        """
        try:
            items = list(current_path.iterdir())
            
            for item in items:
                if item.name.startswith('.'):
                    continue
                
                if item.is_file():
                    # Check if file matches a rule
                    rule = self.find_matching_rule(item.name, self.file_rules)
                    if rule:
                        # Check if rule should be applied recursively
                        rule_recursive = rule.get('recursive', False)
                        if not recursive or rule_recursive:
                            destination = Path(root_path) / rule['destination']
                            destination.mkdir(parents=True, exist_ok=True)
                            
                            dest_path = destination / item.name
                            if operations.move_file(item, dest_path):
                                stats['files_moved'] += 1
                
                elif item.is_dir() and recursive:
                    # Recursively process subdirectories
                    self._organize_files(item, root_path, operations, stats, recursive=True)
        
        except (PermissionError, OSError) as e:
            operations.log(f"ERROR: Could not process directory {current_path}: {str(e)}")
            stats['errors'] += 1
    
    def preview(self, root_path: Path, **kwargs) -> List[Dict]:
        """
        Preview what changes would be made.
        
        Args:
            root_path: Root directory
            **kwargs: Additional arguments
            
        Returns:
            List of proposed moves
        """
        preview_moves = []
        
        # Preview folder moves
        if self.folder_rules:
            self._preview_folders(root_path, root_path, preview_moves)
        
        # Preview file moves
        if self.file_rules:
            self._preview_files(root_path, root_path, preview_moves, recursive=False)
        
        return preview_moves
    
    def _preview_folders(self, current_path: Path, root_path: Path, preview_moves: List[Dict]):
        """Preview folder moves."""
        try:
            items = list(current_path.iterdir())
            
            for item in items:
                if item.name.startswith('.'):
                    continue
                
                if item.is_dir():
                    rule = self.find_matching_rule(item.name, self.folder_rules)
                    if rule:
                        destination = Path(root_path) / rule['destination']
                        dest_path = destination / item.name
                        preview_moves.append({
                            'source': str(item.relative_to(root_path)),
                            'destination': str(dest_path.relative_to(root_path)),
                            'type': 'folder',
                            'rule': rule.get('pattern'),
                        })
                    else:
                        self._preview_folders(item, root_path, preview_moves)
        
        except (PermissionError, OSError):
            pass
    
    def _preview_files(self, current_path: Path, root_path: Path, preview_moves: List[Dict], recursive: bool = False):
        """Preview file moves."""
        try:
            items = list(current_path.iterdir())
            
            for item in items:
                if item.name.startswith('.'):
                    continue
                
                if item.is_file():
                    rule = self.find_matching_rule(item.name, self.file_rules)
                    if rule:
                        rule_recursive = rule.get('recursive', False)
                        if not recursive or rule_recursive:
                            destination = Path(root_path) / rule['destination']
                            dest_path = destination / item.name
                            preview_moves.append({
                                'source': str(item.relative_to(root_path)),
                                'destination': str(dest_path.relative_to(root_path)),
                                'type': 'file',
                                'rule': rule.get('pattern'),
                            })
                
                elif item.is_dir() and recursive:
                    self._preview_files(item, root_path, preview_moves, recursive=True)
        
        except (PermissionError, OSError):
            pass
    
    def validate_config(self) -> List[str]:
        """Validate configuration."""
        errors = []
        
        file_rules = self.get_config('file_rules')
        if file_rules and not isinstance(file_rules, list):
            errors.append("'file_rules' must be a list")
        elif file_rules:
            for i, rule in enumerate(file_rules):
                if not isinstance(rule, dict):
                    errors.append(f"file_rules[{i}] must be a dictionary")
                    continue
                if 'pattern' not in rule:
                    errors.append(f"file_rules[{i}] missing required 'pattern' key")
                if 'destination' not in rule:
                    errors.append(f"file_rules[{i}] missing required 'destination' key")
                pattern_type = rule.get('type', 'glob')
                if pattern_type not in ('exact', 'glob', 'regex'):
                    errors.append(f"file_rules[{i}] has invalid 'type' (must be 'exact', 'glob', or 'regex')")
        
        folder_rules = self.get_config('folder_rules')
        if folder_rules and not isinstance(folder_rules, list):
            errors.append("'folder_rules' must be a list")
        elif folder_rules:
            for i, rule in enumerate(folder_rules):
                if not isinstance(rule, dict):
                    errors.append(f"folder_rules[{i}] must be a dictionary")
                    continue
                if 'pattern' not in rule:
                    errors.append(f"folder_rules[{i}] missing required 'pattern' key")
                if 'destination' not in rule:
                    errors.append(f"folder_rules[{i}] missing required 'destination' key")
                pattern_type = rule.get('type', 'glob')
                if pattern_type not in ('exact', 'glob', 'regex'):
                    errors.append(f"folder_rules[{i}] has invalid 'type' (must be 'exact', 'glob', or 'regex')")
        
        return errors

    def validate_rules_with_ai(self) -> Dict[str, Any]:
        """
        Use AI to validate and suggest improvements to rules (optional enhancement).
        
        Returns:
            Dict with validation results and suggestions
        """
        try:
            from file_organizer.ai import get_ai_suggestion, AIProvider
            
            payload = {
                "request": "validate_organization_rules",
                "domain": "library_science",
                "context": {
                    "file_rules": self.file_rules,
                    "folder_rules": self.folder_rules,
                },
                "instructions": """
Review these file organization rules and provide:
1. Assessment of rule quality
2. Suggested improvements
3. Missing patterns
4. Potential conflicts

Return your response as structured text.
""",
            }
            
            result = get_ai_suggestion(payload, provider=AIProvider.AUTO, quick=False)
            if isinstance(result, dict) and result.get("ok"):
                return {
                    "success": True,
                    "validation": result.get("text", ""),
                }
            else:
                return {
                    "success": False,
                    "error": "AI validation failed",
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def suggest_rule_for_file(self, file_path: Path) -> Optional[Dict]:
        """
        Use AI to suggest a rule for organizing a specific file (optional enhancement).
        
        Args:
            file_path: File to create rule for
            
        Returns:
            Suggested rule dict or None if AI not available
        """
        try:
            from file_organizer.ai import get_ai_suggestion, AIProvider
            
            payload = {
                "request": "suggest_organization_rule",
                "domain": "library_science",
                "context": {
                    "filename": file_path.name,
                    "extension": file_path.suffix,
                    "path": str(file_path),
                },
                "instructions": """
Suggest an organization rule for this file following library science principles.

Return a JSON object with:
- pattern: Pattern to match this file (glob or regex)
- type: "glob" or "regex"
- destination: Suggested destination folder path
- reasoning: Brief explanation

Return only the JSON object.
""",
            }
            
            result = get_ai_suggestion(payload, provider=AIProvider.AUTO, quick=True)
            if isinstance(result, dict) and result.get("ok"):
                text = result.get("text", "").strip()
                # Try to parse JSON
                try:
                    import json
                    import re
                    json_match = re.search(r'\{.*\}', text, re.DOTALL)
                    if json_match:
                        rule = json.loads(json_match.group())
                        return rule
                except Exception:
                    pass
        except Exception:
            pass
        
        return None

