# clip_translate

A powerful clipboard translation tool that monitors your clipboard and automatically translates text between languages using multiple AI engines (Google Translate, OpenAI, DeepL, Claude). Available as both a command-line tool and a modern floating window GUI, optimized for Japanese language learning with romaji and hiragana reading support.

## Features

- 🖥️ **Dual Interface**: Choose between CLI and floating window GUI
- 🤖 **Multiple AI Engines**: Google Translate, OpenAI, DeepL, Claude support
- ⚙️ **Easy Configuration**: Settings dialog and config file management  
- 🔄 **Continuous Monitoring**: Automatically detects and translates clipboard changes
- 🎯 **Smart Language Detection**: Only translates text matching your source language
- 🇯🇵 **Japanese Support**: Special features for Japanese including romaji and hiragana readings
- ⚡ **Translation Caching**: Caches translations for improved performance
- 🎨 **Rich Output**: Beautiful colored terminal output (CLI) and modern dark UI (GUI)
- 🔂 **Flexible Modes**: Choose between continuous monitoring or one-time translation
- 🪟 **Floating Window**: Always-on-top, draggable, semi-transparent window (GUI)
- 🎛️ **Adjustable Opacity**: Customize window transparency for your workflow
- 🛡️ **Stability**: Non-selectable text prevents freezing, controlled clipboard access
- 🔄 **Clean Shutdown**: Proper thread management and graceful exit handling

## Installation

```bash
# Clone the repository
git clone https://github.com/ab/clip_translate.git
cd clip_translate

# Install with uv (recommended)
uv pip install -e .

# Or install with pip
pip install -e .
```

## Configuration

### API Keys (Optional)
For engines other than Google Translate, you'll need API keys:

```bash
# Set environment variables
export OPENAI_API_KEY="your-openai-key"
export DEEPL_API_KEY="your-deepl-key" 
export ANTHROPIC_API_KEY="your-claude-key"
```

### Available Engines
- **Google Translate** (default): Free, no setup required
- **OpenAI**: Requires OpenAI API key, uses GPT models
- **DeepL**: Requires DeepL API key, high translation quality
- **Claude**: Requires Anthropic API key, AI-powered translations

### Configuration Options
- **CLI**: Use `clip_translate configure` or `--engine` flag
- **GUI**: Use the settings dialog (⚙️ button) to configure engines
- **Config file**: Automatically saved to `~/.clip_translate/config.json`

## Quick Start

### GUI (Floating Window)

Launch the modern floating window interface:
```bash
# Basic Japanese to English GUI
clip_translate_gui -s ja -t en

# GUI with romaji readings
clip_translate_gui -s ja -t en --romaji

# GUI with hiragana readings
clip_translate_gui -s ja -t en --hiragana
```

### CLI (Command Line)

Use the terminal interface:
```bash
# Basic translation
clip_translate translate -s es -t en

# Japanese with readings
clip_translate translate -s ja -t en --show-original --romaji

# One-time translation (no continuous monitoring)
clip_translate translate -s ja -t en --once
```

## Usage

### GUI Commands

```bash
# Launch floating window
clip_translate_gui [OPTIONS]
```

**GUI Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--source` | `-s` | Source language code | `ja` |
| `--target` | `-t` | Target language code | `en` |
| `--romaji` | `-r` | Show romaji reading for Japanese text | `False` |
| `--hiragana` | `--hira` | Show hiragana reading for Japanese text | `False` |

### CLI Commands

```bash
# Run terminal translation
clip_translate translate [OPTIONS]

# Configure settings
clip_translate configure
```

**CLI Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--source` | `-s` | Source language code | `es` |
| `--target` | `-t` | Target language code | `en` |
| `--engine` | `-e` | Translation engine (google/openai/deepl/claude) | `google` |
| `--show-original` | `-o` | Show original text before translation | `False` |
| `--romaji` | `-r` | Show romaji reading for Japanese text | `False` |
| `--hiragana` | `-h` | Show hiragana reading for Japanese text | `False` |
| `--once` | | Translate only once instead of continuously | `False` |

### List Supported Languages

```bash
clip_translate languages
```

## Examples

### GUI Examples

**Japanese Learning with Floating Window:**
```bash
clip_translate_gui -s ja -t en --romaji
```
- Opens a large, readable floating window
- Shows original Japanese text
- Displays romaji pronunciation
- Shows English translation
- Window stays on top of other apps

**Basic GUI Translation:**
```bash
clip_translate_gui -s es -t en
```
- Floating window for Spanish to English
- Clean, modern dark interface
- Drag to position anywhere on screen
- Adjust opacity with slider

### CLI Examples

**Terminal Translation with Full Japanese Analysis:**
```bash
clip_translate translate -s ja -t en --show-original --romaji
```
Shows in terminal:
- Original Japanese text
- Romaji (romanized) reading  
- English translation

**Using Different Translation Engines:**
```bash
# Use OpenAI for translation
clip_translate translate -s ja -t en --engine openai

# Use DeepL for high-quality translation
clip_translate translate -s fr -t en --engine deepl

# Use Claude for AI-powered translation
clip_translate translate -s zh-cn -t en --engine claude
```

