"""
Wine Recognition API endpoints.
Handles image upload, wine recognition, and wine information retrieval.
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from services.wine_recognition_service import wine_recognition_service
from services.wine_management_service import wine_management_service
from services.session_manager import get_current_user
from models.user import User
from utils.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/wine", tags=["wine"])

@router.post("/recognize")
async def recognize_wine(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Recognize wine from uploaded image.
    
    Args:
        file: Uploaded image file
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Wine recognition result
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )
        
        # Validate file size (max 10MB)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=400,
                detail="File size too large (max 10MB)"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty file"
            )
        
        # Perform wine recognition
        result = wine_recognition_service.recognize_wine_from_image(content)
        
        if not result.success:
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "error": result.error_message,
                    "extracted_text": result.extracted_text,
                    "matched_wines": result.matched_wines or []
                }
            )
        
        # Log successful recognition
        logger.info(f"Wine recognized for user {current_user.id}: {result.wine_name}")
        
        return {
            "success": True,
            "wine_id": result.wine_id,
            "wine_name": result.wine_name,
            "confidence_score": result.confidence_score,
            "extracted_text": result.extracted_text,
            "matched_wines": result.matched_wines
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Wine recognition failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Wine recognition failed"
        )

@router.get("/info/{wine_id}")
async def get_wine_info(
    wine_id: str,
    language: str = "en",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed wine information by ID with multilingual support.
    
    Args:
        wine_id: Wine identifier
        language: Language code for localized content
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Wine information with localized content
    """
    try:
        # Import multilingual service
        from services.multilingual_service import MultilingualService
        multilingual_service = MultilingualService()
        
        # Get localized wine info
        wine_info = multilingual_service.get_localized_wine_info(wine_id, language)
        
        if not wine_info:
            raise HTTPException(
                status_code=404,
                detail="Wine not found"
            )
        
        return {
            "success": True,
            "wine": wine_info,
            "language": language
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get wine info: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve wine information"
        )

@router.post("/feedback/{wine_id}")
async def submit_recognition_feedback(
    wine_id: str,
    feedback_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Submit feedback on wine recognition accuracy.
    
    Args:
        wine_id: Wine identifier
        feedback_data: Feedback data including 'correct' boolean
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Success response
    """
    try:
        is_correct = feedback_data.get('correct', False)
        
        # Update recognition feedback
        wine_recognition_service.update_recognition_feedback(wine_id, is_correct)
        
        logger.info(f"Recognition feedback submitted by user {current_user.id}: {wine_id} - {is_correct}")
        
        return {
            "success": True,
            "message": "Feedback submitted successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to submit feedback"
        )

@router.get("/search")
async def search_wines(
    query: str,
    limit: int = 10,
    vintage: int = None,
    region: str = None,
    wine_type: str = None,
    producer: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Search wines by text query with filters.
    
    Args:
        query: Search query
        limit: Maximum number of results
        vintage: Filter by vintage year
        region: Filter by region
        wine_type: Filter by wine type
        producer: Filter by producer
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Search results
    """
    try:
        if not query or len(query.strip()) < 2:
            raise HTTPException(
                status_code=400,
                detail="Query must be at least 2 characters"
            )
        
        # Build filters
        filters = {}
        if vintage:
            filters['vintage'] = vintage
        if region:
            filters['region'] = region
        if wine_type:
            filters['wine_type'] = wine_type
        if producer:
            filters['producer'] = producer
        
        # Use wine management service for advanced search
        language = current_user.main_language or 'en'
        wines = wine_management_service.search_wines(
            query=query,
            language=language,
            limit=limit,
            filters=filters
        )
        
        return {
            "success": True,
            "wines": wines,
            "total": len(wines)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Wine search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Wine search failed"
        )

@router.get("/popular")
async def get_popular_wines(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get popular wines based on recognition count.
    
    Args:
        limit: Maximum number of results
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Popular wines list
    """
    try:
        language = current_user.main_language or 'en'
        wines = wine_management_service.get_popular_wines(language=language, limit=limit)
        
        return {
            "success": True,
            "wines": wines
        }
        
    except Exception as e:
        logger.error(f"Failed to get popular wines: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve popular wines"
        )

@router.get("/suggestions")
async def get_wine_suggestions(
    q: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get wine suggestions for autocomplete/manual selection.
    
    Args:
        q: Partial wine name query
        limit: Maximum number of suggestions
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Wine suggestions list
    """
    try:
        if not q or len(q.strip()) < 2:
            return {
                "success": True,
                "suggestions": []
            }
        
        language = current_user.main_language or 'en'
        suggestions = wine_management_service.get_wine_suggestions(
            partial_name=q,
            language=language,
            limit=limit
        )
        
        return {
            "success": True,
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"Failed to get wine suggestions: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve wine suggestions"
        )

@router.get("/types")
async def get_wine_types(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get available wine types with localization.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Wine types list
    """
    try:
        language = current_user.main_language or 'en'
        wine_types = wine_management_service.get_wine_types(language=language)
        
        return {
            "success": True,
            "wine_types": wine_types
        }
        
    except Exception as e:
        logger.error(f"Failed to get wine types: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve wine types"
        )

@router.get("/regions")
async def get_wine_regions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get popular wine regions.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Wine regions list
    """
    try:
        language = current_user.main_language or 'en'
        regions = wine_management_service.get_wine_regions(language=language)
        
        return {
            "success": True,
            "regions": regions
        }
        
    except Exception as e:
        logger.error(f"Failed to get wine regions: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve wine regions"
        )