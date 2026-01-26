"""Delete API key command."""

import typer
from questionary import text
from rich.console import Console
from rich.panel import Panel

from core.key_manager import KeyManager
from core.metadata_manager import MetadataManager

console = Console()


def delete_cmd(
    name: str = typer.Option(None, "--name", help="Key name/identifier"),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", help="Interactive mode (default: True)"
    ),
):
    """
    Delete an API key from storage.

    If run interactively (default), prompts for key name if not provided.
    """
    try:
        key_manager = KeyManager()
        metadata_manager = MetadataManager()

        if interactive:
            # Interactive mode with beautiful prompts
            console.print(Panel.fit("[bold red]Delete API Key[/bold red]"))

            # Prompt for key name
            if not name:
                name = text(
                    "Enter the name of the key to delete:",
                    instruction="(e.g., OPENAI_API_KEY)",
                    validate=_validate_key_name,
                ).ask()
                if not name:
                    console.print("[red]Cancelled[/red]")
                    raise typer.Exit()

        # Delete key
        if key_manager.delete_key(name):
            # Delete associated metadata
            metadata_manager.delete_metadata(name)
            console.print(f"[green]Key '{name}' deleted successfully[/green]")
        else:
            console.print(f"[red]Failed to delete key '{name}'[/red]")
            raise typer.Exit(1)

    except typer.Exit:
        # Re-raise typer.Exit exceptions
        raise
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1)


def _validate_key_name(value: str) -> bool:

    """
    Validate key name by checking if it exists in storage.

    Args:
        value: The key name to validate

    Returns:
        True if the key exists, False otherwise
    """
    key_manager = KeyManager()
    try:
        key_manager.key_exists(value)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    typer.run(delete_cmd)
