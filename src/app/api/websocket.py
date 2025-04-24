from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from sqlalchemy.orm import Session
import asyncio
from jose import jwt, JWTError
from typing import Optional
import json
import uuid

from ..services.database import get_db
from ..services.auth import SECRET_KEY, ALGORITHM, get_token_data
from ..services.websocket import manager, heartbeat
from ..models.model import User

router = APIRouter(tags=["websocket"])

@router.websocket("/api/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time updates.
    If a token is provided, the connection will be associated with that user.
    """
    # Initialize connection
    user_id = None
    
    # Authenticate if token is provided
    if token:
        try:
            # Validate token
            token_data = get_token_data(token)
            if token_data and token_data.user_id:
                user_id = token_data.user_id  # This will be a UUID
        except Exception:
            # If token validation fails, still connect but without user association
            pass
    
    await manager.connect(websocket, user_id)
    
    # Start heartbeat
    heartbeat_task = asyncio.create_task(heartbeat(websocket))
    
    try:
        while True:
            # Wait for messages from the client
            data = await websocket.receive_text()
            
            # Process message (can be extended)
            try:
                message = json.loads(data)
                # Handle different message types here if needed
                
                # Echo back for now
                await websocket.send_text(json.dumps({"status": "received", "message": message}))
            except json.JSONDecodeError:
                # Not a valid JSON
                await websocket.send_text(json.dumps({"status": "error", "message": "Invalid JSON"}))
    except WebSocketDisconnect:
        # Client disconnected
        manager.disconnect(websocket, user_id)
        # Cancel heartbeat
        heartbeat_task.cancel()
    except Exception as e:
        # Other errors
        manager.disconnect(websocket, user_id)
        # Cancel heartbeat
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
        user_id_str = payload.get("sub")
        
        # Verify user exists and is active
        if not user_id_str:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
            
        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
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