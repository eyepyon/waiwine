"""
REST API endpoints for translation service management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
import logging

from models.database import get_db
from models.user import User, TranslationSettings
from services.translation_service import translation_service
from services.session_manager import get_current_user

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/translation", tags=["translation"])

# Pydantic models for request/response
class TranslationSettingsRequest(BaseModel):
    text_translation_enabled: bool = True
    voice_translation_enabled: bool = False
    original_voice_volume: float = 0.3
    translated_voice_volume: float = 0.8
    preferred_voice_id: str = None
    voice_speed: float = 1.0
    subtitle_position: str = "bottom"
    subtitle_font_size: int = 16
    subtitle_background_opacity: float = 0.7

class TranslationSettingsResponse(BaseModel):
    id: int
    user_id: str
    text_translation_enabled: bool
    voice_translation_enabled: bool
    original_voice_volume: float
    translated_voice_volume: float
    preferred_voice_id: str = None
    voice_speed: float
    subtitle_position: str
    subtitle_font_size: int
    subtitle_background_opacity: float

class VoiceProfile(BaseModel):
    id: str
    name: str
    gender: str
    language: str

class TranslateTextRequest(BaseModel):
    text: str
    target_language: str
    source_language: str = None

class TranslateTextResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float

class SynthesizeSpeechRequest(BaseModel):
    text: str
    voice_id: str
    speed: float = 1.0

@router.get("/settings", response_model=TranslationSettingsResponse)
async def get_translation_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's translation settings."""
    try:
        settings = current_user.translation_settings
        
        if not settings:
            # Create default settings
            settings = TranslationSettings(user_id=current_user.id)
            db.add(settings)
            db.commit()
            db.refresh(settings)
        
        return TranslationSettingsResponse(
            id=settings.id,
            user_id=settings.user_id,
            text_translation_enabled=settings.text_translation_enabled,
            voice_translation_enabled=settings.voice_translation_enabled,
            original_voice_volume=settings.original_voice_volume,
            translated_voice_volume=settings.translated_voice_volume,
            preferred_voice_id=settings.preferred_voice_id,
            voice_speed=settings.voice_speed,
            subtitle_position=settings.subtitle_position,
            subtitle_font_size=settings.subtitle_font_size,
            subtitle_background_opacity=settings.subtitle_background_opacity
        )
    
    except Exception as e:
        logger.error(f"Error getting translation settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get translation settings"
        )

@router.put("/settings", response_model=TranslationSettingsResponse)
async def update_translation_settings(
    settings_request: TranslationSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's translation settings."""
    try:
        settings = current_user.translation_settings
        
        if not settings:
            settings = TranslationSettings(user_id=current_user.id)
            db.add(settings)
        
        # Update settings
        settings.text_translation_enabled = settings_request.text_translation_enabled
        settings.voice_translation_enabled = settings_request.voice_translation_enabled
        settings.original_voice_volume = settings_request.original_voice_volume
        settings.translated_voice_volume = settings_request.translated_voice_volume
        settings.preferred_voice_id = settings_request.preferred_voice_id
        settings.voice_speed = settings_request.voice_speed
        settings.subtitle_position = settings_request.subtitle_position
        settings.subtitle_font_size = settings_request.subtitle_font_size
        settings.subtitle_background_opacity = settings_request.subtitle_background_opacity
        
        db.commit()
        db.refresh(settings)
        
        return TranslationSettingsResponse(
            id=settings.id,
            user_id=settings.user_id,
            text_translation_enabled=settings.text_translation_enabled,
            voice_translation_enabled=settings.voice_translation_enabled,
            original_voice_volume=settings.original_voice_volume,
            translated_voice_volume=settings.translated_voice_volume,
            preferred_voice_id=settings.preferred_voice_id,
            voice_speed=settings.voice_speed,
            subtitle_position=settings.subtitle_position,
            subtitle_font_size=settings.subtitle_font_size,
            subtitle_background_opacity=settings.subtitle_background_opacity
        )
    
    except Exception as e:
        logger.error(f"Error updating translation settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update translation settings"
        )

@router.get("/voices/{language}", response_model=List[VoiceProfile])
async def get_available_voices(
    language: str,
    current_user: User = Depends(get_current_user)
):
    """Get available voices for a specific language."""
    try:
        voices = translation_service.get_available_voices(language)
        
        return [
            VoiceProfile(
                id=voice['id'],
                name=voice['name'],
                gender=voice['gender'],
                language=language
            )
            for voice in voices
        ]
    
    except Exception as e:
        logger.error(f"Error getting voices for language {language}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get voices for language {language}"
        )

@router.post("/translate", response_model=TranslateTextResponse)
async def translate_text(
    request: TranslateTextRequest,
    current_user: User = Depends(get_current_user)
):
    """Translate text from one language to another."""
    try:
        result = translation_service.translation_service.translate_text(
            request.text,
            request.target_language,
            request.source_language
        )
        
        return TranslateTextResponse(
            original_text=request.text,
            translated_text=result['translated_text'],
            source_language=result['detected_source_language'],
            target_language=request.target_language,
            confidence=result['confidence']
        )
    
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Translation failed"
        )

@router.post("/synthesize")
async def synthesize_speech(
    request: SynthesizeSpeechRequest,
    current_user: User = Depends(get_current_user)
):
    """Convert text to speech audio."""
    try:
        audio_content = translation_service.tts_service.synthesize_speech(
            request.text,
            request.voice_id,
            request.speed
        )
        
        # Return audio as base64 encoded string
        import base64
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')
        
        return {
            "audio_data": audio_base64,
            "format": "mp3",
            "voice_id": request.voice_id,
            "text": request.text
        }
    
    except Exception as e:
        logger.error(f"Error synthesizing speech: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Speech synthesis failed"
        )

@router.get("/languages")
async def get_supported_languages(
    current_user: User = Depends(get_current_user)
):
    """Get list of supported languages for translation."""
    try:
        languages = translation_service.translation_service.get_supported_languages()
        return {"supported_languages": languages}
    
    except Exception as e:
        logger.error(f"Error getting supported languages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get supported languages"
        )

@router.post("/detect-language")
async def detect_language(
    text: str,
    current_user: User = Depends(get_current_user)
):
    """Detect the language of input text."""
    try:
        detected_language = translation_service.translation_service.detect_language(text)
        return {
            "text": text,
            "detected_language": detected_language
        }
    
    except Exception as e:
        logger.error(f"Error detecting language: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Language detection failed"
        )