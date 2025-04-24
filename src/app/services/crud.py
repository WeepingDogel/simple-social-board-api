from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional, Union
import uuid
from sqlalchemy import desc

from ..models.model import User, UserProfile, Post, PostImage, Like, Repost, MediaFile, ModerationAction
from ..schemas.schema import UserCreate, ProfileCreate, PostCreate, ReplyCreate, LikeCreate, RepostCreate
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

def get_user_by_id(db: Session, user_id: Union[str, uuid.UUID]):
    if isinstance(user_id, str):
        try:
            user_id = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: Union[str, uuid.UUID], is_active: bool = None, is_admin: bool = None):
    if isinstance(user_id, str):
        try:
            user_id = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")
    
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
def get_profile(db: Session, user_id: Union[str, uuid.UUID]):
    if isinstance(user_id, str):
        try:
            user_id = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

def update_profile(db: Session, user_id: Union[str, uuid.UUID], profile_data: dict):
    if isinstance(user_id, str):
        try:
            user_id = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")
    
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
def create_post(db: Session, user_id: Union[str, uuid.UUID], post_create: PostCreate):
    if isinstance(user_id, str):
        try:
            user_id = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")
    
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

# Create a reply to a post
def create_reply(db: Session, user_id: Union[str, uuid.UUID], reply_create: ReplyCreate):
    if isinstance(user_id, str):
        try:
            user_id = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    # Check if the post to reply to exists
    reply_to_post_id = reply_create.reply_to_post_id
    if isinstance(reply_to_post_id, str):
        try:
            reply_to_post_id = uuid.UUID(reply_to_post_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid post ID format")
    
    reply_to_post = db.query(Post).filter(Post.id == reply_to_post_id).first()
    if not reply_to_post:
        raise HTTPException(status_code=404, detail="Post to reply to not found")
    
    # Create new reply post
    db_reply = Post(
        content=reply_create.content,
        author_id=user_id,
        reply_to_post_id=reply_to_post.id,
        reply_author_id=reply_to_post.author_id
    )
    
    db.add(db_reply)
    db.commit()
    db.refresh(db_reply)
    
    # Add images if provided
    if reply_create.image_urls:
        # Limit to max 9 images
        image_urls = reply_create.image_urls[:9]
        
        for image_url in image_urls:
            db_image = PostImage(
                post_id=db_reply.id,
                image_url=image_url
            )
            db.add(db_image)
    
    # Increment reply count on the original post
    reply_to_post.reply_count += 1
    
    db.commit()
    db.refresh(db_reply)
    
    return db_reply

def get_post(db: Session, post_id: Union[str, uuid.UUID]):
    if isinstance(post_id, str):
        try:
            post_id = uuid.UUID(post_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid post ID format")
    
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

def get_post_with_author(db: Session, post_id: Union[str, uuid.UUID]):
    if isinstance(post_id, str):
        try:
            post_id = uuid.UUID(post_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid post ID format")
    
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Load author info
    author = db.query(User).filter(User.id == post.author_id).first()
    post.author = author
    
    # If it's a reply, load the replied-to post
    if post.reply_to_post_id:
        reply_to_post = db.query(Post).filter(Post.id == post.reply_to_post_id).first()
        if reply_to_post:
            reply_to_post_author = db.query(User).filter(User.id == reply_to_post.author_id).first()
            reply_to_post.author = reply_to_post_author
            post.reply_to_post = reply_to_post
    
    return post

def get_feed(db: Session, skip: int = 0, limit: int = 20):
    # Simple feed implementation - just get latest posts
    # In a production app, this would be more complex with personalization
    posts = db.query(Post).order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    
    # Load authors for all posts
    for post in posts:
        post.author = db.query(User).filter(User.id == post.author_id).first()
        
        # Load reply info if it's a reply
        if post.reply_to_post_id:
            reply_to = db.query(Post).filter(Post.id == post.reply_to_post_id).first()
            if reply_to:
                reply_to.author = db.query(User).filter(User.id == reply_to.author_id).first()
                post.reply_to_post = reply_to
    
    return posts

def get_user_posts(db: Session, user_id: Union[str, uuid.UUID], skip: int = 0, limit: int = 20):
    if isinstance(user_id, str):
        try:
            user_id = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    posts = db.query(Post).filter(Post.author_id == user_id).order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    
    # Load author for all posts
    user = db.query(User).filter(User.id == user_id).first()
    for post in posts:
        post.author = user
        
        # Load reply info if it's a reply
        if post.reply_to_post_id:
            reply_to = db.query(Post).filter(Post.id == post.reply_to_post_id).first()
            if reply_to:
                reply_to.author = db.query(User).filter(User.id == reply_to.author_id).first()
                post.reply_to_post = reply_to
    
    return posts

def get_post_replies(db: Session, post_id: Union[str, uuid.UUID], skip: int = 0, limit: int = 20):
    if isinstance(post_id, str):
        try:
            post_id = uuid.UUID(post_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid post ID format")
    
    # Check if post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Get replies
    replies = db.query(Post).filter(Post.reply_to_post_id == post_id).order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    
    # Load authors for all replies
    for reply in replies:
        reply.author = db.query(User).filter(User.id == reply.author_id).first()
        reply.reply_to_post = post
        post.author = db.query(User).filter(User.id == post.author_id).first()
    
    return replies

def delete_post(db: Session, post_id: Union[str, uuid.UUID], user_id: Union[str, uuid.UUID], is_admin: bool = False):
    if isinstance(post_id, str):
        try:
            post_id = uuid.UUID(post_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid post ID format")
            
    if isinstance(user_id, str):
        try:
            user_id = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user is author or admin
    if post.author_id != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    # If this is a reply, decrement reply count on parent post
    if post.reply_to_post_id:
        parent_post = db.query(Post).filter(Post.id == post.reply_to_post_id).first()
        if parent_post:
            parent_post.reply_count = max(0, parent_post.reply_count - 1)
    
    # Delete images associated with post
    db.query(PostImage).filter(PostImage.post_id == post_id).delete()
    
    # Delete likes and reposts
    db.query(Like).filter(Like.post_id == post_id).delete()
    db.query(Repost).filter(Repost.post_id == post_id).delete()
    
    # Delete replies to this post
    replies = db.query(Post).filter(Post.reply_to_post_id == post_id).all()
    for reply in replies:
        # Recursively delete replies (without checking auth since parent is being deleted)
        delete_post(db, reply.id, user_id, is_admin=True)
    
    # Delete post
    db.delete(post)
    db.commit()
    
    return {"message": "Post deleted successfully"}

# Interaction CRUD operations
def create_like(db: Session, user_id: Union[str, uuid.UUID], post_id: Union[str, uuid.UUID]):
    if isinstance(user_id, str):
        try:
            user_id = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")
            
    if isinstance(post_id, str):
        try:
            post_id = uuid.UUID(post_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid post ID format")
    
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

def delete_like(db: Session, user_id: Union[str, uuid.UUID], post_id: Union[str, uuid.UUID]):
    if isinstance(user_id, str):
        try:
            user_id = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")
            
    if isinstance(post_id, str):
        try:
            post_id = uuid.UUID(post_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid post ID format")
    
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

def create_repost(db: Session, user_id: Union[str, uuid.UUID], post_id: Union[str, uuid.UUID]):
    if isinstance(user_id, str):
        try:
            user_id = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")
            
    if isinstance(post_id, str):
        try:
            post_id = uuid.UUID(post_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid post ID format")
    
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
                     user_id: Union[str, uuid.UUID], 
                     filename: str, 
                     file_path: str, 
                     file_url: str, 
                     mime_type: str, 
                     file_size: int):
    
    if isinstance(user_id, str):
        try:
            user_id = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")
    
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
                            admin_id: Union[str, uuid.UUID], 
                            action_type: str, 
                            target_user_id: Optional[Union[str, uuid.UUID]] = None,
                            target_post_id: Optional[Union[str, uuid.UUID]] = None,
                            reason: Optional[str] = None):
    
    if isinstance(admin_id, str):
        try:
            admin_id = uuid.UUID(admin_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid admin ID format")
    
    if target_user_id and isinstance(target_user_id, str):
        try:
            target_user_id = uuid.UUID(target_user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid target user ID format")
    
    if target_post_id and isinstance(target_post_id, str):
        try:
            target_post_id = uuid.UUID(target_post_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid target post ID format")
    
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
    return db.query(ModerationAction).order_by(desc(ModerationAction.created_at)).offset(skip).limit(limit).all()
