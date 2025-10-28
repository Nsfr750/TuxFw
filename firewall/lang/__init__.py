"""
Language and Localization Module

This package handles internationalization (i18n) and localization (l10n) for the TuxFw application.
It includes translations and language management functionality.
"""

from firewall.lang.language_manager import LanguageManager, tr
from firewall.lang.translations import translations

__all__ = ['LanguageManager', 'tr', 'translations']
