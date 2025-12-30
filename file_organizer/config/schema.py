"""
Configuration schema validation.
"""

from typing import Dict, List, Any


def validate_config_schema(config: Dict[str, Any]) -> List[str]:
    """
    Validate configuration schema.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    if not isinstance(config, dict):
        return ["Configuration must be a dictionary"]
    
    # Validate strategies section
    if 'strategies' in config:
        strategies = config['strategies']
        if not isinstance(strategies, dict):
            errors.append("'strategies' must be a dictionary")
        else:
            # Validate filetype strategy
            if 'filetype' in strategies:
                filetype_config = strategies['filetype']
                if not isinstance(filetype_config, dict):
                    errors.append("'strategies.filetype' must be a dictionary")
                else:
                    if 'categories' in filetype_config:
                        categories = filetype_config['categories']
                        if not isinstance(categories, dict):
                            errors.append("'strategies.filetype.categories' must be a dictionary")
                    
                    if 'max_depth' in filetype_config:
                        max_depth = filetype_config['max_depth']
                        if not isinstance(max_depth, int) or max_depth < 0:
                            errors.append("'strategies.filetype.max_depth' must be a non-negative integer")
            
            # Validate rule_based strategy
            if 'rule_based' in strategies:
                rule_config = strategies['rule_based']
                if not isinstance(rule_config, dict):
                    errors.append("'strategies.rule_based' must be a dictionary")
                else:
                    if 'file_rules' in rule_config:
                        file_rules = rule_config['file_rules']
                        if not isinstance(file_rules, list):
                            errors.append("'strategies.rule_based.file_rules' must be a list")
                    
                    if 'folder_rules' in rule_config:
                        folder_rules = rule_config['folder_rules']
                        if not isinstance(folder_rules, list):
                            errors.append("'strategies.rule_based.folder_rules' must be a list")
    
    # Validate general section
    if 'general' in config:
        general = config['general']
        if not isinstance(general, dict):
            errors.append("'general' must be a dictionary")
    
    # Validate AI section
    if 'ai' in config:
        ai_config = config['ai']
        if not isinstance(ai_config, dict):
            errors.append("'ai' must be a dictionary")
        else:
            if 'provider' in ai_config:
                provider = ai_config['provider']
                valid_providers = ['auto', 'ollama', 'openai', 'gemini', 'anthropic']
                if provider not in valid_providers:
                    errors.append(f"'ai.provider' must be one of {valid_providers}")
    
    # Validate library_science section
    if 'library_science' in config:
        ls_config = config['library_science']
        if not isinstance(ls_config, dict):
            errors.append("'library_science' must be a dictionary")
    
    return errors

