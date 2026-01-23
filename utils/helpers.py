"""Common utility functions."""

import os
from pathlib import Path
from typing import Optional


def ensure_directory(path: str) -> Path:
    """
    Ensure a directory exists, create if it doesn't.

    Args:
        path: Directory path

    Returns:
        Path object
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def get_project_root() -> Path:
    """
    Get the project root directory.

    Returns:
        Path object for project root
    """
    return Path.cwd()


def check_file_permissions(filepath: str) -> bool:
    """
    Check if file has secure permissions (600).

    Args:
        filepath: Path to file

    Returns:
        True if permissions are secure
    """
    if not os.path.exists(filepath):
        return True

    stat_info = os.stat(filepath)
    mode = oct(stat_info.st_mode)[-3:]
    return mode == "600"


def set_file_permissions(filepath: str, mode: int = 0o600) -> bool:
    """
    Set file permissions.

    Args:
        filepath: Path to file
        mode: Permission mode (default 600)

    Returns:
        True if successful
    """
    try:
        os.chmod(filepath, mode)
        return True
    except (OSError, PermissionError):
        return False


def mask_key(key: str, visible_chars: int = 4) -> str:
    """
    Mask an API key for display.

    Args:
        key: API key to mask
        visible_chars: Number of characters to show at start and end

    Returns:
        Masked key string
    """
    if len(key) <= visible_chars * 2:
        return "*" * len(key)

    start = key[:visible_chars]
    end = key[-visible_chars:]
    middle = "*" * (len(key) - visible_chars * 2)
    return f"{start}{middle}{end}"
