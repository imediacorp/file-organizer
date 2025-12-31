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
        self.batch_size = self.get_config("batch_size", 5)  # Reduced default for better performance
        self.use_cache = self.get_config("use_cache", True)
        self.max_files = self.get_config("max_files", 50)  # Limit total files analyzed
    
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
            # Resolve target_folder relative to root_path
            if isinstance(target_folder, (str, Path)):
                analyze_path = root_path / target_folder
            else:
                analyze_path = root_path / target_folder
            analyze_path = analyze_path.resolve()
            # Ensure it's actually a subpath
            try:
                analyze_path.relative_to(root_path)
            except ValueError:
                raise ValueError(f"'{target_folder}' is not in the subpath of '{root_path}'")
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
        
        print(f"\n📋 Filtering suggestions by confidence threshold ({self.confidence_threshold})...")
        print(f"   Total suggestions: {len(suggestions)}")
        print(f"   Approved (≥{self.confidence_threshold}): {len(filtered_suggestions)}")
        print(f"   Filtered out: {len(suggestions) - len(filtered_suggestions)}")
        
        if not filtered_suggestions:
            print("\n⚠️  No suggestions meet the confidence threshold.")
            print(f"   Try lowering confidence_threshold in config (current: {self.confidence_threshold})")
            return {
                "success": False,
                "error": f"No suggestions meet confidence threshold of {self.confidence_threshold}",
                "statistics": {
                    "total_operations": 0,
                    "file_moves": 0,
                    "errors": 0,
                },
                "suggestions": len(suggestions),
                "filtered": 0,
            }
        
        print(f"\n🚀 Executing {len(filtered_suggestions)} approved moves...")
        
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
            # Resolve target_folder relative to root_path
            if isinstance(target_folder, (str, Path)):
                analyze_path = root_path / target_folder
            else:
                analyze_path = root_path / target_folder
            analyze_path = analyze_path.resolve()
            # Ensure it's actually a subpath
            try:
                analyze_path.relative_to(root_path)
            except ValueError:
                raise ValueError(f"'{target_folder}' is not in the subpath of '{root_path}'")
        else:
            analyze_path = root_path
        
        print(f"\n🔍 Eratosthenes preview mode - analyzing: {analyze_path}")
        suggestions = self._get_ai_suggestions(analyze_path)
        
        # Filter by confidence threshold for preview
        filtered_suggestions = [
            s for s in suggestions
            if s.get("confidence_score", 0) >= self.confidence_threshold
        ]
        
        print(f"\n📊 Preview Summary:")
        print(f"   Total suggestions: {len(suggestions)}")
        print(f"   Will execute (≥{self.confidence_threshold}): {len(filtered_suggestions)}")
        print(f"   Will skip (<{self.confidence_threshold}): {len(suggestions) - len(filtered_suggestions)}")
        
        # Convert to preview format
        preview_moves = []
        for suggestion in filtered_suggestions:
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
        
        # Collect files to analyze (limit to max_files for performance)
        files_to_analyze = []
        for item in path.rglob("*"):
            if item.is_file() and not item.name.startswith("."):
                files_to_analyze.append(item)
                if len(files_to_analyze) >= self.max_files:
                    break
        
        if not files_to_analyze:
            return []
        
        total_files = len(files_to_analyze)
        print(f"\n📊 Eratosthenes analyzing {total_files} files (limited to {self.max_files} for performance)...")
        print(f"   Using batch size: {self.batch_size}")
        print(f"   Confidence threshold: {self.confidence_threshold}")
        print(f"   This may take a few minutes. Please be patient...")
        
        # Analyze in batches
        all_suggestions = []
        num_batches = (total_files + self.batch_size - 1) // self.batch_size
        
        for i in range(0, len(files_to_analyze), self.batch_size):
            batch_num = (i // self.batch_size) + 1
            batch = files_to_analyze[i:i + self.batch_size]
            print(f"   Processing batch {batch_num}/{num_batches} ({len(batch)} files)...", end="", flush=True)
            batch_suggestions = self._analyze_batch(batch, path)
            all_suggestions.extend(batch_suggestions)
            print(f" ✓ ({len(batch_suggestions)} suggestions)")
        
        print(f"\n✅ Analysis complete: {len(all_suggestions)} suggestions generated")
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
Analyze these files and suggest organization. Return a JSON array with one object per file.

Each object must have:
- source: file path (string)
- destination: suggested path relative to root_path (string)  
- classification: category like "Financial/Invoice" (string)
- confidence_score: number 0.0-1.0
- reasoning: brief explanation (string)

Return ONLY valid JSON array, no markdown or extra text.
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
                if not suggestions:
                    # If JSON parsing failed, try text format parsing
                    suggestions = self._parse_text_response(text, files, root_path)
                return suggestions
            else:
                return []
                
        except Exception as e:
            # If exception occurs, try text parsing if we have text
            if isinstance(result, dict) and result.get("ok"):
                text = result.get("text", "")
                return self._parse_text_response(text, files, root_path)
            return []
    
    def _parse_ai_response(self, text: str, files: List[Path], root_path: Path) -> List[Dict[str, Any]]:
        """Parse AI response and extract suggestions."""
        suggestions = []
        
        # Try to extract JSON from response
        try:
            import re
            
            # First, try to extract JSON from markdown code blocks
            json_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_block_match:
                text = json_block_match.group(1)
            
            # Try to find JSON array directly
            json_match = re.search(r'\[.*?\]', text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                if isinstance(parsed, list):
                    parsed_list = parsed
                else:
                    parsed_list = []
            else:
                # Try to find nested structure like {"suggested_orgs": [...]}
                nested_match = re.search(r'\{\s*"[^"]*":\s*(\[.*?\])\s*\}', text, re.DOTALL)
                if nested_match:
                    parsed_list = json.loads(nested_match.group(1))
                else:
                    # Try parsing the whole text as JSON
                    try:
                        parsed_obj = json.loads(text)
                        if isinstance(parsed_obj, dict):
                            # Look for array values
                            for key, value in parsed_obj.items():
                                if isinstance(value, list):
                                    parsed_list = value
                                    break
                            else:
                                parsed_list = []
                        elif isinstance(parsed_obj, list):
                            parsed_list = parsed_obj
                        else:
                            parsed_list = []
                    except Exception:
                        parsed_list = []
            
            # Process parsed suggestions
            if isinstance(parsed_list, list) and parsed_list:
                for i, item in enumerate(parsed_list):
                    if i < len(files):
                        file_path = files[i]
                        relative_source = file_path.relative_to(root_path)
                        
                        # Handle classification as list or string
                        classification = item.get("classification", "Unknown")
                        if isinstance(classification, list):
                            classification = "/".join(classification)
                        
                        suggestion = {
                            "source": str(file_path),
                            "destination": str(root_path / item.get("destination", relative_source)),
                            "classification": classification,
                            "confidence_score": float(item.get("confidence_score", 0.5)),
                            "reasoning": item.get("reasoning", ""),
                            "metadata": item.get("metadata", {}),
                        }
                        
                        if "suggested_filename" in item:
                            dest_path = Path(suggestion["destination"])
                            suggestion["destination"] = str(dest_path.parent / item["suggested_filename"])
                        
                        suggestions.append(suggestion)
        except Exception as e:
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
                    "reasoning": "Basic organization by file type (fallback)",
                    "metadata": {},
                })
        
        return suggestions
    
    def _parse_text_response(self, text: str, files: List[Path], root_path: Path) -> List[Dict[str, Any]]:
        """Parse text-format AI response when JSON parsing fails."""
        suggestions = []
        
        try:
            import re
            
            # Look for patterns like "Source: path" and "Destination: path"
            # Handle various formats the AI might use
            
            # Pattern 1: Numbered list with Source/Destination
            # "1. **Source:** path\n**Destination:** path"
            pattern1 = r'(?:\d+\.\s*)?(?:Source|source)[:\s]+\*?\*?([^\n*]+)\*?\*?.*?(?:Destination|destination)[:\s]+\*?\*?([^\n*]+)\*?\*?'
            matches = list(re.finditer(pattern1, text, re.DOTALL | re.IGNORECASE))
            
            # Pattern 2: Simple "Source: path" "Destination: path" on separate lines
            if not matches:
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if 'source' in line.lower() and i + 1 < len(lines):
                        source_line = line
                        dest_line = lines[i + 1] if i + 1 < len(lines) else ""
                        if 'destination' in dest_line.lower():
                            source_match = re.search(r'[:\s]+([^\n*]+)', source_line, re.IGNORECASE)
                            dest_match = re.search(r'[:\s]+([^\n*]+)', dest_line, re.IGNORECASE)
                            if source_match and dest_match:
                                matches.append(type('Match', (), {
                                    'group': lambda self, n: source_match.group(1) if n == 1 else dest_match.group(1) if n == 2 else "",
                                    'groups': lambda self: (source_match.group(1), dest_match.group(1))
                                })())
            
            # Process matches
            for i, match in enumerate(matches):
                if i < len(files):
                    file_path = files[i]
                    source_text = match.group(1).strip() if hasattr(match, 'group') and len(match.groups()) >= 1 else ""
                    dest_text = match.group(2).strip() if hasattr(match, 'group') and len(match.groups()) >= 2 else ""
                    
                    # Extract confidence from text if available
                    confidence_score = 0.6  # Default
                    confidence_match = re.search(r'confidence[:\s]+([^\n]+)', text[i*200:(i+1)*200] if i*200 < len(text) else "", re.IGNORECASE)
                    if confidence_match:
                        conf_text = confidence_match.group(1).lower()
                        if 'high' in conf_text or '0.8' in conf_text or '0.9' in conf_text:
                            confidence_score = 0.8
                        elif 'low' in conf_text or '0.3' in conf_text or '0.4' in conf_text:
                            confidence_score = 0.4
                        else:
                            num_match = re.search(r'0?\.\d+', conf_text)
                            if num_match:
                                confidence_score = float(num_match.group())
                    
                    # Build destination path
                    if not dest_text:
                        dest_text = str(file_path.relative_to(root_path))
                    
                    if dest_text.startswith(str(root_path)):
                        destination = dest_text
                    elif dest_text.startswith('/'):
                        destination = str(root_path / dest_text.lstrip('/'))
                    else:
                        destination = str(root_path / dest_text)
                    
                    suggestions.append({
                        "source": str(file_path),
                        "destination": destination,
                        "classification": "Unknown",
                        "confidence_score": confidence_score,
                        "reasoning": "AI-suggested organization (parsed from text)",
                        "metadata": {},
                    })
        except Exception:
            pass
        
        # If we still have no suggestions, create basic ones
        if not suggestions:
            for file_path in files:
                relative_path = file_path.relative_to(root_path)
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
                    "reasoning": "Basic organization by file type (fallback)",
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

