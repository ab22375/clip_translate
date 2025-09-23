"""Translation engine implementations."""

import asyncio
import os
from abc import ABC, abstractmethod

from loguru import logger


class TranslationBackend(ABC):
    """Abstract base class for translation backends."""

    @abstractmethod
    async def detect_language(self, text: str) -> str | None:
        """Detect the language of the given text."""
        pass

    @abstractmethod
    async def translate(self, text: str, source: str, target: str) -> str:
        """Translate text from source to target language."""
        pass

    @abstractmethod
    def get_supported_languages(self) -> dict[str, str]:
        """Get dictionary of supported language codes and names."""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate that the backend is properly configured."""
        pass


class GoogleTranslateBackend(TranslationBackend):
    """Google Translate backend using googletrans library."""

    def __init__(self):
        from googletrans import LANGUAGES, Translator

        self.translator = Translator()
        self.languages = LANGUAGES

    async def detect_language(self, text: str) -> str | None:
        """Detect the language of the given text."""
        try:
            detection = await self.translator.detect(text.strip())
            return detection.lang
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return None

    async def translate(self, text: str, source: str, target: str) -> str:
        """Translate text from source to target language."""
        try:
            result = await self.translator.translate(text, src=source, dest=target)
            return result.text
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise

    def get_supported_languages(self) -> dict[str, str]:
        """Get dictionary of supported language codes and names."""
        return self.languages

    def validate_config(self) -> bool:
        """Google Translate doesn't require configuration."""
        return True


