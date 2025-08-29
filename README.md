# clip_translate

A modern Python project with best practices.

## Features

- 🚀 Modern Python 3.12
- 📦 Dependency management with uv
- 🧪 Testing with pytest
- 📊 Code coverage reporting
- 🔍 Static analysis with ruff and mypy
- 🎨 Code formatting with black
- 📚 Documentation with mkdocs
- 🔧 Pre-commit hooks for code quality
- 🏗️ Type hints and validation with pydantic
- 🖥️  CLI with typer and rich
- 📝 Structured logging with loguru

## Installation

```bash
# Development installation
uv sync --dev
```

## Usage

```bash
# Run the CLI
clip_translate --help

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Format code
uv run black .

# Lint code
uv run ruff check .

# Type check
uv run mypy .
```

## Development

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run pre-commit on all files
uv run pre-commit run --all-files
```

## Project Structure

```
clip_translate/
├── src/clip_translate/          # Source code
│   ├── __init__.py
│   ├── cli.py                  # Command-line interface
│   └── core.py                 # Core functionality
├── tests/                      # Test files
│   ├── conftest.py
│   └── test_core.py
├── docs/                       # Documentation
├── scripts/                    # Utility scripts
├── pyproject.toml             # Project configuration
├── README.md
└── .gitignore
```

## License

MIT License - see LICENSE file for details.
