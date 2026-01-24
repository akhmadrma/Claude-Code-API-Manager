"""API key format validators for different services."""

import json
import os
import re
from pathlib import Path
from typing import  Dict, Any, TypedDict, NotRequired

from dotenv import load_dotenv


class EnvironmentVariables(TypedDict):
    """Environment variables section of settings.json."""
    ANTHROPIC_DEFAULT_HAIKU_MODEL: NotRequired[str]
    ANTHROPIC_DEFAULT_SONNET_MODEL: NotRequired[str]
    ANTHROPIC_DEFAULT_OPUS_MODEL: NotRequired[str]
    ANTHROPIC_AUTH_TOKEN: NotRequired[str]
    ANTHROPIC_BASE_URL: NotRequired[str]
    API_TIMEOUT_MS: NotRequired[str]
    CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC: NotRequired[str]


class ClaudeSettings(TypedDict):
    """Type definition for Claude Code settings.json."""
    env: NotRequired[EnvironmentVariables]
    alwaysThinkingEnabled: NotRequired[bool]


class ValidationError(Exception):
    """Custom validation error."""

    def __init__(self, message: str, service: str = "unknown"):
        self.message = message
        self.service = service
        super().__init__(self.message)


class KeyValidator:
    """Base validator for API keys."""

    # Common service patterns
    PATTERNS = {
        "OpenAI": r"^sk-[a-zA-Z0-9]{48}$",
        "GitHub": r"^ghp_[a-zA-Z0-9]{36}$|^gho_[a-zA-Z0-9]{36}$|^ghu_[a-zA-Z0-9]{36}$|^ghs_[a-zA-Z0-9]{36}$|^ghr_[a-zA-Z0-9]{36}$",
        "AWS": r"^AKIA[0-9A-Z]{16}$",
        "Google": r"^AIza[a-zA-Z0-9_\-]{35}$",
        "Stripe": r"^sk_live_[a-zA-Z0-9]{24,}$|^sk_test_[a-zA-Z0-9]{24,}$",
        "Slack": r"^xoxb-[a-zA-Z0-9-]{10,}$|^xoxp-[a-zA-Z0-9-]{10,}$",
        "Twilio": r"^AC[a-zA-Z0-9_\-]{32}$",
        "SendGrid": r"^SG\.[a-zA-Z0-9_\-]{22}\.[a-zA-Z0-9_\-]{43}$",
    }

    @classmethod
    def validate(cls, key: str, service: str) -> bool:
        """
        Validate an API key against its service pattern.

        Args:
            key: The API key to validate
            service: The service name (case-insensitive)

        Returns:
            True if valid

        Raises:
            ValidationError: If key format is invalid
        """
        if not key or not key.strip():
            raise ValidationError("API key cannot be empty", service)

        service_lower = service.lower()

        # Check if we have a pattern for this service
        pattern = None
        for svc_name, pattern_str in cls.PATTERNS.items():
            if svc_name.lower() == service_lower:
                pattern = re.compile(pattern_str)
                break

        if pattern is None:
            # No pattern defined for this service, do basic validation
            if len(key) < 10:
                raise ValidationError(
                    f"API key seems too short for {service} (minimum 10 characters)",
                    service
                )
            return True

        if not pattern.match(key):
            raise ValidationError(
                f"API key format does not match expected pattern for {service}",
                service
            )

        return True

    @classmethod
    def get_supported_services(cls) -> list[str]:
        """Get list of services with validation patterns."""
        return list(cls.PATTERNS.keys())

    @classmethod
    def is_service_supported(cls, service: str) -> bool:
        """Check if a service has validation patterns."""
        return service.lower() in [s.lower() for s in cls.PATTERNS.keys()]


