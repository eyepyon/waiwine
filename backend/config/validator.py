"""
Environment variable validation system.
"""
import os
import sys
from typing import List, Dict, Any
from .settings import Config

class ConfigValidator:
    """Environment variable validation and checking."""
    
    REQUIRED_VARS = [
        'LIVEKIT_API_KEY',
        'LIVEKIT_API_SECRET', 
        'LIVEKIT_URL',
        'SECRET_KEY',
        'JWT_SECRET_KEY'
    ]
    
    OAUTH_REQUIRED_VARS = {
        'google': ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET'],
        'twitter': ['TWITTER_CLIENT_ID', 'TWITTER_CLIENT_SECRET'],
        'line': ['LINE_CLIENT_ID', 'LINE_CLIENT_SECRET']
    }
    
    @classmethod
    def validate_required_vars(cls) -> List[str]:
        """Check for required environment variables."""
        missing_vars = []
        
        for var in cls.REQUIRED_VARS:
            if not os.getenv(var):
                missing_vars.append(var)
        
        return missing_vars
    
    @classmethod
    def validate_oauth_providers(cls) -> Dict[str, Dict[str, Any]]:
        """Check OAuth provider configurations."""
        provider_status = {}
        
        for provider, vars_needed in cls.OAUTH_REQUIRED_VARS.items():
            missing = [var for var in vars_needed if not os.getenv(var)]
            provider_status[provider] = {
                'enabled': len(missing) == 0,
                'missing_vars': missing
            }
        
        return provider_status
    
    @classmethod
    def validate_all(cls) -> bool:
        """Comprehensive configuration validation."""
        missing_required = cls.validate_required_vars()
        oauth_status = cls.validate_oauth_providers()
        
        if missing_required:
            print(f"❌ Missing required environment variables: {', '.join(missing_required)}")
            return False
        
        enabled_providers = [p for p, status in oauth_status.items() if status['enabled']]
        
        if not enabled_providers:
            print("❌ No OAuth providers are properly configured")
            return False
        
        print(f"✅ Configuration valid. Enabled OAuth providers: {', '.join(enabled_providers)}")
        return True
    
    @classmethod
    def get_validation_report(cls) -> Dict[str, Any]:
        """Get detailed validation report."""
        return {
            'missing_required': cls.validate_required_vars(),
            'oauth_providers': cls.validate_oauth_providers(),
            'is_valid': cls.validate_all()
        }

def validate_config_on_startup():
    """Validate configuration on application startup."""
    if not ConfigValidator.validate_all():
        print("Configuration validation failed. Please check your environment variables.")
        return False
    return True