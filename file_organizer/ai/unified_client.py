"""Unified AI client supporting multiple providers with automatic fallback."""

import json
import time
from enum import Enum
from typing import Any, Dict, Optional

try:
    from .providers.ollama_client import get_ollama_suggestion, check_ollama_health
    from .providers.openai_client import get_openai_suggestion, _is_openai_available
    from .providers.gemini_client import get_gemini_suggestion, _is_gemini_available
    from .providers.anthropic_client import get_anthropic_suggestion, _is_anthropic_available
    from .providers.grok_client import get_grok_suggestion, _is_grok_available
    from .cache import get_cache
    from .metrics import get_metrics_collector
except Exception:
    get_ollama_suggestion = None
    check_ollama_health = None
    get_openai_suggestion = None
    _is_openai_available = None
    get_gemini_suggestion = None
    _is_gemini_available = None
    get_anthropic_suggestion = None
    _is_anthropic_available = None
    get_grok_suggestion = None
    _is_grok_available = None
    get_cache = None
    get_metrics_collector = None


class AIProvider(str, Enum):
    """AI provider selection options."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    GROK = "grok"
    AUTO = "auto"  # Try Ollama first (local), then Gemini, Grok, OpenAI, Anthropic


def _is_ollama_available() -> bool:
    """Check if Ollama service is available."""
    if check_ollama_health is None:
        return False
    try:
        is_healthy, _ = check_ollama_health(timeout=3)
        return is_healthy
    except Exception:
        return False


def get_ai_suggestion(
    payload: Dict[str, Any],
    *,
    provider: AIProvider | str = AIProvider.AUTO,
    use_cache: bool = True,
    cache_ttl: Optional[int] = None,
    use_skills: Optional[bool] = None,
    skill_resources: bool = False,
    **kwargs
) -> Dict[str, Any] | str:
    """Request an AI suggestion from the specified provider with automatic fallback.
    
    Args:
        payload: dict containing metrics/context (must be JSON-serializable)
        provider: AI provider to use (AIProvider enum or string)
        use_cache: Enable response caching
        cache_ttl: Cache time-to-live in seconds
        use_skills: Enable skill enhancement (None = auto-detect)
        skill_resources: Include full skill resources
        **kwargs: Additional arguments passed to the underlying provider client
            - quick: bool (use quick timeout)
            - timeout: int (override timeout)
            - return_text: bool (return plain string instead of dict)
            - model: str (override model)
            - endpoint: str (override endpoint)
            - system: str (system prompt, Ollama only)
    
    Returns:
        Dict with keys: {"ok": bool, "text": str, "raw": Any, "error": Optional[str]}
        Or a string if return_text=True (and quick mode or explicit)
    """
    # Enhance payload with skills if enabled
    try:
        from .skills.integration import enhance_payload_with_skill, should_use_skills
        if should_use_skills(payload, use_skills):
            payload = enhance_payload_with_skill(payload, include_resources=skill_resources)
    except Exception:
        # Skills integration not available, continue without enhancement
        pass
    
    # Normalize provider
    if isinstance(provider, str):
        try:
            provider = AIProvider(provider.lower())
        except ValueError:
            provider = AIProvider.AUTO
    
    # Track start time and payload size for metrics
    start_time = time.time()
    try:
        payload_size = len(json.dumps(payload, default=str).encode("utf-8"))
    except Exception:
        payload_size = len(str(payload).encode("utf-8"))
    
    # Check cache first
    if use_cache and get_cache is not None:
        cache = get_cache()
        cached_response = cache.get(payload, str(provider), ttl=cache_ttl)
        if cached_response is not None:
            if get_metrics_collector is not None:
                try:
                    collector = get_metrics_collector()
                    collector.record(
                        provider=str(provider),
                        duration_ms=0,
                        success=cached_response.get("ok", False),
                        cached=True,
                        payload_size=payload_size,
                        response_size=len(str(cached_response.get("text", "")).encode("utf-8")),
                    )
                except Exception:
                    pass
            if kwargs.get("return_text") or kwargs.get("quick"):
                return cached_response.get("text", "")
            return cached_response
    
    # Determine which provider to use
    actual_provider = None
    if provider == AIProvider.AUTO:
        # Try Ollama first (local), then cloud providers
        if _is_ollama_available():
            actual_provider = AIProvider.OLLAMA
        elif _is_gemini_available and _is_gemini_available():
            actual_provider = AIProvider.GEMINI
        elif _is_grok_available and _is_grok_available():
            actual_provider = AIProvider.GROK
        elif _is_openai_available and _is_openai_available():
            actual_provider = AIProvider.OPENAI
        elif _is_anthropic_available and _is_anthropic_available():
            actual_provider = AIProvider.ANTHROPIC
        else:
            # None available - try Ollama anyway (might give better error)
            actual_provider = AIProvider.OLLAMA
    else:
        actual_provider = provider
    
    provider_name = str(actual_provider).lower() if actual_provider else "unknown"
    
    # Call the appropriate provider
    result = None
    error_msg = None
    
    try:
        if actual_provider == AIProvider.OLLAMA:
            if get_ollama_suggestion is None:
                error_msg = "Ollama client not available"
            else:
                system_prompt = payload.get("system_prompt")
                ollama_kwargs = kwargs.copy()
                if system_prompt and "system" not in ollama_kwargs:
                    ollama_kwargs["system"] = system_prompt
                result = get_ollama_suggestion(payload, **ollama_kwargs)
        
        elif actual_provider == AIProvider.OPENAI:
            if get_openai_suggestion is None:
                error_msg = "OpenAI client not available"
            else:
                result = get_openai_suggestion(payload, **kwargs)
        
        elif actual_provider == AIProvider.GEMINI:
            if get_gemini_suggestion is None:
                error_msg = "Gemini client not available"
            else:
                result = get_gemini_suggestion(payload, **kwargs)
        
        elif actual_provider == AIProvider.ANTHROPIC:
            if get_anthropic_suggestion is None:
                error_msg = "Anthropic client not available"
            else:
                result = get_anthropic_suggestion(payload, **kwargs)
        
        elif actual_provider == AIProvider.GROK:
            if get_grok_suggestion is None:
                error_msg = "Grok client not available"
            else:
                result = get_grok_suggestion(payload, **kwargs)
        
        else:
            error_msg = f"Unknown provider: {actual_provider}"
    
    except Exception as e:
        error_msg = f"{provider_name} error: {e}"
        # Try fallback if in AUTO mode
        if provider == AIProvider.AUTO and actual_provider != AIProvider.OLLAMA:
            try:
                if _is_ollama_available() and get_ollama_suggestion is not None:
                    system_prompt = payload.get("system_prompt")
                    ollama_kwargs = kwargs.copy()
                    if system_prompt and "system" not in ollama_kwargs:
                        ollama_kwargs["system"] = system_prompt
                    result = get_ollama_suggestion(payload, **ollama_kwargs)
                    error_msg = None
            except Exception:
                pass
    
    # Handle result
    duration_ms = (time.time() - start_time) * 1000
    
    if error_msg:
        if get_metrics_collector is not None:
            try:
                collector = get_metrics_collector()
                collector.record(
                    provider=provider_name,
                    duration_ms=duration_ms,
                    success=False,
                    cached=False,
                    error=error_msg,
                    payload_size=payload_size,
                    response_size=0,
                )
            except Exception:
                pass
        
        if kwargs.get("return_text") or kwargs.get("quick"):
            return f"AI error: {error_msg}"
        return {"ok": False, "text": "", "raw": None, "error": error_msg}
    
    # Process result
    if result is None:
        error_msg = f"{provider_name} returned no result"
        if kwargs.get("return_text") or kwargs.get("quick"):
            return f"AI error: {error_msg}"
        return {"ok": False, "text": "", "raw": None, "error": error_msg}
    
    # Normalize result to dict if needed
    if isinstance(result, str):
        if result.startswith("AI error:"):
            error_msg = result
            if get_metrics_collector is not None:
                try:
                    collector = get_metrics_collector()
                    collector.record(
                        provider=provider_name,
                        duration_ms=duration_ms,
                        success=False,
                        cached=False,
                        error=error_msg,
                        payload_size=payload_size,
                        response_size=0,
                    )
                except Exception:
                    pass
            return result
        result = {"ok": True, "text": result, "raw": None, "error": None}
    
    # Record metrics
    if get_metrics_collector is not None:
        try:
            collector = get_metrics_collector()
            success = result.get("ok", False)
            response_size = len(str(result.get("text", "")).encode("utf-8"))
            collector.record(
                provider=provider_name,
                duration_ms=duration_ms,
                success=success,
                cached=False,
                error=result.get("error"),
                payload_size=payload_size,
                response_size=response_size,
            )
        except Exception:
            pass
    
    # Cache successful responses
    if use_cache and get_cache is not None and result.get("ok"):
        try:
            cache = get_cache()
            cache.set(payload, provider_name, result, ttl=cache_ttl)
        except Exception:
            pass
    
    # Return result
    if kwargs.get("return_text") or kwargs.get("quick"):
        if result.get("ok"):
            return result.get("text", "")
        return f"AI error: {result.get('error', 'Unknown error')}"
    
    return result


def get_provider_status() -> Dict[str, Any]:
    """Get status of all available AI providers.
    
    Returns:
        Dict with provider availability and health status
    """
    status = {
        "ollama": {
            "available": False,
            "healthy": False,
            "error": None,
        },
        "openai": {
            "available": False,
            "configured": False,
        },
        "gemini": {
            "available": False,
            "configured": False,
        },
        "anthropic": {
            "available": False,
            "configured": False,
        },
        "grok": {
            "available": False,
            "configured": False,
        },
    }
    
    # Check Ollama
    if check_ollama_health is not None:
        try:
            is_healthy, error = check_ollama_health(timeout=3)
            status["ollama"]["healthy"] = is_healthy
            status["ollama"]["available"] = is_healthy
            if error:
                status["ollama"]["error"] = error
        except Exception as e:
            status["ollama"]["error"] = str(e)
    
    # Check OpenAI
    if _is_openai_available is not None:
        status["openai"]["configured"] = _is_openai_available()
        status["openai"]["available"] = status["openai"]["configured"]
    
    # Check Gemini
    if _is_gemini_available is not None:
        status["gemini"]["configured"] = _is_gemini_available()
        status["gemini"]["available"] = status["gemini"]["configured"]
    
    # Check Anthropic
    if _is_anthropic_available is not None:
        status["anthropic"]["configured"] = _is_anthropic_available()
        status["anthropic"]["available"] = status["anthropic"]["configured"]
    
    # Check Grok
    if _is_grok_available is not None:
        status["grok"]["configured"] = _is_grok_available()
        status["grok"]["available"] = status["grok"]["configured"]
    
    return status