class OpenAIBackend(TranslationBackend):
    """OpenAI GPT-based translation backend."""

    # Language mapping for OpenAI (common languages)
    LANGUAGES = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "ja": "Japanese",
        "ko": "Korean",
        "zh-cn": "Chinese (Simplified)",
        "zh-tw": "Chinese (Traditional)",
        "ar": "Arabic",
        "hi": "Hindi",
        "nl": "Dutch",
        "pl": "Polish",
        "tr": "Turkish",
        "sv": "Swedish",
        "da": "Danish",
        "no": "Norwegian",
        "fi": "Finnish",
        "el": "Greek",
        "he": "Hebrew",
        "th": "Thai",
        "vi": "Vietnamese",
        "id": "Indonesian",
        "ms": "Malay",
        "cs": "Czech",
        "hu": "Hungarian",
        "ro": "Romanian",
        "uk": "Ukrainian",
        "bg": "Bulgarian",
        "hr": "Croatian",
        "sr": "Serbian",
        "sk": "Slovak",
        "sl": "Slovenian",
        "lt": "Lithuanian",
        "lv": "Latvian",
        "et": "Estonian",
        "fa": "Persian",
        "ur": "Urdu",
        "bn": "Bengali",
        "ta": "Tamil",
        "te": "Telugu",
        "mr": "Marathi",
        "gu": "Gujarati",
        "sw": "Swahili",
        "af": "Afrikaans",
        "ca": "Catalan",
        "eu": "Basque",
        "ga": "Irish",
        "cy": "Welsh",
        "is": "Icelandic",
        "mk": "Macedonian",
        "sq": "Albanian",
        "mt": "Maltese",
        "tl": "Filipino",
        "auto": "Auto-detect",
    }

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize OpenAI client."""
        if self.api_key:
            try:
                from openai import AsyncOpenAI

                self.client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                logger.error("OpenAI library not installed. Run: pip install openai")
                self.client = None

    async def detect_language(self, text: str) -> str | None:
        """Detect the language of the given text."""
        if not self.client:
            return None

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a language detection system. Respond with ONLY the ISO 639-1 language code (e.g., 'en', 'es', 'ja'). If unsure, respond with 'unknown'.",
                    },
                    {
                        "role": "user",
                        "content": f"What language is this text written in? Text: {text[:500]}",
                    },
                ],
                temperature=0,
                max_tokens=10,
            )

            lang_code = response.choices[0].message.content.strip().lower()
            return lang_code if lang_code in self.LANGUAGES else None

        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return None

    async def translate(self, text: str, source: str, target: str) -> str:
        """Translate text from source to target language."""
        if not self.client:
            raise ValueError("OpenAI client not initialized. Check API key.")

        source_name = self.LANGUAGES.get(source, source)
        target_name = self.LANGUAGES.get(target, target)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator. Translate text from {source_name} to {target_name}. Maintain the original formatting and style. Only provide the translation, no explanations.",
                    },
                    {"role": "user", "content": text},
                ],
                temperature=0.3,
                max_tokens=4096,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise

    def get_supported_languages(self) -> dict[str, str]:
        """Get dictionary of supported language codes and names."""
        return self.LANGUAGES

    def validate_config(self) -> bool:
        """Validate that API key is set."""
        return bool(self.api_key and self.client)


class DeepLBackend(TranslationBackend):
    """DeepL translation backend."""

    # DeepL language codes
    LANGUAGES = {
        "bg": "Bulgarian",
        "cs": "Czech",
        "da": "Danish",
        "de": "German",
        "el": "Greek",
        "en": "English",
        "en-gb": "English (British)",
        "en-us": "English (American)",
        "es": "Spanish",
        "et": "Estonian",
        "fi": "Finnish",
        "fr": "French",
        "hu": "Hungarian",
        "id": "Indonesian",
        "it": "Italian",
        "ja": "Japanese",
        "ko": "Korean",
        "lt": "Lithuanian",
        "lv": "Latvian",
        "nb": "Norwegian",
        "nl": "Dutch",
        "pl": "Polish",
        "pt": "Portuguese",
        "pt-br": "Portuguese (Brazilian)",
        "pt-pt": "Portuguese (European)",
        "ro": "Romanian",
        "ru": "Russian",
        "sk": "Slovak",
        "sl": "Slovenian",
        "sv": "Swedish",
        "tr": "Turkish",
        "uk": "Ukrainian",
        "zh": "Chinese (Simplified)",
        "auto": "Auto-detect",
    }

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("DEEPL_API_KEY")
        self.translator = None
        self._init_translator()

    def _init_translator(self):
        """Initialize DeepL translator."""
        if self.api_key:
            try:
                import deepl

                self.translator = deepl.Translator(self.api_key)
            except ImportError:
                logger.error("DeepL library not installed. Run: pip install deepl")
                self.translator = None

    async def detect_language(self, text: str) -> str | None:
        """Detect the language of the given text."""
        if not self.translator:
            return None

        try:
            # DeepL doesn't have a separate detect endpoint
            # We can use translate with target 'en' and check source language
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.translator.translate_text(text[:500], target_lang="EN-US"),
            )

            # Convert DeepL language code to our standard codes
            detected = result.detected_source_lang.lower()
            if detected == "en":
                detected = "en-us"
            elif detected == "pt":
                detected = "pt-pt"

            return detected if detected in self.LANGUAGES else None

        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return None

    async def translate(self, text: str, source: str, target: str) -> str:
        """Translate text from source to target language."""
        if not self.translator:
            raise ValueError("DeepL translator not initialized. Check API key.")

        try:
            # Convert our language codes to DeepL format
            deepl_target = target.upper()
            if target == "en":
                deepl_target = "EN-US"
            elif target == "pt":
                deepl_target = "PT-PT"
            elif target == "zh" or target == "zh-cn":
                deepl_target = "ZH"

            # DeepL source can be None for auto-detect
            deepl_source = None if source == "auto" else source.upper()

            # Run translation in executor since deepl library is sync
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.translator.translate_text(
                    text, source_lang=deepl_source, target_lang=deepl_target
                ),
            )

            return result.text

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise

    def get_supported_languages(self) -> dict[str, str]:
        """Get dictionary of supported language codes and names."""
        return self.LANGUAGES

    def validate_config(self) -> bool:
        """Validate that API key is set."""
        return bool(self.api_key and self.translator)


class ClaudeBackend(TranslationBackend):
    """Anthropic Claude translation backend."""

    # Use same language set as OpenAI for now
    LANGUAGES = OpenAIBackend.LANGUAGES.copy()

    def __init__(
        self, api_key: str | None = None, model: str = "claude-3-haiku-20240307"
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize Anthropic client."""
        if self.api_key:
            try:
                from anthropic import AsyncAnthropic

                self.client = AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                logger.error(
                    "Anthropic library not installed. Run: pip install anthropic"
                )
                self.client = None

    async def detect_language(self, text: str) -> str | None:
        """Detect the language of the given text."""
        if not self.client:
            return None

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=10,
                temperature=0,
                system="You are a language detection system. Respond with ONLY the ISO 639-1 language code (e.g., 'en', 'es', 'ja'). If unsure, respond with 'unknown'.",
                messages=[
                    {
                        "role": "user",
                        "content": f"What language is this text written in? Text: {text[:500]}",
                    }
                ],
            )

            lang_code = response.content[0].text.strip().lower()
            return lang_code if lang_code in self.LANGUAGES else None

        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return None

    async def translate(self, text: str, source: str, target: str) -> str:
        """Translate text from source to target language."""
        if not self.client:
            raise ValueError("Claude client not initialized. Check API key.")

        source_name = self.LANGUAGES.get(source, source)
        target_name = self.LANGUAGES.get(target, target)

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.3,
                system=f"You are a professional translator. Translate text from {source_name} to {target_name}. Maintain the original formatting and style. Only provide the translation, no explanations.",
                messages=[{"role": "user", "content": text}],
            )

            return response.content[0].text.strip()

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise

    def get_supported_languages(self) -> dict[str, str]:
        """Get dictionary of supported language codes and names."""
        return self.LANGUAGES

    def validate_config(self) -> bool:
        """Validate that API key is set."""
        return bool(self.api_key and self.client)


def get_backend(engine: str, **kwargs) -> TranslationBackend:
    """Factory function to get translation backend."""
    engine = engine.lower()

    if engine == "google":
        return GoogleTranslateBackend()
    elif engine == "openai":
        return OpenAIBackend(**kwargs)
    elif engine == "deepl":
        return DeepLBackend(**kwargs)
    elif engine == "claude":
        return ClaudeBackend(**kwargs)
    else:
        raise ValueError(f"Unknown translation engine: {engine}")
