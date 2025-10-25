"""
Session management utilities for JWT tokens and user sessions.
"""
import jwt
import time
from typing import Dict, Any, Optional, Set
from datetime import datetime, timedelta
from config.settings import Config


class SessionManager:
    """Manage user sessions and JWT tokens."""
    
    def __init__(self):
        self.config = Config()
        # In-memory token blacklist (use Redis in production)
        self._blacklisted_tokens: Set[str] = set()
    
    def create_session_token(self, user_data: Dict[str, Any]) -> str:
        """
        Create JWT session token for user.
        
        Args:
            user_data: User information to encode in token
            
        Returns:
            JWT token string
        """
        payload = {
            'user_id': user_data['id'],
            'email': user_data['email'],
            'name': user_data['name'],
            'main_language': user_data.get('main_language', 'ja'),
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=7),  # 7 days expiration
            'type': 'access_token'
        }
        
        return jwt.encode(payload, self.config.JWT_SECRET_KEY, algorithm='HS256')
    
    def create_refresh_token(self, user_id: str) -> str:
        """
        Create refresh token for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Refresh token string
        """
        payload = {
            'user_id': user_id,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=30),  # 30 days expiration
            'type': 'refresh_token'
        }
        
        return jwt.encode(payload, self.config.JWT_SECRET_KEY, algorithm='HS256')
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate JWT token and return payload.
        
        Args:
            token: JWT token to validate
            
        Returns:
            Token payload if valid, None otherwise
        """
        if token in self._blacklisted_tokens:
            return None
        
        try:
            payload = jwt.decode(token, self.config.JWT_SECRET_KEY, algorithms=['HS256'])
            
            # Check token type
            if payload.get('type') != 'access_token':
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def validate_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate refresh token.
        
        Args:
            token: Refresh token to validate
            
        Returns:
            Token payload if valid, None otherwise
        """
        if token in self._blacklisted_tokens:
            return None
        
        try:
            payload = jwt.decode(token, self.config.JWT_SECRET_KEY, algorithms=['HS256'])
            
            # Check token type
            if payload.get('type') != 'refresh_token':
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_access_token(self, refresh_token: str, user_data: Dict[str, Any]) -> Optional[str]:
        """
        Create new access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            user_data: Current user data
            
        Returns:
            New access token if refresh is successful
        """
        payload = self.validate_refresh_token(refresh_token)
        if not payload:
            return None
        
        # Verify user ID matches
        if payload['user_id'] != user_data['id']:
            return None
        
        return self.create_session_token(user_data)
    
    def blacklist_token(self, token: str) -> bool:
        """
        Add token to blacklist (logout).
        
        Args:
            token: Token to blacklist
            
        Returns:
            True if successful
        """
        self._blacklisted_tokens.add(token)
        return True
    
    def is_token_blacklisted(self, token: str) -> bool:
        """
        Check if token is blacklisted.
        
        Args:
            token: Token to check
            
        Returns:
            True if token is blacklisted
        """
        return token in self._blacklisted_tokens
    
    def cleanup_expired_tokens(self):
        """
        Clean up expired tokens from blacklist.
        This should be called periodically to prevent memory leaks.
        """
        # For production, implement proper cleanup with Redis expiration
        # For now, we'll keep all tokens in memory
        pass
    
    def get_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a token without validating expiration.
        
        Args:
            token: JWT token
            
        Returns:
            Token information if decodable
        """
        try:
            payload = jwt.decode(
                token, 
                self.config.JWT_SECRET_KEY, 
                algorithms=['HS256'],
                options={"verify_exp": False}  # Don't verify expiration
            )
            return payload
        except jwt.InvalidTokenError:
            return None
    
    def create_state_token(self, provider: str, redirect_url: Optional[str] = None) -> str:
        """
        Create OAuth state token for CSRF protection.
        
        Args:
            provider: OAuth provider name
            redirect_url: Optional redirect URL after auth
            
        Returns:
            State token
        """
        payload = {
            'provider': provider,
            'redirect_url': redirect_url,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=10),  # 10 minutes expiration
            'type': 'oauth_state'
        }
        
        return jwt.encode(payload, self.config.JWT_SECRET_KEY, algorithm='HS256')
    
    def validate_state_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate OAuth state token.
        
        Args:
            token: State token to validate
            
        Returns:
            State payload if valid
        """
        try:
            payload = jwt.decode(token, self.config.JWT_SECRET_KEY, algorithms=['HS256'])
            
            # Check token type
            if payload.get('type') != 'oauth_state':
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


# Global session manager instance
session_manager = SessionManager()