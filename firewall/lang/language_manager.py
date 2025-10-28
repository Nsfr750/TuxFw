import json
import logging
import os
from typing import Dict, Any

class LanguageManager:
    def __init__(self, lang_dir: str = 'lang'):
        self.lang_dir = lang_dir
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.current_lang = 'en'
        self.logger = logging.getLogger(__name__)
        self._load_translations()
    
    def _load_translations(self):
        try:
            # Import the translations dictionary directly
            from firewall.lang.translations import translations
            self.translations = translations
        except (ImportError, AttributeError) as e:
            # Fallback to default translations if import fails
            self.translations = {
                'en': {
                    'error': 'Error loading translations',
                    'window_title': 'Firewall Manager',
                    'common': {
                        'close': 'Close',
                        'save': 'Save',
                        'cancel': 'Cancel'
                    }
                },
                'it': {
                    'error': 'Errore nel caricamento delle traduzioni',
                    'window_title': 'Gestore Firewall',
                    'common': {
                        'close': 'Chiudi',
                        'save': 'Salva',
                        'cancel': 'Annulla'
                    }
                }
            }
            self.logger.warning(f'Using fallback translations: {str(e)}')
    
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