**Quick One-Time Translation:**
```bash
clip_translate translate -s fr -t en --once
```
Translates French text in clipboard to English once and exits.

**Continuous Background Translation:**
```bash
clip_translate translate -s zh-cn -t es --show-original
```
Continuously monitors clipboard for Chinese text and translates to Spanish.

## How It Works

### GUI Mode
1. **Floating Window**: Opens a modern, always-on-top floating window
2. **Clipboard Monitoring**: Continuously monitors clipboard changes (every 500ms)
3. **Language Detection**: Verifies clipboard content matches your source language
4. **Smart Display**: Only shows original text if language matches
5. **Translation**: Translates using selected engine (Google/OpenAI/DeepL/Claude) in background thread
6. **Reading Generation**: Creates romaji/hiragana readings for Japanese (if enabled)
7. **Visual Feedback**: Updates window with original, reading, and translated text
8. **Engine Selection**: Choose translation engine via settings dialog
9. **Manual Copy**: Use "Copy Translation" button to copy result to clipboard

### CLI Mode  
1. **Terminal Monitoring**: Runs in terminal with continuous clipboard monitoring
2. **Language Detection**: Verifies clipboard content matches source language
3. **Translation**: Translates matching text using selected engine
4. **Auto-Replace**: Translated text replaces original in clipboard  
5. **Rich Display**: Shows results in terminal with color formatting
6. **Engine Configuration**: Set via `--engine` flag or `clip_translate configure`

## Language Codes

Common language codes:
- `en` - English
- `ja` - Japanese
- `zh-cn` - Chinese (Simplified)
- `zh-tw` - Chinese (Traditional)
- `ko` - Korean
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `ru` - Russian
- `ar` - Arabic
- `hi` - Hindi

Use `clip_translate languages` to see all supported languages.

## Features in Detail

### Smart Language Detection
The tool only translates text that matches your specified source language. If you copy English text while translating from Japanese, it will be skipped.

### Japanese Reading Support
For Japanese learners, the tool provides:
- **Romaji**: Romanized pronunciation using Hepburn system
- **Hiragana**: Converts kanji to hiragana for reading practice

### Translation Caching
Previously translated text is cached during the session for instant retrieval.

### Clean Output
- Automatically removes empty lines from translations
- Clear visual separation between translations
- Color-coded status indicators (CLI) and visual status labels (GUI)

### GUI-Specific Features
- **Modern Interface**: Dark theme optimized for macOS
- **Window Controls**: Always-on-top, draggable, adjustable opacity
- **Large Text Areas**: 1050x910px window for comfortable reading
- **Reading Display**: Dedicated purple area for Japanese romaji/hiragana
- **Status Indicators**: Real-time status updates (Detecting, Translating, Cached, etc.)
- **Language Dropdowns**: Easy switching between language pairs
- **Controlled Copying**: Copy button prevents clipboard monitoring conflicts
- **Non-Selectable Text**: Prevents system freezing from CMD+C conflicts
- **Persistent Display**: Text remains visible after copying for reference

## Development

```bash
# Development installation
uv sync --dev

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

## Project Structure

```
clip_translate/
├── src/clip_translate/          # Source code
│   ├── __init__.py             # Package initialization
│   ├── config.py               # Configuration management
│   ├── core.py                 # Shared translation engine
│   ├── engines.py              # Translation backend implementations
│   ├── cli.py                  # CLI interface with typer
│   ├── gui.py                  # GUI interface with PyQt6
│   └── settings_dialog.py      # GUI settings dialog
├── tests/                      # Test files  
├── docs/                       # Documentation
├── CLAUDE.md                   # Instructions for AI assistants
├── README.md                   # This file
├── pyproject.toml              # Project configuration
└── .gitignore
```

## Requirements

- Python 3.12+
- Internet connection for translation APIs
- Optional: API keys for OpenAI, DeepL, or Claude

## Troubleshooting

### Commands not found
Make sure you've installed the package:
```bash
uv pip install -e .
```
Available commands: `clip_translate` and `clip_translate_gui`

### Japanese readings not showing  
Install the Japanese processing library:
```bash
uv add pykakasi
```
Then use `--romaji` or `--hiragana` flags.

### GUI not launching or crashing
- Ensure PyQt6 is installed (should be automatic)
- Try running with `--help` first to test argument parsing
- Check for error messages in terminal

### GUI freezing or system hanging
- **Fixed**: Text areas are now non-selectable to prevent CMD+C conflicts
- Use only the "Copy Translation" button to copy results
- Text cannot be manually selected to avoid clipboard monitoring loops

### Application not closing properly
- **Fixed**: Proper shutdown handling implemented
- Window close button terminates all background processes
- Ctrl+C in terminal now exits cleanly without errors

### No translation happening
**GUI:**
- Check internet connection
- Ensure clipboard contains text in the specified source language
- Look at status label for error messages
- Try different text or restart the application

**CLI:**
- Check clipboard contains text in source language
- Verify internet connection  
- Try with `--show-original` to see what's being detected

### GUI argument errors
- Don't use `-h` for hiragana (conflicts with help)
- Use `--hiragana` or `--hira` instead
- Use `clip_translate_gui --help` to see all options

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Author

Created by ab@ab8.it