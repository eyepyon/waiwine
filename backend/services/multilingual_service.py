"""
Multilingual content service for handling translations and localized content.
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models.wine import Wine, Translation, VoiceProfile
from ..models.database import get_db


class MultilingualService:
    """Service for managing multilingual content and translations."""
    
    def get_localized_wine_info(self, wine_id: str, language: str = 'en') -> Optional[Dict[str, Any]]:
        """
        Get wine information with localized content.
        
        Args:
            wine_id: Wine ID
            language: Target language code
            
        Returns:
            Localized wine information or None if not found
        """
        db = next(get_db())
        try:
            wine = db.query(Wine).filter(Wine.id == wine_id).first()
            if not wine:
                return None
            
            return {
                'id': wine.id,
                'name': wine.get_localized_name(language),
                'original_name': wine.name,
                'vintage': wine.vintage,
                'region': self._get_localized_region(wine, language),
                'original_region': wine.region,
                'producer': wine.producer,
                'wine_type': wine.wine_type,
                'localized_type': self._get_localized_wine_type(wine.wine_type, language),
                'alcohol_content': wine.alcohol_content,
                'image_url': wine.image_url,
                'tasting_notes': wine.get_localized_tasting_notes(language),
                'recognition_count': wine.recognition_count,
                'created_at': wine.created_at.isoformat(),
                'updated_at': wine.updated_at.isoformat()
            }
        finally:
            db.close()
    
    def search_wines_localized(self, query: str, language: str = 'en', limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search wines with localized content.
        
        Args:
            query: Search query
            language: Target language code
            limit: Maximum number of results
            
        Returns:
            List of localized wine information
        """
        db = next(get_db())
        try:
            # Search in both original and translated names
            wines = db.query(Wine).filter(
                Wine.name.ilike(f'%{query}%') |
                Wine.producer.ilike(f'%{query}%') |
                Wine.region.ilike(f'%{query}%')
            ).limit(limit).all()
            
            results = []
            for wine in wines:
                localized_info = {
                    'id': wine.id,
                    'name': wine.get_localized_name(language),
                    'original_name': wine.name,
                    'vintage': wine.vintage,
                    'region': self._get_localized_region(wine, language),
                    'producer': wine.producer,
                    'wine_type': wine.wine_type,
                    'localized_type': self._get_localized_wine_type(wine.wine_type, language),
                    'alcohol_content': wine.alcohol_content,
                    'image_url': wine.image_url,
                    'recognition_count': wine.recognition_count
                }
                
                # Check if query matches translated content
                localized_name = wine.get_localized_name(language).lower()
                localized_region = self._get_localized_region(wine, language).lower()
                
                if (query.lower() in localized_name or 
                    query.lower() in localized_region or
                    query.lower() in wine.name.lower() or
                    query.lower() in (wine.producer or '').lower() or
                    query.lower() in (wine.region or '').lower()):
                    results.append(localized_info)
            
            return results
        finally:
            db.close()
    
    def get_translation(self, key: str, language: str = 'en') -> Optional[str]:
        """
        Get translation for a specific key and language.
        
        Args:
            key: Translation key
            language: Target language code
            
        Returns:
            Translated text or None if not found
        """
        db = next(get_db())
        try:
            translation = db.query(Translation).filter(
                and_(
                    Translation.key == key,
                    Translation.language == language
                )
            ).first()
            
            return translation.value if translation else None
        finally:
            db.close()
    
    def set_translation(self, key: str, language: str, value: str) -> bool:
        """
        Set or update a translation.
        
        Args:
            key: Translation key
            language: Target language code
            value: Translation value
            
        Returns:
            True if successful
        """
        db = next(get_db())
        try:
            translation = db.query(Translation).filter(
                and_(
                    Translation.key == key,
                    Translation.language == language
                )
            ).first()
            
            if translation:
                translation.value = value
            else:
                translation = Translation(key=key, language=language, value=value)
                db.add(translation)
            
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_available_voices(self, language: str) -> List[Dict[str, Any]]:
        """
        Get available voice profiles for a language.
        
        Args:
            language: Target language code
            
        Returns:
            List of voice profiles
        """
        db = next(get_db())
        try:
            voices = db.query(VoiceProfile).filter(
                VoiceProfile.language == language
            ).all()
            
            return [
                {
                    'id': voice.id,
                    'voice_name': voice.voice_name,
                    'gender': voice.gender,
                    'description': voice.get_localized_description(language),
                    'sample_audio_url': voice.sample_audio_url
                }
                for voice in voices
            ]
        finally:
            db.close()
    
    def update_wine_translations(self, wine_id: str, translations: Dict[str, Dict[str, str]]) -> bool:
        """
        Update wine translations.
        
        Args:
            wine_id: Wine ID
            translations: Dictionary with translation data
                         {'name': {'ja': '日本語名', 'en': 'English name'}, ...}
            
        Returns:
            True if successful
        """
        db = next(get_db())
        try:
            wine = db.query(Wine).filter(Wine.id == wine_id).first()
            if not wine:
                return False
            
            # Update name translations
            if 'name' in translations:
                wine.name_translations = translations['name']
            
            # Update region translations
            if 'region' in translations:
                wine.region_translations = translations['region']
            
            # Update tasting notes translations
            if 'tasting_notes' in translations:
                wine.tasting_notes_translations = translations['tasting_notes']
            
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """
        Get list of supported languages.
        
        Returns:
            List of supported languages
        """
        return [
            {'code': 'ja', 'name': '日本語', 'english_name': 'Japanese'},
            {'code': 'en', 'name': 'English', 'english_name': 'English'},
            {'code': 'ko', 'name': '한국어', 'english_name': 'Korean'},
            {'code': 'zh', 'name': '中文', 'english_name': 'Chinese'},
            {'code': 'es', 'name': 'Español', 'english_name': 'Spanish'},
            {'code': 'fr', 'name': 'Français', 'english_name': 'French'},
            {'code': 'de', 'name': 'Deutsch', 'english_name': 'German'}
        ]
    
    def _get_localized_region(self, wine: Wine, language: str) -> str:
        """Get localized region name."""
        if wine.region_translations and language in wine.region_translations:
            return wine.region_translations[language]
        return wine.region or ''
    
    def _get_localized_wine_type(self, wine_type: str, language: str) -> str:
        """Get localized wine type."""
        if not wine_type:
            return ''
        
        # Try to get translation from database
        type_key = f'wine.type.{wine_type.lower()}'
        translation = self.get_translation(type_key, language)
        
        if translation:
            return translation
        
        # Fallback to hardcoded translations
        type_translations = {
            'red': {
                'ja': '赤ワイン',
                'en': 'Red Wine',
                'ko': '레드 와인',
                'zh': '红酒',
                'es': 'Vino Tinto',
                'fr': 'Vin Rouge',
                'de': 'Rotwein'
            },
            'white': {
                'ja': '白ワイン',
                'en': 'White Wine',
                'ko': '화이트 와인',
                'zh': '白酒',
                'es': 'Vino Blanco',
                'fr': 'Vin Blanc',
                'de': 'Weißwein'
            },
            'rose': {
                'ja': 'ロゼワイン',
                'en': 'Rosé Wine',
                'ko': '로제 와인',
                'zh': '桃红酒',
                'es': 'Vino Rosado',
                'fr': 'Vin Rosé',
                'de': 'Roséwein'
            },
            'sparkling': {
                'ja': 'スパークリングワイン',
                'en': 'Sparkling Wine',
                'ko': '스파클링 와인',
                'zh': '起泡酒',
                'es': 'Vino Espumoso',
                'fr': 'Vin Pétillant',
                'de': 'Schaumwein'
            },
            'dessert': {
                'ja': 'デザートワイン',
                'en': 'Dessert Wine',
                'ko': '디저트 와인',
                'zh': '甜酒',
                'es': 'Vino de Postre',
                'fr': 'Vin de Dessert',
                'de': 'Dessertwein'
            },
            'fortified': {
                'ja': '酒精強化ワイン',
                'en': 'Fortified Wine',
                'ko': '주정강화 와인',
                'zh': '加强酒',
                'es': 'Vino Fortificado',
                'fr': 'Vin Fortifié',
                'de': 'Likörwein'
            }
        }
        
        wine_type_lower = wine_type.lower()
        if wine_type_lower in type_translations and language in type_translations[wine_type_lower]:
            return type_translations[wine_type_lower][language]
        
        return wine_type