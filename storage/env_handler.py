"""Environment file operations handler."""

import os
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv, set_key, unset_key


class EnvHandler:
    """Handle .env file operations."""

    def __init__(self, env_path: Optional[Path] = None):
        """
        Initialize env handler.

        Args:
            env_path: Path to .env file
        """
        self.env_path = env_path or Path.cwd() / ".env"

    def ensure_env_file(self) -> Path:
        """
        Ensure .env file exists with proper permissions.

        Returns:
            Path to .env file
        """
        if not self.env_path.exists():
            self.env_path.touch(mode=0o600)

        # Ensure secure permissions
        self.set_permissions(0o600)
        return self.env_path

    def set_permissions(self, mode: int) -> bool:
        """
        Set file permissions.

        Args:
            mode: Permission mode (e.g., 0o600)

        Returns:
            True if successful
        """
        try:
            self.env_path.chmod(mode)
            return True
        except Exception as e:
            print(f"Warning: Could not set permissions: {e}")
            return False

    def check_permissions(self) -> tuple[bool, str]:
        """
        Check if permissions are secure.

        Returns:
            Tuple of (is_secure, message)
        """
        if not self.env_path.exists():
            return True, "File does not exist yet"

        stat_info = os.stat(self.env_path)
        mode = oct(stat_info.st_mode)[-3:]

        if mode == "600":
            return True, f"Permissions are secure: {mode}"
        else:
            return False, f"Warning: Permissions are too open: {mode} (should be 600)"

    def read_env(self) -> Dict[str, Optional[str]]:
        """
        Read all environment variables from .env.

        Returns:
            Dictionary of variables
        """
        load_dotenv(self.env_path)
        return dict(os.environ)

    def write_key(self, key: str, value: str) -> bool:
        """
        Write a key-value pair to .env.

        Args:
            key: Variable name
            value: Variable value

        Returns:
            True if successful
        """
        try:
            set_key(str(self.env_path), key, value)
            self.set_permissions(0o600)
            return True
        except Exception as e:
            print(f"Error writing to .env: {e}")
            return False

    def remove_key(self, key: str) -> bool:
        """
        Remove a key from .env.

        Args:
            key: Variable name

        Returns:
            True if successful
        """
        try:
            unset_key(str(self.env_path), key)
            return True
        except Exception as e:
            print(f"Error removing from .env: {e}")
            return False

    def get_backup_path(self) -> Path:
        """
        Get path for backup file.

        Returns:
            Path to backup .env file
        """
        return self.env_path.with_suffix(".env.backup")
