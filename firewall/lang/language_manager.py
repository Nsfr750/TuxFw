import json
import os
from typing import Dict, Any

class LanguageManager:
    def __init__(self, lang_dir: str = 'lang'):
        self.lang_dir = lang_dir
        self.translations: Dict[str, Dict[str, str]] = {}
        self.current_lang = 'en'
        self._load_translations()
    
    def _load_translations(self):
        try:
            from . import translations
            self.translations = translations.translations
        except ImportError:
            # Fallback to default translations if module import fails
            self.translations = {
                'en': {
                    'error': 'Error loading translations',
                    'window_title': 'Firewall Manager',
                },
                'it': {
                    'error': 'Errore nel caricamento delle traduzioni',
                    'window_title': 'Gestore Firewall',
                }
            }
    
    def set_language(self, lang_code: str) -> bool:
        """Set the current language."""
        if lang_code in self.translations:
            self.current_lang = lang_code
            return True
        return False
    
    def get_languages(self) -> Dict[str, str]:
        """Get available languages."""
        return {
            'en': self.get_text('english', 'en'),
            'it': self.get_text('italian', 'it')
        }
    
    def get_text(self, key: str, lang: str = None) -> str:
        """Get translated text for the given key."""
        lang = lang or self.current_lang
        return self.translations.get(lang, {}).get(key, 
               self.translations.get('en', {}).get(key, f'[{key}]'))
    
    def get_current_language(self) -> str:
        """Get the current language code."""
        return self.current_lang

# Create a global instance
language_manager = LanguageManager()

def tr(key: str) -> str:
    """Translation shortcut function."""
    return language_manager.get_text(key)
