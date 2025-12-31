"""Grok (xAI) AI provider client."""

import json
import os
import time
from typing import Any, Dict, Optional

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class GrokClientError(RuntimeError):
    """Grok client error."""
    pass


def _load_hdpd_config(config_name: str) -> Optional[Dict[str, Any]]:
    """Load configuration from HDPD config directory.
    
    Args:
        config_name: Name of config file (e.g., 'grok', 'gemini')
        
    Returns:
        Dict with config values or None if not found
    """
    hdpd_config_path = os.path.expanduser("~/PycharmProjects/HDPD/config")
    config_file = os.path.join(hdpd_config_path, f"{config_name}.yaml")
    
    if not os.path.exists(config_file):
        return None
    
    try:
        import yaml
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def _get_grok_api_key() -> Optional[str]:
    """Get Grok API key from HDPD config or environment."""
    # Try HDPD config first
    config = _load_hdpd_config("grok")
    if config and config.get("api_key") and config["api_key"] != "REPLACE_ME":
        api_key = config["api_key"]
        # Check for placeholder values
        low = str(api_key).strip().lower()
        if low not in {"replace_me", "<replace_me>", "", "todo"} and "replace" not in low:
            if not (low.startswith("re") and low.endswith("me") and "*" in low):
                return api_key
    
    # Fallback to environment
    return os.environ.get("XAI_API_KEY")


def _is_grok_available() -> bool:
    """Check if Grok is configured."""
    if not HTTPX_AVAILABLE:
        return False
    api_key = _get_grok_api_key()
    if not api_key:
        return False
    low = str(api_key).strip().lower()
    if low in {"replace_me", "<replace_me>", "", "todo"} or "replace" in low:
        return False
    if low.startswith("re") and low.endswith("me") and "*" in low:
        return False
    return True


def get_grok_suggestion(
    payload: Dict[str, Any],
    *,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    timeout: Optional[int] = None,
    endpoint: Optional[str] = None,
    quick: bool = False,
    return_text: Optional[bool] = None,
) -> Dict[str, Any] | str:
    """Request an AI suggestion from Grok/xAI.
    
    Args:
        payload: Dict containing request context
        api_key: API key (defaults to HDPD config or XAI_API_KEY env var)
        model: Model name (defaults to grok-3)
        timeout: Request timeout in seconds
        endpoint: API endpoint override
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
    
    # Get API key: explicit param → HDPD config → environment
    api_key = api_key or _get_grok_api_key()
    if not api_key:
        error_msg = "Missing XAI_API_KEY (set in HDPD config/grok.yaml or XAI_API_KEY env var)"
        if return_text is True or (return_text is None and quick):
            return f"AI error: {error_msg}"
        return {"ok": False, "text": "", "raw": None, "error": error_msg}
    
    # Get config from HDPD or defaults
    config = _load_hdpd_config("grok") or {}
    endpoint = endpoint or config.get("api_url") or os.environ.get("XAI_API_URL") or "https://api.x.ai/v1"
    endpoint = endpoint.rstrip("/")
    if not endpoint.endswith("/chat/completions"):
        endpoint = endpoint + "/chat/completions"
    
    model = model or config.get("model") or os.environ.get("GROK_MODEL") or "grok-3"
    
    # Map legacy model names
    legacy_map = {
        "grok-1": "grok-3",
        "grok1": "grok-3",
        "grok-2": "grok-3",
        "grok-2-beta": "grok-3",
        "grok-2-latest": "grok-3",
    }
    model_input = str(model).strip()
    model = legacy_map.get(model_input.lower(), model_input)
    
    if timeout is None:
        base_timeout = config.get("timeout") or int(os.environ.get("GROK_TIMEOUT", "30"))
        quick_timeout = config.get("timeout_quick") or int(os.environ.get("GROK_TIMEOUT_QUICK", "15"))
        timeout = quick_timeout if quick else base_timeout
    else:
        timeout = int(timeout)
    
    # Extract system prompt from payload
    system_prompt = payload.get("system_prompt", "")
    if not system_prompt:
        system_prompt = "You are a helpful assistant."
    
    # Build user content from payload
    user_payload = {k: v for k, v in payload.items() if k != "system_prompt"}
    try:
        user_content = json.dumps(user_payload, default=str)
        if len(user_content) > 12000:
            user_content = user_content[:12000] + "\n… [truncated]"
    except Exception:
        user_content = str(user_payload)[:12000]
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": os.environ.get(
            "HDPD_AI_UA",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        ),
    }
    
    temperature = 0.15 if quick else 0.2
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": temperature,
    }
    
    try:
        start_time = time.time()
        with httpx.Client(timeout=timeout) as client:
            response = client.post(endpoint, json=body, headers=headers)
            response.raise_for_status()
            response_data = response.json()
        
        # Extract text from response
        text = ""
        if "choices" in response_data and len(response_data["choices"]) > 0:
            choice = response_data["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                text = choice["message"]["content"].strip()
        
        result = {
            "ok": True,
            "text": text,
            "raw": response_data,
            "error": None,
        }
        
        if return_text is True or (return_text is None and quick):
            return text
        
        return result
        
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
        # Handle 404 (model not found) by trying grok-3
        if e.response.status_code == 404 and model != "grok-3":
            try:
                body["model"] = "grok-3"
                with httpx.Client(timeout=timeout) as client:
                    response = client.post(endpoint, json=body, headers=headers)
                    response.raise_for_status()
                    response_data = response.json()
                text = ""
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    choice = response_data["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        text = choice["message"]["content"].strip()
                result = {"ok": True, "text": text, "raw": response_data, "error": None}
                if return_text is True or (return_text is None and quick):
                    return text
                return result
            except Exception:
                pass
        
        if return_text is True or (return_text is None and quick):
            return f"AI error: {error_msg}"
        return {"ok": False, "text": "", "raw": None, "error": error_msg}
    except httpx.HTTPError as e:
        error_msg = f"HTTP error: {e}"
        if return_text is True or (return_text is None and quick):
            return f"AI error: {error_msg}"
        return {"ok": False, "text": "", "raw": None, "error": error_msg}
    except Exception as e:
        error_msg = f"Grok error: {e}"
        if return_text is True or (return_text is None and quick):
            return f"AI error: {error_msg}"
        return {"ok": False, "text": "", "raw": None, "error": error_msg}

