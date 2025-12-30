"""Integration helpers for using skills with AI suggestions."""

from typing import Any, Dict, Optional

try:
    from .manager import get_skill_instructions
except Exception:
    get_skill_instructions = None


def enhance_payload_with_skill(
    payload: Dict[str, Any],
    domain: Optional[str] = None,
    include_resources: bool = False
) -> Dict[str, Any]:
    """Enhance an AI payload with domain-specific skill instructions.
    
    Args:
        payload: Original payload dict (may contain system_prompt, domain, etc.)
        domain: Domain name to use (defaults to payload.get("domain"))
        include_resources: Whether to include skill resources in the prompt
    
    Returns:
        Enhanced payload with skill instructions integrated into system_prompt
    """
    if get_skill_instructions is None:
        return payload
    
    # Extract domain from payload if not provided
    if domain is None:
        domain = payload.get("domain") or payload.get("skill_domain")
    
    if not domain:
        return payload
    
    # Get skill instructions for the domain
    skill_instructions = get_skill_instructions(domain, include_resources=include_resources)
    
    if not skill_instructions:
        return payload
    
    # Integrate skill instructions with existing system_prompt
    existing_system = payload.get("system_prompt", "")
    
    if existing_system:
        enhanced_system = f"{existing_system}\n\n{skill_instructions}"
    else:
        enhanced_system = skill_instructions
    
    # Create enhanced payload
    enhanced = payload.copy()
    enhanced["system_prompt"] = enhanced_system
    enhanced["_skill_enhanced"] = True
    enhanced["_skill_domain"] = domain
    
    return enhanced


def should_use_skills(payload: Dict[str, Any], use_skills: Optional[bool] = None) -> bool:
    """Determine if skills should be used for a payload.
    
    Args:
        payload: Payload dict
        use_skills: Explicit flag (None = auto-detect from payload)
    
    Returns:
        True if skills should be used
    """
    if use_skills is not None:
        return use_skills
    
    # Auto-detect: use skills if domain is specified and not explicitly disabled
    if payload.get("_skip_skills", False):
        return False
    
    domain = payload.get("domain") or payload.get("skill_domain")
    return domain is not None and domain != ""

