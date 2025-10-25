"""
Wine Information Management Service.
Handles wine database operations, caching, and manual wine selection.
"""
import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from models.wine import Wine, Translation
from utils.database import get_db
from config.settings import get_config

logger = logging.getLogger(__name__)

class WineManagementService:
    """Service for managing wine information and database operations."""
    
    def __init__(self):
        self.config = get_config()
        self._cache = {}  # Simple in-memory cache
        self._cache_ttl = timedelta(hours=1)  # Cache for 1 hour
    
    def get_wine_by_id(self, wine_id: str, language: str = 'en') -> Optional[Dict[str, Any]]:
        """
        Get wine information by ID with localization.
        
        Args:
            wine_id: Wine identifier
            language: Language code for localization
            
        Returns:
            Wine information dictionary or None
        """
        try:
            # Check cache first
            cache_key = f"wine_{wine_id}_{language}"
            if self._is_cached(cache_key):
                return self._cache[cache_key]['data']
            
            db = next(get_db())
            wine = db.query(Wine).filter(Wine.id == wine_id).first()
            
            if not wine:
                return None
            
            wine_data = self._format_wine_data(wine, language)
            
            # Cache the result
            self._cache_wine_data(cache_key, wine_data)
            
            return wine_data
            
        except Exception as e:
            logger.error(f"Failed to get wine by ID {wine_id}: {e}")
            return None
    
    def search_wines(
        self, 
        query: str, 
        language: str = 'en',
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search wines with filters and localization.
        
        Args:
            query: Search query
            language: Language code for localization
            limit: Maximum number of results
            filters: Additional filters (vintage, region, type, etc.)
            
        Returns:
            List of wine dictionaries
        """
        try:
            db = next(get_db())
            
            # Build base query
            wine_query = db.query(Wine)
            
            # Apply text search
            if query and query.strip():
                search_term = f"%{query.strip()}%"
                wine_query = wine_query.filter(
                    or_(
                        Wine.name.ilike(search_term),
                        Wine.producer.ilike(search_term),
                        Wine.region.ilike(search_term)
                    )
                )
            
            # Apply filters
            if filters:
                if filters.get('vintage'):
                    wine_query = wine_query.filter(Wine.vintage == filters['vintage'])
                
                if filters.get('region'):
                    wine_query = wine_query.filter(Wine.region.ilike(f"%{filters['region']}%"))
                
                if filters.get('wine_type'):
                    wine_query = wine_query.filter(Wine.wine_type == filters['wine_type'])
                
                if filters.get('producer'):
                    wine_query = wine_query.filter(Wine.producer.ilike(f"%{filters['producer']}%"))
                
                if filters.get('min_alcohol'):
                    wine_query = wine_query.filter(Wine.alcohol_content >= filters['min_alcohol'])
                
                if filters.get('max_alcohol'):
                    wine_query = wine_query.filter(Wine.alcohol_content <= filters['max_alcohol'])
            
            # Order by recognition count (popularity) and name
            wine_query = wine_query.order_by(
                Wine.recognition_count.desc().nullslast(),
                Wine.name
            )
            
            # Apply limit
            wines = wine_query.limit(limit).all()
            
            # Format results
            results = []
            for wine in wines:
                wine_data = self._format_wine_data(wine, language)
                results.append(wine_data)
            
            return results
            
        except Exception as e:
            logger.error(f"Wine search failed: {e}")
            return []
    
    def get_popular_wines(self, language: str = 'en', limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get popular wines based on recognition count.
        
        Args:
            language: Language code for localization
            limit: Maximum number of results
            
        Returns:
            List of popular wine dictionaries
        """
        try:
            # Check cache first
            cache_key = f"popular_wines_{language}_{limit}"
            if self._is_cached(cache_key):
                return self._cache[cache_key]['data']
            
            db = next(get_db())
            
            wines = db.query(Wine).filter(
                Wine.recognition_count > 0
            ).order_by(
                Wine.recognition_count.desc()
            ).limit(limit).all()
            
            results = []
            for wine in wines:
                wine_data = self._format_wine_data(wine, language)
                results.append(wine_data)
            
            # Cache the results
            self._cache_wine_data(cache_key, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get popular wines: {e}")
            return []
    
    def get_wine_suggestions(self, partial_name: str, language: str = 'en', limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get wine suggestions for autocomplete/manual selection.
        
        Args:
            partial_name: Partial wine name
            language: Language code for localization
            limit: Maximum number of suggestions
            
        Returns:
            List of wine suggestions
        """
        try:
            if not partial_name or len(partial_name.strip()) < 2:
                return []
            
            db = next(get_db())
            search_term = f"%{partial_name.strip()}%"
            
            wines = db.query(Wine).filter(
                or_(
                    Wine.name.ilike(search_term),
                    Wine.producer.ilike(search_term)
                )
            ).order_by(
                Wine.recognition_count.desc().nullslast(),
                Wine.name
            ).limit(limit).all()
            
            suggestions = []
            for wine in wines:
                suggestions.append({
                    'id': wine.id,
                    'name': wine.get_localized_name(language),
                    'producer': wine.producer,
                    'vintage': wine.vintage,
                    'display_name': f"{wine.get_localized_name(language)} ({wine.producer})" + 
                                   (f" {wine.vintage}" if wine.vintage else "")
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to get wine suggestions: {e}")
            return []
    
    def create_wine(self, wine_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a new wine entry.
        
        Args:
            wine_data: Wine information dictionary
            
        Returns:
            Wine ID if successful, None otherwise
        """
        try:
            db = next(get_db())
            
            wine_id = str(uuid.uuid4())
            
            wine = Wine(
                id=wine_id,
                name=wine_data['name'],
                producer=wine_data.get('producer'),
                vintage=wine_data.get('vintage'),
                region=wine_data.get('region'),
                wine_type=wine_data.get('wine_type'),
                alcohol_content=wine_data.get('alcohol_content'),
                image_url=wine_data.get('image_url'),
                name_translations=wine_data.get('name_translations', {}),
                tasting_notes_translations=wine_data.get('tasting_notes_translations', {}),
                region_translations=wine_data.get('region_translations', {}),
                recognition_keywords=wine_data.get('recognition_keywords', [])
            )
            
            db.add(wine)
            db.commit()
            
            # Clear relevant caches
            self._clear_cache_pattern("popular_wines_")
            
            logger.info(f"Created new wine: {wine_id}")
            return wine_id
            
        except Exception as e:
            logger.error(f"Failed to create wine: {e}")
            return None
    
    def update_wine(self, wine_id: str, wine_data: Dict[str, Any]) -> bool:
        """
        Update existing wine information.
        
        Args:
            wine_id: Wine identifier
            wine_data: Updated wine information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db = next(get_db())
            wine = db.query(Wine).filter(Wine.id == wine_id).first()
            
            if not wine:
                return False
            
            # Update fields
            for field, value in wine_data.items():
                if hasattr(wine, field) and value is not None:
                    setattr(wine, field, value)
            
            wine.updated_at = datetime.utcnow()
            db.commit()
            
            # Clear caches
            self._clear_cache_pattern(f"wine_{wine_id}_")
            self._clear_cache_pattern("popular_wines_")
            
            logger.info(f"Updated wine: {wine_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update wine {wine_id}: {e}")
            return False
    
    def increment_recognition_count(self, wine_id: str) -> bool:
        """
        Increment recognition count for a wine.
        
        Args:
            wine_id: Wine identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db = next(get_db())
            wine = db.query(Wine).filter(Wine.id == wine_id).first()
            
            if wine:
                wine.recognition_count = (wine.recognition_count or 0) + 1
                wine.updated_at = datetime.utcnow()
                db.commit()
                
                # Clear popular wines cache
                self._clear_cache_pattern("popular_wines_")
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to increment recognition count for {wine_id}: {e}")
            return False
    
    def get_wine_types(self, language: str = 'en') -> List[Dict[str, str]]:
        """
        Get available wine types with localization.
        
        Args:
            language: Language code for localization
            
        Returns:
            List of wine type dictionaries
        """
        wine_types = [
            {'value': 'red', 'label_key': 'wine.type.red'},
            {'value': 'white', 'label_key': 'wine.type.white'},
            {'value': 'rosé', 'label_key': 'wine.type.rose'},
            {'value': 'sparkling', 'label_key': 'wine.type.sparkling'},
            {'value': 'dessert', 'label_key': 'wine.type.dessert'},
            {'value': 'fortified', 'label_key': 'wine.type.fortified'}
        ]
        
        # Add localized labels
        for wine_type in wine_types:
            wine_type['label'] = self._get_translation(wine_type['label_key'], language)
        
        return wine_types
    
    def get_wine_regions(self, language: str = 'en') -> List[Dict[str, str]]:
        """
        Get popular wine regions from database.
        
        Args:
            language: Language code for localization
            
        Returns:
            List of region dictionaries
        """
        try:
            db = next(get_db())
            
            # Get regions with wine counts
            regions = db.query(
                Wine.region,
                func.count(Wine.id).label('wine_count')
            ).filter(
                Wine.region.isnot(None)
            ).group_by(
                Wine.region
            ).order_by(
                func.count(Wine.id).desc()
            ).limit(50).all()
            
            region_list = []
            for region, count in regions:
                region_list.append({
                    'value': region,
                    'label': region,
                    'wine_count': count
                })
            
            return region_list
            
        except Exception as e:
            logger.error(f"Failed to get wine regions: {e}")
            return []
    
    def _format_wine_data(self, wine: Wine, language: str) -> Dict[str, Any]:
        """Format wine data for API response."""
        return {
            'id': wine.id,
            'name': wine.get_localized_name(language),
            'original_name': wine.name,
            'producer': wine.producer,
            'vintage': wine.vintage,
            'region': wine.region,
            'wine_type': wine.wine_type,
            'wine_type_label': self._get_translation(f'wine.type.{wine.wine_type}', language) if wine.wine_type else None,
            'alcohol_content': wine.alcohol_content,
            'image_url': wine.image_url,
            'tasting_notes': wine.get_localized_tasting_notes(language),
            'recognition_count': wine.recognition_count or 0,
            'created_at': wine.created_at.isoformat() if wine.created_at else None,
            'updated_at': wine.updated_at.isoformat() if wine.updated_at else None
        }
    
    def _get_translation(self, key: str, language: str) -> str:
        """Get translation for a key and language."""
        try:
            db = next(get_db())
            translation = db.query(Translation).filter(
                and_(Translation.key == key, Translation.language == language)
            ).first()
            
            if translation:
                return translation.value
            
            # Fallback to English
            if language != 'en':
                translation = db.query(Translation).filter(
                    and_(Translation.key == key, Translation.language == 'en')
                ).first()
                
                if translation:
                    return translation.value
            
            # Return key if no translation found
            return key
            
        except Exception as e:
            logger.error(f"Failed to get translation for {key}: {e}")
            return key
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if data is cached and not expired."""
        if cache_key not in self._cache:
            return False
        
        cached_item = self._cache[cache_key]
        return datetime.now() < cached_item['expires_at']
    
    def _cache_wine_data(self, cache_key: str, data: Any) -> None:
        """Cache wine data with expiration."""
        self._cache[cache_key] = {
            'data': data,
            'expires_at': datetime.now() + self._cache_ttl
        }
    
    def _clear_cache_pattern(self, pattern: str) -> None:
        """Clear cache entries matching a pattern."""
        keys_to_remove = [key for key in self._cache.keys() if key.startswith(pattern)]
        for key in keys_to_remove:
            del self._cache[key]

# Service instance
wine_management_service = WineManagementService()