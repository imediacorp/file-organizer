"""Taxonomy and controlled vocabulary management."""

from pathlib import Path
from typing import Dict, List, Optional, Set, Any
import json

try:
    from file_organizer.ai import get_ai_suggestion, AIProvider
except Exception:
    get_ai_suggestion = None
    AIProvider = None


class TaxonomyManager:
    """Manages taxonomy and controlled vocabulary for file organization."""
    
    def __init__(self, taxonomy_file: Optional[Path] = None):
        """Initialize taxonomy manager.
        
        Args:
            taxonomy_file: Optional path to taxonomy JSON file
        """
        self.taxonomy_file = taxonomy_file
        self.taxonomy: Dict[str, Any] = {}
        self.load_taxonomy()
    
    def load_taxonomy(self) -> None:
        """Load taxonomy from file."""
        if self.taxonomy_file and self.taxonomy_file.exists():
            try:
                with open(self.taxonomy_file, 'r', encoding='utf-8') as f:
                    self.taxonomy = json.load(f)
            except Exception:
                self.taxonomy = self._get_default_taxonomy()
        else:
            self.taxonomy = self._get_default_taxonomy()
    
    def save_taxonomy(self) -> None:
        """Save taxonomy to file."""
        if self.taxonomy_file:
            self.taxonomy_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.taxonomy_file, 'w', encoding='utf-8') as f:
                json.dump(self.taxonomy, f, indent=2)
    
    def _get_default_taxonomy(self) -> Dict[str, Any]:
        """Get default taxonomy structure."""
        return {
            "categories": {
                "Financial": {
                    "subcategories": ["Taxes", "Invoices", "Receipts", "Bank Statements", "Investments"],
                    "keywords": ["invoice", "receipt", "tax", "financial", "payment", "bill"],
                },
                "Legal": {
                    "subcategories": ["Contracts", "Compliance", "Legal Correspondence"],
                    "keywords": ["contract", "agreement", "legal", "compliance", "law"],
                },
                "Business": {
                    "subcategories": ["Reports", "Presentations", "Business Plans", "Marketing"],
                    "keywords": ["report", "presentation", "business", "marketing", "plan"],
                },
                "Personal": {
                    "subcategories": ["Correspondence", "Personal Records", "Photos"],
                    "keywords": ["personal", "correspondence", "photo", "personal record"],
                },
                "Medical": {
                    "subcategories": ["Health Records", "Insurance", "Medical Bills"],
                    "keywords": ["medical", "health", "insurance", "doctor", "hospital"],
                },
                "Educational": {
                    "subcategories": ["Certificates", "Transcripts", "Course Materials"],
                    "keywords": ["certificate", "transcript", "education", "course", "degree"],
                },
            },
            "document_types": [
                "Invoice", "Receipt", "Contract", "Report", "Presentation",
                "Certificate", "Statement", "Correspondence", "Photo", "Video",
            ],
        }
    
    def classify_file(self, filename: str, content_hint: Optional[str] = None) -> Optional[str]:
        """Classify a file using taxonomy.
        
        Args:
            filename: File name
            content_hint: Optional hint about file content
            
        Returns:
            Category name or None
        """
        text_to_search = f"{filename} {content_hint or ''}".lower()
        
        categories = self.taxonomy.get("categories", {})
        best_match = None
        best_score = 0
        
        for category, data in categories.items():
            keywords = data.get("keywords", [])
            score = sum(1 for keyword in keywords if keyword.lower() in text_to_search)
            if score > best_score:
                best_score = score
                best_match = category
        
        return best_match
    
    def validate_taxonomy(self, path: Path, provider: str = "auto") -> Dict[str, Any]:
        """Validate existing taxonomy against AI recommendations.
        
        Args:
            path: Directory to validate
            provider: AI provider to use
            
        Returns:
            Dict with validation results
        """
        if get_ai_suggestion is None:
            return {
                "success": False,
                "error": "AI client not available",
            }
        
        # Collect folder structure
        folders = []
        for item in path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                folders.append(item.name)
        
        # Create AI payload
        payload = {
            "request": "validate_taxonomy",
            "domain": "library_science",
            "context": {
                "current_structure": folders,
                "taxonomy": self.taxonomy,
            },
            "instructions": """
Validate this taxonomy and folder structure against library science best practices.

Provide:
1. Assessment of current taxonomy
2. Suggested improvements
3. Missing categories
4. Inconsistencies
5. Recommendations

Return your response as structured text.
""",
        }
        
        try:
            result = get_ai_suggestion(
                payload,
                provider=provider if isinstance(provider, str) else AIProvider.AUTO,
                use_cache=True,
            )
            
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
    
    def get_category_suggestions(self, filename: str) -> List[str]:
        """Get suggested categories for a filename.
        
        Args:
            filename: File name
            
        Returns:
            List of suggested category names
        """
        suggestions = []
        text = filename.lower()
        
        categories = self.taxonomy.get("categories", {})
        for category, data in categories.items():
            keywords = data.get("keywords", [])
            if any(keyword.lower() in text for keyword in keywords):
                suggestions.append(category)
        
        return suggestions

