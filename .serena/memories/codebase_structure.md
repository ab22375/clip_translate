# Codebase Structure

## Project Layout
```
src/clip_translate/
├── __init__.py          # Package initialization with version info
├── config.py            # Configuration management with pydantic
├── core.py              # Core TranslationEngine class (shared logic)
├── engines.py           # Translation backend implementations
├── cli.py               # CLI implementation with typer
├── gui.py               # GUI implementation with PyQt6
└── settings_dialog.py   # GUI settings dialog
```

## Entry Points
- `clip_translate` → `clip_translate.cli:main`
- `clip_translate_gui` → `clip_translate.gui:main`

## Key Components

### Core Engine (`core.py`)
- **TranslationEngine**: Main translation orchestrator
  - Manages translation backends
  - Handles caching
  - Language detection and validation
  - Japanese text processing (romaji/hiragana)

### Translation Backends (`engines.py`)
- **TranslationBackend**: Abstract base class
- **GoogleTranslateBackend**: Google Translate API
- **OpenAIBackend**: OpenAI API
- **DeepLBackend**: DeepL API  
- **ClaudeBackend**: Anthropic Claude API
- **get_backend()**: Factory function

### CLI (`cli.py`)
- Uses typer for command structure
- Rich console for formatting
- Async translation loop
- Command: `translate`, `languages`, `configure`

### GUI (`gui.py`)
- **FloatingTranslator**: Main GUI window class
- **TranslationWorker**: QThread for background translation
- Always-on-top floating window
- Timer-based clipboard monitoring

### Configuration (`config.py`)
- **Config**: Pydantic model for settings
- Environment variable support
- API key management