class ConfigValidator:
    """Validator for Claude Code settings.json configuration."""
    load_dotenv(Path(__file__).parent.parent / ".env")

    DEFAULT_CLAUDE_DIR = Path.home() / os.getenv("DEFAULT_CLAUDE_DIR", "test")
    SETTINGS_FILE = "settings.json"
    SETTINGS_EXAMPLE = "settings.example.json"

    # Required and optional settings structure
    REQUIRED_TOP_LEVEL_KEYS: list[str] = []
    OPTIONAL_TOP_LEVEL_KEYS: list[str] = ["env", "alwaysThinkingEnabled"]

    # Required environment variables
    REQUIRED_ENV_VARS: list[str] = []
    OPTIONAL_ENV_VARS: list[str] = [
        "ANTHROPIC_DEFAULT_HAIKU_MODEL",
        "ANTHROPIC_DEFAULT_SONNET_MODEL",
        "ANTHROPIC_DEFAULT_OPUS_MODEL",
        "ANTHROPIC_AUTH_TOKEN",
        "ANTHROPIC_BASE_URL",
        "API_TIMEOUT_MS",
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"
    ]

    @classmethod
    def get_claude_dir(cls) -> Path:
        """Get the Claude configuration directory path."""
        return cls.DEFAULT_CLAUDE_DIR

    @classmethod
    def get_settings_path(cls) -> Path:
        """Get the full path to settings.json."""
        return cls.get_claude_dir() / cls.SETTINGS_FILE

    @classmethod
    def is_claude_installed(cls) -> bool:
        """Check if Claude Code is installed (directory exists)."""
        return cls.get_claude_dir().exists()

    @classmethod
    def settings_exists(cls) -> bool:
        """Check if settings.json file exists."""
        return cls.get_settings_path().exists()

    @classmethod
    def validate_installation(cls) -> tuple[bool, str]:
        """
        Validate Claude Code installation.

        Returns:
            (is_valid, message) tuple
        """
        if not cls.is_claude_installed():
            return False, f"Claude Code directory not found at {cls.get_claude_dir()}"

        return True, "Claude Code installation valid"

    @classmethod
    def load_settings(cls) -> ClaudeSettings:
        """
        Load settings.json file.

        Returns:
            Parsed settings dictionary with proper typing

        Raises:
            ValidationError: If file cannot be loaded or parsed
        """
        settings_path = cls.get_settings_path()

        if not settings_path.exists():
            raise ValidationError(f"Settings file not found: {str(settings_path)}", "config")

        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings: ClaudeSettings = json.load(f)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in settings file: {e}", "config")
        except Exception as e:
            raise ValidationError(f"Error reading settings file: {e}", "config")

        return settings

    @classmethod
    def validate_structure(cls, settings: ClaudeSettings) -> list[str]:
        """
        Validate settings structure.

        Args:
            settings: Parsed settings dictionary with proper typing

        Returns:
            List of validation errors (empty if valid)
        """
        errors: list[str] = []

        # Validate top-level keys
        # Note: TypedDict is erased at runtime, so json.load() returns a regular dict
        # We don't need isinstance check since ClaudeSettings is always a dict type
        
        # Check for unknown keys (warn but don't fail)
        known_keys = set(cls.REQUIRED_TOP_LEVEL_KEYS + cls.OPTIONAL_TOP_LEVEL_KEYS)
        unknown_keys  = set(settings.keys()) - known_keys
        if unknown_keys:
            raise ValidationError(f"Unknown keys in settings: {', '.join(unknown_keys)}", "config")

        # Validate env section if present
        if "env" in settings:
            
            # Check for unknown env vars
            known_env = set(cls.REQUIRED_ENV_VARS + cls.OPTIONAL_ENV_VARS)
            unknown_env = set(settings["env"].keys()) - known_env
            if unknown_env:
                raise ValidationError(f"Unknown env vars: {', '.join(unknown_env)}", "env")

        return errors

    @classmethod
    def validate_env_vars(cls, settings: ClaudeSettings) -> list[str]:
        """
        Validate environment variables in settings.

        Args:
            settings: Parsed settings dictionary with proper typing

        Returns:
            List of validation errors (empty if valid)
        """
        errors: list[str] = []

        # Check if "env" key exists in settings (env section is optional)
        if "env" not in settings:
            return errors

        env: EnvironmentVariables = settings["env"]

        # Validate required env vars
        for var in cls.REQUIRED_ENV_VARS:
            if var not in env or not env[var]:
                errors.append(f"Required environment variable missing or empty: {var}")

        # Validate types and formats
        if "API_TIMEOUT_MS" in env and env["API_TIMEOUT_MS"]:
            try:
                timeout = int(env["API_TIMEOUT_MS"])
                if timeout <= 0:
                    errors.append("API_TIMEOUT_MS must be a positive integer")
            except ValueError:
                errors.append("API_TIMEOUT_MS must be an integer")


        # Validate ANTHROPIC_AUTH_TOKEN format if present
        if "ANTHROPIC_AUTH_TOKEN" in env and env["ANTHROPIC_AUTH_TOKEN"]:
            token = env["ANTHROPIC_AUTH_TOKEN"]
            if len(token) < 20:
                errors.append("ANTHROPIC_AUTH_TOKEN seems too short (should be at least 20 characters)")

        # Validate ANTHROPIC_BASE_URL format if present
        if "ANTHROPIC_BASE_URL" in env and env["ANTHROPIC_BASE_URL"]:
            url = env["ANTHROPIC_BASE_URL"]
            if not url.startswith(("http://", "https://")):
                errors.append("ANTHROPIC_BASE_URL must start with http:// or https://")

        return errors

    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """
        Perform comprehensive validation of settings.json.

        Returns:
            (is_valid, errors) tuple
        """
        errors : list[str] = []

        # Check installation
        installed, msg = cls.validate_installation()
        if not installed:
            return False, [msg]

        # Load settings
        try:
            settings = cls.load_settings()
        except ValidationError as e:
            return False, [str(e)]

        # Validate structure
        structure_errors = cls.validate_structure(settings)
        errors.extend(structure_errors)

        # Validate environment variables
        env_errors = cls.validate_env_vars(settings)
        errors.extend(env_errors)

        # Filter out warnings (only include actual errors)
        critical_errors = [e for e in errors if not e.startswith("Warning:")]

        return len(critical_errors) == 0, errors

    @classmethod
    def validate_and_report(cls) -> Dict[str, Any]:
        """
        Validate settings and return detailed report.

        Returns:
            Dictionary with validation results and details
        """
        is_valid, errors = cls.validate()

        report: Dict[str, Any] = {
            "valid": is_valid,
            "errors": errors,
            "claude_dir": str(cls.get_claude_dir()),
            "settings_path": str(cls.get_settings_path()),
            "installed": cls.is_claude_installed(),
            "settings_exists": cls.settings_exists()
        }

        if is_valid:
            try:
                settings = cls.load_settings()
                report["settings"] = settings
                report["env_vars_count"] = len(settings.get("env", {}))
            except Exception:
                pass

        return report