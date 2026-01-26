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
    name: str = typer.Option(None, "--name", help="Key name/identifier"),
    provider: str = typer.Option(None, "--provider", help="provider type"),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", help="Interactive mode (default: True)"
    ),
):
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
            if not name:
                name = text(
                    "Enter a name for this key:",
                    instruction="ensure no spaces, TABs, or newlines",
                    validate=_validate_name,
                ).ask()
                if not name:
                    console.print("[red]Cancelled[/red]")
                    raise typer.Exit()
            else:
                # Validate name if provided via argument
                _validate_name(name)

            # Prompt for provider type
            if not provider:
                providers = PROVIDERS
                provider = select("Select provider type:", choices=providers).ask()

                if not provider:
                    console.print("[red]Cancelled[/red]")
                    raise typer.Exit()

            # Prompt for API key value (masked)
            key_value = password(
                "Enter the API key value:", instruction="(input will be hidden)"
            ).ask()

            if not key_value:
                console.print("[red]API key value is required[/red]")
                raise typer.Exit(1)

            # Prompt for description (optional)
            description = text("Enter a description (optional):", default="").ask() or None

            # Prompt for tags (optional)
            tags_input = (
                text("Enter tags separated by commas (optional):", default="").ask() or None
            )

            tags = [t.strip() for t in tags_input.split(",")] if tags_input else []

        else:
            # Non-interactive mode - require arguments
            if not name or not provider:
                console.print(
                    "[red]Error: --name and --provider required in non-interactive mode[/red]"
                )
                raise typer.Exit(1)

            # Validate name
            _validate_name(name)

            # For now, we can't securely get the key value in non-interactive mode
            # without exposing it in shell history. This is a design decision.
            console.print(
                "[yellow]Warning: Non-interactive mode is not recommended for security[/yellow]"
            )
            console.print(
                "[yellow]Please use interactive mode to avoid exposing keys in shell history[/yellow]"
            )
            raise typer.Exit(1)

        # Validate and add the key
        try:
            # Validate provider is a valid Provider type
            if provider not in PROVIDERS:
                console.print(f"[red]Error: Invalid provider '{provider}'. Valid providers are: {', '.join(PROVIDERS)}[/red]")
                raise typer.Exit(1)
                
            api_key = key_manager.add_key(
                name=name,
                key_value=key_value,
                provider=provider,  # Provider is a TypeAlias for literal strings, no constructor needed
                description=description,
                tags=tags,
            )

            # Save metadata
            metadata_manager.save_metadata(api_key)

            # Success message
            console.print(
                Panel.fit(
                    f"[bold green]✓ API key added successfully![/bold green]\n\n"
                    f"[cyan]Name:[/cyan] {name}\n"
                    f"[cyan]provider:[/cyan] {provider}\n"
                    f"[cyan]Description:[/cyan] {description or 'N/A'}\n"
                    f"[cyan]Tags:[/cyan] {', '.join(tags) if tags else 'None'}",
                    title="Success",
                )
            )

        except ValidationError as e:
            console.print(f"[red]Validation error: {e.message}[/red]")
            raise typer.Exit(1)
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1)


def _validate_name(value: str) -> bool:
    """
    Validate API key name to ensure it doesn't contain spaces.

    Args:
        value: The proposed name for the API key

    Returns:
        True if valid

    Raises:
        typer.Exit: If validation fails
    """
    # Check for spaces - .env files cannot have spaces in variable names
    if " " in value or "\t" in value or "\n" in value:
        console.print(f"[red]Error: Key name cannot contain spaces or whitespace characters[/red]")
        console.print(f"[yellow]Invalid name: '{value}'[/yellow]")
        raise typer.Exit(1)

    # Check if key already exists
    key_manager = KeyManager()
    if key_manager.key_exists(value):
        console.print(f"[red]Key '{value}' already exists[/red]")
        raise typer.Exit(1)

    return True


if __name__ == "__main__":
    typer.run(add_cmd)
