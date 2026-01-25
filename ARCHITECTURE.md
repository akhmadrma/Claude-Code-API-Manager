# Claude Code API Manager - Architecture Document

## Project Overview

**Project Name**: CAPIM (Cloud Code API Manager)
**Version**: 1.0.0
**Purpose**: Interactive CLI tool for managing API keys with beautiful terminal UI and Claude Code settings integration
**Target Users**: Developers managing multiple API keys across different services and Claude Code configurations

## Tech Stack

| Component           | Technology        | Purpose                                                   |
| ------------------- | ----------------- | --------------------------------------------------------- |
| CLI Framework       | Typer             | Command-line interface with type hints and automatic help |
| UI/Display          | Rich              | Beautiful terminal output with colors, tables, and panels |
| Interactive Prompts | Questionary       | OpenCommit-style interactive menus and selections         |
| Storage             | python-dotenv     | Read/write API keys to .env files                         |
| Data Validation     | Pydantic          | Type validation for models and configurations             |
| Encryption          | cryptography      | Backup file encryption                                    |
| Settings Management | Custom exporters  | Claude Code settings.json generation and validation       |

## Core Features

### 1. CRUD Operations

- **Create**: Add new API keys with metadata (name, service, description)
- **Read**: View individual API key details
- **Update**: Modify existing API key values or metadata
- **Delete**: Remove API keys with confirmation prompts
- **List**: Display all stored API keys in formatted table
- **Use**: Interactive selection and usage of stored keys

### 2. Metadata Storage

- Separate `keys_metadata.json` file for storing:
  - Key name (identifier)
  - Service type (OpenAI, GitHub, AWS, etc.)
  - Description (user-defined purpose)
  - Tags (for categorization)
  - Created timestamp
  - Updated timestamp
- Enables rich display without exposing actual key values
- Supports filtering and search functionality

### 3. Environment Variable Export

- **Single Key Export**: `cloudcode export KEY_NAME`
- **Bulk Export**: `cloudcode export --all` or `cloudcode export --service openai`
- **Shell Integration**: `eval $(cloudcode export KEY_NAME)`
- Generates shell-compatible export commands
- Supports both bash/zsh and fish shell formats
- Temporary vs permanent export options

### 4. Backup and Restore

- **Backup Creation**:
  - Encrypted backups of `.env` and `keys_metadata.json`
  - Timestamp-based naming: `backup_YYYYMMDD_HHMMSS.enc`
  - Password-protected encryption
  - Optional compression
- **Restore Operations**:
  - List available backups
  - Preview backup contents before restore
  - Confirmation prompts before overwriting
  - Merge or replace options

### 5. Search and Filter

- **Filter by Service**: Display only keys for specific services
- **Filter by Tags**: Search using custom tags
- **Filter by Date**: Show keys created/updated within date range
- **Text Search**: Find keys by name or description
- **Color-coded Display**: Different colors for different service types

### 6. Security Enhancement

- **File Permission Checks**:
  - Verify `.env` has 600 permissions (Unix/Linux)
  - Warn on overly permissive settings
  - Auto-fix option for incorrect permissions
- **Git Safety**:
  - Auto-generate `.gitignore` entries
  - Check if `.env` is tracked in git
  - Warning display if sensitive files detected in git
- **Key Validation**:
  - Format validation before storage
  - Service-specific pattern matching
- **Secure Display**:
  - Masked key values in list view
  - Optional reveal with confirmation

### 7. Settings Configuration

- `settings.json` editor for:
  - Default service types
  - Display preferences
  - Backup location
  - Shell export format
  - Security preferences

### 8. Claude Code Integration (NEW)

- **Settings Validation**:
  - Validate Claude Code installation directory
  - Check settings.json structure and format
  - Verify environment variables configuration
  - Model configuration validation

- **Automatic Settings Creation**:
  - Generate settings.json with proper structure
  - Support for multiple API providers (Anthropic, GLM)
  - Pre-configured model mappings for each provider
  - Automatic backup before creating new settings

- **Provider Management**:
  - `constants/providers.py`: Provider type definitions
  - `constants/providerModel.py`: Model configurations per provider
  - `constants/providerUrl.py`: Base URL management for providers
  - `constants/settings.py`: Settings structure validation

