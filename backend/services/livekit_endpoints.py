"""
FastAPI endpoints for LiveKit room management.
"""
from typing import Dict, List
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.services.livekit_service import livekit_service
from backend.services.session_manager import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/api/rooms", tags=["rooms"])

class JoinRoomRequest(BaseModel):
    """Request model for joining a room."""
    wine_id: str

class JoinRoomResponse(BaseModel):
    """Response model for joining a room."""
    room_name: str
    access_token: str
    livekit_url: str
    wine_id: str
    participants_count: int

class LeaveRoomRequest(BaseModel):
    """Request model for leaving a room."""
    room_name: str

class RoomInfoResponse(BaseModel):
    """Response model for room information."""
    room_name: str
    wine_id: str
    wine_name: str
    participants_count: int
    created_at: str
    last_activity: str

@router.post("/join", response_model=JoinRoomResponse)
async def join_wine_room(
    request: JoinRoomRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Join or create a wine room for video chat.
    
    Creates a new room if one doesn't exist for the wine,
    or joins an existing room.
    """
    try:
        room_info = livekit_service.join_room(
            wine_id=request.wine_id,
            user_id=current_user.id
        )
        
        return JoinRoomResponse(**room_info)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to join room: {str(e)}"
        )

@router.post("/leave")
async def leave_room(
    request: LeaveRoomRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Leave a room and update participant count.
    """
    try:
        success = livekit_service.leave_room(
            user_id=current_user.id,
            room_name=request.room_name
        )
        
        if success:
            return {"message": "Successfully left room"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to leave room"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error leaving room: {str(e)}"
        )

@router.get("/wine/{wine_id}")
async def get_wine_rooms(
    wine_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get all active rooms for a specific wine.
    """
    try:
        rooms = livekit_service.get_active_rooms_for_wine(wine_id)
        return {"rooms": rooms}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get wine rooms: {str(e)}"
        )

@router.get("/{room_name}", response_model=RoomInfoResponse)
async def get_room_info(
    room_name: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific room.
    """
    try:
        room_info = livekit_service.get_room_info(room_name)
        
        if not room_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found"
            )
        
        return RoomInfoResponse(**room_info)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get room info: {str(e)}"
        )

@router.get("/")
async def list_user_rooms(
    current_user: User = Depends(get_current_user)
):
    """
    List all rooms the current user has access to.
    This is a placeholder - in a real implementation,
    you might track user room memberships.
    """
    try:
        # For now, return empty list
        # In a full implementation, you'd track which rooms a user has joined
        return {"rooms": []}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list rooms: {str(e)}"
        )

@router.delete("/cleanup")
async def cleanup_inactive_rooms(
    hours: int = 24,
    current_user: User = Depends(get_current_user)
):
    """
    Clean up inactive rooms (admin function).
    """
    try:
        # In a real app, you'd check if user has admin privileges
        cleaned_count = livekit_service.cleanup_inactive_rooms(hours)
        
        return {
            "message": f"Cleaned up {cleaned_count} inactive rooms",
            "cleaned_count": cleaned_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup rooms: {str(e)}"
        )