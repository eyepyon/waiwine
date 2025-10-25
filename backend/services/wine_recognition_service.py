"""
Wine Recognition Service using Google Vision API.
Handles image processing, text extraction, and wine database matching.
"""
import io
import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from google.cloud import vision
from google.oauth2 import service_account
import requests
from sqlalchemy.orm import Session

from backend.config.settings import get_config
from backend.models.wine import Wine
from backend.utils.database import get_db

logger = logging.getLogger(__name__)

@dataclass
class WineRecognitionResult:
    """Result of wine recognition process."""
    wine_id: Optional[str] = None
    wine_name: Optional[str] = None
    confidence_score: float = 0.0
    extracted_text: str = ""
    matched_wines: List[Dict] = None
    error_message: Optional[str] = None
    success: bool = False

class WineRecognitionService:
    """Service for recognizing wine labels from images."""
    
    def __init__(self):
        self.config = get_config()
        self.vision_client = self._initialize_vision_client()
        
    def _initialize_vision_client(self) -> Optional[vision.ImageAnnotatorClient]:
        """Initialize Google Vision API client."""
        try:
            if self.config.GOOGLE_APPLICATION_CREDENTIALS:
                # Use service account credentials
                credentials = service_account.Credentials.from_service_account_file(
                    self.config.GOOGLE_APPLICATION_CREDENTIALS
                )
                return vision.ImageAnnotatorClient(credentials=credentials)
            elif self.config.GOOGLE_VISION_API_KEY:
                # Use API key (less secure, for development)
                logger.warning("Using API key for Vision API. Consider using service account in production.")
                return vision.ImageAnnotatorClient()
            else:
                logger.error("No Google Vision API credentials configured")
                return None
        except Exception as e:
            logger.error(f"Failed to initialize Vision API client: {e}")
            return None
    
    def recognize_wine_from_image(self, image_data: bytes) -> WineRecognitionResult:
        """
        Recognize wine from image data.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            WineRecognitionResult with recognition details
        """
        if not self.vision_client:
            return WineRecognitionResult(
                error_message="Vision API client not initialized",
                success=False
            )
        
        try:
            # Extract text from image
            extracted_text = self._extract_text_from_image(image_data)
            
            if not extracted_text:
                return WineRecognitionResult(
                    extracted_text="",
                    error_message="No text found in image",
                    success=False
                )
            
            # Search for wines based on extracted text
            matched_wines = self._search_wines_by_text(extracted_text)
            
            if not matched_wines:
                return WineRecognitionResult(
                    extracted_text=extracted_text,
                    matched_wines=[],
                    error_message="No matching wines found",
                    success=False
                )
            
            # Get best match
            best_match = matched_wines[0]
            confidence_score = self._calculate_confidence_score(extracted_text, best_match)
            
            return WineRecognitionResult(
                wine_id=best_match.get('id'),
                wine_name=best_match.get('name'),
                confidence_score=confidence_score,
                extracted_text=extracted_text,
                matched_wines=matched_wines[:5],  # Return top 5 matches
                success=True
            )
            
        except Exception as e:
            logger.error(f"Wine recognition failed: {e}")
            return WineRecognitionResult(
                error_message=f"Recognition failed: {str(e)}",
                success=False
            )
    
    def _extract_text_from_image(self, image_data: bytes) -> str:
        """Extract text from image using Google Vision API."""
        try:
            image = vision.Image(content=image_data)
            
            # Perform text detection
            response = self.vision_client.text_detection(image=image)
            texts = response.text_annotations
            
            if response.error.message:
                raise Exception(f'Vision API error: {response.error.message}')
            
            if texts:
                # Return the first (most comprehensive) text annotation
                return texts[0].description
            
            return ""
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise
    
    def _search_wines_by_text(self, text: str) -> List[Dict]:
        """
        Search for wines based on extracted text.
        
        Args:
            text: Extracted text from wine label
            
        Returns:
            List of matching wine dictionaries
        """
        # Clean and normalize text
        cleaned_text = self._clean_text(text)
        
        # Extract potential wine information
        wine_keywords = self._extract_wine_keywords(cleaned_text)
        
        # Search in local database first
        db_matches = self._search_local_database(wine_keywords)
        
        if db_matches:
            return db_matches
        
        # If no local matches, try external wine API
        api_matches = self._search_external_wine_api(wine_keywords)
        
        return api_matches
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common OCR artifacts
        cleaned = re.sub(r'[^\w\s\-\.\,\&\']', ' ', cleaned)
        
        return cleaned
    
    def _extract_wine_keywords(self, text: str) -> Dict[str, List[str]]:
        """Extract potential wine-related keywords from text."""
        keywords = {
            'names': [],
            'producers': [],
            'regions': [],
            'vintages': [],
            'types': []
        }
        
        # Extract years (potential vintages)
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        keywords['vintages'] = years
        
        # Extract common wine regions (basic list)
        regions = [
            'Bordeaux', 'Burgundy', 'Champagne', 'Tuscany', 'Napa', 'Sonoma',
            'Rioja', 'Barolo', 'Chianti', 'Mosel', 'Loire', 'Rhone'
        ]
        
        text_upper = text.upper()
        for region in regions:
            if region.upper() in text_upper:
                keywords['regions'].append(region)
        
        # Extract wine types
        wine_types = ['Cabernet', 'Merlot', 'Chardonnay', 'Pinot', 'Sauvignon']
        for wine_type in wine_types:
            if wine_type.upper() in text_upper:
                keywords['types'].append(wine_type)
        
        # Extract potential producer/wine names (words in title case)
        words = text.split()
        potential_names = []
        
        for i, word in enumerate(words):
            if word.istitle() and len(word) > 2:
                # Look for sequences of title case words
                sequence = [word]
                j = i + 1
                while j < len(words) and words[j].istitle() and len(words[j]) > 1:
                    sequence.append(words[j])
                    j += 1
                
                if len(sequence) >= 2:  # At least 2 words for a wine name
                    potential_names.append(' '.join(sequence))
        
        keywords['names'] = potential_names[:5]  # Top 5 potential names
        
        return keywords
    
    def _search_local_database(self, keywords: Dict[str, List[str]]) -> List[Dict]:
        """Search for wines in local database."""
        try:
            db = next(get_db())
            matches = []
            
            # Search by name
            for name in keywords['names']:
                wines = db.query(Wine).filter(
                    Wine.name.ilike(f'%{name}%')
                ).limit(10).all()
                
                for wine in wines:
                    matches.append({
                        'id': wine.id,
                        'name': wine.name,
                        'producer': wine.producer,
                        'vintage': wine.vintage,
                        'region': wine.region,
                        'wine_type': wine.wine_type,
                        'source': 'local'
                    })
            
            # Search by producer
            for producer in keywords.get('producers', []):
                wines = db.query(Wine).filter(
                    Wine.producer.ilike(f'%{producer}%')
                ).limit(5).all()
                
                for wine in wines:
                    wine_dict = {
                        'id': wine.id,
                        'name': wine.name,
                        'producer': wine.producer,
                        'vintage': wine.vintage,
                        'region': wine.region,
                        'wine_type': wine.wine_type,
                        'source': 'local'
                    }
                    if wine_dict not in matches:
                        matches.append(wine_dict)
            
            return matches[:10]  # Return top 10 matches
            
        except Exception as e:
            logger.error(f"Local database search failed: {e}")
            return []
    
    def _search_external_wine_api(self, keywords: Dict[str, List[str]]) -> List[Dict]:
        """Search external wine API for matches."""
        if not self.config.WINE_API_KEY:
            logger.warning("No Wine API key configured")
            return []
        
        try:
            matches = []
            
            # Search by wine names
            for name in keywords['names'][:3]:  # Limit API calls
                api_results = self._call_wine_api(name)
                matches.extend(api_results)
            
            return matches[:10]  # Return top 10 matches
            
        except Exception as e:
            logger.error(f"External wine API search failed: {e}")
            return []
    
    def _call_wine_api(self, query: str) -> List[Dict]:
        """Call external wine API."""
        try:
            # This is a placeholder for wine API integration
            # Replace with actual wine API (Wine.com, Vivino, etc.)
            
            headers = {
                'Authorization': f'Bearer {self.config.WINE_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'search': query,
                'limit': 5
            }
            
            # Placeholder URL - replace with actual wine API endpoint
            response = requests.get(
                f"{self.config.WINE_API_BASE_URL}/search",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Transform API response to our format
                wines = []
                for item in data.get('wines', []):
                    wines.append({
                        'id': f"api_{item.get('id')}",
                        'name': item.get('name'),
                        'producer': item.get('winery'),
                        'vintage': item.get('vintage'),
                        'region': item.get('region'),
                        'wine_type': item.get('type'),
                        'source': 'api'
                    })
                
                return wines
            
            return []
            
        except Exception as e:
            logger.error(f"Wine API call failed: {e}")
            return []
    
    def _calculate_confidence_score(self, extracted_text: str, wine_match: Dict) -> float:
        """Calculate confidence score for a wine match."""
        score = 0.0
        text_upper = extracted_text.upper()
        
        # Check name match
        if wine_match.get('name'):
            name_words = wine_match['name'].upper().split()
            name_matches = sum(1 for word in name_words if word in text_upper)
            if name_words:
                score += (name_matches / len(name_words)) * 0.4
        
        # Check producer match
        if wine_match.get('producer'):
            producer_words = wine_match['producer'].upper().split()
            producer_matches = sum(1 for word in producer_words if word in text_upper)
            if producer_words:
                score += (producer_matches / len(producer_words)) * 0.3
        
        # Check vintage match
        if wine_match.get('vintage'):
            vintage_str = str(wine_match['vintage'])
            if vintage_str in extracted_text:
                score += 0.2
        
        # Check region match
        if wine_match.get('region'):
            if wine_match['region'].upper() in text_upper:
                score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def get_wine_info(self, wine_id: str) -> Optional[Dict]:
        """Get detailed wine information by ID."""
        try:
            if wine_id.startswith('api_'):
                # External API wine
                return self._get_external_wine_info(wine_id)
            else:
                # Local database wine
                return self._get_local_wine_info(wine_id)
                
        except Exception as e:
            logger.error(f"Failed to get wine info for {wine_id}: {e}")
            return None
    
    def _get_local_wine_info(self, wine_id: str) -> Optional[Dict]:
        """Get wine info from local database."""
        try:
            db = next(get_db())
            wine = db.query(Wine).filter(Wine.id == wine_id).first()
            
            if wine:
                return {
                    'id': wine.id,
                    'name': wine.name,
                    'producer': wine.producer,
                    'vintage': wine.vintage,
                    'region': wine.region,
                    'wine_type': wine.wine_type,
                    'alcohol_content': wine.alcohol_content,
                    'image_url': wine.image_url,
                    'tasting_notes': wine.tasting_notes_translations or {},
                    'recognition_count': wine.recognition_count
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get local wine info: {e}")
            return None
    
    def _get_external_wine_info(self, wine_id: str) -> Optional[Dict]:
        """Get wine info from external API."""
        # Placeholder for external API integration
        return None
    
    def update_recognition_feedback(self, wine_id: str, user_feedback: bool) -> None:
        """Update recognition feedback for machine learning improvement."""
        try:
            if not wine_id.startswith('api_'):
                db = next(get_db())
                wine = db.query(Wine).filter(Wine.id == wine_id).first()
                
                if wine:
                    # Increment recognition count for successful recognitions
                    if user_feedback:
                        wine.recognition_count = (wine.recognition_count or 0) + 1
                        db.commit()
                        
        except Exception as e:
            logger.error(f"Failed to update recognition feedback: {e}")

# Service instance
wine_recognition_service = WineRecognitionService()