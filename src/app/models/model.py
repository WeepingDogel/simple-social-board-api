from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Float, UniqueConstraint, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    posts = relationship("Post", back_populates="author", foreign_keys="Post.author_id")
    likes = relationship("Like", back_populates="user")
    reposts = relationship("Repost", back_populates="user")
    replies = relationship("Post", back_populates="reply_author", foreign_keys="Post.reply_author_id")
    
    # Followers relationships
    followers = relationship("Follower", back_populates="following_user", foreign_keys="Follower.following_id")
    following = relationship("Follower", back_populates="follower_user", foreign_keys="Follower.follower_id")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"


class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    display_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    background_color = Column(String, default="#ffffff")
    bio = Column(String(160), nullable=True)  # Twitter-style bio, limited to 160 chars
    follower_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, display_name='{self.display_name}')>"


class Post(Base):
    __tablename__ = "posts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)  # Using Text instead of String(4000) for more flexibility
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    like_count = Column(Integer, default=0)
    repost_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    
    # For reposts
    original_post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=True)
    
    # For replies
    reply_to_post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=True)
    reply_author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    author = relationship("User", back_populates="posts", foreign_keys=[author_id])
    reply_author = relationship("User", back_populates="replies", foreign_keys=[reply_author_id])
    images = relationship("PostImage", back_populates="post")
    likes = relationship("Like", back_populates="post")
    reposts = relationship("Repost", back_populates="post")
    original_post = relationship("Post", foreign_keys=[original_post_id], remote_side=[id], backref="reposts_of")
    reply_to_post = relationship("Post", foreign_keys=[reply_to_post_id], remote_side=[id], backref="replies")

    def __repr__(self):
        return f"<Post(id={self.id}, author_id={self.author_id})>"


class PostImage(Base):
    __tablename__ = "post_images"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False)
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    post = relationship("Post", back_populates="images")

    def __repr__(self):
        return f"<PostImage(id={self.id}, post_id={self.post_id})>"


class Like(Base):
    __tablename__ = "likes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")
    
    # Unique constraint to prevent multiple likes by the same user
    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),
    )

    def __repr__(self):
        return f"<Like(user_id={self.user_id}, post_id={self.post_id})>"


class Repost(Base):
    __tablename__ = "reposts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="reposts")
    post = relationship("Post", back_populates="reposts")
    
    # Unique constraint to prevent multiple reposts by the same user
    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='unique_user_post_repost'),
    )

    def __repr__(self):
        return f"<Repost(user_id={self.user_id}, post_id={self.post_id})>"


class MediaFile(Base):
    __tablename__ = "media_files"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    uploader_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MediaFile(id={self.id}, filename='{self.filename}')>"


class ModerationAction(Base):
    __tablename__ = "moderation_actions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action_type = Column(String, nullable=False)  # "DELETE_POST", "BAN_USER", etc.
    target_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    target_post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=True)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ModerationAction(id={self.id}, action_type='{self.action_type}')>"


class Follower(Base):
    __tablename__ = "followers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    follower_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    following_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    follower_user = relationship("User", back_populates="following", foreign_keys=[follower_id])
    following_user = relationship("User", back_populates="followers", foreign_keys=[following_id])
    
    # Unique constraint to prevent duplicate follows
    __table_args__ = (
        UniqueConstraint('follower_id', 'following_id', name='unique_follower_following'),
    )

    def __repr__(self):
        return f"<Follower(follower_id={self.follower_id}, following_id={self.following_id})>"


