from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..services.database import get_db
from ..services.auth import get_current_admin_user
from ..services.crud import (
    get_users,
    update_user,
    delete_post,
    get_user_by_id,
    create_moderation_action,
    get_moderation_actions
)
from ..models.model import User
from ..schemas.schema import UserResponse, ModerateAction, ModerationActionResponse

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}}
)

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all users.
    Admin-only endpoint.
    """
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.put("/users/{user_id}/set-active")
async def set_user_active_status(
    user_id: int,
    is_active: bool,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Set a user's active status.
    Admin-only endpoint.
    """
    # Don't allow admin to deactivate themselves
    if user_id == current_user.id and not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user = update_user(db, user_id, is_active=is_active)
    
    # Log moderation action
    action_type = "ACTIVATE_USER" if is_active else "DEACTIVATE_USER"
    create_moderation_action(
        db, 
        admin_id=current_user.id, 
        action_type=action_type, 
        target_user_id=user_id
    )
    
    return {"message": f"User active status set to {is_active}"}

@router.put("/users/{user_id}/set-admin")
async def set_user_admin_status(
    user_id: int,
    is_admin: bool,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Set a user's admin status.
    Admin-only endpoint.
    """
    # Don't allow admin to remove their own admin status
    if user_id == current_user.id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove your own admin status"
        )
    
    user = update_user(db, user_id, is_admin=is_admin)
    
    # Log moderation action
    action_type = "GRANT_ADMIN" if is_admin else "REVOKE_ADMIN"
    create_moderation_action(
        db, 
        admin_id=current_user.id, 
        action_type=action_type, 
        target_user_id=user_id
    )
    
    return {"message": f"User admin status set to {is_admin}"}

@router.delete("/posts/{post_id}")
async def delete_post_admin(
    post_id: int,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a post (admin action).
    Admin-only endpoint.
    """
    result = delete_post(db, post_id, current_user.id, is_admin=True)
    
    # Log moderation action
    create_moderation_action(
        db, 
        admin_id=current_user.id, 
        action_type="DELETE_POST", 
        target_post_id=post_id,
        reason=reason
    )
    
    return {"message": "Post deleted successfully", "reason": reason}

@router.post("/moderate", response_model=ModerationActionResponse)
async def moderate_content(
    action: ModerateAction,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Take a moderation action.
    Admin-only endpoint.
    """
    # Validate action type
    valid_actions = ["DELETE_POST", "BAN_USER", "WARN_USER", "UNBAN_USER"]
    if action.action_type not in valid_actions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action type. Must be one of: {valid_actions}"
        )
    
    # Check target exists based on action type
    if action.action_type.endswith("_USER") and not action.target_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User actions require target_user_id"
        )
    
    if action.action_type.endswith("_POST") and not action.target_post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post actions require target_post_id"
        )
    
    # If banning user, check user exists
    if action.action_type == "BAN_USER" and action.target_user_id:
        user = get_user_by_id(db, action.target_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Ban user (set to inactive)
        update_user(db, action.target_user_id, is_active=False)
    
    # If unbanning user
    if action.action_type == "UNBAN_USER" and action.target_user_id:
        user = get_user_by_id(db, action.target_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Unban user (set to active)
        update_user(db, action.target_user_id, is_active=True)
        
    # Create moderation action record
    moderation_action = create_moderation_action(
        db,
        admin_id=current_user.id,
        action_type=action.action_type,
        target_user_id=action.target_user_id,
        target_post_id=action.target_post_id,
        reason=action.reason
    )
    
    return moderation_action

@router.get("/actions", response_model=List[ModerationActionResponse])
async def get_moderation_action_history(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get history of moderation actions.
    Admin-only endpoint.
    """
    actions = get_moderation_actions(db, skip=skip, limit=limit)
    return actions 