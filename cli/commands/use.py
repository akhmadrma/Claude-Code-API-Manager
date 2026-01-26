from typing import Optional

from questionary import text
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import typer

from core.key_manager import KeyManager
from core.metadata_manager import MetadataManager
from core.export_manager import ExportClaudeSettings
from utils.helpers import mask_key

console = Console()


def use_cmd(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Name of the key to use"),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", "-i/-I", help="Interactive mode (default: True)"
    ),
):
    """
    Use a stored API key to generate a valid Claude Code settings.json file.

    Requires the name of the key to use. If not provided, will prompt for selection in interactive mode.

    If the key is already active, will do nothing. Otherwise, will deactivate the previous key and activate the selected key.

    After activation, will export the settings to the correct location.

    :param name: Name of the key to use
    :param interactive: Interactive mode (default: True)
    :raises typer.Exit: If key not found or cancelled
    :raises Exception: If failed to export settings
    """
    try:
        metadata_manager = MetadataManager()
        key_manager = KeyManager()
        export_manager = ExportClaudeSettings()

        if interactive:
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

            console.print(table)
            console.print(f"\n[dim]Showing {len(all_metadata.values())} key(s)[/dim]")

            # Interactive mode with beautiful prompts
            console.print(Panel.fit("[bold cyan]Use Key[/bold cyan]"))
            

            # Prompt for key name
            name = text(
                "Enter the name of the key to use:",
                instruction="(e.g., OPENAI_API_KEY)",
                # TODO : Add validation
            ).ask()
            if not name:
                console.print("[red]Cancelled[/red]")
                return

        if name:
            key_metadata = metadata_manager.get_metadata(name)
            key_value: str = key_manager.get_key_value(name)

            if not key_metadata or not key_value:
                console.print("[red]Key not found.[/red]")
                return

            # get active key
            previous_active_key = key_manager.get_active_key()
            if previous_active_key.name == name:
                console.print("[red]Keys is already active.[/red]")
                return
            # deactife previous key
            previous_active_key = key_manager.set_inactive_key(previous_active_key.name)
            metadata_manager.save_metadata (previous_active_key)

            # actibate new key
            current_active_key = key_manager.set_active_key(name)
            metadata_manager.save_metadata (current_active_key)

            exported_settings = export_manager.export_settings(key_value,key_metadata.provider)
            if not exported_settings:
                console.print("[red]Failed to export settings.[/red]")
                return
            console.print(f'[green]Successfully activated key {name}[/green]')

        else:
            console.print("[red]Key name not provided.[/red]")
            return

    except Exception as e:
        print(f"Error: {e}")