- **Export Functionality**:
  - `ExportClaudeSettings`: Generate Claude-compatible settings.json
  - Backup support for existing settings
  - Environment variable configuration
  - Model selection and configuration

## Project Structure

```
capim/
├── cli/
│   ├── __init__.py
│   ├── main.py                 # Typer app entry point
│   └── commands/
│       ├── __init__.py
│       ├── add.py              # Create new API key (IMPLEMENTED)
│       ├── list.py             # List keys with filters (IMPLEMENTED)
│       ├── delete.py           # Delete key (IMPLEMENTED)
│       ├── use.py              # Interactive key selection (IMPLEMENTED)
│       └── validate.py         # Claude settings validation (IMPLEMENTED)
│
├── core/
│   ├── __init__.py
│   ├── key_manager.py          # Core CRUD logic (IMPLEMENTED)
│   ├── metadata_manager.py     # Metadata operations (IMPLEMENTED)
│   ├── export_manager.py       # Export logic + Claude settings export (IMPLEMENTED)
│   ├── validators.py           # Key format validators + Claude config validation (IMPLEMENTED)
│   └── models.py               # Pydantic models (APIKey, Settings, Environment, BackupMetadata)
│
├── constans/                   # Provider and settings constants (NOTE: "constans" not "constants")
│   ├── __init__.py
│   ├── providers.py            # Provider type definitions (IMPLEMENTED)
│   ├── providerModel.py        # Model configurations per provider (IMPLEMENTED)
│   ├── providerUrl.py          # Base URL management (IMPLEMENTED)
│   └── settings.py             # Settings structure validation (IMPLEMENTED)
│
├── storage/
│   ├── __init__.py
│   ├── env_handler.py          # .env file operations (IMPLEMENTED)
│   └── metadata_handler.py     # JSON metadata operations (IMPLEMENTED)
│
├── ui/
│   ├── __init__.py
│   └── display.py              # Rich display utilities (IMPLEMENTED)
│
├── utils/
│   ├── __init__.py
│   ├── crypto.py               # Encryption utilities (IMPLEMENTED)
│   ├── shell.py                # Shell command generators (IMPLEMENTED)
│   └── helpers.py              # Common utilities (IMPLEMENTED)
│
├── tests/
│   └── __init__.py
│
├── claudedocs/                 # Claude documentation (TODO: Add content)
├── .env                        # API keys storage (gitignored)
├── .gitignore
├── .prettierignore
├── .prettierrc
├── pyproject.toml              # Dependencies and project config
├── README.md
└── ARCHITECTURE.md
```

## Data Models

### API Key Model (Pydantic)

```python
class APIKey(BaseModel):
    name: str
    service: str
    description: Optional[str]
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
```

### Settings Model

```python
class Settings(BaseModel):
    backup_location: str = "./backups"
    default_services: List[str] = []
    display_masked: bool = True
    auto_gitignore: bool = True
    shell_format: str = "bash"
```

### Environment Model (NEW)

```python
class Environment(BaseModel):
    """Claude API environment configuration."""
    anthropic_default_haiku_model: str
    anthropic_default_sonnet_model: str
    anthropic_default_opus_model: str
    anthropic_auth_token: str
    anthropic_base_url: BaseURL
    api_timeout_ms: int
    claude_code_disable_nonessential_traffic: bool
```

### Provider Models (NEW)

```python
Provider: TypeAlias = Literal["anthropic", "glm"]

class Model(BaseModel):
    """Default model configurations for each provider."""
    provider: Provider
    anthropic_default_haiku_model: str
    anthropic_default_sonnet_model: str
    anthropic_default_opus_model: str

class BaseURL(BaseModel):
    """Base URL configuration for different API providers."""
    provider: Provider
    value: str  # Validated base URL
```

## CLI Command Structure

### Currently Implemented Commands

- `capi add` - Add new API key (interactive)
- `capi list` - List keys with filters  
- `capi delete KEY_NAME` - Delete key
- `capi use` - Interactive key selection
- `capi validate` - Validate Claude Code settings.json
- `capi validate --report` - Display validation report as JSON
- `capi version` - Show version information

### Planned Commands (Not Yet Implemented)

