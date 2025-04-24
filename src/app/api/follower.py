from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
import math

from ..services.database import get_db
from ..services.auth import get_current_active_user
from ..models.model import User, UserProfile, Follower
from ..schemas.schema import (
    FollowCreate, 
    FollowResponse, 
    FollowerUserResponse, 
    FollowListResponse
)

router = APIRouter(tags=["followers"])

@router.post("/api/follow", response_model=FollowResponse, status_code=status.HTTP_201_CREATED,
           summary="Follow a user",
           description="Follow a user by their user ID",
           responses={
               201: {
                   "description": "Successfully followed user",
                   "content": {
                       "application/json": {
                           "example": {
                               "id": "123e4567-e89b-12d3-a456-426614174000",
                               "follower_id": "123e4567-e89b-12d3-a456-426614174000",
                               "following_id": "123e4567-e89b-12d3-a456-426614174001",
                               "created_at": "2023-01-02T15:30:00Z"
                           }
                       }
                   }
               },
               400: {
                   "description": "Bad request, can't follow yourself",
                   "content": {
                       "application/json": {
                           "example": {"detail": "You cannot follow yourself"}
                       }
                   }
               },
               404: {
                   "description": "User not found",
                   "content": {
                       "application/json": {
                           "example": {"detail": "User not found"}
                       }
                   }
               },
               409: {
                   "description": "Already following this user",
                   "content": {
                       "application/json": {
                           "example": {"detail": "You are already following this user"}
                       }
                   }
               }
           })
async def follow_user(
    follow_data: FollowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Follow a user by providing their user ID"""
    # Check if user exists
    user_to_follow = db.query(User).filter(User.id == follow_data.user_id).first()
    if not user_to_follow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check if user is trying to follow themselves
    if current_user.id == follow_data.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot follow yourself")
    
    # Check if already following
    existing_follow = db.query(Follower).filter(
        Follower.follower_id == current_user.id,
        Follower.following_id == follow_data.user_id
    ).first()
    
    if existing_follow:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="You are already following this user"
        )
    
    # Create new follow relationship
    new_follow = Follower(
        follower_id=current_user.id,
        following_id=follow_data.user_id
    )
    
    # Update follower and following counts
    follower_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    following_profile = db.query(UserProfile).filter(UserProfile.user_id == follow_data.user_id).first()
    
    if follower_profile:
        follower_profile.following_count += 1
    
    if following_profile:
        following_profile.follower_count += 1
    
    db.add(new_follow)
    db.commit()
    db.refresh(new_follow)
    
    return new_follow

@router.delete("/api/follow/{user_id}", status_code=status.HTTP_204_NO_CONTENT,
             summary="Unfollow a user",
             description="Unfollow a user by their user ID",
             responses={
                 204: {"description": "Successfully unfollowed user"},
                 404: {
                     "description": "User not found or not following this user",
                     "content": {
                         "application/json": {
                             "example": {"detail": "You are not following this user"}
                         }
                     }
                 }
             })
async def unfollow_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Unfollow a user by their user ID"""
    # Check if follow relationship exists
    follow = db.query(Follower).filter(
        Follower.follower_id == current_user.id,
        Follower.following_id == user_id
    ).first()
    
    if not follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="You are not following this user"
        )
    
    # Update follower and following counts
    follower_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    following_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if follower_profile and follower_profile.following_count > 0:
        follower_profile.following_count -= 1
    
    if following_profile and following_profile.follower_count > 0:
        following_profile.follower_count -= 1
    
    # Delete the follow relationship
    db.delete(follow)
    db.commit()
    
    return None

@router.get("/api/users/{user_id}/followers", response_model=FollowListResponse,
          summary="Get user followers",
          description="Get a list of users who follow the specified user",
          responses={
              200: {
                  "description": "List of followers",
                  "content": {
                      "application/json": {
                          "example": {
                              "items": [
                                  {
                                      "id": "123e4567-e89b-12d3-a456-426614174001",
                                      "username": "johndoe",
                                      "display_name": "John Doe",
                                      "avatar_url": "/static/media/avatars/user1.jpg",
                                      "created_at": "2023-01-01T12:00:00Z"
                                  }
                              ],
                              "total": 1,
                              "page": 1, 
                              "limit": 10,
                              "pages": 1
                          }
                      }
                  }
              },
              404: {
                  "description": "User not found",
                  "content": {
                      "application/json": {
                          "example": {"detail": "User not found"}
                      }
                  }
              }
          })
