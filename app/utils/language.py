"""
Language Management Utilities
============================

Multi-language support for the Twitter Analysis Platform.
"""

import json
import os
from pathlib import Path
from flask import session, current_app

class LanguageManager:
    """Language manager for handling translations"""
    
    def __init__(self):
        self.translations = {}
        self.supported_languages = ['tr', 'en']
        self.default_language = 'tr'
        self.load_translations()
    
    def load_translations(self):
        """Load all translation files"""
        translations_dir = Path(__file__).parent.parent / 'translations'
        
        for lang in self.supported_languages:
            lang_file = translations_dir / f'{lang}.json'
            if lang_file.exists():
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        self.translations[lang] = json.load(f)
                except Exception as e:
                    print(f"Error loading translation file {lang_file}: {e}")
                    self.translations[lang] = {}
            else:
                self.translations[lang] = {}
    
    def get_current_language(self):
        """Get current language from session"""
        return session.get('language', self.default_language)
    
    def set_language(self, language):
        """Set language in session"""
        if language in self.supported_languages:
            session['language'] = language
            return True
        return False
    
    def get_text(self, key_path, language=None):
        """
        Get translated text by key path (e.g., 'nav.dashboard')
        
        Args:
            key_path (str): Dot-separated path to the translation key
            language (str): Language code (uses current language if None)
        
        Returns:
            str: Translated text or key_path if not found
        """
        if language is None:
            language = self.get_current_language()
        
        if language not in self.translations:
            language = self.default_language
        
        translation_dict = self.translations.get(language, {})
        if not translation_dict:
            return key_path
        
        # Navigate through nested dictionary using key path
        keys = key_path.split('.')
        current_dict = translation_dict
        
        for key in keys:
            if isinstance(current_dict, dict) and key in current_dict:
                current_dict = current_dict[key]
            else:
                return key_path  # Return key path if translation not found
        
        return current_dict if isinstance(current_dict, str) else key_path
    
    def get_language_info(self):
        """Get information about all supported languages"""
        language_info = {
            'tr': {'name': 'Türkçe', 'flag': '🇹🇷'},
            'en': {'name': 'English', 'flag': '🇺🇸'}
        }
        
        return {
            'current': self.get_current_language(),
            'supported': self.supported_languages,
            'info': language_info
        }

# Global language manager instance
language_manager = LanguageManager()

def get_text(key_path, language=None):
    """Global function to get translated text"""
    return language_manager.get_text(key_path, language)

def set_language(language):
    """Global function to set language"""
    return language_manager.set_language(language)

def get_current_language():
    """Global function to get current language"""
    return language_manager.get_current_language()

def get_language_info():
    """Global function to get language information"""
    return language_manager.get_language_info() 