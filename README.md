# clip_translate

A powerful clipboard translation tool that monitors your clipboard and automatically translates text between languages. Optimized for Japanese language learning with romaji and hiragana reading support.

## Features

- 🔄 **Continuous Monitoring**: Automatically detects and translates clipboard changes
- 🎯 **Smart Language Detection**: Only translates text matching your source language
- 🇯🇵 **Japanese Support**: Special features for Japanese including romaji and hiragana readings
- ⚡ **Translation Caching**: Caches translations for improved performance
- 🎨 **Rich Terminal Output**: Beautiful colored output with clear formatting
- 🔂 **Flexible Modes**: Choose between continuous monitoring or one-time translation

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

## Quick Start

### Basic Translation

Translate Spanish to English continuously:
```bash
clip_translate translate -s es -t en
```

### Japanese Translation with Readings

Translate Japanese to English with original text and romaji:
```bash
clip_translate translate -s ja -t en --show-original --romaji
```

### One-Time Translation

Translate clipboard content once and exit:
```bash
clip_translate translate -s ja -t en --once
```

## Usage

### Main Command

```bash
clip_translate translate [OPTIONS]
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--source` | `-s` | Source language code | `es` |
| `--target` | `-t` | Target language code | `en` |
| `--show-original` | `-o` | Show original text before translation | `False` |
| `--romaji` | `-r` | Show romaji reading for Japanese text | `False` |
| `--hiragana` | `-h` | Show hiragana reading for Japanese text | `False` |
| `--once` | | Translate only once instead of continuously | `False` |

### List Supported Languages

```bash
clip_translate languages
```

## Examples

### Continuous Japanese to English Translation
```bash
clip_translate translate -s ja -t en
```
Copy any Japanese text to your clipboard and it will be automatically translated to English.

### Japanese with Full Analysis
```bash
clip_translate translate -s ja -t en --show-original --romaji
```
Shows:
- Original Japanese text
- Romaji (romanized) reading
- English translation

### Quick One-Time Translation
```bash
clip_translate translate -s fr -t en --once
```
Translates French text in clipboard to English once and exits.

### Chinese to Spanish
```bash
clip_translate translate -s zh-cn -t es --show-original
```

## How It Works

1. **Clipboard Monitoring**: The tool continuously monitors your clipboard for changes
2. **Language Detection**: When new text is detected, it verifies the language matches your source setting
3. **Translation**: If the language matches, it translates the text using Google Translate
4. **Clipboard Update**: The translated text replaces the original in your clipboard
5. **Display**: Results are shown in the terminal with formatting

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
- Color-coded status indicators

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
│   ├── __init__.py
│   └── cli.py                  # CLI with all translation logic
├── tests/                      # Test files
├── docs/                       # Documentation
├── CLAUDE.md                   # Instructions for AI assistants
├── pyproject.toml             # Project configuration
├── README.md                   # This file
└── .gitignore
```

## Requirements

- Python 3.10+
- Internet connection for Google Translate API

## Troubleshooting

### Command not found
Make sure you've installed the package:
```bash
uv pip install -e .
```

### Japanese readings not showing
Install the Japanese processing library:
```bash
uv add pykakasi
```

### No translation happening
- Check that your clipboard contains text in the source language
- Verify internet connection
- Try with `--show-original` to see what's being detected

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Author

Created by ab@ab8.it