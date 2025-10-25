"""
OAuth provider configuration and management.
"""
import os
from typing import Dict, Any, Optional, List
from config.settings import Config

class OAuthConfig:
    """OAuth provider configuration management."""
    
    @classmethod
    def get_provider_config(cls, provider: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific OAuth provider."""
        configs = {
            'google': cls._get_google_config(),
            'twitter': cls._get_twitter_config(),
            'line': cls._get_line_config()
        }
        
        return configs.get(provider.lower())
    
    @classmethod
    def get_all_providers(cls) -> Dict[str, Dict[str, Any]]:
        """Get all available OAuth provider configurations."""
        return {
            'google': cls._get_google_config(),
            'twitter': cls._get_twitter_config(),
            'line': cls._get_line_config()
        }
    
    @classmethod
    def get_enabled_providers(cls) -> Dict[str, Dict[str, Any]]:
        """Get only enabled OAuth providers."""
        all_providers = cls.get_all_providers()
        return {
            name: config 
            for name, config in all_providers.items() 
            if config and config.get('enabled', False)
        }
    
    @classmethod
    def _get_google_config(cls) -> Optional[Dict[str, Any]]:
        """Get Google OAuth configuration."""
        client_id = Config.GOOGLE_CLIENT_ID
        client_secret = Config.GOOGLE_CLIENT_SECRET
        
        if not client_id or not client_secret:
            return None
        
        return {
            'enabled': True,
            'provider_name': 'google',
            'display_name': 'Google',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': ['openid', 'email', 'profile'],
            'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
            'token_url': 'https://oauth2.googleapis.com/token',
            'userinfo_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
            'revoke_url': 'https://oauth2.googleapis.com/revoke',
            'redirect_uri': f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/api/auth/google/callback",
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent'
        }
    
    @classmethod
    def _get_twitter_config(cls) -> Optional[Dict[str, Any]]:
        """Get Twitter/X OAuth configuration."""
        client_id = Config.TWITTER_CLIENT_ID
        client_secret = Config.TWITTER_CLIENT_SECRET
        bearer_token = Config.TWITTER_BEARER_TOKEN
        
        if not client_id or not client_secret:
            return None
        
        return {
            'enabled': True,
            'provider_name': 'twitter',
            'display_name': 'X (Twitter)',
            'client_id': client_id,
            'client_secret': client_secret,
            'bearer_token': bearer_token,
            'scope': ['tweet.read', 'users.read', 'offline.access'],
            'authorize_url': 'https://twitter.com/i/oauth2/authorize',
            'token_url': 'https://api.twitter.com/2/oauth2/token',
            'userinfo_url': 'https://api.twitter.com/2/users/me',
            'revoke_url': 'https://api.twitter.com/2/oauth2/revoke',
            'redirect_uri': f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/api/auth/twitter/callback",
            'response_type': 'code',
            'code_challenge_method': 'S256'  # PKCE required for Twitter OAuth 2.0
        }
    
    @classmethod
    def _get_line_config(cls) -> Optional[Dict[str, Any]]:
        """Get LINE Login configuration."""
        client_id = Config.LINE_CLIENT_ID
        client_secret = Config.LINE_CLIENT_SECRET
        
        if not client_id or not client_secret:
            return None
        
        return {
            'enabled': True,
            'provider_name': 'line',
            'display_name': 'LINE',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': ['profile', 'openid'],
            'authorize_url': 'https://access.line.me/oauth2/v2.1/authorize',
            'token_url': 'https://api.line.me/oauth2/v2.1/token',
            'userinfo_url': 'https://api.line.me/v2/profile',
            'revoke_url': 'https://api.line.me/oauth2/v2.1/revoke',
            'redirect_uri': f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/api/auth/line/callback",
            'response_type': 'code'
        }
    
    @classmethod
    def validate_provider_config(cls, provider: str) -> Dict[str, Any]:
        """Validate a specific provider configuration."""
        config = cls.get_provider_config(provider)
        
        if not config:
            return {
                'valid': False,
                'error': f'Provider {provider} is not configured or missing required credentials'
            }
        
        # Check required fields
        required_fields = ['client_id', 'client_secret', 'authorize_url', 'token_url']
        missing_fields = [field for field in required_fields if not config.get(field)]
        
        if missing_fields:
            return {
                'valid': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }
        
        return {
            'valid': True,
            'provider': provider,
            'display_name': config.get('display_name', provider),
            'scopes': config.get('scope', [])
        }
    
    @classmethod
    def get_authorization_url(cls, provider: str, state: str, **kwargs) -> Optional[str]:
        """Generate authorization URL for a provider."""
        config = cls.get_provider_config(provider)
        
        if not config:
            return None
        
        from urllib.parse import urlencode
        
        params = {
            'client_id': config['client_id'],
            'redirect_uri': config['redirect_uri'],
            'response_type': config['response_type'],
            'scope': ' '.join(config['scope']),
            'state': state
        }
        
        # Provider-specific parameters
        if provider == 'google':
            params.update({
                'access_type': config.get('access_type', 'offline'),
                'prompt': config.get('prompt', 'consent')
            })
        elif provider == 'twitter':
            # Twitter OAuth 2.0 with PKCE
            code_verifier = kwargs.get('code_verifier')
            code_challenge = kwargs.get('code_challenge')
            if code_verifier and code_challenge:
                params.update({
                    'code_challenge': code_challenge,
                    'code_challenge_method': config.get('code_challenge_method', 'S256')
                })
        
        # Add any additional parameters
        params.update(kwargs.get('extra_params', {}))
        
        return f"{config['authorize_url']}?{urlencode(params)}"
    
    @classmethod
    def get_frontend_provider_list(cls) -> List[Dict[str, Any]]:
        """Get provider list formatted for frontend consumption."""
        enabled_providers = cls.get_enabled_providers()
        
        return [
            {
                'name': name,
                'displayName': config['display_name'],
                'enabled': True
            }
            for name, config in enabled_providers.items()
        ]

# OAuth state management
class OAuthStateManager:
    """Manage OAuth state tokens for security."""
    
    @staticmethod
    def generate_state() -> str:
        """Generate a secure state token."""
        import secrets
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_code_verifier() -> str:
        """Generate PKCE code verifier."""
        import secrets
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_code_challenge(code_verifier: str) -> str:
        """Generate PKCE code challenge from verifier."""
        import hashlib
        import base64
        
        digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
    
    @staticmethod
    def store_state(state: str, provider: str, user_data: Optional[Dict] = None) -> bool:
        """Store OAuth state (implement with Redis or database)."""
        import time
        # TODO: Implement state storage
        # For now, we'll use a simple in-memory store (not suitable for production)
        if not hasattr(OAuthStateManager, '_state_store'):
            OAuthStateManager._state_store = {}
        
        OAuthStateManager._state_store[state] = {
            'provider': provider,
            'user_data': user_data,
            'timestamp': time.time()
        }
        
        return True
    
    @staticmethod
    def validate_and_consume_state(state: str) -> Optional[Dict]:
        """Validate and consume OAuth state."""
        import time
        
        if not hasattr(OAuthStateManager, '_state_store'):
            return None
        
        state_data = OAuthStateManager._state_store.pop(state, None)
        
        if not state_data:
            return None
        
        # Check if state is expired (5 minutes)
        if time.time() - state_data['timestamp'] > 300:
            return None
        
        return state_data