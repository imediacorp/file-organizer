"""AI-powered organization strategy using Library Science Expert."""

from pathlib import Path
from typing import Dict, List, Optional, Any
import json

from file_organizer.core.strategy import Strategy
from file_organizer.core.operations import FileOperations

try:
    from file_organizer.ai import get_ai_suggestion, AIProvider
except Exception:
    get_ai_suggestion = None
    AIProvider = None


class AISuggestedStrategy(Strategy):
    """
    AI-powered organization strategy that uses Eratosthenes (Library Science Expert)
    to analyze files and suggest optimal organization structure.
    
    Named after the ancient Greek librarian and geographer who organized knowledge
    at the Library of Alexandria, this strategy applies systematic organization
    principles to file management.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize AI suggested strategy."""
        super().__init__(config)
        self.provider = self.get_config("provider", "auto")
        self.confidence_threshold = self.get_config("confidence_threshold", 0.6)
        self.batch_size = self.get_config("batch_size", 10)
        self.use_cache = self.get_config("use_cache", True)
    
    def organize(self, root_path: Path, operations: FileOperations, **kwargs) -> Dict:
        """
        Organize files using AI suggestions.
        
        Args:
            root_path: Root directory to organize
            operations: FileOperations instance
            **kwargs: Additional arguments
            
        Returns:
            Dictionary with organization results
        """
        if get_ai_suggestion is None:
            return {
                "success": False,
                "error": "AI client not available. Install dependencies and configure API keys.",
                "statistics": {"total_operations": 0, "file_moves": 0, "errors": 1},
            }
        
        target_folder = kwargs.get("target_folder")
        if target_folder:
            analyze_path = root_path / target_folder
        else:
            analyze_path = root_path
        
        # Get AI suggestions
        suggestions = self._get_ai_suggestions(analyze_path)
        
        if not suggestions:
            return {
                "success": False,
                "error": "No organization suggestions generated",
                "statistics": {"total_operations": 0, "file_moves": 0, "errors": 1},
            }
        
        # Filter by confidence threshold
        filtered_suggestions = [
            s for s in suggestions
            if s.get("confidence_score", 0) >= self.confidence_threshold
        ]
        
        # Execute moves
        executed = 0
        errors = 0
        
        for suggestion in filtered_suggestions:
            source = Path(suggestion["source"])
            destination = Path(suggestion["destination"])
            
            # Ensure destination parent exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                if source.is_file():
                    operations.move_file(source, destination)
                    executed += 1
                elif source.is_dir():
                    operations.move_folder(source, destination)
                    executed += 1
            except Exception as e:
                errors += 1
                operations.log_error(f"Failed to move {source}: {e}")
        
        return {
            "success": True,
            "statistics": {
                "total_operations": len(filtered_suggestions),
                "file_moves": executed,
                "errors": errors,
            },
            "suggestions": len(suggestions),
            "filtered": len(filtered_suggestions),
        }
    
    def preview(self, root_path: Path, **kwargs) -> List[Dict]:
        """
        Preview AI-suggested organization without executing.
        
        Args:
            root_path: Root directory to analyze
            **kwargs: Additional arguments
            
        Returns:
            List of proposed moves
        """
        if get_ai_suggestion is None:
            return []
        
        target_folder = kwargs.get("target_folder")
        if target_folder:
            analyze_path = root_path / target_folder
        else:
            analyze_path = root_path
        
        suggestions = self._get_ai_suggestions(analyze_path)
        
        # Convert to preview format
        preview_moves = []
        for suggestion in suggestions:
            preview_moves.append({
                "source": suggestion["source"],
                "destination": suggestion["destination"],
                "confidence": suggestion.get("confidence_score", 0),
                "reasoning": suggestion.get("reasoning", ""),
            })
        
        return preview_moves
    
    def _get_ai_suggestions(self, path: Path) -> List[Dict[str, Any]]:
        """Get AI suggestions for files in path."""
        if get_ai_suggestion is None:
            return []
        
        # Collect files to analyze
        files_to_analyze = []
        for item in path.rglob("*"):
            if item.is_file() and not item.name.startswith("."):
                files_to_analyze.append(item)
        
        if not files_to_analyze:
            return []
        
        # Analyze in batches
        all_suggestions = []
        
        for i in range(0, len(files_to_analyze), self.batch_size):
            batch = files_to_analyze[i:i + self.batch_size]
            batch_suggestions = self._analyze_batch(batch, path)
            all_suggestions.extend(batch_suggestions)
        
        return all_suggestions
    
    def _analyze_batch(self, files: List[Path], root_path: Path) -> List[Dict[str, Any]]:
        """Analyze a batch of files."""
        if get_ai_suggestion is None:
            return []
        
        # Build context for AI
        file_contexts = []
        for file_path in files:
            relative_path = file_path.relative_to(root_path)
            file_contexts.append({
                "path": str(relative_path),
                "name": file_path.name,
                "extension": file_path.suffix,
                "size": file_path.stat().st_size,
            })
        
        # Create AI payload
        payload = {
            "request": "suggest_file_organization",
            "domain": "library_science",
            "context": {
                "files": file_contexts,
                "root_path": str(root_path),
            },
            "instructions": """
Analyze these files and suggest optimal organization structure following library science principles.

For each file, provide:
1. Classification (document type and category)
2. Suggested destination path (relative to root)
3. Confidence score (0.0 to 1.0)
4. Reasoning (brief explanation)
5. Suggested filename if current name is not optimal
6. Extracted metadata (title, date, author, subject, type, keywords)

Return your response as a JSON array of suggestions, each with:
- source: original file path
- destination: suggested destination path
- classification: document type/category
- confidence_score: float between 0.0 and 1.0
- reasoning: explanation
- suggested_filename: optional better filename
- metadata: dict with extracted metadata fields
""",
        }
        
        try:
            # Get AI suggestion
            result = get_ai_suggestion(
                payload,
                provider=self.provider if isinstance(self.provider, str) else AIProvider.AUTO,
                use_cache=self.use_cache,
                quick=False,
            )
            
            if isinstance(result, dict) and result.get("ok"):
                text = result.get("text", "")
                
                # Try to parse JSON from response
                suggestions = self._parse_ai_response(text, files, root_path)
                return suggestions
            else:
                return []
                
        except Exception as e:
            return []
    
    def _parse_ai_response(self, text: str, files: List[Path], root_path: Path) -> List[Dict[str, Any]]:
        """Parse AI response and extract suggestions."""
        suggestions = []
        
        # Try to extract JSON from response
        try:
            # Look for JSON array in the response
            import re
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                if isinstance(parsed, list):
                    for i, item in enumerate(parsed):
                        if i < len(files):
                            file_path = files[i]
                            relative_source = file_path.relative_to(root_path)
                            
                            suggestion = {
                                "source": str(file_path),
                                "destination": str(root_path / item.get("destination", relative_source)),
                                "classification": item.get("classification", "Unknown"),
                                "confidence_score": float(item.get("confidence_score", 0.5)),
                                "reasoning": item.get("reasoning", ""),
                                "metadata": item.get("metadata", {}),
                            }
                            
                            if "suggested_filename" in item:
                                dest_path = Path(suggestion["destination"])
                                suggestion["destination"] = str(dest_path.parent / item["suggested_filename"])
                            
                            suggestions.append(suggestion)
        except Exception:
            # Fallback: create basic suggestions from file paths
            for file_path in files:
                relative_path = file_path.relative_to(root_path)
                # Basic organization by extension
                ext = file_path.suffix.lower()
                if ext in [".pdf", ".doc", ".docx"]:
                    category = "Documents"
                elif ext in [".jpg", ".jpeg", ".png", ".gif"]:
                    category = "Images"
                else:
                    category = "Other"
                
                suggestions.append({
                    "source": str(file_path),
                    "destination": str(root_path / category / relative_path.name),
                    "classification": category,
                    "confidence_score": 0.3,
                    "reasoning": "Basic organization by file type",
                    "metadata": {},
                })
        
        return suggestions
    
    def validate_config(self) -> List[str]:
        """Validate strategy configuration."""
        errors = []
        
        if self.confidence_threshold < 0 or self.confidence_threshold > 1:
            errors.append("confidence_threshold must be between 0 and 1")
        
        if self.batch_size < 1:
            errors.append("batch_size must be at least 1")
        
        return errors

