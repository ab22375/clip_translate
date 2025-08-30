# Project Overview - clip_translate

## Purpose
`clip_translate` is a Python application that monitors clipboard content and automatically translates text between languages. It provides dual interfaces: a CLI tool and a modern GUI application. The project is particularly optimized for Japanese translations with support for romaji and hiragana readings.

## Key Features
- **Dual Interface**: CLI tool (`clip_translate`) and floating window GUI (`clip_translate_gui`)
- Continuous clipboard monitoring and automatic translation
- Language detection to filter content by source language
- Japanese text support with romaji/hiragana readings via `pykakasi`
- One-time translation mode (CLI only)
- Translation caching for performance
- Multiple translation backends: Google Translate, OpenAI, DeepL, Claude
- Rich terminal output with colors (CLI) and modern dark UI (GUI)
- Always-on-top floating window with adjustable opacity (GUI)

## Tech Stack
- **Language**: Python 3.12+
- **Build System**: hatchling
- **Package Manager**: uv
- **CLI Framework**: typer + rich
- **GUI Framework**: PyQt6
- **Async**: asyncio for translation operations
- **Logging**: loguru
- **Japanese Processing**: pykakasi
- **Clipboard**: pyperclip
- **Translation APIs**: googletrans, openai, deepl, anthropic
- **Config Management**: pydantic + python-dotenv

## Architecture
- **Core Engine**: `TranslationEngine` class in `core.py` handles all translation logic
- **CLI**: Direct async operations with typer CLI framework
- **GUI**: QThread workers for non-blocking UI with PyQt6
- **Backends**: Pluggable translation backend system (Google, OpenAI, DeepL, Claude)
- **Configuration**: Centralized config system with environment variable support