async def get_user_followers(
    user_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get a list of users who follow the specified user"""
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Get total count of followers
    total = db.query(func.count(Follower.id)).filter(Follower.following_id == user_id).scalar()
    
    # Calculate pagination
    pages = math.ceil(total / limit)
    offset = (page - 1) * limit
    
    # Get followers with pagination
    followers = db.query(
        User, UserProfile
    ).join(
        Follower, User.id == Follower.follower_id
    ).outerjoin(
        UserProfile, User.id == UserProfile.user_id
    ).filter(
        Follower.following_id == user_id
    ).order_by(
        Follower.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    # Format the results
    result_items = []
    for user, profile in followers:
        display_name = None
        avatar_url = None
        
        if profile:
            display_name = profile.display_name
            avatar_url = profile.avatar_url
            
        result_items.append(
            FollowerUserResponse(
                id=user.id,
                username=user.username,
                display_name=display_name,
                avatar_url=avatar_url,
                created_at=user.created_at
            )
        )
    
    return FollowListResponse(
        items=result_items,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )

@router.get("/api/users/{user_id}/following", response_model=FollowListResponse,
          summary="Get users followed by a user",
          description="Get a list of users followed by the specified user",
          responses={
              200: {
                  "description": "List of followed users",
                  "content": {
                      "application/json": {
                          "example": {
                              "items": [
                                  {
                                      "id": "123e4567-e89b-12d3-a456-426614174002",
                                      "username": "janedoe",
                                      "display_name": "Jane Doe",
                                      "avatar_url": "/static/media/avatars/user2.jpg",
                                      "created_at": "2023-01-01T12:00:00Z"
                                  }
                              ],
                              "total": 1,
                              "page": 1, 
                              "limit": 10,
                              "pages": 1
                          }
                      }
                  }
              },
              404: {
                  "description": "User not found",
                  "content": {
                      "application/json": {
                          "example": {"detail": "User not found"}
                      }
                  }
              }
          })
async def get_user_following(
    user_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get a list of users followed by the specified user"""
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Get total count of following
    total = db.query(func.count(Follower.id)).filter(Follower.follower_id == user_id).scalar()
    
    # Calculate pagination
    pages = math.ceil(total / limit)
    offset = (page - 1) * limit
    
    # Get following with pagination
    following = db.query(
        User, UserProfile
    ).join(
        Follower, User.id == Follower.following_id
    ).outerjoin(
        UserProfile, User.id == UserProfile.user_id
    ).filter(
        Follower.follower_id == user_id
    ).order_by(
        Follower.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    # Format the results
    result_items = []
    for user, profile in following:
        display_name = None
        avatar_url = None
        
        if profile:
            display_name = profile.display_name
            avatar_url = profile.avatar_url
            
        result_items.append(
            FollowerUserResponse(
                id=user.id,
                username=user.username,
                display_name=display_name,
                avatar_url=avatar_url,
                created_at=user.created_at
            )
        )
    
    return FollowListResponse(
        items=result_items,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )

@router.get("/api/users/{user_id}/is-following/{target_id}", 
          summary="Check if a user is following another",
          description="Check if the specified user is following the target user",
          responses={
              200: {
                  "description": "Following status",
                  "content": {
                      "application/json": {
                          "example": {"is_following": True}
                      }
                  }
              },
              404: {
                  "description": "User not found",
                  "content": {
                      "application/json": {
                          "example": {"detail": "User not found"}
                      }
                  }
              }
          })
async def check_following_status(
    user_id: UUID,
    target_id: UUID,
    db: Session = Depends(get_db)
):
    """Check if a user is following another user"""
    # Check if both users exist
    user = db.query(User).filter(User.id == user_id).first()
    target = db.query(User).filter(User.id == target_id).first()
    
    if not user or not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check following status
    is_following = db.query(Follower).filter(
        Follower.follower_id == user_id,
        Follower.following_id == target_id
    ).first() is not None
    
    return {"is_following": is_following} 