# Cloud Code API Manager - Architecture Document

## Project Overview

**Project Name**: Cloud Code API Manager  
**Version**: 1.0.0  
**Purpose**: Interactive CLI tool for managing API keys with beautiful terminal UI  
**Target Users**: Developers managing multiple API keys across different services

## Tech Stack

| Component           | Technology    | Purpose                                                   |
| ------------------- | ------------- | --------------------------------------------------------- |
| CLI Framework       | Typer         | Command-line interface with type hints and automatic help |
| UI/Display          | Rich          | Beautiful terminal output with colors, tables, and panels |
| Interactive Prompts | Questionary   | OpenCommit-style interactive menus and selections         |
| Storage             | python-dotenv | Read/write API keys to .env files                         |
| Data Validation     | Pydantic      | Type validation for models and configurations             |
| Encryption          | cryptography  | Backup file encryption                                    |

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

## Project Structure

```
cloud-code-api-manager/
├── cli/
│   ├── __init__.py
│   ├── main.py                 # Typer app entry point
│   └── commands/
│       ├── __init__.py
│       ├── add.py              # Create new API key
│       ├── list.py             # List keys with filters
│       ├── show.py             # Show single key details
│       ├── update.py           # Update existing key
│       ├── delete.py           # Delete key
│       ├── use.py              # Interactive key selection
│       ├── export.py           # Environment variable export
│       ├── backup.py           # Backup operations
│       ├── restore.py          # Restore operations
│       └── config.py           # Settings.json editor
│
├── core/
│   ├── __init__.py
│   ├── key_manager.py          # Core CRUD logic
│   ├── metadata_manager.py     # Metadata operations
│   ├── export_manager.py       # Export logic
│   ├── backup_manager.py       # Backup/restore logic
│   ├── filter_engine.py        # Search and filter logic
│   ├── security.py             # Security checks and validations
│   ├── validators.py           # Key format validators
│   └── models.py               # Pydantic models
│
├── storage/
│   ├── __init__.py
│   ├── env_handler.py          # .env file operations
│   ├── metadata_handler.py     # JSON metadata operations
│   ├── backup_handler.py       # Backup file operations
│   └── settings_handler.py     # Settings.json operations
│
├── ui/
│   ├── __init__.py
│   ├── display.py              # Rich display utilities
│   ├── prompts.py              # Questionary prompts
│   ├── tables.py               # Table formatters
│   └── themes.py               # Color schemes
│
├── utils/
│   ├── __init__.py
│   ├── crypto.py               # Encryption utilities
│   ├── shell.py                # Shell command generators
│   └── helpers.py              # Common utilities
│
├── tests/
│   ├── __init__.py
│   ├── test_key_manager.py
│   ├── test_metadata.py
│   ├── test_export.py
│   ├── test_backup.py
│   └── test_security.py
│
├── .env                        # API keys storage (gitignored)
├── keys_metadata.json          # Key metadata (gitignored)
├── settings.json               # Application settings
├── .gitignore
├── pyproject.toml              # Dependencies and project config
├── README.md
└── LICENSE
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

## CLI Command Structure

### Key Management

- `cloudcode add` - Add new API key (interactive)
- `cloudcode list [--service SERVICE] [--tag TAG]` - List keys with filters
- `cloudcode show KEY_NAME` - Show key details
- `cloudcode update KEY_NAME` - Update key value or metadata
- `cloudcode delete KEY_NAME` - Delete key
- `cloudcode use` - Interactive key selection

### Export

- `cloudcode export KEY_NAME` - Export single key
- `cloudcode export --all` - Export all keys
- `cloudcode export --service SERVICE` - Export by service

### Backup/Restore

- `cloudcode backup [--password PASSWORD]` - Create backup
- `cloudcode backup list` - List available backups
- `cloudcode restore BACKUP_FILE` - Restore from backup

### Configuration

- `cloudcode config edit` - Edit settings.json interactively
- `cloudcode config show` - Display current settings
- `cloudcode config reset` - Reset to defaults

### Security

- `cloudcode security check` - Run security audit
- `cloudcode security fix` - Auto-fix permission issues

## Workflow Examples

### Adding a New API Key

1. User runs `cloudcode add`
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

1. User runs `cloudcode use`
2. Questionary displays filtered list of keys
3. User selects key with arrow keys
4. Options presented:
   - Copy to clipboard
   - Export to environment
   - Display value
   - Cancel

### Creating Backup

1. User runs `cloudcode backup`
2. Prompts for password (optional)
3. Creates encrypted archive
4. Displays success with backup location
5. Rich progress bar during encryption

## Security Considerations

### File Permissions

- `.env` must be 600 (owner read/write only)
- `keys_metadata.json` must be 600
- Backup files encrypted with user password

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
pip install cloud-code-api-manager
# or
pipx install cloud-code-api-manager
```

### Quick Start

```bash
# Add your first API key
cloudcode add

# List all keys
cloudcode list

# Use a key
cloudcode use

# Create backup
cloudcode backup
```

## License

MIT License

## Author

[Your Name]

## Contributing

See CONTRIBUTING.md for guidelines
