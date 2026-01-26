"""JSON metadata file operations handler."""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class MetadataHandler:
    """Handle metadata JSON file operations."""

    def __init__(self, metadata_path: Optional[Path] = None):
        """
        Initialize metadata handler.

        Args:
            metadata_path: Path to metadata JSON file
        """
        self.metadata_path = metadata_path or Path.cwd() / "keys_metadata.json"

    def ensure_metadata_file(self) -> Path:
        """
        Ensure metadata file exists with proper permissions.

        Returns:
            Path to metadata file
        """
        if not self.metadata_path.exists():
            self.metadata_path.write_text("{}")
            self.metadata_path.chmod(0o600)

        return self.metadata_path

    def read_all(self) -> Dict[str, Any]:
        """
        Read all metadata from JSON file.

        Returns:
            Dictionary of metadata
        """
        if not self.metadata_path.exists():
            return {}

        try:
            data = json.loads(self.metadata_path.read_text())
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, Exception):
            return {}

    def write_all(self, data: Dict[str, Any]) -> bool:
        """
        Write all metadata to JSON file.

        Args:
            data: Metadata dictionary

        Returns:
            True if successful
        """
        try:
            self.ensure_metadata_file()
            self.metadata_path.write_text(json.dumps(data, indent=2, default=str))
            self.metadata_path.chmod(0o600)
            return True
        except Exception as e:
            print(f"Error writing metadata: {e}")
            return False

    def read_key(self, key_name: str) -> Optional[Dict[str, Any]]:
        """
        Read metadata for a specific key.

        Args:
            key_name: Name of the key

        Returns:
            Metadata dictionary or None
        """
        all_data = self.read_all()
        return all_data.get(key_name)

    def write_key(self, key_name: str, metadata: Dict[str, Any]) -> bool:
        """
        Write metadata for a specific key.

        Args:
            key_name: Name of the key
            metadata: Metadata dictionary

        Returns:
            True if successful
        """
        all_data = self.read_all()
        all_data[key_name] = metadata
        return self.write_all(all_data)

    def delete_key(self, key_name: str) -> bool:
        """
        Delete metadata for a specific key.

        Args:
            key_name: Name of the key

        Returns:
            True if successful
        """
        all_data = self.read_all()

        if key_name not in all_data:
            return False

        del all_data[key_name]
        return self.write_all(all_data)

    def backup(self) -> Optional[Path]:
        """
        Create backup of metadata file.

        Returns:
            Path to backup file or None
        """
        if not self.metadata_path.exists():
            return None

        backup_path = self.metadata_path.with_suffix(".json.backup")
        try:
            backup_path.write_text(self.metadata_path.read_text())
            backup_path.chmod(0o600)
            return backup_path
        except Exception:
            return None

    def restore(self, backup_path: Optional[Path] = None) -> bool:
        """
        Restore metadata from backup.

        Args:
            backup_path: Path to backup file (defaults to .json.backup)

        Returns:
            True if successful
        """
        if backup_path is None:
            backup_path = self.metadata_path.with_suffix(".json.backup")

        if not backup_path.exists():
            return False

        try:
            self.metadata_path.write_text(backup_path.read_text())
            self.metadata_path.chmod(0o600)
            return True
        except Exception:
            return False
