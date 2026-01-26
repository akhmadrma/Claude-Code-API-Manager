"""Add new API key command."""

import typer
from questionary import password, text, select
from rich.console import Console
from rich.panel import Panel

from constans.providers import PROVIDERS
from core.key_manager import KeyManager
from core.metadata_manager import MetadataManager
from core.validators import ValidationError

console = Console()


def add_cmd(
    name: str = typer.Option(None, "--name", "-n", help="Key name/identifier"),
    provider: str = typer.Option(None, "--provider", "-s", help="provider type"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", "-i/-I",
                                     help="Interactive mode (default: True)"),
) :
    """
    Add a new API key to storage.

    If run interactively (default), prompts for all information.
    Otherwise, requires name and provider as arguments.
    """
    try:
        key_manager = KeyManager()
        metadata_manager = MetadataManager()

        if interactive:
            # Interactive mode with beautiful prompts
            console.print(Panel.fit("[bold cyan]Add New API Key[/bold cyan]"))

            # Prompt for key name
            # TODO : Add validation for spacing, .env cannot have spaces
            if not name:
                name = text(
                    "Enter a name for this key:",
                    instruction="(e.g., OPENAI_API_KEY)",
                    # TODO : Add validation
                ).ask()
                if not name:
                    console.print("[red]Cancelled[/red]")
                    raise typer.Exit()

            # Check if key already exists
            if key_manager.key_exists(name):
                console.print(f"[red]Key '{name}' already exists[/red]")
                raise typer.Exit(1)

            # Prompt for provider type
            if not provider:
                providers = PROVIDERS
                provider = select(
                    "Select provider type:",
                    choices=providers
                ).ask()

                if not provider:
                    console.print("[red]Cancelled[/red]")
                    raise typer.Exit()

            # Prompt for API key value (masked)
            key_value = password(
                "Enter the API key value:",
                instruction="(input will be hidden)"
            ).ask()

            if not key_value:
                console.print("[red]API key value is required[/red]")
                raise typer.Exit(1)

            # Prompt for description (optional)
            description = text(
                "Enter a description (optional):",
                default=""
            ).ask() or None

            # Prompt for tags (optional)
            tags_input = text(
                "Enter tags separated by commas (optional):",
                default=""
            ).ask() or None

            tags = [t.strip() for t in tags_input.split(",")] if tags_input else []

        else:
            # Non-interactive mode - require arguments
            if not name or not provider:
                console.print("[red]Error: --name and --provider required in non-interactive mode[/red]")
                raise typer.Exit(1)

            # For now, we can't securely get the key value in non-interactive mode
            # without exposing it in shell history. This is a design decision.
            console.print("[yellow]Warning: Non-interactive mode is not recommended for security[/yellow]")
            console.print("[yellow]Please use interactive mode to avoid exposing keys in shell history[/yellow]")
            raise typer.Exit(1)

        # Validate and add the key
        try:
            api_key = key_manager.add_key(
                name=name,
                key_value=key_value,
                ## fixme: Type "str" is not assignable to type "Provider"
                provider=provider,
                description=description,
                tags=tags,
            )

            # Save metadata
            metadata_manager.save_metadata(api_key)

            # Success message
            console.print(Panel.fit(
                f"[bold green]✓ API key added successfully![/bold green]\n\n"
                f"[cyan]Name:[/cyan] {name}\n"
                f"[cyan]provider:[/cyan] {provider}\n"
                f"[cyan]Description:[/cyan] {description or 'N/A'}\n"
                f"[cyan]Tags:[/cyan] {', '.join(tags) if tags else 'None'}",
                title="Success"
            ))

        except ValidationError as e:
            console.print(f"[red]Validation error: {e.message}[/red]")
            raise typer.Exit(1)
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    typer.run(add_cmd)
