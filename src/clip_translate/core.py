"""Core translation logic shared between CLI and GUI."""

import asyncio
from typing import Dict, Tuple, Optional, Any
from loguru import logger

from .config import Config
from .engines import get_backend, TranslationBackend


class TranslationEngine:
    """Core translation engine with caching and language detection."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.cache: Dict[str, Tuple[str, str]] = {}
        self.converter = None
        self._backend = None
        self._init_backend()
    
    def _init_backend(self):
        """Initialize the translation backend."""
        engine = self.config.get_engine()
        engine_config = self.config.get_engine_config(engine)
        
        try:
            self._backend = get_backend(engine, **engine_config)
            logger.info(f"Initialized {engine} translation backend")
        except Exception as e:
            logger.error(f"Failed to initialize {engine} backend: {e}")
            # Fallback to Google Translate
            if engine != "google":
                logger.info("Falling back to Google Translate")
                self._backend = get_backend("google")
            else:
                raise
    
    def switch_engine(self, engine: str) -> bool:
        """Switch to a different translation engine."""
        try:
            engine_config = self.config.get_engine_config(engine)
            new_backend = get_backend(engine, **engine_config)
            
            # Validate the new backend
            if not new_backend.validate_config():
                logger.error(f"Invalid configuration for {engine} engine")
                return False
            
            self._backend = new_backend
            self.config.set_engine(engine)
            self.config.save_config()
            
            # Clear cache when switching engines
            self.cache.clear()
            
            logger.info(f"Switched to {engine} translation engine")
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch to {engine}: {e}")
            return False
        
    def validate_languages(self, src_lang: str, target_lang: str) -> None:
        """Validate that the source and target languages are supported."""
        supported = self._backend.get_supported_languages()
        if src_lang not in supported and src_lang != 'auto':
            raise ValueError(
                f"Unsupported source language: {src_lang}. "
                f"Supported languages are: {', '.join(supported.keys())}"
            )
        if target_lang not in supported:
            raise ValueError(
                f"Unsupported target language: {target_lang}. "
                f"Supported languages are: {', '.join(supported.keys())}"
            )
    
    def setup_japanese_converter(self, romaji: bool = False, hiragana: bool = False) -> bool:
        """Setup Japanese text converter for readings."""
        try:
            import pykakasi
            kks = pykakasi.kakasi()
            self.converter = kks.convert
            return True
        except ImportError:
            logger.warning("pykakasi not installed for Japanese readings")
            return False
    
    async def detect_language(self, text: str) -> Optional[str]:
        """Detect the language of the given text."""
        return await self._backend.detect_language(text)
    
    async def translate_text(
        self, 
        text: str, 
        source: str, 
        target: str,
        use_cache: bool = True
    ) -> Tuple[str, str, bool]:
        """
        Translate text from source to target language.
        
        Returns:
            Tuple of (translated_text, original_text, was_cached)
        """
        # Clean the input text
        original_lines = [line for line in text.strip().split('\n') if line.strip()]
        original_text = '\n'.join(original_lines)
        
        # Check cache
        if use_cache and text in self.cache:
            translated_text, _ = self.cache[text]
            return translated_text, original_text, True
        
        # Perform translation
        try:
            translated_text = await self._backend.translate(
                original_text, source=source, target=target
            )
            
            # Clean translated text
            translated_lines = [
                line for line in translated_text.strip().split('\n') 
                if line.strip()
            ]
            translated_text = '\n'.join(translated_lines)
            
            # Cache the result
            if use_cache:
                self.cache[text] = (translated_text, original_text)
            
            return translated_text, original_text, False
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise
    
    def get_japanese_reading(
        self, 
        text: str, 
        romaji: bool = False, 
        hiragana: bool = False
    ) -> Optional[str]:
        """Get Japanese reading (romaji or hiragana) for the text."""
        if not self.converter:
            return None
        
        lines = text.split('\n')
        reading_lines = []
        
        for line in lines:
            if line.strip():
                result = self.converter(line)
                
                if romaji:
                    # Convert to romaji
                    romaji_parts = []
                    for item in result:
                        if item['orig'] != item['hepburn']:
                            romaji_parts.append(item['hepburn'])
                        else:
                            romaji_parts.append(item['orig'])
                    reading_line = ' '.join(romaji_parts)
                else:  # hiragana
                    # Convert to hiragana
                    hiragana_parts = []
                    has_japanese = False
                    for item in result:
                        if item['orig'] != item['hira']:
                            has_japanese = True
                            hiragana_parts.append(item['hira'])
                        else:
                            hiragana_parts.append(item['orig'])
                    
                    if not has_japanese:
                        continue
                    reading_line = ''.join(hiragana_parts)
                
                reading_lines.append(reading_line)
        
        return '\n'.join(reading_lines) if reading_lines else None


def get_supported_languages(engine: Optional[str] = None) -> Dict[str, str]:
    """Get dictionary of supported language codes and names."""
    if engine:
        # Get languages for specific engine
        try:
            backend = get_backend(engine)
            return backend.get_supported_languages()
        except:
            pass
    
    # Default to Google Translate languages for compatibility
    from googletrans import LANGUAGES
    return LANGUAGES