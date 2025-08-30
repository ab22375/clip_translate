# Project Instructions for Claude

## Project Overview
`clip_translate` is a Python application that monitors clipboard content and automatically translates text between languages using multiple translation engines (Google Translate, OpenAI, DeepL, Claude). It comes in two forms: a CLI tool and a modern GUI application. The application is particularly optimized for Japanese translations with support for romaji and hiragana readings.

## Key Features
- **Dual Interface**: Both CLI and floating window GUI options
- **Multiple Translation Engines**: Google Translate, OpenAI, DeepL, Claude
- **Configuration Management**: Persistent settings with config file and environment variables
- **Settings GUI**: Configuration dialog for engine settings and API keys
- Continuous clipboard monitoring and translation
- Language detection to only translate matching source language
- Japanese text support with romaji/hiragana readings
- One-time translation mode (CLI only)
- Translation caching for performance
- Rich terminal output with colors (CLI) and modern dark UI (GUI)
- Always-on-top floating window with adjustable opacity (GUI)
- Draggable, resizable interface optimized for macOS (GUI)

## Development Setup
```bash
# Install in development mode
uv pip install -e .

# Set up API keys (optional, for non-Google engines)
export OPENAI_API_KEY="your-openai-key"
export DEEPL_API_KEY="your-deepl-key"
export ANTHROPIC_API_KEY="your-claude-key"

# Run the CLI
clip_translate --help

# Run the GUI
clip_translate_gui --help
```

## Configuration
The application uses a configuration file at `~/.clip_translate/config.json` and supports environment variables:

### Engines Available:
- **google**: Free, no API key required (default)
- **openai**: Requires OPENAI_API_KEY
- **deepl**: Requires DEEPL_API_KEY  
- **claude**: Requires ANTHROPIC_API_KEY

### CLI Configuration:
```bash
# Configure via CLI
clip_translate configure

# Or set engine directly
clip_translate translate --engine openai -s ja -t en
```

### GUI Configuration:
Use the settings dialog in the GUI to configure engines and API keys.

## Code Style & Conventions
- **CLI**: Use `typer` for CLI commands, `rich.console` for terminal output
- **GUI**: Use `PyQt6` for GUI components, async workers for non-blocking translations
- Use `loguru` for logging across both CLI and GUI (not Python's logging module)
- Use `asyncio` for async operations with Google Translate
- **Architecture**: Shared `core.py` module contains translation logic used by both CLI and GUI
- Follow existing code patterns in `cli.py` and `gui.py`

## Testing Commands

### CLI Commands
```bash
# Basic translation
clip_translate translate -s es -t en

# Japanese with readings
clip_translate translate -s ja -t en --show-original --romaji

# One-time translation
clip_translate translate -s ja -t en --once
```

### GUI Commands
```bash
# Basic GUI
clip_translate_gui -s ja -t en

# GUI with romaji readings
clip_translate_gui -s ja -t en --romaji

# GUI with hiragana readings  
clip_translate_gui -s ja -t en --hiragana
```

## Important Implementation Notes

### Language Detection
- Both CLI and GUI use Google Translate's detection API to verify clipboard content matches the source language
- Non-matching languages are skipped with a warning message
- GUI shows "Skipped" status for non-matching languages

### Japanese Text Processing
- Uses `pykakasi` library for Japanese text conversion
- Romaji uses Hepburn romanization system
- Hiragana conversion converts kanji to hiragana
- Only shows readings for actual Japanese text, not romanized text
- GUI displays readings in a dedicated purple-tinted text area

### Translation Architecture
- **Core Engine**: `TranslationEngine` class in `core.py` handles all translation logic
- **Multiple Backends**: Pluggable backend system supporting Google, OpenAI, DeepL, Claude
- **Configuration**: `Config` class manages settings, API keys, and engine selection
- **CLI**: Uses async loops directly for translation
- **GUI**: Uses `QThread` workers to prevent UI blocking with settings dialog
- **Event Loop Management**: GUI carefully manages asyncio loops to prevent "loop closed" errors

### Caching
- Translations are cached in memory during runtime
- Cache stores both translated and original text
- Cache status is shown in CLI output ([cached] vs [new]) and GUI status label

### GUI-Specific Implementation
- **Window Management**: Always-on-top, frameless window with custom title bar
- **Threading**: `TranslationWorker` runs in background thread using `QThread`
- **UI Updates**: All translation results update UI via Qt signals/slots
- **Clipboard Handling**: Timer-based clipboard monitoring (500ms intervals)
- **Language Filtering**: Original text only displayed after successful language detection
- **Text Interaction**: All text areas are non-selectable to prevent clipboard conflicts
- **Copy Control**: Translation copying only via dedicated button to avoid monitoring loops
- **Clean Shutdown**: Proper cleanup of threads, timers, and event loops on window close

## Common Issues & Solutions

1. **Command not found after installation**
   - Use `uv pip install -e .` instead of `uv add --editable .`
   - Commands are `clip_translate` and `clip_translate_gui` (with underscores)

2. **Japanese readings not working**
   - Ensure `pykakasi` is installed: `uv add pykakasi`
   - Check that source language is set to `ja`
   - Use `--romaji` or `--hiragana` flags

3. **GUI argument parsing errors**
   - Don't use `-h` for hiragana (conflicts with help), use `--hiragana` or `--hira`
   - Use `clip_translate_gui --help` to see all options

4. **GUI translation not appearing**
   - Check internet connection
   - Ensure clipboard contains text in the specified source language
   - Look for error messages in the status label

5. **GUI freezing or hanging**
   - This has been fixed by making text areas non-selectable
   - Users cannot select text, preventing CMD+C clipboard conflicts
   - Use only the "Copy Translation" button to copy results

6. **Application not closing properly**
   - This has been fixed with proper shutdown handling
   - Window close event properly terminates all background threads
   - Ctrl+C handling implemented for clean terminal exit

7. **Event loop errors in GUI**
   - This has been fixed in the current version with proper loop management
   - Background worker reuses event loops to prevent "loop closed" errors

8. **Empty lines in output**
   - Both CLI and GUI automatically remove empty lines from translations

## Project Structure
```
src/clip_translate/
├── __init__.py          # Package initialization
├── config.py            # Configuration management with pydantic
├── core.py              # Shared translation engine and logic
├── engines.py           # Translation backend implementations
├── cli.py               # CLI implementation with typer
├── gui.py               # GUI implementation with PyQt6
└── settings_dialog.py   # GUI settings dialog
```

## Dependencies
- `googletrans` - Google Translate API (async)
- `openai` - OpenAI API for GPT translations
- `deepl` - DeepL API for high-quality translations  
- `anthropic` - Claude API for AI translations
- `pyperclip` - Clipboard access
- `pykakasi` - Japanese text processing
- `typer` - CLI framework
- `rich` - Terminal formatting (CLI)
- `PyQt6` - GUI framework
- `loguru` - Logging
- `pydantic` - Configuration validation
- `python-dotenv` - Environment variable loading

## Future Improvements to Consider
- Add file input/output support for both CLI and GUI
- Add translation history saving and browsing
- Add system tray integration for GUI
- Add keyboard shortcuts for GUI controls
- Add support for multiple target languages simultaneously
- Create macOS app bundle with py2app
- Add dark/light mode toggle for GUI
- Add batch translation support
- Add more translation engines (Azure, Baidu, etc.)
- Add user-defined custom prompts for AI engines