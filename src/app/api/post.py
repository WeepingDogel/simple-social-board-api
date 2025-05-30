from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Path
from sqlalchemy.orm import Session
from typing import List, Optional, Union
import json
from datetime import datetime
import uuid

from ..services.database import get_db
from ..services.auth import get_current_user, get_current_admin_user
from ..services.crud import (
    create_post, 
    create_reply,
    get_post,
    get_post_with_author,
    get_feed, 
    get_user_posts,
    get_post_replies,
    delete_post,
    create_like,
    delete_like,
    create_repost
)
from ..services.media import save_multiple_files
from ..services.websocket import manager
from ..models.model import User
from ..schemas.schema import PostCreate, PostResponse, ReplyCreate, PostUpdate, LikeResponse, RepostResponse

# Custom JSON encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, uuid.UUID):
            return str(o)
        return super().default(o)

router = APIRouter(
    prefix="/api/posts",
    tags=["posts"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=PostResponse)
async def create_new_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new post.
    """
    # Create the post
    post = create_post(db, current_user.id, post_data)
    
    # Get post with author data
    post_with_author = get_post_with_author(db, post.id)
    
    # Convert to Pydantic model
    post_response = PostResponse.model_validate(post_with_author)
    
    # Broadcast to WebSocket clients (using dict method to avoid serialization issues)
    await manager.broadcast_post(post_response.model_dump())
    
    return post_response

@router.post("/reply", response_model=PostResponse)
async def create_post_reply(
    reply_data: ReplyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a reply to an existing post.
    """
    # Create the reply
    reply = create_reply(db, current_user.id, reply_data)
    
    # Get reply with author data
    reply_with_author = get_post_with_author(db, reply.id)
    
    # Convert to Pydantic model
    reply_response = PostResponse.model_validate(reply_with_author)
    
    # Broadcast to WebSocket clients
    await manager.broadcast_post(reply_response.model_dump())
    
    return reply_response

@router.post("/with-images", response_model=PostResponse)
async def create_post_with_images(
    content: str = Query(..., max_length=4000),
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new post with uploaded images.
    """
    # Save images
    file_infos = await save_multiple_files(files, current_user.id)
    
    # Extract image URLs
    image_urls = [file_info["file_url"] for file_info in file_infos]
    
    # Create post with image URLs
    post_data = PostCreate(content=content, image_urls=image_urls)
    post = create_post(db, current_user.id, post_data)
    
    # Get post with author data
    post_with_author = get_post_with_author(db, post.id)
    
    # Convert to Pydantic model
    post_response = PostResponse.model_validate(post_with_author)
    
    # Broadcast to WebSocket clients
    await manager.broadcast_post(post_response.model_dump())
    
    return post_response

@router.get("/feed", response_model=List[PostResponse])
async def get_post_feed(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get a feed of posts.
    """
    posts = get_feed(db, skip=skip, limit=limit)
    return posts

@router.get("/user/{user_id}", response_model=List[PostResponse])
async def get_posts_by_user(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get posts by a specific user.
    """
    posts = get_user_posts(db, user_id, skip=skip, limit=limit)
    return posts

@router.get("/{post_id}/replies", response_model=List[PostResponse])
async def get_replies_to_post(
    post_id: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get replies to a specific post.
    """
    replies = get_post_replies(db, post_id, skip=skip, limit=limit)
    return replies

@router.get("/{post_id}", response_model=PostResponse)
async def get_post_by_id(
    post_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific post by ID.
    """
    post = get_post_with_author(db, post_id)
    return post

@router.delete("/{post_id}")
async def delete_post_by_id(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a post.
    Only the post author or an admin can delete a post.
    """
    result = delete_post(db, post_id, current_user.id, current_user.is_admin)
    return result

@router.post("/{post_id}/like", response_model=LikeResponse)
async def like_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Like a post.
    """
    like = create_like(db, current_user.id, post_id)
    
    # Convert to Pydantic model
    like_response = LikeResponse.model_validate(like)
    
    # Broadcast to WebSocket clients
    await manager.broadcast_like(like_response.model_dump())
    
    return like_response

@router.delete("/{post_id}/like")
async def unlike_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unlike a post.
    """
    result = delete_like(db, current_user.id, post_id)
    return result

@router.post("/{post_id}/repost", response_model=RepostResponse)
async def repost_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Repost a post.
    """
    repost = create_repost(db, current_user.id, post_id)
    
    # Convert to Pydantic model
    repost_response = RepostResponse.model_validate(repost)
    
    # Broadcast to WebSocket clients
    await manager.broadcast_repost(repost_response.model_dump())
    
    return repost_response
