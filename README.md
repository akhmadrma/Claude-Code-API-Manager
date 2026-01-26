# CAPI (Cloud Code API Manager)

Interactive CLI tool for managing API keys with beautiful terminal UI and Claude Code settings integration.

## Features

### Currently Implemented

- **CRUD Operations**: Add, list, delete, and use API keys
- **Interactive Selection**: Beautiful terminal UI for key selection using Rich and Questionary
- **Claude Settings Management**: Automatic Claude Code settings.json generation and validation
- **Multi-Provider Support**: Built-in support for Anthropic and GLM API providers
- **Search & Filter**: Filter keys by provider, tag, or text search
- **Validation**: Comprehensive Claude Code configuration validation
- **Security**: File permission checks and Git safety features

## Installation

```bash
pip install capi
# or
pipx install capi
```

## Quick Start

```bash
# Copy .env.example to .env and you can customize claude dir
cp .env.example .env

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
- `capi list` - List keys with filters (--provider, --tag, --search)
- `capi delete KEY_NAME` - Delete key
- `capi use` - Interactive key selection and activation
- `capi validate` - Validate Claude Code settings.json
- `capi validate --report` - Display validation report as JSON
- `capi version` - Show version information

## Project Structure

The project is organized into several key modules:

- **cli/**: Command-line interface and command implementations
- **core/**: Business logic, data models, and validation
- **constans/**: Provider and settings constants (note: "constans" not "constants")
- **storage/**: File handling for .env, metadata, and settings
- **ui/**: Rich display utilities and user interface components
- **utils/**: Common utilities for encryption, shell commands, etc.

## Documentation

- **README.md** (this file) - Overview and quick start guide
- [**ARCHITECTURE.md**](ARCHITECTURE.md)  - Detailed architecture and implementation documentation

## License

MIT License
