from pydantic import BaseModel, EmailStr, HttpUrl, Field, ConfigDict
from datetime import datetime
from typing import Optional, List

# Auth and User schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_admin: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    is_admin: Optional[bool] = False

# Profile schemas
class ProfileBase(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    background_color: Optional[str] = "#ffffff"
    bio: Optional[str] = None

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Post schemas
class PostImageResponse(BaseModel):
    id: int
    image_url: str
    
    model_config = ConfigDict(from_attributes=True)

class PostBase(BaseModel):
    content: str = Field(..., max_length=4000)

class PostCreate(PostBase):
    image_urls: Optional[List[str]] = []  # List of image URLs to attach

class PostUpdate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    like_count: int
    repost_count: int
    original_post_id: Optional[int] = None
    images: List[PostImageResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

# Interaction schemas
class LikeCreate(BaseModel):
    post_id: int

class LikeResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class RepostCreate(BaseModel):
    post_id: int

class RepostResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Media schemas
class MediaUploadResponse(BaseModel):
    id: int
    filename: str
    file_url: str
    
    model_config = ConfigDict(from_attributes=True)

# Admin schemas
class ModerateAction(BaseModel):
    action_type: str  # DELETE_POST, BAN_USER, etc.
    target_user_id: Optional[int] = None
    target_post_id: Optional[int] = None
    reason: Optional[str] = None

class ModerationActionResponse(BaseModel):
    id: int
    admin_id: int
    action_type: str
    target_user_id: Optional[int] = None
    target_post_id: Optional[int] = None
    reason: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
