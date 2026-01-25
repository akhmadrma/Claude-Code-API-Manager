"""Validate Claude Code settings.json configuration."""

import json
from pathlib import Path
from questionary import text
from core.validators import ValidationError
from typer import echo, Exit
import typer
from core.validators import ConfigValidator
from core.export_manager import ExportClaudeSettings


def validate_cmd(
    # json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
    # quiet: bool = typer.Option(False, "--quiet", "-q", help="Only exit code (0=valid, 1=invalid)"),
    report: bool = typer.Option(False, "--report", "-r", help="Display validation report JSON"),
):
    """Validate Claude Code settings.json configuration."""

    if report:
        reportdata = ConfigValidator.validate_and_report()
        echo("✅ Validation: PASSED")
        # Human-readable output
        echo(json.dumps(reportdata, indent=2))
        raise Exit(code=0 if reportdata["valid"] else 1)

    # validate instalation
    validateInstalation = ConfigValidator.validate_installation()
    echo("✅ Validation Instalation: PASSED")
    if not validateInstalation[0]:
        echo(f"❌ Validation: FAILED\n{validateInstalation[1]}")
        raise Exit(code=1)

    # validate settings.json
    try:
        validateSettings = ConfigValidator.load_settings()
    except ValidationError as e:
        echo(f"❌ Validation: FAILED\n{str(e)}")
        answer = text(
            "Do you want to create a new settings file? (y/n): ",
            default="y",
            # fixme : Type of parameter "x" is unknown
            validate=lambda x: x.lower() in ["y", "n"], #
        ).ask()
        if answer == "y":
            # ConfigValidator.create_settings()
            export: Path = ExportClaudeSettings().export_settings({}, backup=False)
            echo("✅ Settings file created in : " + str(export))
            raise Exit(code=0)
        else:
            raise Exit(code=1)

    # validate structure
    try:
        ConfigValidator.validate_structure(validateSettings)
    except ValidationError as e:
        echo(f"❌ Validation: FAILED\n{str(e)}")
        raise Exit(code=1)
    echo("✅ Validation Structure: PASSED")

    # validate environment variables
    try:
        validateEnvVars = ConfigValidator.validate_env_vars(validateSettings)
        echo("✅ Validation Environment Variables: PASSED")
        if validateEnvVars:
            echo("❌ Validation: FAILED")
            for err in validateEnvVars:
                echo(f"  ⚠️  {err}")
            raise Exit(code=1)
    except ValidationError as e:
        echo(f"❌ Validation: FAILED\n{str(e)}")
        raise Exit(code=1)

    echo("✅ Validation: PASSED")
    raise Exit(code=0)
