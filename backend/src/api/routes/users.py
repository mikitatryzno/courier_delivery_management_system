"""User management routes for all roles."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.models.user import User, UserRole
from src.api.schemas.user import (
    UserResponse, 
    UserCreate, 
    UserUpdate,
    UserListResponse,
    UserRoleUpdate,
    UserStatusUpdate
)
from src.api.middleware.auth import (
    get_current_user,
    require_admin,
    require_roles,
    require_authenticated
)
from src.services.user_service import UserService
from src.api.schemas.openapi import OPENAPI_RESPONSES
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

@router.get(
    "/",
    response_model=List[UserResponse],
    summary="List Users",
    description="Get list of users (Admin only)",
    responses={
        200: {
            "description": "List of users retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "email": "admin@example.com",
                            "name": "Admin User",
                            "role": "admin",
                            "phone": "+1234567890",
                            "created_at": "2024-01-01T10:00:00Z",
                            "updated_at": "2024-01-01T10:00:00Z"
                        }
                    ]
                }
            }
        },
        **OPENAPI_RESPONSES
    }
)
def list_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of users to return"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    """
    Get list of users with pagination and filtering.
    
    **Admin only endpoint**
    
    - **skip**: Number of users to skip for pagination
    - **limit**: Maximum number of users to return (1-100)
    - **role**: Filter users by role (admin, courier, sender, recipient)
    - **search**: Search users by name or email
    """
    try:
        user_service = UserService(db)
        users = user_service.get_users(
            skip=skip,
            limit=limit,
            role=role,
            search=search
        )
        
        logger.info(f"Admin {current_user.email} retrieved {len(users)} users")
        return [UserResponse.model_validate(user) for user in users]
        
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User Profile",
    description="Get current user's profile information"
)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile information.
    
    Returns detailed information about the authenticated user.
    """
    return UserResponse.model_validate(current_user)

@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update Current User Profile",
    description="Update current user's profile information"
)
def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile information.
    
    Users can update their own:
    - **name**: Full name
    - **phone**: Phone number
    - **email**: Email address (must be unique)
    
    Note: Role and password cannot be changed through this endpoint.
    """
    try:
        user_service = UserService(db)
        updated_user = user_service.update_user_profile(current_user.id, user_update)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update profile"
            )
        
        logger.info(f"User {current_user.email} updated their profile")
        return UserResponse.model_validate(updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get User by ID",
    description="Get user information by ID (Admin or own profile)"
)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user information by ID.
    
    - **Admins**: Can view any user
    - **Other users**: Can only view their own profile
    """
    try:
        # Check permissions
        if current_user.role != UserRole.ADMIN and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Can only view own profile"
            )
        
        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.model_validate(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )

@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update User",
    description="Update user information (Admin only)"
)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    """
    Update user information.
    
    **Admin only endpoint**
    
    - **name**: Update user's full name
    - **phone**: Update user's phone number
    - **email**: Update user's email (must be unique)
    """
    try:
        user_service = UserService(db)
        updated_user = user_service.update_user_profile(user_id, user_update)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"Admin {current_user.email} updated user {user_id}")
        return UserResponse.model_validate(updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@router.put(
    "/{user_id}/role",
    response_model=UserResponse,
    summary="Update User Role",
    description="Update user role (Admin only)"
)
def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    """
    Update user role.
    
    **Admin only endpoint**
    
    - **role**: New role for the user (admin, courier, sender, recipient)
    
    Note: Be careful when changing admin roles.
    """
    try:
        user_service = UserService(db)
        updated_user = user_service.update_user_role(user_id, role_update.role)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"Admin {current_user.email} changed user {user_id} role to {role_update.role}")
        return UserResponse.model_validate(updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id} role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role"
        )

@router.delete(
    "/{user_id}",
    summary="Delete User",
    description="Delete user account (Admin only)"
)
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    """
    Delete user account.
    
    **Admin only endpoint**
    
    **Warning**: This action cannot be undone. All user data will be permanently deleted.
    
    Note: Cannot delete your own admin account.
    """
    try:
        # Prevent admin from deleting themselves
        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        user_service = UserService(db)
        success = user_service.delete_user(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"Admin {current_user.email} deleted user {user_id}")
        return {"message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

@router.get(
    "/role/{role}",
    response_model=List[UserResponse],
    summary="Get Users by Role",
    description="Get users filtered by role"
)
def get_users_by_role(
    role: UserRole,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.COURIER])),
    db: Session = Depends(get_db)
):
    """
    Get users filtered by role.
    
    **Admin and Courier access**
    
    - **role**: User role to filter by
    - **skip**: Number of users to skip
    - **limit**: Maximum number of users to return
    
    Useful for:
    - Admins: Managing users by role
    - Couriers: Finding senders/recipients for coordination
    """
    try:
        user_service = UserService(db)
        users = user_service.get_users_by_role(role, skip=skip, limit=limit)
        
        logger.info(f"User {current_user.email} retrieved {len(users)} users with role {role}")
        return [UserResponse.model_validate(user) for user in users]
        
    except Exception as e:
        logger.error(f"Error getting users by role {role}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )

@router.get(
    "/stats/summary",
    summary="Get User Statistics",
    description="Get user statistics summary (Admin only)"
)
def get_user_stats(
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    """
    Get user statistics summary.
    
    **Admin only endpoint**
    
    Returns statistics about users by role and registration trends.
    """
    try:
        user_service = UserService(db)
        stats = user_service.get_user_statistics()
        
        logger.info(f"Admin {current_user.email} retrieved user statistics")
        return stats
        
    except Exception as e:
        logger.error(f"Error getting user statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user statistics"
        )