"""
Debug script to check environment variables.
"""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("=" * 50)
print("Environment Variables Check")
print("=" * 50)

# Check Google OAuth
google_client_id = os.getenv('GOOGLE_CLIENT_ID', '')
google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '')

print(f"\nGoogle OAuth Configuration:")
print(f"  GOOGLE_CLIENT_ID set: {bool(google_client_id)}")
print(f"  GOOGLE_CLIENT_ID length: {len(google_client_id)}")
if google_client_id:
    print(f"  GOOGLE_CLIENT_ID preview: {google_client_id[:20]}...")
else:
    print(f"  GOOGLE_CLIENT_ID value: '{google_client_id}'")

print(f"\n  GOOGLE_CLIENT_SECRET set: {bool(google_client_secret)}")
print(f"  GOOGLE_CLIENT_SECRET length: {len(google_client_secret)}")
if google_client_secret:
    print(f"  GOOGLE_CLIENT_SECRET preview: {google_client_secret[:10]}...")
else:
    print(f"  GOOGLE_CLIENT_SECRET value: '{google_client_secret}'")

# Check LiveKit
livekit_key = os.getenv('LIVEKIT_API_KEY', '')
livekit_secret = os.getenv('LIVEKIT_API_SECRET', '')
livekit_url = os.getenv('LIVEKIT_URL', '')

print(f"\nLiveKit Configuration:")
print(f"  LIVEKIT_API_KEY set: {bool(livekit_key)}")
print(f"  LIVEKIT_API_SECRET set: {bool(livekit_secret)}")
print(f"  LIVEKIT_URL: {livekit_url}")

# Check Backend URL
backend_url = os.getenv('BACKEND_URL', 'http://localhost:8000')
print(f"\nBackend Configuration:")
print(f"  BACKEND_URL: {backend_url}")

# Try to load config
print(f"\nTrying to load Config class...")
try:
    from backend.config.settings import Config
    print(f"  Config.GOOGLE_CLIENT_ID: {bool(Config.GOOGLE_CLIENT_ID)}")
    print(f"  Config.GOOGLE_CLIENT_SECRET: {bool(Config.GOOGLE_CLIENT_SECRET)}")
    
    # Try to get OAuth config
    from backend.config.oauth_config import OAuthConfig
    google_config = OAuthConfig.get_provider_config('google')
    
    if google_config:
        print(f"\n✅ Google OAuth config loaded successfully!")
        print(f"  Display name: {google_config.get('display_name')}")
        print(f"  Enabled: {google_config.get('enabled')}")
        print(f"  Redirect URI: {google_config.get('redirect_uri')}")
    else:
        print(f"\n❌ Google OAuth config is None")
        print(f"  This means GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET is empty")
        
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "=" * 50)
