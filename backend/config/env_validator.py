"""
Comprehensive environment variable validation system.
"""
import os
import sys
import re
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse
from .settings import Config

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

class EnvironmentValidator:
    """Comprehensive environment variable validation."""
    
    # Required variables that must be present
    REQUIRED_VARS = [
        'SECRET_KEY',
        'JWT_SECRET_KEY',
    ]
    
    # LiveKit configuration
    LIVEKIT_VARS = [
        'LIVEKIT_API_KEY',
        'LIVEKIT_API_SECRET',
        'LIVEKIT_URL'
    ]
    
    # OAuth provider configurations
    OAUTH_PROVIDERS = {
        'google': {
            'vars': ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET'],
            'name': 'Google OAuth'
        },
        'twitter': {
            'vars': ['TWITTER_CLIENT_ID', 'TWITTER_CLIENT_SECRET'],
            'name': 'Twitter/X OAuth'
        },
        'line': {
            'vars': ['LINE_CLIENT_ID', 'LINE_CLIENT_SECRET'],
            'name': 'LINE Login'
        }
    }
    
    # Google Cloud API configurations
    GOOGLE_CLOUD_APIS = {
        'vision': {
            'vars': ['GOOGLE_VISION_API_KEY'],
            'name': 'Google Vision API'
        },
        'translate': {
            'vars': ['GOOGLE_TRANSLATE_API_KEY'],
            'name': 'Google Translate API'
        },
        'speech': {
            'vars': ['GOOGLE_SPEECH_TO_TEXT_API_KEY'],
            'name': 'Google Speech-to-Text API'
        },
        'tts': {
            'vars': ['GOOGLE_TEXT_TO_SPEECH_API_KEY'],
            'name': 'Google Text-to-Speech API'
        }
    }
    
    # Optional service configurations
    OPTIONAL_SERVICES = {
        'wine_api': {
            'vars': ['WINE_API_KEY', 'WINE_API_BASE_URL'],
            'name': 'Wine Database API'
        },
        'redis': {
            'vars': ['REDIS_URL'],
            'name': 'Redis Cache'
        },
        'email': {
            'vars': ['SMTP_SERVER', 'SMTP_USERNAME', 'SMTP_PASSWORD'],
            'name': 'Email Service'
        },
        'sentry': {
            'vars': ['SENTRY_DSN'],
            'name': 'Sentry Error Tracking'
        },
        'aws_s3': {
            'vars': ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_S3_BUCKET_NAME'],
            'name': 'AWS S3 Storage'
        }
    }
    
    @classmethod
    def validate_required_vars(cls) -> List[str]:
        """Validate required environment variables."""
        missing = []
        
        for var in cls.REQUIRED_VARS:
            if not os.getenv(var):
                missing.append(var)
        
        return missing
    
    @classmethod
    def validate_livekit_config(cls) -> Dict[str, Any]:
        """Validate LiveKit configuration."""
        missing = []
        invalid = []
        
        for var in cls.LIVEKIT_VARS:
            value = os.getenv(var)
            if not value:
                missing.append(var)
            elif var == 'LIVEKIT_URL':
                if not cls._is_valid_websocket_url(value):
                    invalid.append(f"{var}: Invalid WebSocket URL format")
        
        return {
            'enabled': len(missing) == 0,
            'missing': missing,
            'invalid': invalid
        }
    
    @classmethod
    def validate_oauth_providers(cls) -> Dict[str, Dict[str, Any]]:
        """Validate OAuth provider configurations."""
        results = {}
        
        for provider, config in cls.OAUTH_PROVIDERS.items():
            missing = []
            invalid = []
            
            for var in config['vars']:
                value = os.getenv(var)
                if not value:
                    missing.append(var)
                elif 'CLIENT_ID' in var and not cls._is_valid_client_id(value):
                    invalid.append(f"{var}: Invalid client ID format")
            
            results[provider] = {
                'name': config['name'],
                'enabled': len(missing) == 0,
                'missing': missing,
                'invalid': invalid
            }
        
        return results
    
    @classmethod
    def validate_google_cloud_apis(cls) -> Dict[str, Dict[str, Any]]:
        """Validate Google Cloud API configurations."""
        results = {}
        
        for api, config in cls.GOOGLE_CLOUD_APIS.items():
            missing = []
            invalid = []
            
            for var in config['vars']:
                value = os.getenv(var)
                if not value:
                    missing.append(var)
                elif 'API_KEY' in var and not cls._is_valid_api_key(value):
                    invalid.append(f"{var}: Invalid API key format")
            
            results[api] = {
                'name': config['name'],
                'enabled': len(missing) == 0,
                'missing': missing,
                'invalid': invalid
            }
        
        return results
    
    @classmethod
    def validate_optional_services(cls) -> Dict[str, Dict[str, Any]]:
        """Validate optional service configurations."""
        results = {}
        
        for service, config in cls.OPTIONAL_SERVICES.items():
            missing = []
            invalid = []
            
            for var in config['vars']:
                value = os.getenv(var)
                if not value:
                    missing.append(var)
                else:
                    # Specific validations
                    if var == 'REDIS_URL' and not cls._is_valid_redis_url(value):
                        invalid.append(f"{var}: Invalid Redis URL format")
                    elif var == 'SENTRY_DSN' and not cls._is_valid_sentry_dsn(value):
                        invalid.append(f"{var}: Invalid Sentry DSN format")
                    elif 'EMAIL' in var.upper() and '@' in var and not cls._is_valid_email(value):
                        invalid.append(f"{var}: Invalid email format")
            
            results[service] = {
                'name': config['name'],
                'enabled': len(missing) == 0,
                'missing': missing,
                'invalid': invalid
            }
        
        return results
    
    @classmethod
    def validate_database_config(cls) -> Dict[str, Any]:
        """Validate database configuration."""
        database_url = os.getenv('DATABASE_URL', 'sqlite:///wine_chat.db')
        
        try:
            parsed = urlparse(database_url)
            
            if parsed.scheme not in ['sqlite', 'postgresql', 'mysql']:
                return {
                    'valid': False,
                    'error': f"Unsupported database scheme: {parsed.scheme}"
                }
            
            if parsed.scheme == 'sqlite':
                return {'valid': True, 'type': 'sqlite', 'path': parsed.path}
            else:
                return {
                    'valid': True,
                    'type': parsed.scheme,
                    'host': parsed.hostname,
                    'port': parsed.port,
                    'database': parsed.path.lstrip('/')
                }
        
        except Exception as e:
            return {
                'valid': False,
                'error': f"Invalid database URL: {str(e)}"
            }
    
    @classmethod
    def validate_security_config(cls) -> Dict[str, Any]:
        """Validate security-related configuration."""
        issues = []
        
        # Check secret key strength
        secret_key = os.getenv('SECRET_KEY', '')
        if len(secret_key) < 32:
            issues.append("SECRET_KEY should be at least 32 characters long")
        
        jwt_secret = os.getenv('JWT_SECRET_KEY', '')
        if len(jwt_secret) < 32:
            issues.append("JWT_SECRET_KEY should be at least 32 characters long")
        
        # Check for default/weak keys
        weak_keys = [
            'dev-secret-key',
            'change-in-production',
            'your_secret_key',
            'secret',
            '123456'
        ]
        
        for key in [secret_key, jwt_secret]:
            if any(weak in key.lower() for weak in weak_keys):
                issues.append("Detected weak or default secret key")
                break
        
        # Check environment
        environment = os.getenv('ENVIRONMENT', 'development')
        debug = os.getenv('DEBUG', 'False').lower() == 'true'
        
        if environment == 'production' and debug:
            issues.append("DEBUG should be False in production environment")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'environment': environment,
            'debug': debug
        }
    
    @classmethod
    def get_comprehensive_report(cls) -> Dict[str, Any]:
        """Get a comprehensive validation report."""
        report = {
            'timestamp': cls._get_timestamp(),
            'overall_status': 'unknown',
            'required_vars': cls.validate_required_vars(),
            'livekit': cls.validate_livekit_config(),
            'oauth_providers': cls.validate_oauth_providers(),
            'google_cloud_apis': cls.validate_google_cloud_apis(),
            'optional_services': cls.validate_optional_services(),
            'database': cls.validate_database_config(),
            'security': cls.validate_security_config()
        }
        
        # Determine overall status
        critical_issues = []
        
        if report['required_vars']:
            critical_issues.extend(report['required_vars'])
        
        if not report['livekit']['enabled']:
            critical_issues.append('LiveKit configuration incomplete')
        
        if not report['database']['valid']:
            critical_issues.append('Database configuration invalid')
        
        if not report['security']['valid']:
            critical_issues.extend(report['security']['issues'])
        
        # Check if at least one OAuth provider is configured
        oauth_enabled = any(
            provider['enabled'] 
            for provider in report['oauth_providers'].values()
        )
        
        if not oauth_enabled:
            critical_issues.append('No OAuth providers configured')
        
        if critical_issues:
            report['overall_status'] = 'critical'
            report['critical_issues'] = critical_issues
        else:
            report['overall_status'] = 'good'
        
        return report
    
    @classmethod
    def print_validation_report(cls, detailed: bool = False) -> bool:
        """Print a formatted validation report."""
        report = cls.get_comprehensive_report()
        
        print("\n" + "="*60)
        print("🍷 WINE CHAT - ENVIRONMENT VALIDATION REPORT")
        print("="*60)
        
        # Overall status
        status_emoji = "✅" if report['overall_status'] == 'good' else "❌"
        print(f"\n{status_emoji} Overall Status: {report['overall_status'].upper()}")
        
        if report['overall_status'] == 'critical':
            print("\n🚨 CRITICAL ISSUES:")
            for issue in report.get('critical_issues', []):
                print(f"   • {issue}")
        
        # Required variables
        if report['required_vars']:
            print(f"\n❌ Missing Required Variables:")
            for var in report['required_vars']:
                print(f"   • {var}")
        else:
            print(f"\n✅ All required variables present")
        
        # LiveKit
        livekit = report['livekit']
        status = "✅" if livekit['enabled'] else "❌"
        print(f"\n{status} LiveKit Configuration")
        if not livekit['enabled'] and detailed:
            if livekit['missing']:
                print(f"   Missing: {', '.join(livekit['missing'])}")
            if livekit['invalid']:
                for invalid in livekit['invalid']:
                    print(f"   Invalid: {invalid}")
        
        # OAuth Providers
        print(f"\n📱 OAuth Providers:")
        for provider, config in report['oauth_providers'].items():
            status = "✅" if config['enabled'] else "❌"
            print(f"   {status} {config['name']}")
            if not config['enabled'] and detailed:
                if config['missing']:
                    print(f"      Missing: {', '.join(config['missing'])}")
        
        # Google Cloud APIs
        if detailed:
            print(f"\n☁️  Google Cloud APIs:")
            for api, config in report['google_cloud_apis'].items():
                status = "✅" if config['enabled'] else "❌"
                print(f"   {status} {config['name']}")
        
        # Database
        db = report['database']
        status = "✅" if db['valid'] else "❌"
        print(f"\n{status} Database Configuration")
        if db['valid']:
            print(f"   Type: {db.get('type', 'unknown')}")
        elif detailed:
            print(f"   Error: {db.get('error', 'Unknown error')}")
        
        # Security
        security = report['security']
        status = "✅" if security['valid'] else "⚠️"
        print(f"\n{status} Security Configuration")
        print(f"   Environment: {security['environment']}")
        print(f"   Debug Mode: {security['debug']}")
        if not security['valid'] and detailed:
            for issue in security['issues']:
                print(f"   Issue: {issue}")
        
        print("\n" + "="*60)
        
        return report['overall_status'] == 'good'
    
    # Helper validation methods
    @staticmethod
    def _is_valid_websocket_url(url: str) -> bool:
        """Validate WebSocket URL format."""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ['ws', 'wss'] and parsed.netloc
        except:
            return False
    
    @staticmethod
    def _is_valid_client_id(client_id: str) -> bool:
        """Validate OAuth client ID format."""
        return len(client_id) > 10 and not client_id.startswith('your_')
    
    @staticmethod
    def _is_valid_api_key(api_key: str) -> bool:
        """Validate API key format."""
        return len(api_key) > 20 and not api_key.startswith('your_')
    
    @staticmethod
    def _is_valid_redis_url(url: str) -> bool:
        """Validate Redis URL format."""
        try:
            parsed = urlparse(url)
            return parsed.scheme == 'redis' and parsed.netloc
        except:
            return False
    
    @staticmethod
    def _is_valid_sentry_dsn(dsn: str) -> bool:
        """Validate Sentry DSN format."""
        return dsn.startswith('https://') and '@sentry.io' in dsn
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

def validate_environment_on_startup() -> bool:
    """Validate environment on application startup."""
    return EnvironmentValidator.print_validation_report(detailed=True)

def quick_validation_check() -> bool:
    """Quick validation check without detailed output."""
    report = EnvironmentValidator.get_comprehensive_report()
    return report['overall_status'] == 'good'

if __name__ == "__main__":
    # Run validation when script is executed directly
    success = validate_environment_on_startup()
    sys.exit(0 if success else 1)