- `capi show KEY_NAME` - Show key details
- `capi update KEY_NAME` - Update key value or metadata
- `capi export KEY_NAME` - Export single key
- `capi export --all` - Export all keys
- `capi export --service SERVICE` - Export by service
- `capi backup [--password PASSWORD]` - Create backup
- `capi backup list` - List available backups
- `capi restore BACKUP_FILE` - Restore from backup
- `capi config edit` - Edit settings.json interactively
- `capi config show` - Display current settings
- `capi config reset` - Reset to defaults
- `capi security check` - Run security audit
- `capi security fix` - Auto-fix permission issues

### Note on Command Name

The CLI command is `capi` (not `cloudcode`) as defined in `pyproject.toml`:
```toml
[tool.poetry.scripts]
capi = "cli.main:app"
```

## Workflow Examples

### Validating Claude Code Settings (NEW)

1. User runs `capi validate`
2. System checks Claude Code installation
3. Validates settings.json structure and environment variables
4. If validation fails:
   - Prompts user to create new settings file
   - Generates proper settings.json with defaults
   - Backs up existing settings if present
5. Reports validation status with clear pass/fail indicators

### Adding a New API Key

1. User runs `capi add`
2. Questionary prompts for:
   - Key name
   - Service type (with autocomplete)
   - API key value (masked input)
   - Description
   - Tags
3. Validation checks format
4. Stores in `.env` and `keys_metadata.json`
5. Rich panel confirms successful addition

### Using an API Key

1. User runs `capi use`
2. Questionary displays filtered list of keys
3. User selects key with arrow keys
4. Options presented:
   - Copy to clipboard
   - Export to environment
   - Display value
   - Cancel

### Creating Backup

1. User runs `capi backup` (planned - not yet implemented)
2. Prompts for password (optional)
3. Creates encrypted archive
4. Displays success with backup location
5. Rich progress bar during encryption

## Security Considerations

### File Permissions

- `.env` must be 600 (owner read/write only)
- `keys_metadata.json` must be 600
- `settings.json` must be 600
- Backup files encrypted with user password
- Claude Code settings protected with automatic backup

### Git Safety

- Auto-add `.env` and `keys_metadata.json` to `.gitignore`
- Check git status on startup
- Warn if sensitive files are tracked

### Key Display

- Default masked display (e.g., `sk-***...***xyz`)
- Require confirmation to reveal full key
- Clear screen after displaying sensitive data

## Dependencies (pyproject.toml)

```toml
[tool.poetry.dependencies]
python = "^3.9"
typer = "^0.12.0"
rich = "^13.7.0"
questionary = "^2.0.0"
python-dotenv = "^1.0.0"
pydantic = "^2.5.0"
cryptography = "^42.0.0"
pyperclip = "^1.8.2"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
black = "^24.0.0"
ruff = "^0.2.0"
```

## Provider Configuration

### Supported Providers

The tool comes with pre-configured support for:

1. **Anthropic**
   - Base URL: `https://api.anthropic.com`
   - Models: claude-3-haiku, claude-3.5-sonnet, claude-3-opus

2. **GLM (Zhipu AI)**
   - Base URL: `https://api.z.ai/api/anthropic`
   - Models: glm-4.5, glm-4.6, glm-4.7

### Adding New Providers

To add a new provider:

1. Update `constans/providers.py` with provider type
2. Add model mappings to `constans/providerModel.py`
3. Add base URL to `constans/providerUrl.py`
4. Implement provider-specific validation if needed

## Future Enhancements (v2.0)

- Cloud sync (encrypted storage in S3/Dropbox)
- Team sharing with encrypted key exchange
- API key rotation reminders
- Usage analytics (when keys were last used)
- Integration with password managers (1Password, Bitwarden)
- Web UI dashboard
- CI/CD integration commands

## Installation & Usage

### Installation

```bash
pip install capim
# or
pipx install capim
```

### Quick Start

```bash
# Add your first API key
capi add

# List all keys
capi list

# Use a key
capi use

# Validate Claude Code settings
capi validate

# Show version
capi version
```

### Claude Code Setup

```bash
# Validate and auto-create Claude settings if missing
capi validate

# Tool will prompt to create settings.json if validation fails
# Settings include:
# - Provider-specific model configurations
# - Base URL management
# - Environment variable setup
# - Automatic backup of existing settings
```

## License

MIT License

## Author

[Your Name]

## Contributing

See CONTRIBUTING.md for guidelines
