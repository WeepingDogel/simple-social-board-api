from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional
import uuid

from ..models.model import User, UserProfile, Post, PostImage, Like, Repost, MediaFile, ModerationAction
from ..schemas.schema import UserCreate, ProfileCreate, PostCreate, LikeCreate, RepostCreate
from .auth import get_password_hash

# User CRUD operations
def create_user(db: Session, user_create: UserCreate):
    # Check if user with this email exists
    db_user = db.query(User).filter(User.email == user_create.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username exists
    db_user = db.query(User).filter(User.username == user_create.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user with hashed password
    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        email=user_create.email,
        username=user_create.username,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create default profile for user
    db_profile = UserProfile(
        user_id=db_user.id,
        display_name=db_user.username  # Default display name is username
    )
    
    db.add(db_profile)
    db.commit()
    
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, is_active: bool = None, is_admin: bool = None):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if is_active is not None:
        db_user.is_active = is_active
    
    if is_admin is not None:
        db_user.is_admin = is_admin
    
    db.commit()
    db.refresh(db_user)
    return db_user

# Profile CRUD operations
def get_profile(db: Session, user_id: int):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

def update_profile(db: Session, user_id: int, profile_data: dict):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    for key, value in profile_data.items():
        if hasattr(profile, key) and value is not None:
            setattr(profile, key, value)
    
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    return profile

# Post CRUD operations
def create_post(db: Session, user_id: int, post_create: PostCreate):
    # Create new post
    db_post = Post(
        content=post_create.content,
        author_id=user_id
    )
    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    # Add images if provided
    if post_create.image_urls:
        # Limit to max 9 images
        image_urls = post_create.image_urls[:9]
        
        for image_url in image_urls:
            db_image = PostImage(
                post_id=db_post.id,
                image_url=image_url
            )
            db.add(db_image)
        
        db.commit()
        db.refresh(db_post)
    
    return db_post

def get_post(db: Session, post_id: int):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

def get_feed(db: Session, skip: int = 0, limit: int = 20):
    # Simple feed implementation - just get latest posts
    # In a production app, this would be more complex with personalization
    return db.query(Post).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()

def get_user_posts(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    return db.query(Post).filter(Post.author_id == user_id).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()

def delete_post(db: Session, post_id: int, user_id: int, is_admin: bool = False):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user is author or admin
    if post.author_id != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    # Delete images associated with post
    db.query(PostImage).filter(PostImage.post_id == post_id).delete()
    
    # Delete likes and reposts
    db.query(Like).filter(Like.post_id == post_id).delete()
    db.query(Repost).filter(Repost.post_id == post_id).delete()
    
    # Delete post
    db.delete(post)
    db.commit()
    
    return {"message": "Post deleted successfully"}

# Interaction CRUD operations
def create_like(db: Session, user_id: int, post_id: int):
    # Check if post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user already liked this post
    existing_like = db.query(Like).filter(Like.user_id == user_id, Like.post_id == post_id).first()
    if existing_like:
        return existing_like  # User already liked this post
    
    # Create like
    db_like = Like(user_id=user_id, post_id=post_id)
    db.add(db_like)
    
    # Update post like count
    post.like_count += 1
    
    db.commit()
    db.refresh(db_like)
    
    return db_like

def delete_like(db: Session, user_id: int, post_id: int):
    # Find like
    like = db.query(Like).filter(Like.user_id == user_id, Like.post_id == post_id).first()
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    
    # Get post to update count
    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        post.like_count = max(0, post.like_count - 1)  # Ensure it doesn't go below zero
    
    # Delete like
    db.delete(like)
    db.commit()
    
    return {"message": "Like removed successfully"}

def create_repost(db: Session, user_id: int, post_id: int):
    # Check if post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user already reposted this post
    existing_repost = db.query(Repost).filter(Repost.user_id == user_id, Repost.post_id == post_id).first()
    if existing_repost:
        return existing_repost  # User already reposted this post
    
    # Create repost record
    db_repost = Repost(user_id=user_id, post_id=post_id)
    db.add(db_repost)
    
    # Create repost as a new post pointing to original
    db_repost_post = Post(
        content=post.content,
        author_id=user_id,
        original_post_id=post_id
    )
    db.add(db_repost_post)
    
    # Update original post repost count
    post.repost_count += 1
    
    db.commit()
    db.refresh(db_repost)
    
    return db_repost

# Media CRUD operations
def create_media_file(db: Session, 
                     user_id: int, 
                     filename: str, 
                     file_path: str, 
                     file_url: str, 
                     mime_type: str, 
                     file_size: int):
    
    db_media = MediaFile(
        filename=filename,
        file_path=file_path,
        file_url=file_url,
        mime_type=mime_type,
        file_size=file_size,
        uploader_id=user_id
    )
    
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    
    return db_media

# Admin operations
def create_moderation_action(db: Session, 
                            admin_id: int, 
                            action_type: str, 
                            target_user_id: Optional[int] = None,
                            target_post_id: Optional[int] = None,
                            reason: Optional[str] = None):
    
    db_action = ModerationAction(
        admin_id=admin_id,
        action_type=action_type,
        target_user_id=target_user_id,
        target_post_id=target_post_id,
        reason=reason
    )
    
    db.add(db_action)
    db.commit()
    db.refresh(db_action)
    
    return db_action

def get_moderation_actions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ModerationAction).order_by(ModerationAction.created_at.desc()).offset(skip).limit(limit).all()
