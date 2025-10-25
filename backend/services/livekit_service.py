"""
LiveKit room management service for wine chat rooms.
"""
import time
import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from livekit import api
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.config.settings import get_config
from backend.models.database import get_db
from backend.models.wine import RoomSession, Wine
from backend.models.user import User

class LiveKitRoomService:
    """Service for managing LiveKit rooms and tokens."""
    
    def __init__(self):
        self.config = get_config()
        self.api_key = self.config.LIVEKIT_API_KEY
        self.api_secret = self.config.LIVEKIT_API_SECRET
        self.livekit_url = self.config.LIVEKIT_URL
        
        if not self.api_key or not self.api_secret:
            raise ValueError("LiveKit API key and secret must be configured")
    
    def generate_room_name(self, wine_id: str) -> str:
        """Generate a unique room name for a wine."""
        return f"wine-{wine_id}"
    
    def generate_access_token(self, user_id: str, room_name: str, user_name: str = "", is_guest: bool = False) -> str:
        """Generate LiveKit access token for a user to join a room."""
        try:
            token = api.AccessToken(self.api_key, self.api_secret)
            
            # For guest users, generate a unique ID
            if is_guest:
                user_id = f"guest-{uuid.uuid4().hex[:8]}"
                user_name = user_name or f"Guest {uuid.uuid4().hex[:4]}"
            
            token.with_identity(user_id)
            token.with_name(user_name)
            token.with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True
            ))
            
            # Token expires in 24 hours for registered users, 2 hours for guests
            ttl_hours = 2 if is_guest else 24
            token.with_ttl(timedelta(hours=ttl_hours))
            
            return token.to_jwt()
        except Exception as e:
            raise Exception(f"Failed to generate access token: {str(e)}")
    
    def create_or_get_room(self, wine_id: str, user_id: str) -> Tuple[str, str]:
        """
        Create or get existing room for a wine and return room name and access token.
        
        Returns:
            Tuple of (room_name, access_token)
        """
        db = next(get_db())
        try:
            # Get wine information
            wine = db.query(Wine).filter(Wine.id == wine_id).first()
            if not wine:
                raise ValueError(f"Wine with ID {wine_id} not found")
            
            # Get user information
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User with ID {user_id} not found")
            
            room_name = self.generate_room_name(wine_id)
            
            # Check if room session already exists
            room_session = db.query(RoomSession).filter(
                RoomSession.wine_id == wine_id,
                RoomSession.room_name == room_name
            ).first()
            
            if not room_session:
                # Create new room session
                room_session = RoomSession(
                    id=str(uuid.uuid4()),
                    wine_id=wine_id,
                    room_name=room_name,
                    active_participants=0
                )
                db.add(room_session)
                db.commit()
            
            # Update last activity
            room_session.last_activity = datetime.utcnow()
            db.commit()
            
            # Generate access token
            access_token = self.generate_access_token(
                user_id=user_id,
                room_name=room_name,
                user_name=user.name
            )
            
            return room_name, access_token
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def join_room(self, wine_id: str, user_id: str) -> Dict:
        """
        Join a wine room and return room information.
        
        Returns:
            Dictionary with room information and access token
        """
        try:
            room_name, access_token = self.create_or_get_room(wine_id, user_id)
            
            # Get room participants count
            participants_count = self.get_room_participants_count(room_name)
            
            # Update participant count in database
            self._update_participant_count(wine_id, room_name, participants_count + 1)
            
            return {
                'room_name': room_name,
                'access_token': access_token,
                'livekit_url': self.livekit_url,
                'wine_id': wine_id,
                'participants_count': participants_count + 1
            }
            
        except Exception as e:
            raise Exception(f"Failed to join room: {str(e)}")
    
    def leave_room(self, user_id: str, room_name: str) -> bool:
        """
        Handle user leaving a room.
        
        Returns:
            True if successful
        """
        try:
            # Get current participants count
            participants_count = self.get_room_participants_count(room_name)
            
            # Update participant count in database
            wine_id = room_name.replace('wine-', '')
            self._update_participant_count(wine_id, room_name, max(0, participants_count - 1))
            
            return True
            
        except Exception as e:
            print(f"Error leaving room: {str(e)}")
            return False
    
    def get_room_participants_count(self, room_name: str) -> int:
        """
        Get current number of participants in a room.
        
        Note: In a real implementation, this would query the LiveKit server.
        For now, we'll use the database count as a fallback.
        """
        db = next(get_db())
        try:
            room_session = db.query(RoomSession).filter(
                RoomSession.room_name == room_name
            ).first()
            
            return room_session.active_participants if room_session else 0
            
        finally:
            db.close()
    
    def get_active_rooms_for_wine(self, wine_id: str) -> List[Dict]:
        """Get all active rooms for a specific wine."""
        db = next(get_db())
        try:
            # Get rooms that have been active in the last hour
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            
            rooms = db.query(RoomSession).filter(
                and_(
                    RoomSession.wine_id == wine_id,
                    RoomSession.last_activity >= cutoff_time,
                    RoomSession.active_participants > 0
                )
            ).all()
            
            return [
                {
                    'room_name': room.room_name,
                    'participants_count': room.active_participants,
                    'created_at': room.created_at.isoformat(),
                    'last_activity': room.last_activity.isoformat()
                }
                for room in rooms
            ]
            
        finally:
            db.close()
    
    def get_room_info(self, room_name: str) -> Optional[Dict]:
        """Get detailed information about a room."""
        db = next(get_db())
        try:
            room_session = db.query(RoomSession).filter(
                RoomSession.room_name == room_name
            ).first()
            
            if not room_session:
                return None
            
            wine = db.query(Wine).filter(Wine.id == room_session.wine_id).first()
            
            return {
                'room_name': room_name,
                'wine_id': room_session.wine_id,
                'wine_name': wine.name if wine else 'Unknown Wine',
                'participants_count': room_session.active_participants,
                'created_at': room_session.created_at.isoformat(),
                'last_activity': room_session.last_activity.isoformat()
            }
            
        finally:
            db.close()
    
    def _update_participant_count(self, wine_id: str, room_name: str, count: int):
        """Update participant count in database."""
        db = next(get_db())
        try:
            room_session = db.query(RoomSession).filter(
                RoomSession.wine_id == wine_id,
                RoomSession.room_name == room_name
            ).first()
            
            if room_session:
                room_session.active_participants = count
                room_session.last_activity = datetime.utcnow()
                db.commit()
                
        except Exception as e:
            db.rollback()
            print(f"Error updating participant count: {str(e)}")
        finally:
            db.close()
    
    def cleanup_inactive_rooms(self, hours: int = 24):
        """Clean up rooms that have been inactive for specified hours."""
        db = next(get_db())
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            inactive_rooms = db.query(RoomSession).filter(
                RoomSession.last_activity < cutoff_time
            ).all()
            
            for room in inactive_rooms:
                db.delete(room)
            
            db.commit()
            return len(inactive_rooms)
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

# Global service instance
livekit_service = LiveKitRoomService()