import json
from typing import Optional

from questionary import select, text, Choice
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import typer

from core.key_manager import KeyManager
from core.metadata_manager import MetadataManager
from core.export_manager import ExportClaudeSettings
from core.models import APIKey
from utils.helpers import mask_key

console = Console()


def use_cmd(
    name: Optional[str] = typer.Option(None, "--name", help="Name of the key to use"),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", help="Interactive mode (default: True)"
    ),
    merge: bool = typer.Option(
        False, "--merge", help="Merge with existing settings instead of replacing (default: False)"
    ),
    preview: bool = typer.Option(
        False, "--preview/--no-preview", help="Preview changes without writing (default: False)"
    ),
):
    """
    Use a stored API key to generate a valid Claude Code settings.json file.

    Requires the name of the key to use. If not provided, will prompt for selection in interactive mode.

    If the key is already active, will do nothing. Otherwise, will deactivate the previous key and activate the selected key.

    After activation, will export the settings to the correct location.

    :param name: Name of the key to use
    :param interactive: Interactive mode (default: True)
    :param merge: Merge with existing settings instead of replacing
    :param preview: Preview changes without writing to disk
    :raises typer.Exit: If key not found or cancelled
    :raises Exception: If failed to export settings
    """
    try:
        metadata_manager = MetadataManager()
        key_manager = KeyManager()
        export_manager = ExportClaudeSettings()

        # Initialize variables with safe defaults (defensive programming)
        key_metadata: Optional[APIKey] = None
        key_value: Optional[str] = None

        # Path 1: Name provided directly
        if name:
            key_metadata = metadata_manager.get_metadata(name)
            key_value = key_manager.get_key_value(name)

            if not key_metadata or not key_value:
                console.print("[red]Key not found.[/red]")
                return

        # Path 2: Interactive mode
        elif interactive:
            all_metadata = metadata_manager.list_all_metadata()
            if not all_metadata:
                console.print(
                    "[yellow]No API keys found. Use 'cloudcode add' to add your first key.[/yellow]"
                )
                return

            # Create beautiful table
            table = Table(title="API Keys")
            table.add_column("Name", style="cyan", no_wrap=False)
            table.add_column("Service", style="magenta")
            table.add_column("API_KEY", style="white")
            table.add_column("Description", style="white")
            table.add_column("Tags", style="white")
            table.add_column("Status", style="white")
            table.add_column("Created", style="dim")

            for key in all_metadata.values():
                # Mask the key
                masked_key = mask_key(str(key_manager.get_key_value(key.name)))

                if key.status == "active":
                    key.status = f"[green]active[/green]"

                table.add_row(
                    key.name,
                    key.provider,
                    masked_key,
                    key.description or "N/A",
                    ", ".join(key.tags) if key.tags else "N/A",
                    key.status,
                    key.created_at.strftime("%Y-%m-%d") if key.created_at else "N/A",
                )
                continue

            console.print(table)
            console.print(f"\n[dim]Showing {len(all_metadata.values())} key(s)[/dim]")

            # Interactive mode with beautiful prompts
            console.print(Panel.fit("[bold cyan]Use Key[/bold cyan]"))

            # Prompt for key name
            name = text(
                "Enter the name of the key to use:",
                instruction="(e.g., OPENAI_API_KEY)",
                validate=_validate_name,
            ).ask()
            if not name:
                console.print("[red]Cancelled[/red]")
                return

            # Fetch key details for interactive selection
            key_metadata = metadata_manager.get_metadata(name)
            key_value = key_manager.get_key_value(name)

            if not key_metadata or not key_value:
                console.print("[red]Key not found.[/red]")
                return

        # Safety check: Ensure we have the required data
        if not key_value or not key_metadata:
            console.print("[red]Key details not available. Please try again.[/red]")
            return

        # At this point, name is guaranteed to be non-None due to the checks above
        assert name is not None, "Name should be non-None after validation checks"

        # Interactive merge/overwrite prompt (only in interactive mode)
        # Prompt when: settings.json exists AND no --merge flag provided
        interactive_preview: bool = False  # Track if preview was triggered interactively
        if (
            interactive
            and not merge
            and export_manager.settings_path.exists()
        ):
            choice = select(
                "Existing settings.json detected. How would you like to proceed?",
                choices=[
                    Choice("Merge - Preserve existing settings", "merge"),
                    Choice("Overwrite - Replace all settings", "overwrite"),
                    Choice("Preview - Show changes first", "preview"),
                    Choice("Cancel - Exit without changes", "cancel"),
                ],
            ).ask()

            if choice == "cancel":
                console.print("[yellow]Cancelled.[/yellow]")
                return
            elif choice == "merge":
                merge = True
            elif choice == "preview":
                preview = True
                interactive_preview = True  # Mark as interactive preview
            # else: overwrite (default, merge=False)

        # Export settings with merge/preview support
        result = export_manager.export_settings(
            key_value, key_metadata.provider, merge=merge, preview=preview
        )

        # Handle preview mode BEFORE making any metadata changes
        if preview:
            # Show preview of changes (BEFORE making any actual changes)
            from rich.json import JSON

            console.print(Panel.fit("[bold cyan]Settings Preview[/bold cyan]"))

            # Show what metadata changes would occur
            try:
                previous_active_key = key_manager.get_active_key()
                if previous_active_key.name != name:
                    console.print(
                        f"[dim]Would deactivate: [cyan]{previous_active_key.name}[/cyan][/dim]"
                    )
                    console.print(f"[dim]Would activate: [cyan]{name}[/cyan][/dim]\n")
                else:
                    console.print(f"[dim]Key [cyan]{name}[/cyan] is already active.[/dim]\n")
            except KeyError:
                console.print(
                    f"[dim]Would activate: [cyan]{name}[/cyan] (no currently active key)\n"
                )

            if isinstance(result, dict):
                if result["before"] is None:
                    console.print(
                        "[yellow]No existing settings.json file found.[/yellow]"
                    )
                    console.print("\n[bold]New settings to be created:[/bold]")
                    console.print(JSON(json.dumps(result["after"], indent=2)))
                else:
                    changes = result["changes"]

                    if changes["type"] == "update":
                        if changes["added"]:
                            console.print(
                                "\n[bold green]Fields to be added:[/bold green]"
                            )
                            console.print(JSON(json.dumps(changes["added"], indent=2)))

                        if changes["modified"]:
                            console.print(
                                "\n[bold yellow]Fields to be modified:[/bold yellow]"
                            )
                            for key_key, diff in changes["modified"].items():
                                console.print(f"  [cyan]{key_key}[/cyan]:")
                                console.print(f"    [red]- {diff['old']}[/red]")
                                console.print(f"    [green]+ {diff['new']}[/green]")

                        if changes["removed"]:
                            console.print(
                                "\n[bold red]Fields to be removed:[/bold red]"
                            )
                            console.print(
                                JSON(json.dumps(changes["removed"], indent=2))
                            )

                        if (
                            not changes["added"]
                            and not changes["modified"]
                            and not changes["removed"]
                        ):
                            console.print("[dim]No changes detected.[/dim]")

                    console.print("\n[bold]Full resulting settings:[/bold]")
                    console.print(JSON(json.dumps(result["after"], indent=2)))

            console.print("\n[dim]Preview mode - no files were modified.[/dim]")

            # If preview was triggered interactively, ask for confirmation
            if interactive_preview:
                confirm_choice = select(
                    "What would you like to do?",
                    choices=[
                        Choice("Apply changes (merge mode)", "merge"),
                        Choice("Apply changes (overwrite mode)", "overwrite"),
                        Choice("Cancel - Exit without changes", "cancel"),
                    ],
                ).ask()

                if confirm_choice == "cancel":
                    console.print("[yellow]Cancelled.[/yellow]")
                    return
                elif confirm_choice == "merge":
                    merge = True
                # else: overwrite (default, merge=False)

                # Continue with export (don't return)
                # Need to call export_settings again with the correct merge flag
                result = export_manager.export_settings(
                    key_value, key_metadata.provider, merge=merge, preview=False
                )
            else:
                # CLI --preview flag: show message and exit
                console.print(
                    "[dim]Run again without --preview to apply changes.[/dim]"
                )
                return

        # Not preview mode - apply metadata changes
        try:
            # get active key
            previous_active_key = key_manager.get_active_key()
            if previous_active_key.name == name:
                console.print("[red]Key is already active.[/red]")
                return
            # deactife previous key
            previous_active_key = key_manager.set_inactive_key(previous_active_key.name)
            metadata_manager.save_metadata(previous_active_key)

        except KeyError:
            previous_active_key = None

        # actibate new key (moved outside except block)
        current_active_key = key_manager.set_active_key(name)
        metadata_manager.save_metadata(current_active_key)

        if not result:
            console.print("[red]Failed to export settings.[/red]")
            return

        console.print(f"[green]Successfully activated key {name}[/green]")

    except Exception as e:
        print(f"Error: {e}")


def _validate_name(value: str):
    """
    Validate API key name for questionary prompt.

    Args:
        value: API key name to validate

    Returns:
        True if valid, error message string if invalid
    """
    # Check for whitespace characters
    if " " in value or "\t" in value or "\n" in value:
        return "Key name cannot contain spaces or whitespace characters"

    # Check if key exists
    key_manager = KeyManager()
    if not key_manager.key_exists(value):
        return f"Key '{value}' does not exist"

    return True
