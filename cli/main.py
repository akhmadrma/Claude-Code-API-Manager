"""Main CLI entry point for Cloud Code API Manager."""

from typing import Optional
from typer import echo
import typer

# Import command modules
from .commands.delete import delete_cmd
from .commands.add import add_cmd
from .commands.list import list_cmd
from .commands.validate import validate_cmd


app = typer.Typer(
    name="cloudcode",
    help="Interactive CLI tool for managing API keys with beautiful terminal UI",
    add_completion=False,
    no_args_is_help=True,
)



@app.command("version")
def version():
    """Show version information."""
    echo("Cloud Code API Manager v1.0.0")




# Register commands
app.command("add")(add_cmd)
app.command("list")(list_cmd)
app.command("delete")(delete_cmd)
app.command("validate")(validate_cmd)


@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose output"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
):
    """
    Cloud Code API Manager - Interactive CLI for API key management
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = config


if __name__ == "__main__":
    app()
