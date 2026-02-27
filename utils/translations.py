"""
Translation system for bilingual support (English / Armenian).
"""

import json
import os
from typing import Dict


# Default language
DEFAULT_LANGUAGE = "en"

# Available languages
LANGUAGES = {
    "en": "English",
    "hy": "Armenian"
}


def load_translations(language: str = DEFAULT_LANGUAGE) -> Dict[str, str]:
    """
    Load translation dictionary for the specified language.
    
    Args:
        language: Language code ('en' or 'hy')
        
    Returns:
        Dictionary of translation keys to translated strings
    """
    if language not in LANGUAGES:
        language = DEFAULT_LANGUAGE
    
    # Get the directory where this file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    translations_dir = os.path.join(project_root, "translations")
    translation_file = os.path.join(translations_dir, f"{language}.json")
    
    try:
        with open(translation_file, "r", encoding="utf-8") as f:
            translations = json.load(f)
        return translations
    except FileNotFoundError:
        # Fallback to English if translation file not found
        if language != DEFAULT_LANGUAGE:
            return load_translations(DEFAULT_LANGUAGE)
        return {}
    except json.JSONDecodeError:
        return {}


def get_translation_function(translations: Dict[str, str]):
    """
    Create a translation function that uses the provided translations dictionary.
    
    Args:
        translations: Dictionary of translation keys to translated strings
        
    Returns:
        Translation function that takes a key and optional format arguments
    """
    def t(key: str, **kwargs) -> str:
        """
        Translate a key to the current language.
        
        Args:
            key: Translation key
            **kwargs: Format arguments for string formatting
            
        Returns:
            Translated string, or the key itself if not found
        """
        translated = translations.get(key, key)
        
        # If there are format arguments, apply them
        if kwargs:
            try:
                return translated.format(**kwargs)
            except (KeyError, ValueError):
                return translated
        
        return translated
    
    return t

