"""
User management service for profile management and settings.
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from models.user import User, OAuthProvider, TranslationSettings
from models.database import get_db


class UserService:
    """Service for managing user profiles and settings."""
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete user profile information.
        
        Args:
            user_id: User ID
            
        Returns:
            User profile data or None if not found
        """
        db = next(get_db())
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            # Get OAuth providers
            oauth_providers = db.query(OAuthProvider).filter(
                OAuthProvider.user_id == user_id
            ).all()
            
            # Get translation settings
            translation_settings = db.query(TranslationSettings).filter(
                TranslationSettings.user_id == user_id
            ).first()
            
            return {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'main_language': user.main_language,
                'profile_image_url': user.profile_image_url,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat(),
                'oauth_providers': [
                    {
                        'provider': provider.provider_name,
                        'provider_email': provider.provider_email,
                        'linked_at': provider.linked_at.isoformat()
                    }
                    for provider in oauth_providers
                ],
                'translation_settings': self._format_translation_settings(translation_settings) if translation_settings else None
            }
        finally:
            db.close()
    
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update user profile information.
        
        Args:
            user_id: User ID
            updates: Dictionary of fields to update
            
        Returns:
            True if update successful
        """
        db = next(get_db())
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Update allowed fields
            allowed_fields = ['name', 'main_language', 'profile_image_url']
            for field, value in updates.items():
                if field in allowed_fields and hasattr(user, field):
                    setattr(user, field, value)
            
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()
    
    def update_user_language(self, user_id: str, language: str) -> bool:
        """
        Update user's main language setting.
        
        Args:
            user_id: User ID
            language: Language code (e.g., 'ja', 'en', 'ko')
            
        Returns:
            True if update successful
        """
        # Validate language code
        supported_languages = ['ja', 'en', 'ko', 'zh', 'es', 'fr', 'de']
        if language not in supported_languages:
            return False
        
        return self.update_user_profile(user_id, {'main_language': language})
    
    def get_user_translation_settings(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user's translation settings.
        
        Args:
            user_id: User ID
            
        Returns:
            Translation settings or None if not found
        """
        db = next(get_db())
        try:
            settings = db.query(TranslationSettings).filter(
                TranslationSettings.user_id == user_id
            ).first()
            
            return self._format_translation_settings(settings) if settings else None
        finally:
            db.close()
    
    def update_translation_settings(self, user_id: str, settings: Dict[str, Any]) -> bool:
        """
        Update user's translation settings.
        
        Args:
            user_id: User ID
            settings: Translation settings to update
            
        Returns:
            True if update successful
        """
        db = next(get_db())
        try:
            user_settings = db.query(TranslationSettings).filter(
                TranslationSettings.user_id == user_id
            ).first()
            
            if not user_settings:
                # Create new settings if they don't exist
                user_settings = TranslationSettings(user_id=user_id)
                db.add(user_settings)
            
            # Update allowed fields
            allowed_fields = [
                'text_translation_enabled',
                'voice_translation_enabled',
                'original_voice_volume',
                'translated_voice_volume',
                'preferred_voice_id',
                'voice_speed',
                'subtitle_position',
                'subtitle_font_size',
                'subtitle_background_opacity'
            ]
            
            for field, value in settings.items():
                if field in allowed_fields and hasattr(user_settings, field):
                    setattr(user_settings, field, value)
            
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()
    
    def delete_user_account(self, user_id: str) -> bool:
        """
        Delete user account and all associated data.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deletion successful
        """
        db = next(get_db())
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Delete user (cascade will handle related records)
            db.delete(user)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_user_oauth_providers(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get list of OAuth providers linked to user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of OAuth provider information
        """
        db = next(get_db())
        try:
            providers = db.query(OAuthProvider).filter(
                OAuthProvider.user_id == user_id
            ).all()
            
            return [
                {
                    'provider': provider.provider_name,
                    'provider_email': provider.provider_email,
                    'linked_at': provider.linked_at.isoformat()
                }
                for provider in providers
            ]
        finally:
            db.close()
    
    def can_unlink_provider(self, user_id: str, provider: str) -> bool:
        """
        Check if user can unlink a specific OAuth provider.
        
        Args:
            user_id: User ID
            provider: Provider name to check
            
        Returns:
            True if provider can be unlinked
        """
        db = next(get_db())
        try:
            # Count total providers for user
            provider_count = db.query(OAuthProvider).filter(
                OAuthProvider.user_id == user_id
            ).count()
            
            # Can't unlink if it's the only provider
            if provider_count <= 1:
                return False
            
            # Check if the specific provider exists
            provider_exists = db.query(OAuthProvider).filter(
                and_(
                    OAuthProvider.user_id == user_id,
                    OAuthProvider.provider_name == provider
                )
            ).first() is not None
            
            return provider_exists
        finally:
            db.close()
    
    def search_users_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Search for user by email address.
        
        Args:
            email: Email address to search
            
        Returns:
            User information if found
        """
        db = next(get_db())
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return None
            
            return {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'main_language': user.main_language,
                'profile_image_url': user.profile_image_url
            }
        finally:
            db.close()
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get user statistics and activity information.
        
        Args:
            user_id: User ID
            
        Returns:
            User statistics
        """
        db = next(get_db())
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {}
            
            oauth_count = db.query(OAuthProvider).filter(
                OAuthProvider.user_id == user_id
            ).count()
            
            return {
                'account_created': user.created_at.isoformat(),
                'last_updated': user.updated_at.isoformat(),
                'linked_providers_count': oauth_count,
                'main_language': user.main_language
            }
        finally:
            db.close()
    
    def _format_translation_settings(self, settings: TranslationSettings) -> Dict[str, Any]:
        """
        Format translation settings for API response.
        
        Args:
            settings: TranslationSettings object
            
        Returns:
            Formatted settings dictionary
        """
        if not settings:
            return {}
        
        return {
            'text_translation_enabled': settings.text_translation_enabled,
            'voice_translation_enabled': settings.voice_translation_enabled,
            'original_voice_volume': settings.original_voice_volume,
            'translated_voice_volume': settings.translated_voice_volume,
            'preferred_voice_id': settings.preferred_voice_id,
            'voice_speed': settings.voice_speed,
            'subtitle_position': settings.subtitle_position,
            'subtitle_font_size': settings.subtitle_font_size,
            'subtitle_background_opacity': settings.subtitle_background_opacity
        }
    
    def create_default_translation_settings(self, user_id: str) -> bool:
        """
        Create default translation settings for a new user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if creation successful
        """
        db = next(get_db())
        try:
            # Check if settings already exist
            existing = db.query(TranslationSettings).filter(
                TranslationSettings.user_id == user_id
            ).first()
            
            if existing:
                return True  # Already exists
            
            # Create default settings
            settings = TranslationSettings(user_id=user_id)
            db.add(settings)
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
            List of supported languages with codes and names
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