"""
Application startup utilities and checks.
"""
import sys
import os
from typing import Dict, Any
from backend.config.env_validator import EnvironmentValidator
from backend.config.oauth_config import OAuthConfig
from backend.models.database import init_database

class StartupManager:
    """Manage application startup process."""
    
    @classmethod
    def run_startup_checks(cls, verbose: bool = True) -> bool:
        """Run comprehensive startup checks."""
        if verbose:
            print("🍷 Starting Wine Chat Application...")
            print("Running startup checks...\n")
        
        checks = [
            ("Environment Variables", cls._check_environment),
            ("OAuth Configuration", cls._check_oauth_config),
            ("Database Connection", cls._check_database),
            ("External Services", cls._check_external_services)
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            if verbose:
                print(f"Checking {check_name}...")
            
            try:
                result = check_func()
                if result['success']:
                    if verbose:
                        print(f"✅ {check_name}: OK")
                        if result.get('details'):
                            for detail in result['details']:
                                print(f"   • {detail}")
                else:
                    if verbose:
                        print(f"❌ {check_name}: FAILED")
                        if result.get('errors'):
                            for error in result['errors']:
                                print(f"   • {error}")
                    all_passed = False
            
            except Exception as e:
                if verbose:
                    print(f"❌ {check_name}: ERROR - {str(e)}")
                all_passed = False
            
            if verbose:
                print()
        
        if verbose:
            if all_passed:
                print("🎉 All startup checks passed! Application ready to start.")
            else:
                print("🚨 Some startup checks failed. Please review the errors above.")
        
        return all_passed
    
    @classmethod
    def _check_environment(cls) -> Dict[str, Any]:
        """Check environment variable configuration."""
        try:
            report = EnvironmentValidator.get_comprehensive_report()
            
            if report['overall_status'] == 'good':
                return {
                    'success': True,
                    'details': ['All required environment variables configured']
                }
            else:
                errors = []
                if report.get('critical_issues'):
                    errors.extend(report['critical_issues'])
                
                return {
                    'success': False,
                    'errors': errors or ['Environment validation failed']
                }
        
        except Exception as e:
            return {
                'success': False,
                'errors': [f'Environment check failed: {str(e)}']
            }
    
    @classmethod
    def _check_oauth_config(cls) -> Dict[str, Any]:
        """Check OAuth provider configuration."""
        try:
            enabled_providers = OAuthConfig.get_enabled_providers()
            
            if not enabled_providers:
                return {
                    'success': False,
                    'errors': ['No OAuth providers configured']
                }
            
            details = []
            errors = []
            
            for provider_name, config in enabled_providers.items():
                validation = OAuthConfig.validate_provider_config(provider_name)
                
                if validation['valid']:
                    details.append(f"{validation['display_name']} configured")
                else:
                    errors.append(f"{provider_name}: {validation['error']}")
            
            return {
                'success': len(errors) == 0,
                'details': details,
                'errors': errors
            }
        
        except Exception as e:
            return {
                'success': False,
                'errors': [f'OAuth configuration check failed: {str(e)}']
            }
    
    @classmethod
    def _check_database(cls) -> Dict[str, Any]:
        """Check database connection and initialization."""
        try:
            # Initialize database tables
            init_database()
            
            # Test database connection
            from backend.models.database import SessionLocal
            
            db = SessionLocal()
            try:
                # Simple query to test connection
                db.execute("SELECT 1")
                db.close()
                
                return {
                    'success': True,
                    'details': ['Database connection successful', 'Tables initialized']
                }
            
            except Exception as e:
                db.close()
                return {
                    'success': False,
                    'errors': [f'Database connection failed: {str(e)}']
                }
        
        except Exception as e:
            return {
                'success': False,
                'errors': [f'Database initialization failed: {str(e)}']
            }
    
    @classmethod
    def _check_external_services(cls) -> Dict[str, Any]:
        """Check external service connectivity."""
        details = []
        warnings = []
        
        # Check LiveKit connectivity
        livekit_url = os.getenv('LIVEKIT_URL')
        if livekit_url:
            # TODO: Implement actual LiveKit connectivity check
            details.append('LiveKit configuration present')
        else:
            warnings.append('LiveKit URL not configured')
        
        # Check Google Cloud APIs
        google_apis = [
            ('GOOGLE_VISION_API_KEY', 'Google Vision API'),
            ('GOOGLE_TRANSLATE_API_KEY', 'Google Translate API'),
            ('GOOGLE_SPEECH_TO_TEXT_API_KEY', 'Google Speech-to-Text API'),
            ('GOOGLE_TEXT_TO_SPEECH_API_KEY', 'Google Text-to-Speech API')
        ]
        
        for env_var, service_name in google_apis:
            if os.getenv(env_var):
                details.append(f'{service_name} configured')
            else:
                warnings.append(f'{service_name} not configured')
        
        # Check Wine API
        if os.getenv('WINE_API_KEY'):
            details.append('Wine API configured')
        else:
            warnings.append('Wine API not configured')
        
        return {
            'success': True,  # External services are optional
            'details': details,
            'warnings': warnings
        }
    
    @classmethod
    def create_default_data(cls) -> bool:
        """Create default application data."""
        try:
            from backend.models.database import SessionLocal
            from backend.models.wine import VoiceProfile, Translation
            
            db = SessionLocal()
            
            # Create default voice profiles
            default_voices = [
                {
                    'id': 'ja-JP-Wavenet-A',
                    'language': 'ja',
                    'voice_name': 'ja-JP-Wavenet-A',
                    'gender': 'female',
                    'description': '若い女性の声',
                    'description_translations': {
                        'ja': '若い女性の声',
                        'en': 'Young female voice',
                        'ko': '젊은 여성 목소리'
                    }
                },
                {
                    'id': 'en-US-Wavenet-D',
                    'language': 'en',
                    'voice_name': 'en-US-Wavenet-D',
                    'gender': 'male',
                    'description': 'Deep male voice',
                    'description_translations': {
                        'ja': '低い男性の声',
                        'en': 'Deep male voice',
                        'ko': '낮은 남성 목소리'
                    }
                }
            ]
            
            for voice_data in default_voices:
                existing = db.query(VoiceProfile).filter_by(id=voice_data['id']).first()
                if not existing:
                    voice = VoiceProfile(**voice_data)
                    db.add(voice)
            
            # Create default translations
            default_translations = [
                {'key': 'nav.home', 'language': 'ja', 'value': 'ホーム'},
                {'key': 'nav.home', 'language': 'en', 'value': 'Home'},
                {'key': 'nav.camera', 'language': 'ja', 'value': 'カメラ'},
                {'key': 'nav.camera', 'language': 'en', 'value': 'Camera'},
                {'key': 'nav.rooms', 'language': 'ja', 'value': 'ルーム'},
                {'key': 'nav.rooms', 'language': 'en', 'value': 'Rooms'},
            ]
            
            for trans_data in default_translations:
                existing = db.query(Translation).filter_by(
                    key=trans_data['key'],
                    language=trans_data['language']
                ).first()
                if not existing:
                    translation = Translation(**trans_data)
                    db.add(translation)
            
            db.commit()
            db.close()
            
            return True
        
        except Exception as e:
            print(f"Failed to create default data: {str(e)}")
            return False

def run_startup_sequence(verbose: bool = True) -> bool:
    """Run the complete startup sequence."""
    startup_manager = StartupManager()
    
    # Run startup checks
    checks_passed = startup_manager.run_startup_checks(verbose)
    
    if not checks_passed:
        if verbose:
            print("❌ Startup checks failed. Application cannot start safely.")
        return False
    
    # Create default data
    if verbose:
        print("Creating default application data...")
    
    data_created = startup_manager.create_default_data()
    
    if not data_created:
        if verbose:
            print("⚠️  Warning: Failed to create some default data")
    elif verbose:
        print("✅ Default data created successfully")
    
    if verbose:
        print("\n🚀 Application startup complete!")
    
    return True

if __name__ == "__main__":
    # Run startup sequence when script is executed directly
    success = run_startup_sequence(verbose=True)
    sys.exit(0 if success else 1)