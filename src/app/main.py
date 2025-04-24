import os
import psutil
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import service modules
from .services.database import engine, Base, init_db, wait_for_db, apply_migrations

# Import models for reference
from .models.model import User, UserProfile, Post, PostImage, Like, Repost, MediaFile, ModerationAction

# Import API routers
from .api import auth, profile, post, media, admin, websocket, follower

# Tags for API documentation
tags_metadata = [
    {
        "name": "authentication",
        "description": "Authentication operations: register, login, token",
    },
    {
        "name": "profiles",
        "description": "User profile operations",
    },
    {
        "name": "posts",
        "description": "Post operations: create, read, update, delete",
    },
    {
        "name": "media",
        "description": "Media operations: upload images",
    },
    {
        "name": "followers",
        "description": "Follower operations: follow, unfollow, list followers and following",
    },
    {
        "name": "admin",
        "description": "Admin operations: user management, moderation",
    },
    {
        "name": "websocket",
        "description": "WebSocket endpoints for real-time updates",
    },
    {
        "name": "core",
        "description": "Core operations: health check, static files",
    },
]

# API documentation description
document_description = """
# Simple Social Board API

The backend service for an open-source, lightweight social media platform built with microservices architecture.

## Features

- **User Authentication**: Register, login, and JWT-based authentication
- **User Profiles**: Customize profiles with avatars and background colors
- **Posts**: Create posts with text (up to 500 words) and images (up to 9)
- **Social Interactions**: Like and repost functionality
- **Real-time Updates**: WebSockets for live feed updates
- **Media Uploads**: Image uploading and storage
- **Admin Dashboard**: User and content moderation

## API Structure

- `/api/auth/`: Authentication endpoints
- `/api/profiles/`: User profile management
- `/api/posts/`: Post creation and interaction
- `/api/media/`: Media upload
- `/api/admin/`: Admin operations
- `/api/ws/`: WebSocket connections
- `/static/`: Static files (images, etc.)
"""

# Create FastAPI app
app = FastAPI(
    title="Simple Social Board API",
    description=document_description,
    version="1.0.0",
    openapi_tags=tags_metadata
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create static files directory if not exist
if not os.path.exists("static"):
    os.makedirs("static")
    
# Create media directory if not exist
if not os.path.exists("static/media"):
    os.makedirs("static/media")
    
# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(post.router)
app.include_router(media.router)
app.include_router(admin.router)
app.include_router(websocket.router)
app.include_router(follower.router)

# Initialize database on startup
@app.on_event("startup")
async def startup_db_client():
    logger.info("Starting up database client...")
    # Wait for database to be available
    if wait_for_db():
        # Initialize database with improved function that handles UUID support
        init_db()
        # Apply any pending migrations
        apply_migrations()
        logger.info("Database initialized successfully")
    else:
        logger.error("Failed to connect to database")

@app.get("/", tags=["core"], summary="Root endpoint", 
         description="Endpoint root that returns a simple greeting message.", 
         response_description="A simple message.",
         responses={
             200: {
                "description": "API information retrieved successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "title": "Simple Social Board API Backend",
                            "description": "A social media platform built with FastAPI",
                            "version": "1.0.0"
                        }
                    }
                },
             },
             500: {
                 "description": "Internal Server Error",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Internal Server Error"}
                        }
                    },
            },
         })
async def root():
    return {
        "title": "Simple Social Board API Backend",
        "description": "A social media platform built with FastAPI",
        "version": "1.0.0",
        }

@app.get("/health", tags=["core"], summary="Health check endpoint",
            description="Endpoint to check the health of the application.",
            response_description="Health status of the application.",
            responses={
                200: {
                    "description": "Health status retrieved successfully",
                    "content": {
                        "application/json": {
                            "example": {
                                "status": "healthy",
                                "cpu_usage": "23.5%",
                                "memory_usage": "43.2%",
                                "disk_usage": "67.8%",
                                "total_memory": "16.00 GB",
                                "available_memory": "9.12 GB"
                            }
                        }
                    },
                },
                500: {
                    "description": "Internal server error",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Error fetching system metrics"}
                        }
                    },
                },
            })
async def health():
    try:
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        return {
            "status": "healthy",
            "cpu_usage": f"{cpu_percent}%",
            "memory_usage": f"{memory.percent}%",
            "disk_usage": f"{disk.percent}%",
            "total_memory": f"{memory.total / (1024*1024*1024):.2f} GB",
            "available_memory": f"{memory.available / (1024*1024*1024):.2f} GB"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching system metrics: {str(e)}")
    
@app.get("/static/{file_path:path}", tags=["core"], summary="Static file endpoint",
            description="Endpoint to serve static files.",
            response_description="Static file content.",
            responses={
                200: {
                    "description": "Static file content",
                    "content": {
                        "application/json": {
                            "example": {"message": "File served successfully"}
                        }
                    },
                },
                404: {
                    "description": "File not found",
                    "content": {
                        "application/json": {
                            "example": {"detail": "The requested file does not exist"}
                        }
                    },
                },
                500: {
                    "description": "Internal server error",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Error serving static file"}
                        }
                    },
                },
            })
async def static_file(file_path: str):
    try:
        file_path = os.path.join("static", file_path)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        return {"message": "Static file content"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@app.get("/static", tags=["core"], summary="Static files endpoint",
            description="Endpoint to list static files.",
            response_description="List of static files.",
            responses={
                200: {
                    "description": "List of static files successfully retrieved",
                    "content": {
                        "application/json": {
                            "example": {
                                "files": [
                                    "media/",
                                    "avatars/",
                                    "image1.jpg",
                                    "image2.png"
                                ]
                            }
                        }
                    },
                },
                500: {
                    "description": "Internal server error",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Error listing static files"}
                        }
                    },
                },
            })
async def list_static_files():
    try:
        files = os.listdir("static")
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing static files: {str(e)}")