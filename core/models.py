"""Core data models for API key management."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class APIKey(BaseModel):
    """API Key model with metadata."""

    name: str = Field(..., description="Unique identifier for the API key")
    service: str = Field(..., description="Service type (OpenAI, GitHub, AWS, etc.)")
    description: Optional[str] = Field(None, description="User-defined purpose")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Validate that name is not empty."""
        if not v.strip():
            raise ValueError("name cannot be empty")
        return v.strip()

    @field_validator("service")
    @classmethod
    def service_must_not_be_empty(cls, v: str) -> str:
        """Validate that service is not empty."""
        if not v.strip():
            raise ValueError("service cannot be empty")
        return v.strip()


class Settings(BaseModel):
    """Application settings model."""

    backup_location: str = Field(default="./backups", description="Backup directory path")
    default_services: List[str] = Field(
        default_factory=lambda: ["OpenAI", "GitHub", "AWS", "Google"],
        description="Default service types for autocomplete"
    )
    display_masked: bool = Field(default=True, description="Mask keys in display")
    auto_gitignore: bool = Field(default=True, description="Auto-add sensitive files to gitignore")
    shell_format: str = Field(default="bash", description="Shell export format (bash/zsh/fish)")

    @field_validator("shell_format")
    @classmethod
    def validate_shell_format(cls, v: str) -> str:
        """Validate shell format."""
        allowed = {"bash", "zsh", "fish"}
        v = v.lower()
        if v not in allowed:
            raise ValueError(f"shell_format must be one of {allowed}")
        return v


class BackupMetadata(BaseModel):
    """Backup file metadata."""

    filename: str = Field(..., description="Backup filename")
    created_at: datetime = Field(..., description="Backup creation timestamp")
    size_bytes: int = Field(..., description="Backup file size")
    encrypted: bool = Field(default=True, description="Whether backup is encrypted")
    key_count: int = Field(..., description="Number of keys in backup")
