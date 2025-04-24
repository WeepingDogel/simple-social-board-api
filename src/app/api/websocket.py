from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from sqlalchemy.orm import Session
import asyncio
from jose import jwt, JWTError

from ..services.database import get_db
from ..services.auth import SECRET_KEY, ALGORITHM
from ..services.websocket import manager, heartbeat
from ..models.model import User

router = APIRouter(tags=["websocket"])

@router.websocket("/api/ws/feed")
async def websocket_feed(
    websocket: WebSocket,
    token: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time feed updates.
    If token is provided, connects as authenticated user,
    otherwise connects anonymously (only for broadcast).
    """
    user_id = None
    
    # Try to authenticate if token provided
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = int(payload.get("sub"))
            
            # Verify user exists and is active
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
                if not user or not user.is_active:
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                    return
        except (JWTError, ValueError):
            # Invalid token
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    
    # Accept connection
    await manager.connect(websocket, user_id)
    
    # Start heartbeat task
    heartbeat_task = asyncio.create_task(heartbeat(websocket))
    
    try:
        # Handle incoming messages (if any)
        while True:
            # This is mainly to detect disconnection
            # Most communication is server -> client for the feed
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Client disconnected
        manager.disconnect(websocket, user_id)
    finally:
        # Cancel heartbeat task
        heartbeat_task.cancel()

@router.websocket("/api/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(...),  # Token is required for notifications
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for user-specific notifications.
    Token is required as notifications are user-specific.
    """
    try:
        # Authenticate user
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        
        # Verify user exists and is active
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
            
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
            
        # Accept connection
        await manager.connect(websocket, user_id)
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": f"Connected to notification stream for user {user_id}"
        })
        
        # Start heartbeat task
        heartbeat_task = asyncio.create_task(heartbeat(websocket))
        
        try:
            # Handle incoming messages (if any)
            while True:
                # This is mainly to detect disconnection
                await websocket.receive_text()
        except WebSocketDisconnect:
            # Client disconnected
            manager.disconnect(websocket, user_id)
        finally:
            # Cancel heartbeat task
            heartbeat_task.cancel()
            
    except (JWTError, ValueError):
        # Invalid token
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION) 