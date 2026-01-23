"""Environment variable export functionality."""

from typing import Dict, List, Optional
from .key_manager import KeyManager


class ExportManager:
    """Manage environment variable exports."""

    def __init__(self, key_manager: KeyManager, shell_format: str = "bash"):
        """
        Initialize export manager.

        Args:
            key_manager: KeyManager instance
            shell_format: Shell format (bash, zsh, fish)
        """
        self.key_manager = key_manager
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
        commands = []
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

    def print_exports(self, key_names: Optional[List[str]] = None,
                     service: Optional[str] = None, all_keys: bool = False):
        """
        Print export commands to stdout.

        Args:
            key_names: Specific keys to export
            service: Export by service
            all_keys: Export all keys
        """
        commands = []

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
