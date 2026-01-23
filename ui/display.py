"""Rich display utilities."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from typing import Any, Dict, List, Optional

console = Console()


def print_success(message: str, title: str = "Success"):
    """Print a success message in a panel."""
    console.print(Panel.fit(
        f"[bold green]✓ {message}[/bold green]",
        title=title,
        border_style="green"
    ))


def print_error(message: str, title: str = "Error"):
    """Print an error message in a panel."""
    console.print(Panel.fit(
        f"[bold red]✗ {message}[/bold red]",
        title=title,
        border_style="red"
    ))


def print_warning(message: str, title: str = "Warning"):
    """Print a warning message in a panel."""
    console.print(Panel.fit(
        f"[bold yellow]⚠ {message}[/bold yellow]",
        title=title,
        border_style="yellow"
    ))


def print_info(message: str, title: str = "Info"):
    """Print an info message in a panel."""
    console.print(Panel.fit(
        f"[bold cyan]ℹ {message}[/bold cyan]",
        title=title,
        border_style="cyan"
    ))


def create_key_table(keys: List[Dict[str, Any]]) -> Table:
    """
    Create a Rich table for displaying keys.

    Args:
        keys: List of key dictionaries

    Returns:
        Rich Table object
    """
    table = Table(title="API Keys")
    table.add_column("Name", style="cyan", no_wrap=False)
    table.add_column("Service", style="magenta")
    table.add_column("Description", style="white")
    table.add_column("Tags", style="green")
    table.add_column("Created", style="dim")

    for key in keys:
        table.add_row(
            key.get("name", "N/A"),
            key.get("service", "N/A"),
            key.get("description", "N/A") or "N/A",
            ", ".join(key.get("tags", [])) or "None",
            key.get("created_at", "N/A")
        )

    return table


def create_metadata_table(metadata: Dict[str, Any]) -> Table:
    """
    Create a Rich table for displaying metadata.

    Args:
        metadata: Dictionary of metadata

    Returns:
        Rich Table object
    """
    table = Table(show_header=False, box=None)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")

    for key, value in metadata.items():
        if isinstance(value, list):
            value = ", ".join(value) if value else "None"
        table.add_row(key.replace("_", " ").title(), str(value) or "N/A")

    return table


def print_key_details(key: Dict[str, Any], show_value: bool = False):
    """
    Print detailed information about a single key.

    Args:
        key: Key dictionary
        show_value: Whether to show the actual key value
    """
    metadata_table = create_metadata_table(key)

    if show_value and "value" in key:
        value_panel = Panel(
            f"[white]{key['value']}[/white]",
            title="[bold yellow]API Key Value[/bold yellow]",
            border_style="yellow"
        )
        console.print(value_panel)
        console.print()

    console.print(Panel(
        metadata_table,
        title="[bold cyan]Key Details[/bold cyan]",
        border_style="cyan"
    ))


def print_progress(message: str):
    """Print a progress message."""
    console.print(f"[dim]⏳ {message}...[/dim]")


def print_step(step: int, total: int, message: str):
    """Print a step message."""
    console.print(f"[dim][{step}/{total}] {message}[/dim]")


def confirm_action(prompt: str, default: bool = False) -> bool:
    """
    Ask for user confirmation.

    Args:
        prompt: Confirmation prompt message
        default: Default value if user just presses Enter

    Returns:
        True if user confirms
    """
    from questionary import confirm as qconfirm

    return qconfirm.question(prompt, default=default).ask()
