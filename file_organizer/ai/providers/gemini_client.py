"""Google Gemini AI provider client."""

import json
import os
import time
from typing import Any, Dict, Optional

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class GeminiClientError(RuntimeError):
    """Gemini client error."""
    pass


def _is_gemini_available() -> bool:
    """Check if Gemini is configured."""
    if not HTTPX_AVAILABLE:
        return False
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return False
    low = str(api_key).strip().lower()
    if low in {"replace_me", "<replace_me>", "", "todo"} or "replace" in low:
        return False
    if low.startswith("re") and low.endswith("me") and "*" in low:
        return False
    return True


def get_gemini_suggestion(
    payload: Dict[str, Any],
    *,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    timeout: Optional[int] = None,
    quick: bool = False,
    return_text: Optional[bool] = None,
) -> Dict[str, Any] | str:
    """Request an AI suggestion from Google Gemini.
    
    Args:
        payload: Dict containing request context
        api_key: API key (defaults to GEMINI_API_KEY env var)
        model: Model name (defaults to gemini-1.5-flash)
        timeout: Request timeout in seconds
        quick: Use quick timeout mode
        return_text: Return plain text instead of dict
        
    Returns:
        Dict with {"ok": bool, "text": str, "raw": Any, "error": Optional[str]}
        Or string if return_text=True
    """
    if not HTTPX_AVAILABLE:
        error_msg = "httpx not available. Install with: pip install httpx"
        if return_text is True or (return_text is None and quick):
            return f"AI error: {error_msg}"
        return {"ok": False, "text": "", "raw": None, "error": error_msg}
    
    api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        error_msg = "Missing GEMINI_API_KEY"
        if return_text is True or (return_text is None and quick):
            return f"AI error: {error_msg}"
        return {"ok": False, "text": "", "raw": None, "error": error_msg}
    
    model = model or os.environ.get("GEMINI_MODEL") or "gemini-1.5-flash"
    
    if timeout is None:
        timeout = 15 if quick else 30
    
    # Build prompt from payload
    prompt_parts = []
    
    system_prompt = payload.get("system_prompt", "")
    if system_prompt:
        prompt_parts.append(f"System: {system_prompt}\n")
    
    request_text = payload.get("request", "")
    instructions = payload.get("instructions", "")
    context = payload.get("context", {})
    
    if request_text:
        prompt_parts.append(f"Request: {request_text}")
    if instructions:
        prompt_parts.append(f"\nInstructions:\n{instructions}")
    if context:
        prompt_parts.append(f"\nContext:\n{json.dumps(context, indent=2, default=str)}")
    
    prompt = "\n".join(prompt_parts) if prompt_parts else json.dumps(payload, indent=2, default=str)
    
    # Gemini API endpoint
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    
    request_data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    if "temperature" in payload:
        request_data["generationConfig"] = {"temperature": payload["temperature"]}
    
    try:
        params = {"key": api_key}
        
        start_time = time.time()
        with httpx.Client(timeout=timeout) as client:
            response = client.post(api_url, json=request_data, params=params)
            response.raise_for_status()
            response_data = response.json()
        
        # Extract text from response
        text = ""
        if "candidates" in response_data and len(response_data["candidates"]) > 0:
            candidate = response_data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                parts = candidate["content"]["parts"]
                if parts and "text" in parts[0]:
                    text = parts[0]["text"]
        
        result = {
            "ok": True,
            "text": text,
            "raw": response_data,
            "error": None,
        }
        
        if return_text is True or (return_text is None and quick):
            return text
        
        return result
        
    except httpx.HTTPError as e:
        error_msg = f"HTTP error: {e}"
        if return_text is True or (return_text is None and quick):
            return f"AI error: {error_msg}"
        return {"ok": False, "text": "", "raw": None, "error": error_msg}
    except Exception as e:
        error_msg = f"Gemini error: {e}"
        if return_text is True or (return_text is None and quick):
            return f"AI error: {error_msg}"
        return {"ok": False, "text": "", "raw": None, "error": error_msg}

