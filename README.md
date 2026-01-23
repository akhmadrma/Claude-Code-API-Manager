# Cloud Code API Manager

Interactive CLI tool for managing API keys with beautiful terminal UI.

## Features

- **CRUD Operations**: Add, view, update, and delete API keys
- **Interactive Selection**: Beautiful terminal UI for key selection
- **Environment Export**: Export keys to shell environment variables
- **Backup & Restore**: Encrypted backup functionality
- **Search & Filter**: Find keys by service, tags, or text
- **Security**: File permission checks and Git safety features

## Installation

```bash
pip install cloud-code-api-manager
# or
pipx install cloud-code-api-manager
```

## Quick Start

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

## Documentation

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## License

MIT License
