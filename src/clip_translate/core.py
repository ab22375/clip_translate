"""Core translation logic shared between CLI and GUI."""

import asyncio
from typing import Dict, Tuple, Optional, Any
from googletrans import Translator, LANGUAGES
from loguru import logger


class TranslationEngine:
    """Core translation engine with caching and language detection."""
    
    def __init__(self):
        self.translator = Translator()
        self.cache: Dict[str, Tuple[str, str]] = {}
        self.converter = None
        
    def validate_languages(self, src_lang: str, target_lang: str) -> None:
        """Validate that the source and target languages are supported."""
        if src_lang not in LANGUAGES.keys():
            raise ValueError(
                f"Unsupported source language: {src_lang}. "
                f"Supported languages are: {', '.join(LANGUAGES.keys())}"
            )
        if target_lang not in LANGUAGES.keys():
            raise ValueError(
                f"Unsupported target language: {target_lang}. "
                f"Supported languages are: {', '.join(LANGUAGES.keys())}"
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
        try:
            detection = await self.translator.detect(text.strip())
            return detection.lang
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return None
    
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
            translated = await self.translator.translate(
                original_text, src=source, dest=target
            )
            
            # Clean translated text
            translated_lines = [
                line for line in translated.text.strip().split('\n') 
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


def get_supported_languages() -> Dict[str, str]:
    """Get dictionary of supported language codes and names."""
    return LANGUAGES