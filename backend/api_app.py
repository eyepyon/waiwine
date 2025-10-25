"""
FastAPI application for OAuth authentication and API endpoints.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os

from .services.auth_endpoints import auth_router
from .services.user_endpoints import user_router
from .models.database import init_database
from .config.env_validator import ConfigValidator

# Create FastAPI app
app = FastAPI(
    title="Wine Chat API",
    description="OAuth authentication and API endpoints for Wine Chat application",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Vue.js dev server
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8080",  # Alternative Vue.js port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(user_router)

# Import and include wine recognition router
from .services.wine_recognition_endpoints import router as wine_router
app.include_router(wine_router)

# Import and include LiveKit room management router
from .services.livekit_endpoints import router as livekit_router
app.include_router(livekit_router)

# Import and include translation WebSocket endpoint
from .services.translation_endpoints import translation_websocket_endpoint
from fastapi import WebSocket, Depends
from .models.database import get_db

# Import and include translation API router
from .services.translation_api_endpoints import router as translation_router
app.include_router(translation_router)

# Import and include multilingual content router
from .services.multilingual_endpoints import multilingual_router
app.include_router(multilingual_router)

@app.websocket("/ws/translation/{user_id}/{room_id}")
async def websocket_translation_endpoint(
    websocket: WebSocket,
    user_id: str,
    room_id: str,
    token: str = None,
    db = Depends(get_db)
):
    """WebSocket endpoint for real-time translation."""
    await translation_websocket_endpoint(websocket, user_id, room_id, token, db)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    # Validate configuration
    if not ConfigValidator.validate_all():
        raise RuntimeError("Configuration validation failed")
    
    # Initialize database
    init_database()
    
    print("🚀 FastAPI server started successfully")
    print("📋 Available OAuth providers:")
    
    from .config.oauth_config import OAuthConfig
    enabled_providers = OAuthConfig.get_enabled_providers()
    for provider_name in enabled_providers.keys():
        print(f"   ✅ {provider_name}")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Wine Chat API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

if __name__ == "__main__":
    # Run the server
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "127.0.0.1")
    
    uvicorn.run(
        "backend.api_app:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )