# CAPIM (Cloud Code API Manager)

Interactive CLI tool for managing API keys with beautiful terminal UI and Claude Code settings integration.

## Features

### Currently Implemented

- **CRUD Operations**: Add, list, delete, and use API keys
- **Interactive Selection**: Beautiful terminal UI for key selection using Rich and Questionary
- **Claude Settings Management**: Automatic Claude Code settings.json generation and validation
- **Multi-Provider Support**: Built-in support for Anthropic and GLM API providers
- **Validation**: Comprehensive Claude Code configuration validation
- **Security**: File permission checks and Git safety features

### Planned Features (Not Yet Implemented)

- Environment Export: Export keys to shell environment variables
- Backup & Restore: Encrypted backup functionality for both API keys and settings
- Search & Filter: Find keys by service, tags, or text
- Update operations: Modify existing API key values or metadata
- Show command: Display individual API key details

## Installation

```bash
pip install capim
# or
pipx install capim
```

## Quick Start

```bash
# Add your first API key
capi add

# List all keys
capi list

# Use a key
capi use

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

- **Anthropic**: claude-3-haiku, claude-3.5-sonnet, claude-3-opus
- **GLM**: glm-4.5, glm-4.6, glm-4.7

### Features

- Automatic settings.json generation with proper structure
- Backup of existing settings before modification
- Environment variable validation
- Model configuration per provider
- Base URL management for different providers

## Available Commands

### Currently Implemented

- `capi add` - Add new API key (interactive)
- `capi list` - List keys with filters
- `capi delete KEY_NAME` - Delete key
- `capi use` - Interactive key selection
- `capi validate` - Validate Claude Code settings.json
- `capi validate --report` - Display validation report as JSON
- `capi version` - Show version information

### Planned Commands

- `capi show KEY_NAME` - Show key details
- `capi update KEY_NAME` - Update key value or metadata
- `capi export KEY_NAME` - Export single key
- `capi export --all` - Export all keys
- `capi backup [--password PASSWORD]` - Create backup
- `capi config edit` - Edit settings.json interactively
- `capi security check` - Run security audit

## Project Structure

The project is organized into several key modules:

- **cli/**: Command-line interface and command implementations
- **core/**: Business logic, data models, and validation
- **constans/**: Provider and settings constants (note: "constans" not "constants")
- **storage/**: File handling for .env, metadata, and settings
- **ui/**: Rich display utilities and user interface components
- **utils/**: Common utilities for encryption, shell commands, etc.

## Documentation

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## License

MIT License
