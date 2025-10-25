"""
WebSocket endpoints for real-time translation functionality.
"""
import asyncio
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from backend.models.database import get_db
from backend.services.translation_service import translation_service
from backend.services.session_manager import get_current_user_from_token

logger = logging.getLogger(__name__)

class TranslationWebSocketManager:
    """Manage WebSocket connections for real-time translation."""
    
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, WebSocket] = {}
        # Store room participants for broadcasting
        self.room_participants: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, room_id: str):
        """Accept WebSocket connection and start translation session."""
        await websocket.accept()
        
        self.active_connections[user_id] = websocket
        
        # Add user to room participants
        if room_id not in self.room_participants:
            self.room_participants[room_id] = set()
        self.room_participants[room_id].add(user_id)
        
        logger.info(f"Translation WebSocket connected for user {user_id} in room {room_id}")
    
    def disconnect(self, user_id: str, room_id: str):
        """Handle WebSocket disconnection."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # Remove user from room participants
        if room_id in self.room_participants:
            self.room_participants[room_id].discard(user_id)
            if not self.room_participants[room_id]:
                del self.room_participants[room_id]
        
        # Stop translation session
        translation_service.stop_translation_session(user_id)
        
        logger.info(f"Translation WebSocket disconnected for user {user_id}")
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send message to specific user."""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
    
    async def broadcast_to_room(self, room_id: str, message: dict, exclude_user: str = None):
        """Broadcast message to all participants in a room."""
        if room_id not in self.room_participants:
            return
        
        participants = self.room_participants[room_id].copy()
        if exclude_user:
            participants.discard(exclude_user)
        
        for user_id in participants:
            await self.send_to_user(user_id, message)
    
    def get_room_participants(self, room_id: str) -> Set[str]:
        """Get list of participants in a room."""
        return self.room_participants.get(room_id, set())

# Global WebSocket manager
websocket_manager = TranslationWebSocketManager()

async def handle_translation_websocket(
    websocket: WebSocket,
    user_id: str,
    room_id: str,
    db: Session = Depends(get_db)
):
    """Handle WebSocket connection for real-time translation."""
    try:
        # Connect WebSocket
        await websocket_manager.connect(websocket, user_id, room_id)
        
        # Start translation session
        await translation_service.start_translation_session(user_id, room_id, db)
        
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            'type': 'connection_established',
            'user_id': user_id,
            'room_id': room_id,
            'message': 'Translation service connected'
        }))
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                await process_translation_message(user_id, room_id, message, db)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    'type': 'error',
                    'message': 'Invalid JSON format'
                }))
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                await websocket.send_text(json.dumps({
                    'type': 'error',
                    'message': 'Internal server error'
                }))
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    
    finally:
        websocket_manager.disconnect(user_id, room_id)

async def process_translation_message(user_id: str, room_id: str, message: dict, db: Session):
    """Process incoming translation WebSocket messages."""
    message_type = message.get('type')
    
    try:
        if message_type == 'audio_data':
            await handle_audio_data(user_id, room_id, message)
        
        elif message_type == 'recognition_result':
            await handle_recognition_result(user_id, room_id, message)
        
        elif message_type == 'update_settings':
            await handle_settings_update(user_id, message, db)
        
        elif message_type == 'get_voices':
            await handle_get_voices(user_id, message)
        
        elif message_type == 'ping':
            await websocket_manager.send_to_user(user_id, {'type': 'pong'})
        
        else:
            logger.warning(f"Unknown message type: {message_type}")
    
    except Exception as e:
        logger.error(f"Error processing message type {message_type}: {e}")
        await websocket_manager.send_to_user(user_id, {
            'type': 'error',
            'message': f'Error processing {message_type}'
        })

async def handle_audio_data(user_id: str, room_id: str, message: dict):
    """Handle incoming audio data for speech recognition."""
    try:
        audio_data = message.get('data', [])
        
        # Convert audio data to bytes (assuming it's a list of float values)
        if isinstance(audio_data, list):
            # Convert float32 array to bytes
            import struct
            audio_bytes = b''.join(struct.pack('<f', sample) for sample in audio_data)
        else:
            audio_bytes = audio_data
        
        # Process audio data
        await translation_service.process_audio_data(user_id, audio_bytes)
        
    except Exception as e:
        logger.error(f"Error handling audio data: {e}")

async def handle_recognition_result(user_id: str, room_id: str, message: dict):
    """Handle speech recognition results."""
    try:
        transcript = message.get('transcript', '')
        is_final = message.get('is_final', False)
        
        if not transcript:
            return
        
        # Process recognition result and get translations
        translation_results = await translation_service.process_recognition_result(
            user_id, transcript, is_final
        )
        
        if translation_results:
            # Broadcast translations to room participants
            for result in translation_results:
                await websocket_manager.broadcast_to_room(
                    room_id, 
                    result, 
                    exclude_user=user_id
                )
    
    except Exception as e:
        logger.error(f"Error handling recognition result: {e}")

async def handle_settings_update(user_id: str, message: dict, db: Session):
    """Handle translation settings updates."""
    try:
        settings_data = message.get('settings', {})
        
        success = await translation_service.update_translation_settings(
            user_id, settings_data, db
        )
        
        await websocket_manager.send_to_user(user_id, {
            'type': 'settings_updated',
            'success': success
        })
    
    except Exception as e:
        logger.error(f"Error updating settings: {e}")

async def handle_get_voices(user_id: str, message: dict):
    """Handle request for available voices."""
    try:
        language = message.get('language', 'en')
        voices = translation_service.get_available_voices(language)
        
        await websocket_manager.send_to_user(user_id, {
            'type': 'voices_list',
            'language': language,
            'voices': voices
        })
    
    except Exception as e:
        logger.error(f"Error getting voices: {e}")

# WebSocket endpoint function for FastAPI
async def translation_websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    room_id: str,
    token: str = None,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for translation service."""
    # Validate user token if provided
    if token:
        try:
            current_user = get_current_user_from_token(token, db)
            if not current_user or current_user.id != user_id:
                await websocket.close(code=1008, reason="Invalid authentication")
                return
        except Exception:
            await websocket.close(code=1008, reason="Authentication failed")
            return
    
    await handle_translation_websocket(websocket, user_id, room_id, db)