"""Skill definition and metadata structures."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SkillMetadata:
    """Metadata for a skill (loaded first, before full instructions)."""
    name: str
    domain: str
    description: str
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    author: Optional[str] = None


@dataclass
class Skill:
    """A skill containing domain-specific expertise.
    
    Skills follow a progressive loading strategy:
    1. Metadata is loaded first (lightweight)
    2. Full instructions are loaded when skill is activated
    3. Resources are loaded on-demand as needed
    """
    metadata: SkillMetadata
    instructions: str
    resources: Dict[str, Any] = field(default_factory=dict)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_system_prompt(self, include_resources: bool = False) -> str:
        """Convert skill to a system prompt for AI."""
        parts = [
            f"# {self.metadata.name} Skill",
            f"Domain: {self.metadata.domain}",
            "",
            "## Instructions",
            self.instructions,
        ]
        
        if include_resources and self.resources:
            parts.extend([
                "",
                "## Resources",
                self._format_resources(),
            ])
        
        if self.examples:
            parts.extend([
                "",
                "## Examples",
                self._format_examples(),
            ])
        
        return "\n".join(parts)
    
    def _format_resources(self) -> str:
        """Format resources as text."""
        lines = []
        for key, value in self.resources.items():
            if isinstance(value, str):
                lines.append(f"### {key}\n{value}")
            elif isinstance(value, dict):
                lines.append(f"### {key}\n{self._dict_to_text(value)}")
            else:
                lines.append(f"### {key}\n{str(value)}")
        return "\n\n".join(lines)
    
    def _format_examples(self) -> str:
        """Format examples as text."""
        lines = []
        for i, example in enumerate(self.examples, 1):
            lines.append(f"### Example {i}")
            if isinstance(example, dict):
                lines.append(self._dict_to_text(example))
            else:
                lines.append(str(example))
        return "\n\n".join(lines)
    
    @staticmethod
    def _dict_to_text(d: Dict[str, Any], indent: int = 0) -> str:
        """Convert dict to readable text format."""
        lines = []
        prefix = "  " * indent
        for key, value in d.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(Skill._dict_to_text(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"{prefix}  -")
                        lines.append(Skill._dict_to_text(item, indent + 2))
                    else:
                        lines.append(f"{prefix}  - {item}")
            else:
                lines.append(f"{prefix}{key}: {value}")
        return "\n".join(lines)

