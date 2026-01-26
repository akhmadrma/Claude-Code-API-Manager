"""Validate Claude Code settings.json configuration."""

import json
from pathlib import Path
from questionary import text
from core.validators import ValidationError
from typer import echo, Exit
import typer
from core.validators import ConfigValidator
from core.export_manager import ExportClaudeSettings
from pydantic import BaseModel, field_validator, ValidationError as PydanticValidationError


class YesNoInput(BaseModel):
    """Validate yes/no input (y/n, case-insensitive)."""
    value: str

    @field_validator('value')
    @classmethod
    def validate_yes_no(cls, v: str) -> str:
        """Validate input is 'y' or 'n' (case-insensitive)."""
        if v.lower() not in ['y', 'n']:
            raise ValueError("Please enter 'y' or 'n'")
        return v.lower()


def _validate_yes_no(value: str) -> bool:
    """Wrapper for Pydantic validation (returns True if valid)."""
    try:
        YesNoInput(value=value)
        return True
    except PydanticValidationError:
        return False


def validate_cmd(
    report: bool = typer.Option(False, "--report", help="Display validation report JSON"),
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
    if not validateInstalation[0]:
        echo(f"❌ Validation: FAILED\n{validateInstalation[1]}")
        raise Exit(code=1)
    echo("✅ Validation Instalation: PASSED")

    # validate settings.json
    try:
        validateSettings = ConfigValidator.load_settings()
    except ValidationError as e:
        echo(f"❌ Validation: FAILED\n{str(e)}")
        answer = text(
            "Do you want to create a new settings file? (y/n): ",
            default="y",
            validate=_validate_yes_no,
        ).ask()
        if answer == "y":
            # ConfigValidator.create_settings()
            export: Path = ExportClaudeSettings().export_settings("placeholder-api-key", backup=False)
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
