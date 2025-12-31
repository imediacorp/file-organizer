"""Standalone AI advisory tools for file organization.

Eratosthenes: Knowledge/Content Management agent providing intelligent
file organization assistance through AI-powered analysis.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import json

try:
    from file_organizer.ai import get_ai_suggestion, AIProvider
except Exception:
    get_ai_suggestion = None
    AIProvider = None


def suggest_organization_structure(
    path: Path,
    provider: str = "auto",
    max_files: int = 50,
    timeout: Optional[int] = None,
) -> Dict[str, Any]:
    """Analyze directory structure and suggest organization improvements.
    
    Args:
        path: Directory to analyze
        provider: AI provider to use
        max_files: Maximum number of files to analyze
        
    Returns:
        Dict with organization suggestions
    """
    if get_ai_suggestion is None:
        return {
            "success": False,
            "error": "AI client not available",
            "suggestions": [],
        }
    
    if not path.exists() or not path.is_dir():
        return {
            "success": False,
            "error": f"Path does not exist or is not a directory: {path}",
            "suggestions": [],
        }
    
    # Collect file information
    files = []
    for item in path.rglob("*"):
        if item.is_file() and not item.name.startswith("."):
            if len(files) >= max_files:
                break
            relative_path = item.relative_to(path)
            files.append({
                "path": str(relative_path),
                "name": item.name,
                "extension": item.suffix,
                "size": item.stat().st_size,
            })
    
    if not files:
        return {
            "success": True,
            "suggestions": [],
            "message": "No files found to analyze",
        }
    
    # Get current structure
    folders = []
    for item in path.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            folders.append(item.name)
    
    # Create AI payload
    payload = {
        "request": "analyze_organization_structure",
        "domain": "library_science",
        "context": {
            "root_path": str(path),
            "current_structure": folders,
            "files": files[:max_files],
        },
        "instructions": """
Analyze this directory structure and suggest improvements following library science principles.

Provide:
1. Overall assessment of current organization
2. Suggested top-level folder structure
3. Recommendations for reorganizing files
4. Naming convention suggestions
5. Metadata extraction priorities

Return your response as structured text with clear sections.
""",
    }
    
    try:
        result = get_ai_suggestion(
            payload,
            provider=provider if isinstance(provider, str) else AIProvider.AUTO,
            use_cache=True,
            timeout=timeout if timeout is not None else 45,  # Longer timeout for classification
        )
        
        if isinstance(result, dict) and result.get("ok"):
            return {
                "success": True,
                "suggestions": result.get("text", ""),
                "files_analyzed": len(files),
            }
        else:
            # Get more detailed error information
            error_msg = "AI analysis failed"
            if isinstance(result, dict):
                error_detail = result.get("error")
                if error_detail:
                    error_msg = f"AI analysis failed: {error_detail}"
            elif isinstance(result, str) and result.startswith("AI error:"):
                error_msg = result
            return {
                "success": False,
                "error": error_msg,
                "suggestions": [],
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Exception: {str(e)}",
            "suggestions": [],
        }


def classify_document(
    file_path: Path,
    provider: str = "auto",
    timeout: Optional[int] = None,
) -> Dict[str, Any]:
    """Classify a single document using AI.
    
    Args:
        file_path: File to classify
        provider: AI provider to use
        
    Returns:
        Dict with classification results
    """
    if get_ai_suggestion is None:
        return {
            "success": False,
            "error": "AI client not available",
        }
    
    if not file_path.exists() or not file_path.is_file():
        return {
            "success": False,
            "error": f"File does not exist: {file_path}",
        }
    
    # Create AI payload
    payload = {
        "request": "classify_document",
        "domain": "library_science",
        "context": {
            "filename": file_path.name,
            "extension": file_path.suffix,
            "size": file_path.stat().st_size,
            "path": str(file_path),
        },
        "instructions": """
Classify this document following library science principles.

Provide:
1. Document type (e.g., Invoice, Contract, Report, etc.)
2. Category (e.g., Financial, Legal, Business, Personal, etc.)
3. Suggested folder location
4. Confidence score (0.0 to 1.0)
5. Extracted metadata (title, date, author, subject, keywords)

