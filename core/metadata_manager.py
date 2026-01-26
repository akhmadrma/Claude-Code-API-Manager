"""Metadata operations for API keys."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from typing_extensions import TypedDict

from constans.providers import Provider
from .models import APIKey


class MetadataDict(TypedDict, total=False):
    """Type definition for metadata storage format."""

    name: str
    provider: Provider
    description: Optional[str]
    tags: List[str]
    status: str
    created_at: datetime
    updated_at: datetime


class MetadataManager:
    """Manage API key metadata storage."""

    @staticmethod
    def _metadata_to_api_key(api_data: MetadataDict) -> APIKey:
        """Convert metadata dict to APIKey object."""
        # Validate and cast string fields
        if "name" not in api_data:
            raise ValueError("name field is required and must be a string")
        api_data["name"] = str(api_data["name"])

        if "provider" not in api_data:
            raise ValueError("provider field is required and must be a string")
        if "description" in api_data and api_data["description"] is not None:
            # if not :
            #     raise ValueError("description field must be a string or None")
            api_data["description"] = str(api_data["description"])
        else:
            api_data["description"] = None

        if "tags" not in api_data:
            api_data["tags"] = []
        # elif not isinstance(api_data['tags'], list):
        #     raise ValueError("tags field must be a list")
        else:
            # Ensure all tags are strings
            api_data["tags"] = [str(tag) for tag in api_data["tags"]]

        # Handle both string and datetime objects for timestamp fields
        created_at = api_data.get("created_at")
        if isinstance(created_at, str):
            api_data["created_at"] = datetime.fromisoformat(created_at)
        elif isinstance(created_at, datetime):
            api_data["created_at"] = created_at
        else:
            raise ValueError(f"Invalid type for created_at: {type(created_at)}")

        updated_at = api_data.get("updated_at")
        if isinstance(updated_at, str):
            api_data["updated_at"] = datetime.fromisoformat(updated_at)
        elif isinstance(updated_at, datetime):
            api_data["updated_at"] = updated_at
        else:
            raise ValueError(f"Invalid type for updated_at: {type(updated_at)}")

        return APIKey(**api_data)

    def __init__(self, metadata_path: Optional[Path] = None):
        """
        Initialize metadata manager.

        Args:
            metadata_path: Path to metadata JSON file
        """
        self.metadata_path = metadata_path or Path.cwd() / "keys_metadata.json"
        self._ensure_metadata_file()

    def _ensure_metadata_file(self):
        """Create metadata file if it doesn't exist."""
        if not self.metadata_path.exists():
            self.metadata_path.write_text("{}")
            # Set secure permissions
            self.metadata_path.chmod(0o600)

    def save_metadata(self, api_key: APIKey):
        """
        Save or update metadata for an API key.

        Preserves the original created_at timestamp when updating an existing key.
        Only updates the updated_at timestamp to the current time.

        Args:
            api_key: APIKey object to save
        """
        metadata = self._load_all_metadata()
        existing_metadata = metadata.get(api_key.name)

        api_dict = api_key.model_dump(mode="python")

        # Convert datetime objects to strings for JSON serialization
        if existing_metadata:
            # Updating existing key: preserve original created_at
            ## fixme pylance error
            api_dict["created_at"] = existing_metadata["created_at"]
            # Update updated_at to current time
            api_dict["updated_at"] = datetime.now().isoformat()
        else:
            # Creating new key: both timestamps set to current time (from api_key object)
            api_dict["created_at"] = api_dict["created_at"].isoformat()
            api_dict["updated_at"] = api_dict["updated_at"].isoformat()

        metadata[api_key.name] = api_dict  # type: ignore
        self._write_metadata(metadata)

    def get_metadata(self, name: str) -> Optional[APIKey]:
        """
        Retrieve metadata for a key.

        Args:
            name: Key identifier

        Returns:
            APIKey object or None
        """
        metadata = self._load_all_metadata()
        data = metadata.get(name)

        if not data:
            return None

        return self._metadata_to_api_key(data)

    def delete_metadata(self, name: str) -> bool:
        """
        Delete metadata for a key.

        Args:
            name: Key identifier

        Returns:
            True if deleted
        """
        metadata = self._load_all_metadata()

        if name not in metadata:
            return False

        del metadata[name]
        self._write_metadata(metadata)
        return True

    def list_all_metadata(self) -> Dict[str, APIKey]:
        """
        Get all metadata.

        Returns:
            Dictionary of APIKey objects
        """
        metadata = self._load_all_metadata()
        return {name: self._metadata_to_api_key(data) for name, data in metadata.items()}

    def filter_by_service(self, provider: str) -> List[APIKey]:
        """
        Filter keys by service.

        Args:
            service: Service type

        Returns:
            List of APIKey objects
        """
        all_metadata = self.list_all_metadata()
        return [key for key in all_metadata.values() if key.provider.lower() == provider.lower()]

    def filter_by_tags(self, tags: List[str]) -> List[APIKey]:
        """
        Filter keys by tags.

        Args:
            tags: List of tags to match

        Returns:
            List of APIKey objects
        """
        all_metadata = self.list_all_metadata()
        tags_lower = [t.lower() for t in tags]

        return [
            key
            for key in all_metadata.values()
            if any(tag.lower() in tags_lower for tag in key.tags)
        ]

    def search(self, query: str) -> List[APIKey]:
        """
        Search keys by name or description.

        Args:
            query: Search query

        Returns:
            List of matching APIKey objects
        """
        all_metadata = self.list_all_metadata()
        query_lower = query.lower()

        return [
            key
            for key in all_metadata.values()
            if query_lower in key.name.lower()
            or (key.description and query_lower in key.description.lower())
        ]

    def _load_all_metadata(self) -> Dict[str, MetadataDict]:
        """Load all metadata from file."""
        try:
            data = json.loads(self.metadata_path.read_text())
            return data if isinstance(data, dict) else {}  # type: ignore
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _write_metadata(self, metadata: Dict[str, MetadataDict]) -> None:
        """Write metadata to file."""
        self.metadata_path.write_text(json.dumps(metadata, indent=2, default=str))
        self.metadata_path.chmod(0o600)
