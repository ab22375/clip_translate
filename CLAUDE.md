# Project Instructions for Claude

## Project Overview
`clip_translate` is a Python CLI tool that monitors clipboard content and automatically translates text between languages using Google Translate. It's particularly optimized for Japanese translations with support for romaji and hiragana readings.

## Key Features
- Continuous clipboard monitoring and translation
- Language detection to only translate matching source language
- Japanese text support with romaji/hiragana readings
- One-time translation mode
- Translation caching for performance
- Rich terminal output with colors

## Development Setup
```bash
# Install in development mode
uv pip install -e .

# Run the CLI
clip_translate --help
```

## Code Style & Conventions
- Use `typer` for CLI commands (not argparse or click)
- Use `rich.console` for terminal output
- Use `loguru` for logging (not Python's logging module)
- Use `asyncio` for async operations with Google Translate
- Follow existing code patterns in `cli.py`

## Testing Commands
```bash
# Basic translation
clip_translate translate -s es -t en

# Japanese with readings
clip_translate translate -s ja -t en --show-original --romaji

# One-time translation
clip_translate translate -s ja -t en --once
```

## Important Implementation Notes

### Language Detection
- The tool uses Google Translate's detection API to verify clipboard content matches the source language
- Non-matching languages are skipped with a warning message

### Japanese Text Processing
- Uses `pykakasi` library for Japanese text conversion
- Romaji uses Hepburn romanization
- Hiragana conversion converts kanji to hiragana
- Only shows readings for actual Japanese text, not romanized text

### Caching
- Translations are cached in memory during runtime
- Cache stores both translated and original text
- Cache status is shown in the output ([cached] vs [new])

## Common Issues & Solutions

1. **Command not found after installation**
   - Use `uv pip install -e .` instead of `uv add --editable .`
   - The command is `clip_translate` (with underscore)

2. **Japanese readings not working**
   - Ensure `pykakasi` is installed: `uv add pykakasi`
   - Check that source language is set to `ja`

3. **Empty lines in output**
   - The tool automatically removes empty lines from both original and translated text

## Project Structure
```
src/clip_translate/
├── __init__.py     # Package initialization
└── cli.py          # Main CLI implementation with all commands
```

## Dependencies
- `googletrans` - Google Translate API (async)
- `pyperclip` - Clipboard access
- `pykakasi` - Japanese text processing
- `typer` - CLI framework
- `rich` - Terminal formatting
- `loguru` - Logging

## Future Improvements to Consider
- Add support for translation APIs other than Google
- Add file input/output support
- Add translation history saving
- Add support for multiple target languages simultaneously
- Add automatic language pair detection