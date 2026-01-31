"""Environment variable export functionality."""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from constans.providerModel import Model
from constans.providerUrl import Provider
from core.models import Environment, BaseURL

from .key_manager import KeyManager


class ExportClaudeSettings:
    """Export Claude settings to ~/.claude/settings.json with backup support."""

    def __init__(self, settings_path: Optional[Path] = None):
        """
        Initialize Claude settings exporter.

        Args:
            settings_path: Path to Claude settings file (defaults to ~/.claude/settings.json)
        """
        self.settings_path = (
            settings_path or Path.home() / os.getenv("DEFAULT_CLAUDE_DIR", ".claude") / "settings.json"
        )

    def export_settings(
        self,
        api_keys: str = "placeholder-api-key",
        provider: Provider = "anthropic",
        backup: bool = False,
        merge: bool = False,
        preview: bool = False,
    ) -> Union[Path, Dict[str, Any]]:
        """
        Export API keys to Claude settings file.

        Args:
            api_keys: Dictionary of API keys to export
            provider: API provider to use
            backup: Whether to backup existing settings before export
            merge: Whether to merge with existing settings instead of replacing
            preview: If True, return diff without writing to disk

        Returns:
            Path to the exported settings file, or dict with preview data if preview=True

        Raises:
            IOError: If export fails
        """
        # Ensure directory exists
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing settings if merge mode is enabled
        existing_settings = self._load_existing_settings() if merge else None

        # Prepare new settings data
        new_settings = self._prepare_settings(api_keys, provider)

        # Merge with existing settings if merge mode is enabled
        if merge and existing_settings:
            final_settings = self._deep_merge(existing_settings, new_settings)
        else:
            final_settings = new_settings

        # Generate preview if requested
        if preview:
            return self._generate_diff(existing_settings, final_settings)

        # Backup existing settings if requested and file exists
        if backup and self.settings_path.exists():
            self._backup_settings()

        # Write to file
        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(final_settings, f, indent=2)
            return self.settings_path
        except Exception as e:
            raise IOError(f"Failed to export Claude settings: {e}") from e

    def _backup_settings(self) -> Path:
        """
        Create backup of existing settings file.

        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = (
            self.settings_path.parent / f"{self.settings_path.stem}.backup.{timestamp}.json"
        )

        try:
            shutil.copy2(self.settings_path, backup_path)
            return backup_path
        except Exception as e:
            raise IOError(f"Failed to create backup: {e}") from e

    def _prepare_settings(self, api_keys: str, provider: Provider = "anthropic") -> Dict[str, Any]:
        """
        Prepare Claude settings structure.

        Args:
            api_keys: Dictionary of API keys

        Returns:
            Claude settings dictionary
        """
        # Create Environment object with the first API key as auth token
        # Use the first available key or a placeholder
        model = Model.create_provider_models(provider)
        base_url = BaseURL.create_for_provider(provider)
        env = Environment(
            anthropic_default_haiku_model=model.to_values()[0],
            anthropic_default_sonnet_model=model.to_values()[1],
            anthropic_default_opus_model=model.to_values()[2],
            anthropic_auth_token=api_keys or "placeholder-token",
            anthropic_base_url=base_url,
            api_timeout_ms=30000,
            claude_code_disable_nonessential_traffic=False,
        )

        # Create settings dictionary that matches the SettingsJSON structure
        settings_dict: object = {
            "env": {
                "ANTHROPIC_DEFAULT_HAIKU_MODEL": env.anthropic_default_haiku_model,
                "ANTHROPIC_DEFAULT_SONNET_MODEL": env.anthropic_default_sonnet_model,
                "ANTHROPIC_DEFAULT_OPUS_MODEL": env.anthropic_default_opus_model,
                "ANTHROPIC_AUTH_TOKEN": env.anthropic_auth_token,
                "ANTHROPIC_BASE_URL": base_url.to_values(),
                "API_TIMEOUT_MS": env.api_timeout_ms,
                "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": env.claude_code_disable_nonessential_traffic,
            },
            "alwaysThinkingEnabled": True,
        }

        return settings_dict

    def _load_existing_settings(self) -> Optional[Dict[str, Any]]:
        """
        Load existing settings from file.

        Returns:
            Existing settings dictionary, or None if file doesn't exist

        Raises:
            IOError: If file exists but contains invalid JSON
        """
        if not self.settings_path.exists():
            return None

        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise IOError(
                f"Existing settings file contains invalid JSON: {e}. "
                f"Please fix or remove {self.settings_path} before proceeding."
            ) from e
        except Exception as e:
            raise IOError(f"Failed to load existing settings: {e}") from e

    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge two dictionaries.

        Values from 'update' take precedence over values from 'base'.
        Nested dictionaries are merged recursively.

        Args:
            base: Base dictionary (existing settings)
            update: Update dictionary (new settings to apply)

        Returns:
            Merged dictionary
        """
        result = base.copy()

        for key, value in update.items():
            # If both values are dicts, merge them recursively
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                # Otherwise, the new value wins (replace or add)
                result[key] = value

        return result

    def _generate_diff(
        self, before: Optional[Dict[str, Any]], after: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a diff showing changes between before and after states.

        Args:
            before: Settings before changes (may be None)
            after: Settings after changes

        Returns:
            Dictionary with 'before', 'after', and 'changes' keys
        """
        changes: Dict[str, Any] = {}

        if before is None:
            # No existing file, all changes are additions
            changes = {"type": "create", "added": after}
        else:
            # Calculate what changed
            added: Dict[str, Any] = {}
            modified: Dict[str, Any] = {}
            removed: Dict[str, Any] = {}

            # Find added and modified keys
            all_keys = set(before.keys()) | set(after.keys())

            for key in all_keys:
                if key not in before:
                    added[key] = after[key]
                elif key not in after:
                    removed[key] = before[key]
                elif before[key] != after[key]:
                    modified[key] = {"old": before[key], "new": after[key]}

            changes = {
                "type": "update",
                "added": added,
                "modified": modified,
                "removed": removed,
            }

        return {
            "before": before,
            "after": after,
            "changes": changes,
        }

    def list_backups(self) -> List[Path]:
        """
        List all backup files.

        Returns:
            List of backup file paths sorted by modification time (newest first)
        """
        backup_pattern = f"{self.settings_path.stem}.backup.*.json"
        backups = list(self.settings_path.parent.glob(backup_pattern))

        # Sort by modification time, newest first
        backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return backups

    def cleanup_old_backups(self, keep: int = 5) -> int:
        """
        Remove old backup files, keeping the most recent ones.

        Args:
            keep: Number of backups to keep

        Returns:
            Number of backups removed
        """
        backups = self.list_backups()
        to_remove = backups[keep:] if len(backups) > keep else []

        for backup in to_remove:
            try:
                backup.unlink()
            except Exception:
                pass

        return len(to_remove)


class ExportManager:
    """Manage environment variable exports with file support and backup."""

    def __init__(
        self, key_manager: KeyManager, export_dir: Optional[Path] = None, shell_format: str = "bash"
    ):
        """
        Initialize export manager.

        Args:
            key_manager: KeyManager instance
            export_dir: Directory for export files (defaults to ./exports)
            shell_format: Shell format (bash, zsh, fish)
        """
        self.key_manager = key_manager
        self.export_dir = export_dir or Path.cwd() / "exports"
        self.shell_format = shell_format.lower()

    def export_single(self, key_name: str, export_name: Optional[str] = None) -> str:
        """
        Generate export command for a single key.

        Args:
            key_name: Name of key to export
            export_name: Optional environment variable name (defaults to key_name)

        Returns:
            Export command string
        """
        value = self.key_manager.get_key_value(key_name)
        export_name = export_name or key_name.upper()

        if self.shell_format in ("bash", "zsh"):
            return f"export {export_name}='{value}'"
        elif self.shell_format == "fish":
            return f"set -gx {export_name} '{value}'"
        else:
            raise ValueError(f"Unsupported shell format: {self.shell_format}")

    def export_multiple(self, key_names: List[str], prefix: str = "") -> List[str]:
        """
        Generate export commands for multiple keys.

        Args:
            key_names: List of key names to export
            prefix: Optional prefix for environment variable names

        Returns:
            List of export command strings
        """
        commands: List[str] = []
        for name in key_names:
            env_name = prefix + name.upper() if prefix else name.upper()
            commands.append(self.export_single(name, env_name))
        return commands

    def export_all(self, prefix: str = "") -> List[str]:
        """
        Generate export commands for all keys.

        Args:
            prefix: Optional prefix for environment variable names

        Returns:
            List of export command strings
        """
        all_keys = self.key_manager.list_all_keys()
        return self.export_multiple(list(all_keys.keys()), prefix)

    def export_by_service(self, service: str, prefix: str = "") -> List[str]:
        """
        Generate export commands for keys of a specific service.

        Args:
            service: Service type to filter by
            prefix: Optional prefix for environment variable names

        Returns:
            List of export command strings
        """
        # This would use MetadataManager to filter by service
        # For now, export all keys
        return self.export_all(prefix)

    def generate_eval_script(self, commands: List[str]) -> str:
        """
        Generate eval-compatible script.

        Args:
            commands: List of export commands

        Returns:
            Script string suitable for eval
        """
        return "\n".join(commands)

    def print_exports(
        self,
        key_names: Optional[List[str]] = None,
        service: Optional[str] = None,
        all_keys: bool = False,
    ):
        """
        Print export commands to stdout.

        Args:
            key_names: Specific keys to export
            service: Export by service
            all_keys: Export all keys
        """
        commands: List[str] = []

        if all_keys:
            commands = self.export_all()
        elif service:
            commands = self.export_by_service(service)
        elif key_names:
            commands = self.export_multiple(key_names)
        else:
            return

        for cmd in commands:
            print(cmd)

    def export_to_file(self, commands: List[str], filename: str, backup: bool = True) -> Path:
        """
        Export commands to a file with optional backup.

        Args:
            commands: List of export commands
            filename: Name of the export file
            backup: Whether to backup existing file

        Returns:
            Path to the exported file

        Raises:
            IOError: If export fails
        """
        # Ensure export directory exists
        self.export_dir.mkdir(parents=True, exist_ok=True)

        export_path = self.export_dir / filename

        # Backup existing file if requested
        if backup and export_path.exists():
            self._backup_export_file(export_path)

        # Write commands to file
        try:
            with open(export_path, "w", encoding="utf-8") as f:
                f.write(self.generate_eval_script(commands))
            return export_path
        except Exception as e:
            raise IOError(f"Failed to export to file: {e}") from e

    def export_all_to_file(
        self, filename: Optional[str] = None, prefix: str = "", backup: bool = True
    ) -> Path:
        """
        Export all keys to a file.

        Args:
            filename: Name of the export file (defaults to export_<shell>.sh)
            prefix: Optional prefix for environment variable names
            backup: Whether to backup existing file

        Returns:
            Path to the exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{self.shell_format}_{timestamp}.sh"

        commands = self.export_all(prefix)
        return self.export_to_file(commands, filename, backup)

    def _backup_export_file(self, file_path: Path) -> Path:
        """
        Create backup of existing export file.

        Args:
            file_path: Path to file to backup

        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.export_dir / f"{file_path.stem}.backup.{timestamp}{file_path.suffix}"

        try:
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            raise IOError(f"Failed to create backup: {e}") from e

    def list_export_backups(self, filename: Optional[str] = None) -> List[Path]:
        """
        List backup files for exports.

        Args:
            filename: Specific filename to filter backups for

        Returns:
            List of backup file paths sorted by modification time (newest first)
        """
        if filename:
            backup_pattern = f"{Path(filename).stem}.backup.*"
        else:
            backup_pattern = "*.backup.*"

        backups = list(self.export_dir.glob(backup_pattern))

        # Sort by modification time, newest first
        backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return backups

    def cleanup_old_exports(self, keep: int = 5) -> int:
        """
        Remove old export and backup files, keeping the most recent ones.

        Args:
            keep: Number of recent files to keep

        Returns:
            Number of files removed
        """
        # Get all export files
        all_exports = list(self.export_dir.glob("export_*.sh"))
        all_exports.extend(self.list_export_backups())

        # Sort by modification time, newest first
        all_exports.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        # Remove files beyond keep limit
        to_remove = all_exports[keep:] if len(all_exports) > keep else []

        for file_path in to_remove:
            try:
                file_path.unlink()
            except Exception:
                pass

        return len(to_remove)

    def get_export_dir(self) -> Path:
        """
        Get the export directory path.

        Returns:
            Path to export directory
        """
        return self.export_dir
