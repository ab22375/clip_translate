# Development Commands

## Installation & Setup
```bash
# Install in development mode
uv pip install -e .

# Install development dependencies
uv sync --dev
```

## Code Quality & Testing
```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=src

# Linting
ruff check .
ruff check . --fix  # Auto-fix issues

# Formatting
black .
ruff format .

# Type checking
mypy src/

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

## Running the Application
```bash
# CLI version
clip_translate --help
clip_translate translate -s ja -t en
clip_translate translate -s ja -t en --romaji --once

# GUI version
clip_translate_gui --help
clip_translate_gui -s ja -t en --romaji
```

## Development Tools
```bash
# Documentation
mkdocs serve    # Serve docs locally
mkdocs build    # Build docs

# Performance profiling
python -m memory_profiler script.py
```

## System Commands (macOS)
```bash
# Standard Unix tools available
ls, cd, grep, find, git
# Use rg (ripgrep) instead of grep when possible
```