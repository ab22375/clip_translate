# Style and Conventions

## Code Style
- **Line length**: 88 characters (Black standard)
- **Python version**: 3.12+
- **Quote style**: Double quotes
- **Indentation**: 4 spaces

## Linting & Formatting
- **Formatter**: Black + Ruff format
- **Linter**: Ruff (replaces flake8, isort, pyupgrade)
- **Type checker**: MyPy with strict settings

## Type Hints
- **Required**: All functions must have type hints
- **Strict mode**: MyPy configured with strict settings
- **Generic types**: Disallow `Any` types where possible

## Naming Conventions
- **Functions/variables**: snake_case
- **Classes**: PascalCase
- **Constants**: UPPER_SNAKE_CASE
- **Private attributes**: Leading underscore

## Architecture Patterns
- **Async/await**: Used for translation operations
- **Dependency injection**: Backends passed to TranslationEngine
- **Shared core**: Common logic in `core.py` used by CLI and GUI
- **Threading**: QThread for GUI background operations
- **Caching**: In-memory translation cache

## Import Organization
- Standard library imports first
- Third-party imports second
- Local imports last
- Use `from` imports sparingly

## Logging
- Use `loguru` instead of Python's `logging` module
- Consistent log levels and formatting
- No print statements in production code

## Error Handling
- Use specific exception types
- Proper async exception handling
- User-friendly error messages for CLI/GUI