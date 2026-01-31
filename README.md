# CAPI (Cloud Code API Manager)

Interactive CLI tool for managing API keys with beautiful terminal UI and Claude Code settings integration.

## Features

### Currently Implemented

- **CRUD Operations**: Add, list, delete, and use API keys
- **Interactive Selection**: Beautiful terminal UI for key selection using Rich and Questionary
- **Claude Settings Management**: Automatic Claude Code settings.json generation and validation
- **Multi-Provider Support**: Built-in support for Anthropic, GLM, and Kimi API providers
- **Search & Filter**: Filter keys by provider, tag, or text search
- **Validation**: Comprehensive Claude Code configuration validation
- **Security**: File permission checks and secure storage in `~/.capi/`
- **Merge/Preview Modes**: Preview changes before applying, merge with existing settings

## Installation

```bash
pip install capi
# or
pipx install capi
```

## Quick Start

```bash
# Add your first API key
capi add

# List all keys
capi list

# List keys with filters
capi list --service anthropic
capi list --tag production
capi list --search "github"

# Use a key (interactive mode with preview/merge options)
capi use

# Use a key with specific options
capi use --name MY_API_KEY --merge
capi use --name MY_API_KEY --preview

# Delete a key
capi delete KEY_NAME

# Validate Claude Code settings
capi validate

# Show version
capi version
```

## Claude Settings Management

The tool includes comprehensive Claude Code settings.json management:

### Automatic Settings Creation

When validation fails, the tool offers to create a new settings.json file with sensible defaults:

```bash
capi validate
# If settings.json is missing, you'll be prompted:
# Do you want to create a new settings file? (y/n):
```

### Provider Configuration

Supports multiple API providers with pre-configured models:

| Provider | Base URL | Models |
|----------|----------|--------|
| **Anthropic** | `https://api.anthropic.com` | claude-3-haiku-20240307, claude-3-5-sonnet-20241022, claude-3-opus-20240229 |
| **GLM** | `https://api.z.ai/api/anthropic` | glm-4.5, glm-4.6, glm-4.7 |
| **Kimi** | `https://api.kimi.com/coding/` | K2.5 |

### Features

- Automatic settings.json generation with proper structure
- Backup of existing settings before modification
- Merge mode to preserve existing settings
- Preview mode to see changes before applying
- Environment variable validation
- Model configuration per provider
- Base URL management for different providers

## Available Commands

### Currently Implemented

| Command | Description | Options |
|---------|-------------|---------|
| `capi add` | Add new API key (interactive) | `--name`, `--provider`, `--interactive/--no-interactive` |
| `capi list` | List keys with filters | `--service`, `--tag`, `--search` |
| `capi delete` | Delete a key | `--name`, `--interactive/--no-interactive` |
| `capi use` | Interactive key selection and activation | `--name`, `--interactive/--no-interactive`, `--merge`, `--preview` |
| `capi validate` | Validate Claude Code settings.json | `--report` (JSON output) |
| `capi version` | Show version information | - |

## Project Structure

The project is organized into several key modules:

```
capi/
├── cli/                    # Command-line interface
│   ├── main.py            # Typer app entry point
│   └── commands/          # Command implementations
│       ├── add.py
│       ├── delete.py
│       ├── list.py
│       ├── use.py
│       └── validate.py
├── core/                   # Business logic
│   ├── models.py          # Pydantic data models
│   ├── key_manager.py     # API key CRUD operations
│   ├── metadata_manager.py # Metadata operations
│   ├── export_manager.py  # Claude settings export
│   └── validators.py      # Validation logic
├── constans/              # Constants (note: "constans" not "constants")
│   ├── providers.py       # Provider type definitions
│   ├── providerModel.py   # Model configurations
│   └── providerUrl.py     # Base URL management
├── storage/               # File handling
│   ├── env_handler.py     # .env file operations
│   └── metadata_handler.py # JSON metadata operations
├── ui/                    # User interface
│   └── display.py         # Rich display utilities
└── utils/                 # Common utilities
    ├── crypto.py          # Encryption utilities
    ├── helpers.py         # Common utilities
    └── shell.py           # Shell command generators
```

## Storage

API keys and metadata are stored securely in your home directory:

- **API Keys**: `~/.capi/.env` (600 permissions)
- **Metadata**: `~/.capi/keys_metadata.json` (key name, provider, description, tags, status)
- **Claude Settings**: `~/.claude/settings.json` (or path specified by `DEFAULT_CLAUDE_DIR` env var)

## Environment Configuration

You can customize the Claude Code settings directory by setting the `DEFAULT_CLAUDE_DIR` environment variable in `~/.capi/.env`:

```bash
DEFAULT_CLAUDE_DIR="/home/user/.claude"
```

## Documentation

- **README.md** (this file) - Overview and quick start guide
- [**ARCHITECTURE.md**](ARCHITECTURE.md) - Detailed architecture and implementation documentation

## License

MIT License
