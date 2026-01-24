"""Core API key CRUD operations."""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv, set_key, unset_key
from .models import APIKey
from .validators import KeyValidator


class KeyManager:
    """Manage API key storage and retrieval."""

    def __init__(self, env_path: Optional[Path] = None):
        """
        Initialize key manager.

        Args:
            env_path: Path to .env file (defaults to ./.env)
        """
        self.env_path = env_path or Path.cwd() / ".env"
        self._ensure_env_file()

    def _ensure_env_file(self):
        """Create .env file if it doesn't exist."""
        if not self.env_path.exists():
            self.env_path.touch(mode=0o600)
            # Set proper permissions
            os.chmod(self.env_path, 0o600)

#fixme pylint bug
    def add_key(self, name: str, key_value: str, service: str,
                description: Optional[str] = None, tags: List[str] = None) -> APIKey:
        """
        Add a new API key.

        Args:
            name: Key identifier
            key_value: The actual API key
            service: Service type
            description: Optional description
            tags: Optional tags

        Returns:
            APIKey object

        Raises:
            ValidationError: If key format is invalid
            ValueError: If key already exists
        """
        # Validate key format
        KeyValidator.validate(key_value, service)

        # Check if key already exists
        if self.key_exists(name):
            raise ValueError(f"Key '{name}' already exists")

        # Create APIKey model
        api_key = APIKey(
            name=name,
            service=service,
            description=description,
            tags=tags or []
        )

        # Store in .env file
        set_key(str(self.env_path), name, key_value)

        return api_key

    def get_key_value(self, name: str) -> str:
        """
        Retrieve API key value.

        Args:
            name: Key identifier

        Returns:
            The API key value

        Raises:
            KeyError: If key not found
        """
        load_dotenv(self.env_path)
        value = os.getenv(name)

        if not value:
            raise KeyError(f"Key '{name}' not found")

        return value

    def update_key(self, name: str, new_value: Optional[str] = None,
                   service: Optional[str] = None, description: Optional[str] = None,
                   tags: Optional[List[str]] = None) -> APIKey:
        """
        Update an existing API key.

        Args:
            name: Key identifier
            new_value: New key value (optional)
            service: New service (optional)
            description: New description (optional)
            tags: New tags (optional)

        Returns:
            Updated APIKey object

        Raises:
            KeyError: If key not found
            ValidationError: If new value format is invalid
        """
        if not self.key_exists(name):
            raise KeyError(f"Key '{name}' not found")

        # fixme pylint, pylance bug
        current_value = self.get_key_value(name)

        if new_value:
            # Validate new value
            service_to_check = service or self._get_service_from_metadata(name)
            KeyValidator.validate(new_value, service_to_check or "unknown")
            set_key(str(self.env_path), name, new_value)
            # fixme pylint bug
            current_value = new_value

        # Update metadata (would be handled by MetadataManager)
        # For now, return basic APIKey
        return APIKey(
            name=name,
            service=service or "unknown",
            description=description,
            tags=tags or []
        )

    def delete_key(self, name: str) -> bool:
        """
        Delete an API key.

        Args:
            name: Key identifier

        Returns:
            True if deleted

        Raises:
            KeyError: If key not found
        """
        if not self.key_exists(name):
            raise KeyError(f"Key '{name}' not found")

        unset_key(str(self.env_path), name)
        return True

    def key_exists(self, name: str) -> bool:
        """Check if a key exists."""
        load_dotenv(self.env_path)
        return os.getenv(name) is not None

    def list_all_keys(self) -> Dict[str, str]:
        """
        List all stored keys (names only, no values).

        Returns:
            Dictionary of key names
        """
        load_dotenv(self.env_path)
        return {k: k for k in os.environ if k.startswith(('sk-', 'ghp_', 'AKIA', 'API_'))}

    def _get_service_from_metadata(self, name: str) -> Optional[str]:
        """Get service type from metadata (placeholder)."""
        # This would interact with MetadataManager
        return None

    def check_permissions(self) -> bool:
        """Check if .env file has secure permissions (600)."""
        if not self.env_path.exists():
            return True

        stat_info = os.stat(self.env_path)
        mode = oct(stat_info.st_mode)[-3:]
        return mode == "600"

    def fix_permissions(self) -> bool:
        """Fix .env file permissions to 600."""
        try:
            os.chmod(self.env_path, 0o600)
            return True
        except Exception:
            return False
