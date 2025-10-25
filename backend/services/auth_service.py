"""
OAuth Authentication Service for multiple providers.
Handles OAuth flows, user sessions, and JWT token management.
"""
import jwt
import time
import secrets
import hashlib
import base64
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
from urllib.parse import urlencode
import requests
from sqlalchemy.orm import Session

from ..models.user import User, OAuthProvider, TranslationSettings
from ..models.database import get_db
from ..config.oauth_config import OAuthConfig, OAuthStateManager
from ..config.settings import Config
from .session_manager import session_manager


class AuthenticationService:
    """Main authentication service handling OAuth flows and session management."""
    
    def __init__(self):
        self.config = Config()
        self.oauth_config = OAuthConfig()
        self.state_manager = OAuthStateManager()
    
    def get_authorization_url(self, provider: str, redirect_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate OAuth authorization URL for a provider.
        
        Args:
            provider: OAuth provider name ('google', 'twitter', 'line')
            redirect_url: Optional frontend redirect URL after auth
            
        Returns:
            Dict containing authorization URL and state information
        """
        # Validate provider
        provider_config = self.oauth_config.get_provider_config(provider)
        if not provider_config:
            raise ValueError(f"Provider '{provider}' is not configured or enabled")
        
        # Generate state token for security
        state = self.state_manager.generate_state()
        
        # Store state with provider info
        state_data = {
            'provider': provider,
            'redirect_url': redirect_url,
            'timestamp': time.time()
        }
        self.state_manager.store_state(state, provider, state_data)
        
        # Generate authorization URL
        auth_params = {
            'client_id': provider_config['client_id'],
            'redirect_uri': provider_config['redirect_uri'],
            'response_type': provider_config['response_type'],
            'scope': ' '.join(provider_config['scope']),
            'state': state
        }
        
        # Provider-specific parameters
        if provider == 'google':
            auth_params.update({
                'access_type': provider_config.get('access_type', 'offline'),
                'prompt': provider_config.get('prompt', 'consent')
            })
        elif provider == 'twitter':
            # Generate PKCE parameters for Twitter OAuth 2.0
            code_verifier = self.state_manager.generate_code_verifier()
            code_challenge = self.state_manager.generate_code_challenge(code_verifier)
            
            # Store code verifier with state
            state_data['code_verifier'] = code_verifier
            self.state_manager.store_state(state, provider, state_data)
            
            auth_params.update({
                'code_challenge': code_challenge,
                'code_challenge_method': provider_config.get('code_challenge_method', 'S256')
            })
        
        authorization_url = f"{provider_config['authorize_url']}?{urlencode(auth_params)}"
        
        return {
            'authorization_url': authorization_url,
            'state': state,
            'provider': provider
        }
    
    def handle_oauth_callback(self, provider: str, code: str, state: str) -> Dict[str, Any]:
        """
        Handle OAuth callback and complete authentication flow.
        
        Args:
            provider: OAuth provider name
            code: Authorization code from provider
            state: State token for validation
            
        Returns:
            Dict containing user info and JWT token
        """
        # Validate state
        state_data = self.state_manager.validate_and_consume_state(state)
        if not state_data or state_data['provider'] != provider:
            raise ValueError("Invalid or expired state token")
        
        # Get provider configuration
        provider_config = self.oauth_config.get_provider_config(provider)
        if not provider_config:
            raise ValueError(f"Provider '{provider}' is not configured")
        
        # Exchange code for access token
        token_data = self._exchange_code_for_token(provider, code, state_data)
        
        # Get user info from provider
        user_info = self._get_user_info_from_provider(provider, token_data['access_token'])
        
        # Create or update user
        db = next(get_db())
        try:
            user = self._create_or_update_user(db, provider, user_info)
            
            # Generate JWT token
            jwt_token = self._generate_jwt_token(user)
            
            return {
                'success': True,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'main_language': user.main_language,
                    'profile_image_url': user.profile_image_url
                },
                'token': jwt_token,
                'redirect_url': state_data.get('redirect_url')
            }
        finally:
            db.close()
    
    def _exchange_code_for_token(self, provider: str, code: str, state_data: Dict) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        provider_config = self.oauth_config.get_provider_config(provider)
        
        token_params = {
            'client_id': provider_config['client_id'],
            'client_secret': provider_config['client_secret'],
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': provider_config['redirect_uri']
        }
        
        # Provider-specific parameters
        if provider == 'twitter':
            # Add PKCE code verifier for Twitter
            code_verifier = state_data.get('code_verifier')
            if code_verifier:
                token_params['code_verifier'] = code_verifier
        
        # Make token request
        response = requests.post(
            provider_config['token_url'],
            data=token_params,
            headers={'Accept': 'application/json'}
        )
        
        if response.status_code != 200:
            raise ValueError(f"Token exchange failed: {response.text}")
        
        return response.json()
    
    def _get_user_info_from_provider(self, provider: str, access_token: str) -> Dict[str, Any]:
        """Get user information from OAuth provider."""
        provider_config = self.oauth_config.get_provider_config(provider)
        
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Provider-specific API calls
        if provider == 'google':
            response = requests.get(provider_config['userinfo_url'], headers=headers)
        elif provider == 'twitter':
            # Twitter API v2 requires specific user fields
            url = f"{provider_config['userinfo_url']}?user.fields=id,name,username,profile_image_url"
            response = requests.get(url, headers=headers)
        elif provider == 'line':
            response = requests.get(provider_config['userinfo_url'], headers=headers)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        if response.status_code != 200:
            raise ValueError(f"Failed to get user info: {response.text}")
        
        user_data = response.json()
        
        # Normalize user data across providers
        return self._normalize_user_data(provider, user_data)
    
    def _normalize_user_data(self, provider: str, raw_data: Dict) -> Dict[str, Any]:
        """Normalize user data from different providers to a common format."""
        if provider == 'google':
            return {
                'provider_user_id': raw_data['id'],
                'email': raw_data.get('email'),
                'name': raw_data.get('name'),
                'profile_image_url': raw_data.get('picture')
            }
        elif provider == 'twitter':
            # Twitter API v2 response format
            user_data = raw_data.get('data', {})
            return {
                'provider_user_id': user_data['id'],
                'email': None,  # Twitter doesn't provide email by default
                'name': user_data.get('name'),
                'profile_image_url': user_data.get('profile_image_url')
            }
        elif provider == 'line':
            return {
                'provider_user_id': raw_data['userId'],
                'email': None,  # LINE doesn't provide email
                'name': raw_data.get('displayName'),
                'profile_image_url': raw_data.get('pictureUrl')
            }
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _create_or_update_user(self, db: Session, provider: str, user_info: Dict) -> User:
        """Create new user or update existing user with OAuth provider info."""
        provider_user_id = user_info['provider_user_id']
        
        # Check if OAuth provider already exists
        oauth_provider = db.query(OAuthProvider).filter(
            OAuthProvider.provider_name == provider,
            OAuthProvider.provider_user_id == provider_user_id
        ).first()
        
        if oauth_provider:
            # User already exists, return the user
            return oauth_provider.user
        
        # Check if user exists by email (for account linking)
        user = None
        if user_info.get('email'):
            user = db.query(User).filter(User.email == user_info['email']).first()
        
        if not user:
            # Create new user
            user_id = self._generate_user_id()
            user = User(
                id=user_id,
                email=user_info.get('email') or f"{provider}_{provider_user_id}@example.com",
                name=user_info.get('name') or f"User_{provider_user_id}",
                main_language='ja',  # Default language
                profile_image_url=user_info.get('profile_image_url')
            )
            db.add(user)
            db.flush()  # Get user ID
            
            # Create default translation settings
            translation_settings = TranslationSettings(user_id=user.id)
            db.add(translation_settings)
        
        # Link OAuth provider to user
        new_oauth_provider = OAuthProvider(
            user_id=user.id,
            provider_name=provider,
            provider_user_id=provider_user_id,
            provider_email=user_info.get('email')
        )
        db.add(new_oauth_provider)
        
        db.commit()
        return user
    
    def _generate_user_id(self) -> str:
        """Generate unique user ID."""
        return f"user_{secrets.token_urlsafe(16)}"
    
    def _generate_jwt_token(self, user: User) -> str:
        """Generate JWT token for user session."""
        user_data = {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'main_language': user.main_language
        }
        
        return session_manager.create_session_token(user_data)
    
    def validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate JWT token and return user data.
        
        Args:
            token: JWT token string
            
        Returns:
            User data if token is valid, None otherwise
        """
        return session_manager.validate_token(token)
    
    def refresh_jwt_token(self, token: str) -> Optional[str]:
        """
        Refresh JWT token if it's still valid.
        
        Args:
            token: Current JWT token
            
        Returns:
            New JWT token if refresh is successful, None otherwise
        """
        payload = self.validate_jwt_token(token)
        if not payload:
            return None
        
        # Get user from database to ensure they still exist
        db = next(get_db())
        try:
            user = db.query(User).filter(User.id == payload['user_id']).first()
            if not user:
                return None
            
            return self._generate_jwt_token(user)
        finally:
            db.close()
    
    def logout_user(self, token: str) -> bool:
        """
        Logout user by invalidating token.
        
        Args:
            token: JWT token to invalidate
            
        Returns:
            True if logout successful
        """
        return session_manager.blacklist_token(token)
    
    def get_user_by_token(self, token: str) -> Optional[User]:
        """
        Get user object from JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            User object if token is valid, None otherwise
        """
        payload = self.validate_jwt_token(token)
        if not payload:
            return None
        
        db = next(get_db())
        try:
            return db.query(User).filter(User.id == payload['user_id']).first()
        finally:
            db.close()
    
    def link_oauth_provider(self, user_id: str, provider: str, auth_code: str, state: str) -> bool:
        """
        Link additional OAuth provider to existing user account.
        
        Args:
            user_id: Existing user ID
            provider: OAuth provider to link
            auth_code: Authorization code from provider
            state: State token for validation
            
        Returns:
            True if linking successful
        """
        try:
            # Validate state
            state_data = self.state_manager.validate_and_consume_state(state)
            if not state_data or state_data['provider'] != provider:
                return False
            
            # Exchange code for token and get user info
            token_data = self._exchange_code_for_token(provider, auth_code, state_data)
            user_info = self._get_user_info_from_provider(provider, token_data['access_token'])
            
            # Check if this provider is already linked to another user
            db = next(get_db())
            try:
                existing_oauth = db.query(OAuthProvider).filter(
                    OAuthProvider.provider_name == provider,
                    OAuthProvider.provider_user_id == user_info['provider_user_id']
                ).first()
                
                if existing_oauth:
                    return False  # Provider already linked to another account
                
                # Link provider to user
                new_oauth_provider = OAuthProvider(
                    user_id=user_id,
                    provider_name=provider,
                    provider_user_id=user_info['provider_user_id'],
                    provider_email=user_info.get('email')
                )
                db.add(new_oauth_provider)
                db.commit()
                
                return True
            finally:
                db.close()
                
        except Exception:
            return False
    
    def unlink_oauth_provider(self, user_id: str, provider: str) -> bool:
        """
        Unlink OAuth provider from user account.
        
        Args:
            user_id: User ID
            provider: OAuth provider to unlink
            
        Returns:
            True if unlinking successful
        """
        db = next(get_db())
        try:
            # Check if user has multiple providers (don't allow unlinking the last one)
            provider_count = db.query(OAuthProvider).filter(
                OAuthProvider.user_id == user_id
            ).count()
            
            if provider_count <= 1:
                return False  # Can't unlink the last provider
            
            # Remove the OAuth provider
            oauth_provider = db.query(OAuthProvider).filter(
                OAuthProvider.user_id == user_id,
                OAuthProvider.provider_name == provider
            ).first()
            
            if oauth_provider:
                db.delete(oauth_provider)
                db.commit()
                return True
            
            return False
        finally:
            db.close()
    
    def get_user_oauth_providers(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get list of OAuth providers linked to user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of linked OAuth providers
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