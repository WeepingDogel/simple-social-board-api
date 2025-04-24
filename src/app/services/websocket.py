from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Any
import json
import asyncio
from datetime import datetime
import uuid

class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime and UUID objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)

class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates
    """
    def __init__(self):
        # Active connections mapped by user_id
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # All connections for broadcasting
        self.broadcast_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket, user_id: uuid.UUID = None):
        """Connect a WebSocket client"""
        await websocket.accept()
        
        # Add to broadcast list
        self.broadcast_connections.append(websocket)
        
        # If user is authenticated, add to user-specific list
        if user_id:
            user_id_str = str(user_id)
            if user_id_str not in self.active_connections:
                self.active_connections[user_id_str] = []
            self.active_connections[user_id_str].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: uuid.UUID = None):
        """Disconnect a WebSocket client"""
        # Remove from broadcast list
        if websocket in self.broadcast_connections:
            self.broadcast_connections.remove(websocket)
        
        # If user was authenticated, remove from user-specific list
        if user_id:
            user_id_str = str(user_id)
            if user_id_str in self.active_connections:
                if websocket in self.active_connections[user_id_str]:
                    self.active_connections[user_id_str].remove(websocket)
                
                # Clean up empty lists
                if not self.active_connections[user_id_str]:
                    del self.active_connections[user_id_str]
    
    async def send_personal_message(self, message: Any, user_id: uuid.UUID):
        """Send a message to a specific user's connections"""
        user_id_str = str(user_id)
        if user_id_str in self.active_connections:
            message_json = message if isinstance(message, str) else json.dumps(message, cls=DateTimeEncoder)
            
            # Send to all connections for this user
            for connection in self.active_connections[user_id_str]:
                try:
                    await connection.send_text(message_json)
                except Exception:
                    # Connection might be closed
                    pass
    
    async def broadcast(self, message: Any):
        """Broadcast a message to all connected clients"""
        message_json = message if isinstance(message, str) else json.dumps(message, cls=DateTimeEncoder)
        
        # Send to all connections
        for connection in self.broadcast_connections:
            try:
                await connection.send_text(message_json)
            except Exception:
                # Connection might be closed
                pass
    
    async def broadcast_post(self, post: dict):
        """Broadcast a new post to all connected clients"""
        await self.broadcast({
            "type": "new_post",
            "data": post
        })
    
    async def broadcast_like(self, like: dict):
        """Broadcast a like event to all connected clients"""
        await self.broadcast({
            "type": "new_like",
            "data": like
        })
    
    async def broadcast_repost(self, repost: dict):
        """Broadcast a repost event to all connected clients"""
        await self.broadcast({
            "type": "new_repost",
            "data": repost
        })

# Create a global connection manager instance
manager = ConnectionManager()

# Heartbeat to keep connections alive
async def heartbeat(websocket: WebSocket):
    """Send periodic heartbeat to keep WebSocket connections alive"""
    try:
        while True:
            await asyncio.sleep(30)  # Send heartbeat every 30 seconds
            await websocket.send_text(json.dumps({"type": "heartbeat"}))
    except Exception:
        # Connection closed or other error
        pass 