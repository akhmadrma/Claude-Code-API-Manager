# Claude Code API Manager - Architecture Document

## Project Overview

**Project Name**: CAPI (Cloud Code API Manager)
**Version**: 0.1.0
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

- **Create**: Add new API keys with metadata (name, provider, description, tags)
- **Read**: View individual API key details
- **Update**: Modify existing API key values or metadata (implemented in core)
- **Delete**: Remove API keys with confirmation prompts
- **List**: Display all stored API keys in formatted table with filtering
- **Use**: Interactive selection and activation of stored keys with merge/preview modes

### 2. Metadata Storage

- Separate `keys_metadata.json` file for storing:
  - Key name (identifier)
  - Provider type (anthropic, glm, kimi)
  - Description (user-defined purpose)
  - Tags (for categorization)
  - Status (active/inactive)
  - Created timestamp
  - Updated timestamp
- Enables rich display without exposing actual key values
- Supports filtering and search functionality
- Stored in `~/.capi/keys_metadata.json`

### 3. Search and Filter

- **Filter by Provider**: Display only keys for specific providers (`--service` flag)
- **Filter by Tags**: Search using custom tags (`--tag` flag)
- **Text Search**: Find keys by name or description (`--search` flag)
- Color-coded Display: Different colors for different provider types

### 4. Security Enhancement

- **File Permission Checks**:
  - Verify `.env` has 600 permissions (Unix/Linux)
  - Warn on overly permissive settings
  - Auto-fix option for incorrect permissions
- **Key Validation**:
  - Format validation before storage
  - Provider-specific pattern matching
- **Secure Display**:
  - Masked key values in list view
  - Only last 4 characters visible
- **Secure Storage**:
  - API keys stored in `~/.capi/.env` with 600 permissions
  - Metadata stored separately from key values

### 5. Claude Code Integration

- **Settings Validation**:
  - Validate Claude Code installation directory
  - Check settings.json structure and format
  - Verify environment variables configuration
  - Model configuration validation

- **Automatic Settings Creation**:
  - Generate settings.json with proper structure
  - Support for multiple API providers (Anthropic, GLM, Kimi)
  - Pre-configured model mappings for each provider
  - Automatic backup before creating new settings

- **Provider Management**:
  - `constans/providers.py`: Provider type definitions
  - `constans/providerModel.py`: Model configurations per provider
  - `constans/providerUrl.py`: Base URL management for providers

- **Export Functionality**:
  - `ExportClaudeSettings`: Generate Claude-compatible settings.json
  - Backup support for existing settings
  - Merge mode to preserve existing settings
  - Preview mode to see changes before applying
  - Environment variable configuration
  - Model selection and configuration

## Project Structure

```
capi/
├── cli/
│   ├── __init__.py
│   ├── main.py                 # Typer app entry point
│   └── commands/
│       ├── __init__.py
│       ├── add.py              # Create new API key
│       ├── list.py             # List keys with filters
│       ├── delete.py           # Delete key
│       ├── use.py              # Interactive key selection and activation
│       └── validate.py         # Claude settings validation
│
├── core/
│   ├── __init__.py
│   ├── key_manager.py          # Core CRUD logic
│   ├── metadata_manager.py     # Metadata operations
│   ├── export_manager.py       # Export logic + Claude settings export
│   ├── validators.py           # Key format validators + Claude config validation
│   └── models.py               # Pydantic models
│
├── constans/                   # Provider and settings constants (NOTE: "constans" not "constants")
│   ├── __init__.py
│   ├── providers.py            # Provider type definitions
│   ├── providerModel.py        # Model configurations per provider
│   └── providerUrl.py          # Base URL management
│
├── storage/
│   ├── __init__.py
│   ├── env_handler.py          # .env file operations
│   └── metadata_handler.py     # JSON metadata operations
│
├── ui/
│   ├── __init__.py
│   └── display.py              # Rich display utilities
│
├── utils/
│   ├── __init__.py
│   ├── crypto.py               # Encryption utilities
│   ├── shell.py                # Shell command generators
│   └── helpers.py              # Common utilities
│
├── tests/
│   └── __init__.py
│
├── .env.example                # Example environment file
├── .gitignore
├── pyproject.toml              # Dependencies and project config
├── README.md
└── ARCHITECTURE.md             # This file
```

## Data Models

### API Key Model (Pydantic)

```python
class APIKey(BaseModel):
    name: str
    provider: Provider
    description: Optional[str]
    tags: List[str] = []
    status: str = "active"
    created_at: datetime
    updated_at: datetime
```

### Environment Model (Pydantic)

```python
class Environment(BaseModel):
    anthropic_default_haiku_model: str
    anthropic_default_sonnet_model: str
    anthropic_default_opus_model: str
    anthropic_auth_token: str
    anthropic_base_url: BaseURL
    api_timeout_ms: int
    claude_code_disable_nonessential_traffic: bool
```

