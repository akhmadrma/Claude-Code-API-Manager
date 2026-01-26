from typing import Optional

from rich.console import Console
import typer

from core.key_manager import KeyManager
from core.metadata_manager import MetadataManager
from core.export_manager import ExportClaudeSettings

console = Console()


def use_cmd(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Name of the key to use"),
):
    print("Interactive key selection not yet implemented")
    try:
        metadata_manager = MetadataManager()
        key_manager = KeyManager()
        export_manager = ExportClaudeSettings()


        if name:
            key_metadata = metadata_manager.get_metadata(name)
            key_value: str = key_manager.get_key_value(name)
            
            if not key_metadata or not key_value:
                console.print("[red]Key not found.[/red]")
                return
            
            exported_settings = export_manager.export_settings(key_value,key_metadata.provider)
            console.print(f'[green]Successfully exported settings to {exported_settings}[/green]')

        else:
            console.print("[red]Key name not provided.[/red]")
            return

    except Exception as e:
        print(f"Error: {e}")
