"""List API keys command."""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table

from core.metadata_manager import MetadataManager
from core.key_manager import KeyManager

console = Console()


def list_cmd(
    provider: Optional[str] = typer.Option(None, "--service", "-s", help="Filter by service"),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag"),
    search: Optional[str] = typer.Option(None, "--search", help="Search in name/description"),
):
    """
    List all stored API keys with optional filtering.

    Keys are displayed in a formatted table with masked values.
    """

    try:
        metadata_manager = MetadataManager()
        key_manager = KeyManager()

        # Get all metadata
        all_metadata = metadata_manager.list_all_metadata()

        if not all_metadata:
            console.print(
                "[yellow]No API keys found. Use 'cloudcode add' to add your first key.[/yellow]"
            )
            return

        # Apply filters
        filtered_keys = list(all_metadata.values())

        if provider:
            filtered_keys = [k for k in filtered_keys if k.provider.lower() == provider.lower()]

        if tag:
            filtered_keys = [k for k in filtered_keys if tag.lower() in [t.lower() for t in k.tags]]

        if search:
            search_lower = search.lower()
            filtered_keys = [
                k
                for k in filtered_keys
                if search_lower in k.name.lower()
                or (k.description and search_lower in k.description.lower())
            ]

        if not filtered_keys:
            console.print("[yellow]No keys match the specified filters.[/yellow]")
            return

        # Create beautiful table
        table = Table(title="API Keys")
        table.add_column("Name", style="cyan", no_wrap=False)
        table.add_column("Service", style="magenta")
        table.add_column("API_KEY", style="white")
        table.add_column("Description", style="white")
        table.add_column("Tags", style="green")
        table.add_column("Created", style="dim")

        for key in filtered_keys:
            # Mask the key
            masked_key = mask_key(str(key_manager.get_key_value(key.name)))

            table.add_row(
                key.name,
                key.provider,
                masked_key,
                key.description or "N/A",
                ", ".join(key.tags) if key.tags else "None",
                key.created_at.strftime("%Y-%m-%d") if key.created_at else "N/A",
            )

        console.print(table)
        console.print(f"\n[dim]Showing {len(filtered_keys)} key(s)[/dim]")

    except Exception as e:
        console.print(f"[red]Error listing keys: {e}[/red]")
        raise typer.Exit(1)


def mask_key(name: str, visible_chars: int = 4) -> str:
    """
    Mask key for display (only show last few characters).

    Args:
        name: Key name to mask
        visible_chars: Number of characters to show at the end

    Returns:
        Masked key name
    """
    if len(name) <= visible_chars:
        return "*" * len(name)

    return "*" * (len(name) - visible_chars) + name[-visible_chars:]


if __name__ == "__main__":
    typer.run(list_cmd)