### Provider Models

```python
Provider: TypeAlias = Literal["anthropic", "glm", "kimi"]

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

| Command | Description | Options |
|---------|-------------|---------|
| `capi add` | Add new API key (interactive) | `--name`, `--provider`, `--interactive/--no-interactive` |
| `capi list` | List keys with filters | `--service`, `--tag`, `--search` |
| `capi delete KEY_NAME` | Delete key | `--name`, `--interactive/--no-interactive` |
| `capi use` | Interactive key selection and activation | `--name`, `--interactive/--no-interactive`, `--merge`, `--preview` |
| `capi validate` | Validate Claude Code settings.json | `--report` |
| `capi version` | Show version information | - |

### Command Name

The CLI command is `capi` as defined in `pyproject.toml`:
```toml
[tool.poetry.scripts]
capi = "cli.main:app"
```

## Workflow Examples

### Adding a New API Key

1. User runs `capi add`
2. Questionary prompts for:
   - Key name (validated - no spaces allowed)
   - Provider type (with autocomplete: anthropic, glm, kimi)
   - API key value (masked input)
   - Description (optional)
   - Tags (optional, comma-separated)
3. Validation checks format
4. Stores in `~/.capi/.env` and `~/.capi/keys_metadata.json`
5. Rich panel confirms successful addition

### Using an API Key

1. User runs `capi use`
2. Questionary displays filtered list of keys in a table
3. User selects key with arrow keys or enters name
4. If existing settings.json detected, prompts for:
   - Merge - Preserve existing settings
   - Overwrite - Replace all settings
   - Preview - Show changes first
   - Cancel - Exit without changes
5. System activates the key by:
   - Deactivating previously active key
   - Marking selected key as active
   - Exporting Claude Code settings with the new key
6. Success message displayed

### Preview Mode

1. User runs `capi use --preview` or selects "Preview" in interactive mode
2. System shows:
   - Which key would be deactivated/activated
   - Fields to be added/modified/removed in settings.json
   - Full resulting settings
3. In interactive mode, prompts to apply changes or cancel
4. No files are modified in preview mode

### Validating Claude Code Settings

1. User runs `capi validate`
2. System checks:
   - Claude Code installation directory exists
   - settings.json structure and environment variables
3. If validation fails:
   - Prompts user to create new settings file
   - Generates proper settings.json with defaults
4. Reports validation status with clear pass/fail indicators

## Security Considerations

### File Permissions

- `~/.capi/.env` must be 600 (owner read/write only)
- `~/.capi/keys_metadata.json` must be 600
- `~/.claude/settings.json` should be 600
- Claude Code settings protected with automatic backup

### Key Display

- Default masked display (e.g., `************xyz` - only last 4 chars visible)
- No reveal option currently implemented
- Clear screen after displaying sensitive data

### Storage Security

- API keys stored separately from metadata
- Keys in `~/.capi/.env`, metadata in `~/.capi/keys_metadata.json`
- Both files created with 600 permissions
- Parent directory `~/.capi/` created with secure permissions

## Dependencies (pyproject.toml)

```toml
[tool.poetry.dependencies]
python = "^3.9"
typer = { version = "^0.21.0", extras = ["all"]}
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
   - Models: claude-3-haiku-20240307, claude-3-5-sonnet-20241022, claude-3-opus-20240229

2. **GLM (Zhipu AI)**
   - Base URL: `https://api.z.ai/api/anthropic`
   - Models: glm-4.5, glm-4.6, glm-4.7

3. **Kimi**
   - Base URL: `https://api.kimi.com/coding/`
   - Models: K2.5

### Adding New Providers

To add a new provider:

1. Update `constans/providers.py` with provider type
2. Add model mappings to `constans/providerModel.py`
3. Add base URL to `constans/providerUrl.py`
4. Implement provider-specific validation if needed

## Installation & Usage

### Installation

```bash
pip install capi
# or
pipx install capi
```

### Quick Start

```bash
# Add your first API key
capi add

# List all keys
capi list

# List keys with filters
capi list --service anthropic
capi list --tag production
capi list --search "github"

# Use a key
capi use

# Use with merge mode
capi use --merge

# Preview changes
capi use --preview

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

## Storage Locations

| File | Location | Purpose |
|------|----------|---------|
| API Keys | `~/.capi/.env` | Secure storage of API key values |
| Metadata | `~/.capi/keys_metadata.json` | Key metadata (name, provider, tags, etc.) |
| Claude Settings | `~/.claude/settings.json` | Claude Code configuration (or path from DEFAULT_CLAUDE_DIR env var) |
| Settings Backups | `~/.claude/settings.backup.*.json` | Automatic backups of settings.json |

## Environment Variables

The following environment variables can be configured in `~/.capi/.env`:

- `DEFAULT_CLAUDE_DIR`: Custom path to Claude Code settings directory (default: `~/.claude`)

## License

MIT License
