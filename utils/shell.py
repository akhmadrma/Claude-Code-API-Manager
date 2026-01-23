"""Shell command generators for environment variable export."""

from typing import Dict, List


class ShellExporter:
    """Generate shell-specific export commands."""

    FORMATS = {
        "bash": 'export {name}="{value}"',
        "zsh": 'export {name}="{value}"',
        "fish": 'set -gx {name} "{value}"',
    }

    @classmethod
    def export_single(cls, name: str, value: str, shell_format: str = "bash") -> str:
        """
        Generate export command for a single key.

        Args:
            name: Environment variable name
            value: Environment variable value
            shell_format: Shell format (bash/zsh/fish)

        Returns:
            Export command string
        """
        format_str = cls.FORMATS.get(shell_format.lower(), cls.FORMATS["bash"])
        return format_str.format(name=name, value=value)

    @classmethod
    def export_multiple(cls, keys: Dict[str, str], shell_format: str = "bash") -> str:
        """
        Generate export commands for multiple keys.

        Args:
            keys: Dictionary of key names and values
            shell_format: Shell format (bash/zsh/fish)

        Returns:
            Multi-line export commands
        """
        return "\n".join(
            cls.export_single(name, value, shell_format)
            for name, value in keys.items()
        )

    @classmethod
    def get_eval_prefix(cls, shell_format: str = "bash") -> str:
        """
        Get eval prefix for shell integration.

        Args:
            shell_format: Shell format (bash/zsh/fish)

        Returns:
            Eval command prefix
        """
        if shell_format.lower() == "fish":
            return ""
        return "eval $("
