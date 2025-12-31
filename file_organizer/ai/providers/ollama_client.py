"""Ollama AI provider client."""

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional


class OllamaClientError(RuntimeError):
    """Ollama client error."""
    pass


def check_ollama_health(endpoint: Optional[str] = None, timeout: int = 5) -> tuple[bool, Optional[str]]:
    """Check if Ollama service is available and healthy.
    
    Args:
        endpoint: Optional Ollama endpoint (defaults to http://localhost:11434)
        timeout: Health check timeout in seconds
        
    Returns:
        Tuple of (is_healthy, error_message_or_None)
    """
    base_url = endpoint or os.environ.get("OLLAMA_ENDPOINT") or "http://localhost:11434"
    base_url = base_url.rstrip("/")
    health_url = f"{base_url}/api/tags"
    
    try:
        req = urllib.request.Request(health_url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return True, None
            return False, f"Health check returned status {resp.status}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"Connection error: {e.reason}"
    except Exception as e:
        return False, f"Health check failed: {e}"


def get_ollama_suggestion(
    payload: Dict[str, Any],
    *,
    model: Optional[str] = None,
    endpoint: Optional[str] = None,
    timeout: Optional[int] = None,
    system: Optional[str] = None,
    quick: bool = False,
    return_text: Optional[bool] = None,
) -> Dict[str, Any] | str:
    """Request an AI suggestion from Ollama.
    
    Args:
        payload: Dict containing request context
        model: Model name (defaults to llama3.1:8b)
        endpoint: Ollama endpoint (defaults to http://localhost:11434)
        timeout: Request timeout in seconds
        system: System prompt
        quick: Use quick timeout mode
        return_text: Return plain text instead of dict
        
    Returns:
        Dict with {"ok": bool, "text": str, "raw": Any, "error": Optional[str]}
        Or string if return_text=True
    """
    base_url = endpoint or os.environ.get("OLLAMA_ENDPOINT") or "http://localhost:11434"
    base_url = base_url.rstrip("/")
    model = model or os.environ.get("OLLAMA_MODEL") or "llama3.1:latest"
    
    if timeout is None:
        timeout = 15 if quick else 30
    timeout = int(timeout)
    
    # Build prompt from payload
    prompt_parts = []
    if system:
        prompt_parts.append(system)
    
    # Extract request/instructions from payload
    request_text = payload.get("request", "")
    instructions = payload.get("instructions", "")
    context = payload.get("context", {})
    
    if request_text:
        prompt_parts.append(f"Request: {request_text}")
    if instructions:
        prompt_parts.append(f"\nInstructions:\n{instructions}")
    if context:
        prompt_parts.append(f"\nContext:\n{json.dumps(context, indent=2, default=str)}")
    
    prompt = "\n".join(prompt_parts)
    
    # Prepare request
    api_url = f"{base_url}/api/generate"
    request_data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    
    if "temperature" in payload:
        request_data["options"] = {"temperature": payload["temperature"]}
    
    try:
        req = urllib.request.Request(
            api_url,
            data=json.dumps(request_data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        
        start_time = time.time()
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                error_msg = f"Ollama API returned status {resp.status}"
                if return_text is True or (return_text is None and quick):
                    return f"AI error: {error_msg}"
                return {"ok": False, "text": "", "raw": None, "error": error_msg}
            
            response_data = json.loads(resp.read().decode("utf-8"))
            text = response_data.get("response", "")
            
            result = {
                "ok": True,
                "text": text,
                "raw": response_data,
                "error": None,
            }
            
            if return_text is True or (return_text is None and quick):
                return text
            
            return result
            
    except urllib.error.HTTPError as e:
        error_msg = f"HTTP {e.code}: {e.reason}"
        if return_text is True or (return_text is None and quick):
            return f"AI error: {error_msg}"
        return {"ok": False, "text": "", "raw": None, "error": error_msg}
    except urllib.error.URLError as e:
        error_msg = f"Connection error: {e.reason}"
        if return_text is True or (return_text is None and quick):
            return f"AI error: {error_msg}"
        return {"ok": False, "text": "", "raw": None, "error": error_msg}
    except Exception as e:
        error_msg = f"Ollama error: {e}"
        if return_text is True or (return_text is None and quick):
            return f"AI error: {error_msg}"
        return {"ok": False, "text": "", "raw": None, "error": error_msg}