Return your response as JSON with these fields.
""",
    }
    
    try:
        result = get_ai_suggestion(
            payload,
            provider=provider if isinstance(provider, str) else AIProvider.AUTO,
            use_cache=True,
            timeout=timeout if timeout is not None else 45,  # Longer timeout for classification
        )
        
        if isinstance(result, dict) and result.get("ok"):
            text = result.get("text", "")
            # Try to parse JSON
            try:
                import re
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    classification = json.loads(json_match.group())
                    return {
                        "success": True,
                        "classification": classification,
                        "raw_response": text,
                    }
            except Exception:
                pass
            
            return {
                "success": True,
                "classification": {"raw_response": text},
            }
        else:
            error_msg = "AI classification failed"
            if isinstance(result, dict) and result.get("error"):
                error_msg = f"AI classification failed: {result.get('error')}"
            return {
                "success": False,
                "error": error_msg,
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def extract_metadata(
    file_path: Path,
    provider: str = "auto",
    timeout: Optional[int] = None,
) -> Dict[str, Any]:
    """Extract metadata from a file using AI.
    
    Args:
        file_path: File to extract metadata from
        provider: AI provider to use
        
    Returns:
        Dict with extracted metadata
    """
    if get_ai_suggestion is None:
        return {
            "success": False,
            "error": "AI client not available",
        }
    
    if not file_path.exists() or not file_path.is_file():
        return {
            "success": False,
            "error": f"File does not exist: {file_path}",
        }
    
    # Create AI payload
    payload = {
        "request": "extract_metadata",
        "domain": "library_science",
        "context": {
            "filename": file_path.name,
            "extension": file_path.suffix,
            "size": file_path.stat().st_size,
            "path": str(file_path),
        },
        "instructions": """
Extract metadata from this file following library science principles.

Extract:
1. Title: Document title or subject
2. Date: Creation, modification, or document date
3. Author/Creator: Person or organization
4. Subject/Topic: Primary subject matter
5. Type: Document type
6. Keywords: Relevant search terms

Return your response as JSON with these fields.
""",
    }
    
    try:
        result = get_ai_suggestion(
            payload,
            provider=provider if isinstance(provider, str) else AIProvider.AUTO,
            use_cache=True,
            timeout=timeout if timeout is not None else 45,  # Longer timeout for classification
        )
        
        if isinstance(result, dict) and result.get("ok"):
            text = result.get("text", "")
            # Try to parse JSON
            try:
                import re
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    metadata = json.loads(json_match.group())
                    return {
                        "success": True,
                        "metadata": metadata,
                        "raw_response": text,
                    }
            except Exception:
                pass
            
            return {
                "success": True,
                "metadata": {"raw_response": text},
            }
        else:
            error_msg = "AI metadata extraction failed"
            if isinstance(result, dict) and result.get("error"):
                error_msg = f"AI metadata extraction failed: {result.get('error')}"
            return {
                "success": False,
                "error": error_msg,
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def suggest_filename(
    file_path: Path,
    content_hint: Optional[str] = None,
    provider: str = "auto",
    timeout: Optional[int] = None,
) -> Dict[str, Any]:
    """Suggest a better filename for a file.
    
    Args:
        file_path: Current file path
        content_hint: Optional hint about file content
        provider: AI provider to use
        
    Returns:
        Dict with filename suggestion
    """
    if get_ai_suggestion is None:
        return {
            "success": False,
            "error": "AI client not available",
        }
    
    # Create AI payload
    payload = {
        "request": "suggest_filename",
        "domain": "library_science",
        "context": {
            "current_filename": file_path.name,
            "extension": file_path.suffix,
            "content_hint": content_hint or "No content hint provided",
        },
        "instructions": """
Suggest a better filename following library science naming conventions.

Consider:
1. Descriptive name that identifies the file
2. Consistent date format (YYYY-MM-DD recommended)
3. Avoid special characters except hyphens/underscores
4. Make it sortable and searchable

Return your response as JSON with:
- suggested_filename: The suggested filename (without path)
- reasoning: Explanation of why this name is better
""",
    }
    
    try:
        result = get_ai_suggestion(
            payload,
            provider=provider if isinstance(provider, str) else AIProvider.AUTO,
            use_cache=True,
            timeout=timeout if timeout is not None else 30,  # Timeout for filename suggestions
        )
        
        if isinstance(result, dict) and result.get("ok"):
            text = result.get("text", "")
            # Try to parse JSON
            try:
                import re
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    suggestion = json.loads(json_match.group())
                    return {
                        "success": True,
                        "suggestion": suggestion,
                        "raw_response": text,
                    }
            except Exception:
                pass
            
            return {
                "success": True,
                "suggestion": {"raw_response": text},
            }
        else:
            error_msg = "AI filename suggestion failed"
            if isinstance(result, dict) and result.get("error"):
                error_msg = f"AI filename suggestion failed: {result.get('error')}"
            return {
                "success": False,
                "error": error_msg,
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }

