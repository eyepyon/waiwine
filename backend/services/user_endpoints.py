"""
FastAPI endpoints for user management.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, EmailStr

from services.user_service import UserService
from services.auth_service import AuthenticationService


# Request/Response models
class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    main_language: Optional[str] = None
    profile_image_url: Optional[str] = None

class UpdateLanguageRequest(BaseModel):
    language: str

class UpdateTranslationSettingsRequest(BaseModel):
    text_translation_enabled: Optional[bool] = None
    voice_translation_enabled: Optional[bool] = None
    original_voice_volume: Optional[float] = None
    translated_voice_volume: Optional[float] = None
    preferred_voice_id: Optional[str] = None
    voice_speed: Optional[float] = None
    subtitle_position: Optional[str] = None
    subtitle_font_size: Optional[int] = None
    subtitle_background_opacity: Optional[float] = None

class UserProfileResponse(BaseModel):
    id: str
    email: str
    name: str
    main_language: str
    profile_image_url: Optional[str] = None
    created_at: str
    updated_at: str
    oauth_providers: List[Dict[str, Any]]
    translation_settings: Optional[Dict[str, Any]] = None

class TranslationSettingsResponse(BaseModel):
    text_translation_enabled: bool
    voice_translation_enabled: bool
    original_voice_volume: float
    translated_voice_volume: float
    preferred_voice_id: Optional[str] = None
    voice_speed: float
    subtitle_position: str
    subtitle_font_size: int
    subtitle_background_opacity: float

class LanguageResponse(BaseModel):
    code: str
    name: str
    english_name: str

class UserStatisticsResponse(BaseModel):
    account_created: str
    last_updated: str
    linked_providers_count: int
    main_language: str


# Create router
user_router = APIRouter(prefix="/api/user", tags=["user_management"])

# Security scheme
security = HTTPBearer()

# Initialize services
user_service = UserService()
auth_service = AuthenticationService()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user from JWT token."""
    token = credentials.credentials
    user = auth_service.get_user_by_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user


@user_router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(current_user = Depends(get_current_user)) -> UserProfileResponse:
    """Get current user's complete profile."""
    try:
        profile = user_service.get_user_profile(current_user.id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return UserProfileResponse(**profile)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get user profile")


@user_router.put("/profile")
async def update_user_profile(
    request: UpdateProfileRequest,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update user profile information."""
    try:
        # Convert request to dict, excluding None values
        updates = {k: v for k, v in request.dict().items() if v is not None}
        
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        success = user_service.update_user_profile(current_user.id, updates)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update profile")
        
        return {
            "success": True,
            "message": "Profile updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update profile")


@user_router.put("/language")
async def update_user_language(
    request: UpdateLanguageRequest,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update user's main language setting."""
    try:
        success = user_service.update_user_language(current_user.id, request.language)
        
        if not success:
            raise HTTPException(status_code=400, detail="Invalid language or update failed")
        
        return {
            "success": True,
            "message": f"Language updated to {request.language}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update language")


@user_router.get("/translation-settings", response_model=TranslationSettingsResponse)
async def get_translation_settings(current_user = Depends(get_current_user)) -> TranslationSettingsResponse:
    """Get user's translation settings."""
    try:
        settings = user_service.get_user_translation_settings(current_user.id)
        
        if not settings:
            # Create default settings if they don't exist
            user_service.create_default_translation_settings(current_user.id)
            settings = user_service.get_user_translation_settings(current_user.id)
        
        return TranslationSettingsResponse(**settings)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get translation settings")


@user_router.put("/translation-settings")
async def update_translation_settings(
    request: UpdateTranslationSettingsRequest,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update user's translation settings."""
    try:
        # Convert request to dict, excluding None values
        updates = {k: v for k, v in request.dict().items() if v is not None}
        
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        success = user_service.update_translation_settings(current_user.id, updates)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update translation settings")
        
        return {
            "success": True,
            "message": "Translation settings updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update translation settings")


@user_router.get("/oauth-providers")
async def get_oauth_providers(current_user = Depends(get_current_user)) -> Dict[str, Any]:
    """Get list of OAuth providers linked to user."""
    try:
        providers = user_service.get_user_oauth_providers(current_user.id)
        
        return {
            "success": True,
            "providers": providers
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get OAuth providers")


@user_router.get("/can-unlink/{provider}")
async def can_unlink_provider(
    provider: str,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """Check if user can unlink a specific OAuth provider."""
    try:
        can_unlink = user_service.can_unlink_provider(current_user.id, provider)
        
        return {
            "can_unlink": can_unlink,
            "provider": provider
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to check provider status")


@user_router.delete("/account")
async def delete_user_account(current_user = Depends(get_current_user)) -> Dict[str, Any]:
    """Delete user account and all associated data."""
    try:
        success = user_service.delete_user_account(current_user.id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to delete account")
        
        return {
            "success": True,
            "message": "Account deleted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete account")


@user_router.get("/statistics", response_model=UserStatisticsResponse)
async def get_user_statistics(current_user = Depends(get_current_user)) -> UserStatisticsResponse:
    """Get user statistics and activity information."""
    try:
        stats = user_service.get_user_statistics(current_user.id)
        
        if not stats:
            raise HTTPException(status_code=404, detail="User statistics not found")
        
        return UserStatisticsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get user statistics")


@user_router.get("/languages", response_model=List[LanguageResponse])
async def get_supported_languages() -> List[LanguageResponse]:
    """Get list of supported languages."""
    try:
        languages = user_service.get_supported_languages()
        return [LanguageResponse(**lang) for lang in languages]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get supported languages")


@user_router.get("/search")
async def search_user_by_email(
    email: EmailStr,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """Search for user by email address (admin function)."""
    try:
        # For now, only allow users to search for themselves
        # In the future, this could be restricted to admin users
        if email != current_user.email:
            raise HTTPException(status_code=403, detail="Can only search for your own email")
        
        user = user_service.search_users_by_email(email)
        
        return {
            "success": True,
            "user": user
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to search user")