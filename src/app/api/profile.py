from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..services.database import get_db
from ..services.auth import get_current_user, get_current_admin_user
from ..services.crud import get_profile, update_profile, get_user_by_id, get_user_posts
from ..models.model import User
from ..schemas.schema import ProfileResponse, ProfileUpdate, PostResponse

router = APIRouter(
    prefix="/api/profiles",
    tags=["profiles"],
    responses={404: {"description": "Not found"}}
)

@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the profile of the currently authenticated user.
    """
    return get_profile(db, current_user.id)

@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the profile of the currently authenticated user.
    """
    return update_profile(db, current_user.id, profile_data.model_dump(exclude_unset=True))

@router.get("/{user_id}", response_model=ProfileResponse)
async def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a user's profile by user ID.
    """
    # Check if user exists
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get profile
    return get_profile(db, user_id)

@router.get("/{user_id}/posts", response_model=List[PostResponse])
async def get_user_profile_posts(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all posts by a specific user, accessed via their profile.
    """
    # Check if user exists
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get posts
    return get_user_posts(db, user_id, skip=skip, limit=limit)

@router.put("/{user_id}", response_model=ProfileResponse)
async def update_user_profile_admin(
    user_id: str,
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to update any user's profile.
    Requires admin privileges.
    """
    # Check if user exists
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update profile
    return update_profile(db, user_id, profile_data.model_dump(exclude_unset=True)) 