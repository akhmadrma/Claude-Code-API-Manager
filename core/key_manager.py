"""Core API key CRUD operations."""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv, set_key, unset_key
from core.metadata_manager import MetadataManager

from constans.providers import Provider
from .models import APIKey

metadata_manager = MetadataManager()


class KeyManager:
    """Manage API key storage and retrieval."""

    def __init__(self, env_path: Optional[Path] = None):
        """
        Initialize key manager.

        Args:
            env_path: Path to .env file (defaults to ./.env)
        """
        self.env_path = env_path or Path.home() / ".capi/.env"
        self._ensure_env_file()

    def _ensure_env_file(self):
        """Create .env file if it doesn't exist."""
        if not self.env_path.exists():
            # Create parent directory if it doesn't exist
            self.env_path.parent.mkdir(parents=True, exist_ok=True)
            # Create file with secure permissions
            self.env_path.touch()
            os.chmod(self.env_path, 0o600)
    def add_key(
        self,
        name: str,
        key_value: str,
        provider: Provider,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> APIKey:
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

        # Check if key already exists
        if self.key_exists(name):
            raise ValueError(f"Key '{name}' already exists")

        # Create APIKey model
        api_key = APIKey(
            name=name,
            provider=provider,
            description=description,
            tags=tags or [],
            status="inactive",
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

    def get_active_key(
        self,
    ) -> APIKey:
        """
        Retrieve the active API key.

        Returns:
            APIKey object

        Raises:
            KeyError: If no active key found
        """
        all_metadata: Dict[str, APIKey] = metadata_manager.list_all_metadata()
        active_key = next((key for key in all_metadata.values() if key.status == "active"), None)

        if not active_key:
            raise KeyError("No active key found")

        return APIKey(
            name=active_key.name,
            provider=active_key.provider,
            description=active_key.description,
            tags=active_key.tags,
            status=active_key.status,
        )

    def update_key(
        self,
        name: str,
        new_value: Optional[str] = None,
        provider: Optional[Provider] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> APIKey:
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
        ## fixme : still not effective
        if not self.key_exists(name):
            raise KeyError(f"Key '{name}' not found")

        provider_to_check = provider or self._get_provider_from_metadata(name)

        if new_value and provider_to_check:
            set_key(str(self.env_path), name, new_value)

        # Update metadata (would be handled by MetadataManager)
        # For now, return basic APIKey
        return APIKey(
            name=name, provider=provider or "anthropic", description=description, tags=tags or []
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

    def set_active_key(self, name: str) -> APIKey:
        """
        Set an API key as active.

        Args:
            name: Key identifier

        Returns:
            True if set

        Raises:
            KeyError: If key not found
        """
        metadata_key = metadata_manager.get_metadata(name)

        if not metadata_key:
            raise KeyError(f"Key '{name}' not found")

        return APIKey(
            name=name,
            provider=metadata_key.provider,
            description=metadata_key.description,
            tags=metadata_key.tags,
            status="active",
        )

    def set_inactive_key(self, name: str) -> APIKey:
        """
        Set an API key as active.

        Args:
            name: Key identifier

        Returns:
            True if set

        Raises:
            KeyError: If key not found
        """
        metadata_key = metadata_manager.get_metadata(name)

        if not metadata_key:
            raise KeyError(f"Key '{name}' not found")

        return APIKey(
            name=name,
            provider=metadata_key.provider,
            description=metadata_key.description,
            tags=metadata_key.tags,
            status="inactive",
        )

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
        return {k: k for k in os.environ if k.startswith(("sk-", "ghp_", "AKIA", "API_"))}

    def _get_provider_from_metadata(self, name: str) -> Optional[Provider]:
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
