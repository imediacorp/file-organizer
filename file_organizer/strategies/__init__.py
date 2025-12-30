"""Organization strategies for file organization."""

from file_organizer.strategies.filetype import FileTypeStrategy
from file_organizer.strategies.rule_based import RuleBasedStrategy

# Try to import AI strategy (may not be available if dependencies missing)
try:
    from file_organizer.strategies.ai_suggested import AISuggestedStrategy
    AI_AVAILABLE = True
except Exception:
    AISuggestedStrategy = None
    AI_AVAILABLE = False

# Strategy registry
_STRATEGIES = {
    'filetype': FileTypeStrategy,
    'rule_based': RuleBasedStrategy,
}

# Register AI strategy if available
if AI_AVAILABLE and AISuggestedStrategy is not None:
    _STRATEGIES['ai_suggested'] = AISuggestedStrategy

def get_strategy(name):
    """Get a strategy class by name."""
    return _STRATEGIES.get(name)

def list_strategies():
    """List all available strategies."""
    return list(_STRATEGIES.keys())

def register_strategy(name, strategy_class):
    """Register a custom strategy."""
    _STRATEGIES[name] = strategy_class

__all__ = ['FileTypeStrategy', 'RuleBasedStrategy', 'get_strategy', 'list_strategies', 'register_strategy']

if AI_AVAILABLE:
    __all__.append('AISuggestedStrategy')

