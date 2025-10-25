"""
FastAPI endpoints for LiveKit-based translation service.
"""
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .livekit_translation_service import livekit_translation_service
from .auth_service import AuthenticationService
from ..models.database import get_db

# Request/Response models
class StartTranslationRequest(BaseModel):
    room_name: str
    source_language: str
    target_languages: List[str]

class UpdateTranslationSettingsRequest(BaseModel):
    text_translation_enabled: Optional[bool] = None
    voice_translation_enabled: Optional[bool] = None
    auto_translate: Optional[bool] = None
    preferred_voice_id: Optional[str] = None
    voice_speed: Optional[float] = None

class TranslationResponse(BaseModel):
    success: bool
    message: Optional[str] = None

# Create router
translation_router = APIRouter(prefix="/api/translation", tags=["translation"])

# Auth service
auth_service = AuthenticationService()


def get_current_user(token: str, db: Session):
    """Get current user from token."""
    user = auth_service.get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


@translation_router.post("/start", response_model=TranslationResponse)
async def start_translation(
    request: StartTranslationRequest,
    token: str,
    db: Session = Depends(get_db)
):
    """Start translation session for a user in a room."""
    
    try:
        user = get_current_user(token, db)
        
        await livekit_translation_service.start_translation_session(
            room_name=request.room_name,
            user_id=user.id,
            source_language=request.source_language,
            target_languages=request.target_languages,
            db=db
        )
        
        return TranslationResponse(
            success=True,
            message="Translation session started"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@translation_router.post("/stop", response_model=TranslationResponse)
async def stop_translation(
    room_name: str,
    token: str,
    db: Session = Depends(get_db)
):
    """Stop translation session for a user."""
    
    try:
        user = get_current_user(token, db)
        
        await livekit_translation_service.stop_translation_session(
            room_name=room_name,
            user_id=user.id
        )
        
        return TranslationResponse(
            success=True,
            message="Translation session stopped"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@translation_router.post("/settings", response_model=TranslationResponse)
async def update_settings(
    request: UpdateTranslationSettingsRequest,
    token: str,
    db: Session = Depends(get_db)
):
    """Update user's translation settings."""
    
    try:
        user = get_current_user(token, db)
        
        settings_data = request.dict(exclude_unset=True)
        
        success = await livekit_translation_service.update_translation_settings(
            user_id=user.id,
            settings_data=settings_data,
            db=db
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update settings")
        
        return TranslationResponse(
            success=True,
            message="Settings updated successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@translation_router.get("/participants/{room_name}")
async def get_room_participants(
    room_name: str,
    token: str,
    db: Session = Depends(get_db)
):
    """Get participants in a room with their language settings."""
    
    try:
        user = get_current_user(token, db)
        
        participants = livekit_translation_service.get_room_participants(room_name)
        
        return {
            "success": True,
            "participants": participants
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@translation_router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for translation."""
    
    return {
        "success": True,
        "languages": [
            {"code": "ja", "name": "Japanese"},
            {"code": "en", "name": "English"},
            {"code": "ko", "name": "Korean"},
            {"code": "zh", "name": "Chinese"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
            {"code": "de", "name": "German"},
        ]
    }
