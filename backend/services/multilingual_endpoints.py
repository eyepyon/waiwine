"""
FastAPI endpoints for multilingual content management.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from .multilingual_service import MultilingualService


# Request/Response models
class LocalizedWineResponse(BaseModel):
    id: str
    name: str
    original_name: str
    vintage: Optional[int] = None
    region: str
    original_region: str
    producer: Optional[str] = None
    wine_type: Optional[str] = None
    localized_type: str
    alcohol_content: Optional[float] = None
    image_url: Optional[str] = None
    tasting_notes: str
    recognition_count: int
    created_at: str
    updated_at: str

class TranslationRequest(BaseModel):
    key: str
    language: str
    value: str

class WineTranslationRequest(BaseModel):
    translations: Dict[str, Dict[str, str]]

class VoiceProfileResponse(BaseModel):
    id: str
    voice_name: str
    gender: Optional[str] = None
    description: str
    sample_audio_url: Optional[str] = None

class LanguageResponse(BaseModel):
    code: str
    name: str
    english_name: str


# Create router
multilingual_router = APIRouter(prefix="/api/multilingual", tags=["multilingual"])

# Initialize service
multilingual_service = MultilingualService()


@multilingual_router.get("/wine/{wine_id}", response_model=LocalizedWineResponse)
async def get_localized_wine(
    wine_id: str,
    language: str = Query(default="en", description="Language code")
) -> LocalizedWineResponse:
    """Get wine information with localized content."""
    try:
        wine_info = multilingual_service.get_localized_wine_info(wine_id, language)
        
        if not wine_info:
            raise HTTPException(status_code=404, detail="Wine not found")
        
        return LocalizedWineResponse(**wine_info)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get localized wine information")


@multilingual_router.get("/wines/search")
async def search_wines_localized(
    q: str = Query(..., description="Search query"),
    language: str = Query(default="en", description="Language code"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of results")
) -> Dict[str, Any]:
    """Search wines with localized content."""
    try:
        results = multilingual_service.search_wines_localized(q, language, limit)
        
        return {
            "success": True,
            "query": q,
            "language": language,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to search wines")


@multilingual_router.get("/translation/{key}")
async def get_translation(
    key: str,
    language: str = Query(default="en", description="Language code")
) -> Dict[str, Any]:
    """Get translation for a specific key."""
    try:
        translation = multilingual_service.get_translation(key, language)
        
        if translation is None:
            raise HTTPException(status_code=404, detail="Translation not found")
        
        return {
            "key": key,
            "language": language,
            "value": translation
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get translation")


@multilingual_router.post("/translation")
async def set_translation(request: TranslationRequest) -> Dict[str, Any]:
    """Set or update a translation."""
    try:
        success = multilingual_service.set_translation(
            request.key,
            request.language,
            request.value
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to set translation")
        
        return {
            "success": True,
            "message": "Translation updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to set translation")


@multilingual_router.get("/voices/{language}", response_model=List[VoiceProfileResponse])
async def get_available_voices(language: str) -> List[VoiceProfileResponse]:
    """Get available voice profiles for a language."""
    try:
        voices = multilingual_service.get_available_voices(language)
        return [VoiceProfileResponse(**voice) for voice in voices]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get voice profiles")


@multilingual_router.put("/wine/{wine_id}/translations")
async def update_wine_translations(
    wine_id: str,
    request: WineTranslationRequest
) -> Dict[str, Any]:
    """Update wine translations."""
    try:
        success = multilingual_service.update_wine_translations(
            wine_id,
            request.translations
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update wine translations")
        
        return {
            "success": True,
            "message": "Wine translations updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update wine translations")


@multilingual_router.get("/languages", response_model=List[LanguageResponse])
async def get_supported_languages() -> List[LanguageResponse]:
    """Get list of supported languages."""
    try:
        languages = multilingual_service.get_supported_languages()
        return [LanguageResponse(**lang) for lang in languages]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get supported languages")


@multilingual_router.get("/wine-types")
async def get_localized_wine_types(
    language: str = Query(default="en", description="Language code")
) -> Dict[str, Any]:
    """Get localized wine type names."""
    try:
        wine_types = ['red', 'white', 'rose', 'sparkling', 'dessert', 'fortified']
        localized_types = {}
        
        for wine_type in wine_types:
            localized_types[wine_type] = multilingual_service._get_localized_wine_type(wine_type, language)
        
        return {
            "language": language,
            "wine_types": localized_types
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get localized wine types")


@multilingual_router.get("/regions")
async def get_popular_wine_regions(
    language: str = Query(default="en", description="Language code"),
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of regions")
) -> Dict[str, Any]:
    """Get popular wine regions with localized names."""
    try:
        # This would typically query the database for popular regions
        # For now, return a hardcoded list of major wine regions
        regions = [
            {"code": "bordeaux", "name": "Bordeaux", "country": "France"},
            {"code": "tuscany", "name": "Tuscany", "country": "Italy"},
            {"code": "napa", "name": "Napa Valley", "country": "USA"},
            {"code": "rioja", "name": "Rioja", "country": "Spain"},
            {"code": "champagne", "name": "Champagne", "country": "France"},
            {"code": "barossa", "name": "Barossa Valley", "country": "Australia"},
            {"code": "douro", "name": "Douro", "country": "Portugal"},
            {"code": "mosel", "name": "Mosel", "country": "Germany"}
        ]
        
        return {
            "language": language,
            "regions": regions[:limit]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get wine regions")