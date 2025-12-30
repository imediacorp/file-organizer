"""Anthropic Claude AI provider client."""

import json
import os
import time
from typing import Any, Dict, Optional

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class AnthropicClientError(RuntimeError):
    """Anthropic client error."""
    pass


def _is_anthropic_available() -> bool:
    """Check if Anthropic is configured."""
    if not HTTPX_AVAILABLE:
        return False
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return False
    low = str(api_key).strip().lower()
    if low in {"replace_me", "<replace_me>", "", "todo"} or "replace" in low:
        return False
    if low.startswith("re") and low.endswith("me") and "*" in low:
        return False
    return True


def get_anthropic_suggestion(
    payload: Dict[str, Any],
    *,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    timeout: Optional[int] = None,
    quick: bool = False,
    return_text: Optional[bool] = None,
) -> Dict[str, Any] | str:
    """Request an AI suggestion from Anthropic Claude.
    
    Args:
        payload: Dict containing request context
        api_key: API key (defaults to ANTHROPIC_API_KEY env var)
        model: Model name (defaults to claude-3-haiku-20240307)
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
    
    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        error_msg = "Missing ANTHROPIC_API_KEY"
        if return_text is True or (return_text is None and quick):
            return f"AI error: {error_msg}"
        return {"ok": False, "text": "", "raw": None, "error": error_msg}
    
    model = model or os.environ.get("ANTHROPIC_MODEL") or "claude-3-haiku-20240307"
    
    if timeout is None:
        timeout = 15 if quick else 30
    
    # Build messages from payload
    messages = []
    
    system_prompt = payload.get("system_prompt", "")
    
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
    
    # Anthropic API endpoint
    api_url = "https://api.anthropic.com/v1/messages"
    
    request_data = {
        "model": model,
        "max_tokens": 4096,
        "messages": messages,
    }
    
    if system_prompt:
        request_data["system"] = system_prompt
    
    if "temperature" in payload:
        request_data["temperature"] = payload["temperature"]
    
    try:
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        
        start_time = time.time()
        with httpx.Client(timeout=timeout) as client:
            response = client.post(api_url, json=request_data, headers=headers)
            response.raise_for_status()
            response_data = response.json()
        
        # Extract text from response
        text = ""
        if "content" in response_data and len(response_data["content"]) > 0:
            content_block = response_data["content"][0]
            if "text" in content_block:
                text = content_block["text"]
        
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
        error_msg = f"Anthropic error: {e}"
        if return_text is True or (return_text is None and quick):
            return f"AI error: {error_msg}"
        return {"ok": False, "text": "", "raw": None, "error": error_msg}

