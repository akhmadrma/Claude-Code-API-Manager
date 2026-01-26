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
                    # TODO : Add validation
                ).ask()
                if not name:
                    console.print("[red]Cancelled[/red]")
                    raise typer.Exit()

        # Check if key exists
        if not key_manager.key_exists(name):
            console.print(f"[red]Key '{name}' not found[/red]")
            raise typer.Exit(1)

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


if __name__ == "__main__":
    typer.run(delete_cmd)
