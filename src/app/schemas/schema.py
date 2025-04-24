from pydantic import BaseModel, EmailStr, HttpUrl, Field, ConfigDict, UUID4
from datetime import datetime
from typing import Optional, List, Union

# Auth and User schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID4
    email: EmailStr
    username: str
    is_admin: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserBasicInfo(BaseModel):
    id: UUID4
    username: str
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"

class TokenData(BaseModel):
    user_id: Optional[UUID4] = None
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
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime
    follower_count: int
    following_count: int
    
    model_config = ConfigDict(from_attributes=True)

# Post schemas
class PostImageResponse(BaseModel):
    id: UUID4
    image_url: str
    
    model_config = ConfigDict(from_attributes=True)

class PostBase(BaseModel):
    content: str = Field(..., max_length=4000)

class PostCreate(PostBase):
    image_urls: Optional[List[str]] = []  # List of image URLs to attach

class ReplyCreate(PostBase):
    reply_to_post_id: UUID4
    image_urls: Optional[List[str]] = []  # List of image URLs to attach

class PostUpdate(PostBase):
    pass

class PostAuthorResponse(BaseModel):
    id: UUID4
    username: str
    
    model_config = ConfigDict(from_attributes=True)

class ReplyToPostResponse(BaseModel):
    id: UUID4
    content: str
    author: PostAuthorResponse
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PostResponse(PostBase):
    id: UUID4
    author_id: UUID4
    author: Optional[PostAuthorResponse] = None
    created_at: datetime
    updated_at: datetime
    like_count: int
    repost_count: int
    reply_count: int
    original_post_id: Optional[UUID4] = None
    reply_to_post_id: Optional[UUID4] = None
    reply_to_post: Optional[ReplyToPostResponse] = None
    images: List[PostImageResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

# Interaction schemas
class LikeCreate(BaseModel):
    post_id: UUID4

class LikeResponse(BaseModel):
    id: UUID4
    user_id: UUID4
    post_id: UUID4
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class RepostCreate(BaseModel):
    post_id: UUID4

class RepostResponse(BaseModel):
    id: UUID4
    user_id: UUID4
    post_id: UUID4
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Media schemas
class MediaUploadResponse(BaseModel):
    id: UUID4
    filename: str
    file_url: str
    
    model_config = ConfigDict(from_attributes=True)

# Admin schemas
class ModerateAction(BaseModel):
    action_type: str  # DELETE_POST, BAN_USER, etc.
    target_user_id: Optional[UUID4] = None
    target_post_id: Optional[UUID4] = None
    reason: Optional[str] = None

class ModerationActionResponse(BaseModel):
    id: UUID4
    admin_id: UUID4
    action_type: str
    target_user_id: Optional[UUID4] = None
    target_post_id: Optional[UUID4] = None
    reason: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Follower schemas
class FollowCreate(BaseModel):
    user_id: UUID4  # ID of the user to follow

class FollowResponse(BaseModel):
    id: UUID4
    follower_id: UUID4
    following_id: UUID4
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class FollowerUserResponse(BaseModel):
    id: UUID4
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class FollowListResponse(BaseModel):
    items: List[FollowerUserResponse]
    total: int
    page: int
    limit: int
    pages: int
    
    model_config = ConfigDict(from_attributes=True)
