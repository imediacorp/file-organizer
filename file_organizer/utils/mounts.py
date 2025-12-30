"""
Utilities for handling mounted drives (external and network).
"""

import os
import platform
from pathlib import Path
from typing import Optional, Tuple, Dict


def is_network_path(path: Path) -> bool:
    """
    Check if a path is on a network drive.
    
    Args:
        path: Path to check
        
    Returns:
        True if path appears to be on a network drive
    """
    path_str = str(path.resolve())
    
    # Windows network paths
    if platform.system() == 'Windows':
        return path_str.startswith('\\\\') or path_str.startswith('//')
    
        # macOS/Linux network mounts (typically in /Volumes, /mnt, or /media)
        # Also check for common network mount indicators
        if platform.system() in ('Darwin', 'Linux'):
            # Check for common network mount points
            # Note: These are heuristics - volumes in /Volumes can be local or network
            network_indicators = [
                '/net',      # Network filesystems
                '/nfs',      # NFS mounts
                '/smb',      # SMB mounts
            ]
            
            for indicator in network_indicators:
                if path_str.startswith(indicator):
                    return True
            
            # /Volumes on macOS can contain both local and network drives
            # /mnt and /media on Linux can contain both local and network mounts
            # We can't reliably detect network vs local without checking mount info
            # For now, return False for these and let the user know it works
    
    return False


def is_path_accessible(path: Path) -> Tuple[bool, Optional[str]]:
    """
    Check if a path is accessible.
    
    Args:
        path: Path to check
        
    Returns:
        Tuple of (is_accessible, error_message)
    """
    try:
        path_obj = Path(path)
        
        # Check if path exists
        if not path_obj.exists():
            return False, f"Path does not exist: {path}"
        
        # Check if it's a directory
        if not path_obj.is_dir():
            return False, f"Path is not a directory: {path}"
        
        # Try to list directory contents (read permission test)
        try:
            list(path_obj.iterdir())
        except PermissionError as e:
            return False, f"Permission denied accessing {path}: {e}"
        except OSError as e:
            return False, f"OS error accessing {path}: {e}"
        
        # Check write permission by trying to create a test file (but don't actually create it)
        try:
            test_path = path_obj / '.file_organizer_test_write'
            # Just check if we can create it, don't actually create
            test_path.touch(exist_ok=False)
            test_path.unlink()
        except PermissionError:
            return True, "Path is readable but not writable (read-only mode)"
        except OSError:
            pass  # Some filesystems don't support touch, but that's OK
        
        return True, None
        
    except Exception as e:
        return False, f"Error checking path {path}: {e}"


def get_path_info(path: Path) -> Dict:
    """
    Get information about a path (mount point, drive type, etc.).
    
    Args:
        path: Path to analyze
        
    Returns:
        Dictionary with path information
    """
    info = {
        'path': str(path),
        'resolved_path': str(path.resolve()),
        'exists': path.exists(),
        'is_dir': path.is_dir() if path.exists() else False,
        'is_network': False,
        'is_readonly': False,
    }
    
    if path.exists():
        # Check if network path
        info['is_network'] = is_network_path(path)
        
        # Check if readonly
        try:
            test_path = path / '.file_organizer_test_write'
            test_path.touch(exist_ok=False)
            test_path.unlink()
            info['is_readonly'] = False
        except (PermissionError, OSError):
            info['is_readonly'] = True
        
        # Get filesystem info if available (Unix-like systems)
        try:
            if hasattr(os, 'statvfs'):
                stat_info = os.statvfs(str(path))
                info['filesystem_info'] = {
                    'total_space': stat_info.f_blocks * stat_info.f_frsize,
                    'free_space': stat_info.f_bavail * stat_info.f_frsize,
                    'used_space': (stat_info.f_blocks - stat_info.f_bavail) * stat_info.f_frsize,
                }
        except (OSError, AttributeError):
            # statvfs may not be available on all systems or for all filesystem types
            pass
    
    return info


def validate_path_for_operations(path: Path, require_write: bool = True) -> Tuple[bool, Optional[str]]:
    """
    Validate that a path is suitable for file organization operations.
    
    Args:
        path: Path to validate
        require_write: If True, path must be writable
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    accessible, error = is_path_accessible(path)
    if not accessible:
        return False, error
    
    if require_write:
        path_info = get_path_info(path)
        if path_info.get('is_readonly', False):
            return False, "Path is read-only. File organization requires write access."
    
    return True, None

