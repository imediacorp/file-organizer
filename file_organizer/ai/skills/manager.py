"""Skill loading and management."""

from typing import Any, Dict, Optional

try:
    from .skill import Skill, SkillMetadata
    from .library_science import get_library_science_skill
except Exception:
    Skill = None
    SkillMetadata = None
    get_library_science_skill = None


# Skill registry
_SKILLS: Dict[str, Skill] = {}


def register_skill(skill: Skill) -> None:
    """Register a skill.
    
    Args:
        skill: Skill instance to register
    """
    if Skill is None:
        return
    _SKILLS[skill.metadata.domain] = skill


def get_skill(domain: str) -> Optional[Skill]:
    """Get a skill by domain.
    
    Args:
        domain: Skill domain name
        
    Returns:
        Skill instance or None if not found
    """
    if domain in _SKILLS:
        return _SKILLS[domain]
    
    # Try to load built-in skills
    if domain == "library_science" and get_library_science_skill is not None:
        try:
            skill = get_library_science_skill()
            register_skill(skill)
            return skill
        except Exception:
            pass
    
    return None


def get_skill_instructions(domain: str, include_resources: bool = False) -> Optional[str]:
    """Get skill instructions as system prompt.
    
    Args:
        domain: Skill domain name
        include_resources: Whether to include skill resources
        
    Returns:
        System prompt string or None if skill not found
    """
    skill = get_skill(domain)
    if skill is None:
        return None
    
    return skill.to_system_prompt(include_resources=include_resources)


def list_skills() -> list[str]:
    """List all registered skill domains.
    
    Returns:
        List of skill domain names
    """
    return list(_SKILLS.keys())


# Initialize built-in skills
def _initialize_builtin_skills():
    """Initialize built-in skills."""
    if get_library_science_skill is not None:
        try:
            skill = get_library_science_skill()
            register_skill(skill)
        except Exception:
            pass


# Auto-initialize on import
_initialize_builtin_skills()

