"""
Application configuration and environment variable management.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class with environment variable management."""
    
    # LiveKit Configuration
    LIVEKIT_API_KEY: str = os.getenv('LIVEKIT_API_KEY', '')
    LIVEKIT_API_SECRET: str = os.getenv('LIVEKIT_API_SECRET', '')
    LIVEKIT_URL: str = os.getenv('LIVEKIT_URL', 'ws://localhost:7880')
    
    # OAuth Provider Configuration
    GOOGLE_CLIENT_ID: str = os.getenv('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET: str = os.getenv('GOOGLE_CLIENT_SECRET', '')
    
    TWITTER_CLIENT_ID: str = os.getenv('TWITTER_CLIENT_ID', '')
    TWITTER_CLIENT_SECRET: str = os.getenv('TWITTER_CLIENT_SECRET', '')
    TWITTER_BEARER_TOKEN: str = os.getenv('TWITTER_BEARER_TOKEN', '')
    
    LINE_CLIENT_ID: str = os.getenv('LINE_CLIENT_ID', '')
    LINE_CLIENT_SECRET: str = os.getenv('LINE_CLIENT_SECRET', '')
    
    # AI/ML Service Configuration
    GOOGLE_VISION_API_KEY: str = os.getenv('GOOGLE_VISION_API_KEY', '')
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    GOOGLE_TRANSLATE_API_KEY: str = os.getenv('GOOGLE_TRANSLATE_API_KEY', '')
    GOOGLE_SPEECH_TO_TEXT_API_KEY: str = os.getenv('GOOGLE_SPEECH_TO_TEXT_API_KEY', '')
    GOOGLE_TEXT_TO_SPEECH_API_KEY: str = os.getenv('GOOGLE_TEXT_TO_SPEECH_API_KEY', '')
    
    # Wine Database API
    WINE_API_KEY: str = os.getenv('WINE_API_KEY', '')
    WINE_API_BASE_URL: str = os.getenv('WINE_API_BASE_URL', 'https://api.wine.com')
    
    # Security Configuration
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
    
    # Database Configuration
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///wine_chat.db')
    
    # Application Configuration
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
    
    # Optional Services
    REDIS_URL: Optional[str] = os.getenv('REDIS_URL')
    SENTRY_DSN: Optional[str] = os.getenv('SENTRY_DSN')

class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///wine_chat_dev.db')

class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/wine_chat')

class TestingConfig(Config):
    """Testing environment configuration."""
    DEBUG = True
    DATABASE_URL = 'sqlite:///:memory:'

# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

def get_config() -> Config:
    """Get configuration based on environment."""
    env = os.getenv('ENVIRONMENT', 'development')
    return config_map.get(env, DevelopmentConfig)()

# OAuth Provider configurations
OAUTH_PROVIDERS = {
    'google': {
        'client_id': Config.GOOGLE_CLIENT_ID,
        'client_secret': Config.GOOGLE_CLIENT_SECRET,
        'scope': ['openid', 'email', 'profile'],
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'token_url': 'https://oauth2.googleapis.com/token',
        'userinfo_url': 'https://www.googleapis.com/oauth2/v2/userinfo'
    },
    'twitter': {
        'client_id': Config.TWITTER_CLIENT_ID,
        'client_secret': Config.TWITTER_CLIENT_SECRET,
        'bearer_token': Config.TWITTER_BEARER_TOKEN,
        'scope': ['tweet.read', 'users.read'],
        'authorize_url': 'https://twitter.com/i/oauth2/authorize',
        'token_url': 'https://api.twitter.com/2/oauth2/token',
        'userinfo_url': 'https://api.twitter.com/2/users/me'
    },
    'line': {
        'client_id': Config.LINE_CLIENT_ID,
        'client_secret': Config.LINE_CLIENT_SECRET,
        'scope': ['profile', 'openid'],
        'authorize_url': 'https://access.line.me/oauth2/v2.1/authorize',
        'token_url': 'https://api.line.me/oauth2/v2.1/token',
        'userinfo_url': 'https://api.line.me/v2/profile'
    }
}