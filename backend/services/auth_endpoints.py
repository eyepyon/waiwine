"""
FastAPI endpoints for OAuth authentication.
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from .auth_service import AuthenticationService
from ..config.oauth_config import OAuthConfig


# Request/Response models
class AuthUrlRequest(BaseModel):
    provider: str
    redirect_url: Optional[str] = None

class AuthUrlResponse(BaseModel):
    authorization_url: str
    state: str
    provider: str

class AuthCallbackResponse(BaseModel):
    success: bool
    user: Optional[Dict[str, Any]] = None
    token: Optional[str] = None
    redirect_url: Optional[str] = None
    error: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    main_language: str
    profile_image_url: Optional[str] = None
    oauth_providers: List[Dict[str, Any]]

class LinkProviderRequest(BaseModel):
    provider: str
    code: str
    state: str

class UnlinkProviderRequest(BaseModel):
    provider: str

class TokenRefreshResponse(BaseModel):
    token: str


# Create router
auth_router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Security scheme
security = HTTPBearer()

# Initialize services
auth_service = AuthenticationService()
oauth_config = OAuthConfig()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user from JWT token."""
    token = credentials.credentials
    user = auth_service.get_user_by_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user


@auth_router.get("/providers")
async def get_available_providers() -> Dict[str, Any]:
    """Get list of available OAuth providers."""
    try:
        providers = oauth_config.get_frontend_provider_list()
        return {
            "success": True,
            "providers": providers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@auth_router.get("/providers/debug")
async def debug_providers() -> Dict[str, Any]:
    """Debug endpoint to check provider configurations."""
    try:
        from ..config.settings import Config
        
        google_config = oauth_config.get_provider_config('google')
        
        return {
            "google_client_id_set": bool(Config.GOOGLE_CLIENT_ID),
            "google_client_secret_set": bool(Config.GOOGLE_CLIENT_SECRET),
            "google_client_id_length": len(Config.GOOGLE_CLIENT_ID) if Config.GOOGLE_CLIENT_ID else 0,
            "google_config_exists": google_config is not None,
            "google_config_enabled": google_config.get('enabled') if google_config else False,
            "all_providers": list(oauth_config.get_all_providers().keys()),
            "enabled_providers": list(oauth_config.get_enabled_providers().keys())
        }
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__
        }


@auth_router.post("/authorize", response_model=AuthUrlResponse)
async def get_authorization_url(request: AuthUrlRequest) -> AuthUrlResponse:
    """Get OAuth authorization URL for a provider."""
    try:
        result = auth_service.get_authorization_url(
            provider=request.provider,
            redirect_url=request.redirect_url
        )
        
        return AuthUrlResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@auth_router.get("/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str,
    state: str,
    error: Optional[str] = None
) -> AuthCallbackResponse:
    """Handle OAuth callback from provider."""
    if error:
        return AuthCallbackResponse(
            success=False,
            error=f"OAuth error: {error}"
        )
    
    try:
        result = auth_service.handle_oauth_callback(
            provider=provider,
            code=code,
            state=state
        )
        
        return AuthCallbackResponse(**result)
        
    except ValueError as e:
        return AuthCallbackResponse(
            success=False,
            error=str(e)
        )
    except Exception as e:
        return AuthCallbackResponse(
            success=False,
            error="Authentication failed"
        )


@auth_router.post("/refresh")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenRefreshResponse:
    """Refresh JWT token."""
    try:
        current_token = credentials.credentials
        new_token = auth_service.refresh_jwt_token(current_token)
        
        if not new_token:
            raise HTTPException(status_code=401, detail="Token refresh failed")
        
        return TokenRefreshResponse(token=new_token)
        
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token refresh failed")


@auth_router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Logout user."""
    try:
        token = credentials.credentials
        success = auth_service.logout_user(token)
        
        return {
            "success": success,
            "message": "Logged out successfully" if success else "Logout failed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Logout failed")


@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)) -> UserResponse:
    """Get current user information."""
    try:
        oauth_providers = auth_service.get_user_oauth_providers(current_user.id)
        
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            main_language=current_user.main_language,
            profile_image_url=current_user.profile_image_url,
            oauth_providers=oauth_providers
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get user info")


@auth_router.post("/link-provider")
async def link_oauth_provider(
    request: LinkProviderRequest,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """Link additional OAuth provider to current user."""
    try:
        success = auth_service.link_oauth_provider(
            user_id=current_user.id,
            provider=request.provider,
            auth_code=request.code,
            state=request.state
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to link provider")
        
        return {
            "success": True,
            "message": f"Successfully linked {request.provider} account"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.post("/unlink-provider")
async def unlink_oauth_provider(
    request: UnlinkProviderRequest,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """Unlink OAuth provider from current user."""
    try:
        success = auth_service.unlink_oauth_provider(
            user_id=current_user.id,
            provider=request.provider
        )
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="Cannot unlink provider (last provider or not found)"
            )
        
        return {
            "success": True,
            "message": f"Successfully unlinked {request.provider} account"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.get("/validate")
async def validate_token(current_user = Depends(get_current_user)) -> Dict[str, Any]:
    """Validate current JWT token."""
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email
    }


# Middleware for handling CORS and security headers
@auth_router.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to responses."""
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    return response