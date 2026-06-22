"""
translator_service.py
----------------------
Wraps the googletrans (Google Translate) API and provides:
 - Text translation
 - Automatic language detection
 - A friendly list of supported languages

All network/API errors are caught and re-raised as TranslationError
so the GUI layer can show clean, user-friendly messages.
"""

from googletrans import Translator, LANGUAGES


class TranslationError(Exception):
    """Custom exception raised when translation/detection fails."""
    pass


class TranslatorService:
    """Provides translation and language detection using Google Translate."""

    def __init__(self):
        self._translator = Translator()

        # Friendly Name -> language code dictionary (e.g. "English" -> "en")
        self.lang_name_to_code = {
            name.title(): code for code, name in LANGUAGES.items()
        }
        # Add an "Auto Detect" option for the source language dropdown
        self.lang_name_to_code = {"Auto Detect": "auto", **self.lang_name_to_code}

        # Reverse lookup: code -> friendly name
        self.code_to_lang_name = {
            code: name.title() for code, name in LANGUAGES.items()
        }

    def get_language_names(self, include_auto: bool = True):
        """Return a sorted list of language names for dropdown menus."""
        names = sorted(
            [n for n in self.lang_name_to_code.keys() if n != "Auto Detect"]
        )
        if include_auto:
            return ["Auto Detect"] + names
        return names

    def code_for(self, language_name: str) -> str:
        """Convert a friendly language name to its ISO code."""
        return self.lang_name_to_code.get(language_name, "en")

    def name_for(self, code: str) -> str:
        """Convert an ISO language code to its friendly display name."""
        return self.code_to_lang_name.get(code, code)

    def detect_language(self, text: str) -> tuple[str, str]:
        """
        Detect the language of the given text.
        Returns a tuple of (language_code, language_name).
        """
        if not text or not text.strip():
            raise TranslationError("Cannot detect language of empty text.")
        try:
            result = self._translator.detect(text)
            code = result.lang
            name = self.name_for(code)
            return code, name
        except Exception as exc:
            raise TranslationError(
                "Language detection failed. Please check your internet connection."
            ) from exc

    def translate(self, text: str, source_lang_name: str, target_lang_name: str) -> dict:
        """
        Translate text from source language to target language.

        Returns a dictionary with:
            translated_text, detected_source_code, detected_source_name
        """
        if not text or not text.strip():
            raise TranslationError("Please enter some text to translate.")

        src_code = self.code_for(source_lang_name)
        dest_code = self.code_for(target_lang_name)

        try:
            if src_code == "auto":
                result = self._translator.translate(text, dest=dest_code)
            else:
                result = self._translator.translate(text, src=src_code, dest=dest_code)

            return {
                "translated_text": result.text,
                "detected_source_code": result.src,
                "detected_source_name": self.name_for(result.src),
            }
        except Exception as exc:
            raise TranslationError(
                "Translation failed. Please check your internet connection and try again."
            ) from exc
