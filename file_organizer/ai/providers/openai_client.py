"""OpenAI-compatible AI provider client."""

import json
import os
import time
from typing import Any, Dict, Optional

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class OpenAIClientError(RuntimeError):
    """OpenAI client error."""
    pass


def _is_openai_available() -> bool:
    """Check if OpenAI is configured."""
    if not HTTPX_AVAILABLE:
        return False
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return False
    low = str(api_key).strip().lower()
    if low in {"replace_me", "<replace_me>", "", "todo"} or "replace" in low:
        return False
    if low.startswith("re") and low.endswith("me") and "*" in low:
        return False
    return True


def get_openai_suggestion(
    payload: Dict[str, Any],
    *,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    endpoint: Optional[str] = None,
    timeout: Optional[int] = None,
    quick: bool = False,
    return_text: Optional[bool] = None,
) -> Dict[str, Any] | str:
    """Request an AI suggestion from OpenAI-compatible API.
    
    Args:
        payload: Dict containing request context
        api_key: API key (defaults to OPENAI_API_KEY env var)
        model: Model name (defaults to gpt-4o-mini)
        endpoint: API endpoint (defaults to https://api.openai.com/v1)
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
    
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        error_msg = "Missing OPENAI_API_KEY"
        if return_text is True or (return_text is None and quick):
            return f"AI error: {error_msg}"
        return {"ok": False, "text": "", "raw": None, "error": error_msg}
    
    endpoint = endpoint or os.environ.get("OPENAI_API_BASE") or "https://api.openai.com/v1"
    endpoint = endpoint.rstrip("/")
    if not endpoint.endswith("/chat/completions"):
        endpoint = endpoint + "/chat/completions"
    
    model = model or os.environ.get("OPENAI_MODEL") or "gpt-4o-mini"
    
    if timeout is None:
        timeout = 15 if quick else 30
    
    # Build messages from payload
    messages = []
    
    system_prompt = payload.get("system_prompt", "")
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    user_content_parts = []
    request_text = payload.get("request", "")
    instructions = payload.get("instructions", "")
    context = payload.get("context", {})
    
    if request_text:
        user_content_parts.append(f"Request: {request_text}")
    if instructions:
        user_content_parts.append(f"\nInstructions:\n{instructions}")
    if context:
        user_content_parts.append(f"\nContext:\n{json.dumps(context, indent=2, default=str)}")
    
    if user_content_parts:
        messages.append({"role": "user", "content": "\n".join(user_content_parts)})
    else:
        messages.append({"role": "user", "content": json.dumps(payload, indent=2, default=str)})
    
    request_data = {
        "model": model,
        "messages": messages,
    }
    
    if "temperature" in payload:
        request_data["temperature"] = payload["temperature"]
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        start_time = time.time()
        with httpx.Client(timeout=timeout) as client:
            response = client.post(endpoint, json=request_data, headers=headers)
            response.raise_for_status()
            response_data = response.json()
        
        # Extract text from response
        text = ""
        if "choices" in response_data and len(response_data["choices"]) > 0:
            choice = response_data["choices"][0]
            if "message" in choice:
                text = choice["message"].get("content", "")
        
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
        error_msg = f"OpenAI error: {e}"
        if return_text is True or (return_text is None and quick):
            return f"AI error: {error_msg}"
        return {"ok": False, "text": "", "raw": None, "error": error_msg}

