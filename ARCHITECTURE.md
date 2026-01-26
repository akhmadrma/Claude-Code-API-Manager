# Claude Code API Manager - Architecture Document

## Project Overview

**Project Name**: CAPIM (Cloud Code API Manager)
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
- **Use**: Interactive selection and activation of stored keys

### 2. Metadata Storage

- Separate `keys_metadata.json` file for storing:
  - Key name (identifier)
  - Provider type (Anthropic, GLM, etc.)
  - Description (user-defined purpose)
  - Tags (for categorization)
  - Active status (for key activation)
  - Created timestamp
  - Updated timestamp
- Enables rich display without exposing actual key values
- Supports filtering and search functionality

### 3. Search and Filter

- **Filter by Provider**: Display only keys for specific providers (--provider flag)
- **Filter by Tags**: Search using custom tags (--tag flag)
- **Text Search**: Find keys by name or description (--search flag)
- Color-coded Display: Different colors for different provider types

### 4. Security Enhancement

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
  - Provider-specific pattern matching
- **Secure Display**:
  - Masked key values in list view
  - Optional reveal with confirmation

### 5. Claude Code Integration

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
  - `constans/providers.py`: Provider type definitions
  - `constans/providerModel.py`: Model configurations per provider
  - `constans/providerUrl.py`: Base URL management for providers
  - `constans/settings.py`: Settings structure validation

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
│   ├── providerUrl.py          # Base URL management
│   └── settings.py             # Settings structure validation
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
├── .env                        # API keys storage (gitignored)
├── .gitignore
├── pyproject.toml              # Dependencies and project config
├── README.md
├── ARCHITECTURE.md             # This file
└── PLANNING.md                 # Future features and roadmap
```

## Data Models

### API Key Model (Pydantic)

```python
class APIKey(BaseModel):
    name: str
    provider: str
    description: Optional[str]
    tags: List[str] = []
    is_active: bool = False
    created_at: datetime
    updated_at: datetime
```

### Provider Models

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
- `capi list [--provider PROVIDER] [--tag TAG] [--search TEXT]` - List keys with filters
- `capi delete KEY_NAME` - Delete key
- `capi use` - Interactive key selection and activation
- `capi validate [--report]` - Validate Claude Code settings.json
- `capi version` - Show version information

### Note on Command Name

The CLI command is `capi` (not `cloudcode`) as defined in `pyproject.toml`:
```toml
[tool.poetry.scripts]
capi = "cli.main:app"
```

## Workflow Examples

### Adding a New API Key

1. User runs `capi add`
2. Questionary prompts for:
   - Key name
   - Provider type (with autocomplete)
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
4. System activates the key by:
   - Deactivating previously active key
   - Marking selected key as active
   - Exporting Claude Code settings with the new key
5. Success message displayed

### Validating Claude Code Settings

1. User runs `capi validate`
2. System checks Claude Code installation
3. Validates settings.json structure and environment variables
4. If validation fails:
   - Prompts user to create new settings file
   - Generates proper settings.json with defaults
   - Backs up existing settings if present
5. Reports validation status with clear pass/fail indicators

## Security Considerations

### File Permissions

- `.env` must be 600 (owner read/write only)
- `keys_metadata.json` must be 600
- `settings.json` must be 600
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
typer = "^0.21.0"
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
   - Base URL: `https://open.bigmodel.cn/api/paas/v4/`
   - Models: glm-4.5, glm-4.6, glm-4.7

### Adding New Providers

To add a new provider:

1. Update `constans/providers.py` with provider type
2. Add model mappings to `constans/providerModel.py`
3. Add base URL to `constans/providerUrl.py`
4. Implement provider-specific validation if needed

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

# List keys with filters
capi list --provider anthropic
capi list --tag production
capi list --search "github"

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


