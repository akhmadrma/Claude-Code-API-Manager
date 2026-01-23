"""Validate Claude Code settings.json configuration."""

import json
from typer import echo, Exit
import typer
from core.validators import ConfigValidator


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
        # echo(f"📁 Claude Dir: {reportdata['claude_dir']}")
        # echo(f"📄 Settings: {reportdata['settings_path']}")
        # echo(f"{'✅' if reportdata['installed'] else '❌'} Installed: {reportdata['installed']}")
        # echo(
        #     f"{'✅' if reportdata['settings_exists'] else '❌'} Settings Exists: {reportdata['settings_exists']}"
        # )

    # validate instalation
    validateInstalation = ConfigValidator.validate_installation()
    echo("✅ Validation Instalation: PASSED")
    if not validateInstalation[0]:
        echo(f"❌ Validation: FAILED\n{validateInstalation[1]}")
        raise Exit(code=1)
    
    # validate settings.json
    validateSettings = ConfigValidator.load_settings()
    echo("✅ Validation Settings,json: PASSED")
    if not validateSettings:
        echo("❌ Validation: FAILED")
        raise Exit(code=1)

    # validate structure
    validateStructure = ConfigValidator.validate_structure(validateSettings)
    echo("✅ Validation Structure: PASSED")
    if validateStructure:
        echo("❌ Validation: FAILED")
        for err in validateStructure:
            echo(f"  ⚠️  {err}")
        raise Exit(code=1)

    # validate environment variables
    validateEnvVars = ConfigValidator.validate_env_vars(validateSettings)
    echo("✅ Validation Environment Variables: PASSED")
    if validateEnvVars:
        echo("❌ Validation: FAILED")
        for err in validateEnvVars:
            echo(f"  ⚠️  {err}")
        raise Exit(code=1)

    raise Exit(code=0)
