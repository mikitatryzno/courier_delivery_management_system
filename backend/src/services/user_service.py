"""User service layer for business logic."""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from src.models.user import User, UserRole
from src.api.schemas.user import UserUpdate
from src.core.security import get_password_hash
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Service class for user-related business logic."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_users(
        self,
        skip: int = 0,
        limit: int = 10,
        role: Optional[UserRole] = None,
        search: Optional[str] = None
    ) -> List[User]:
        """Get users with filtering and pagination."""
        try:
            query = self.db.query(User)
            
            # Filter by role
            if role:
                query = query.filter(User.role == role)
            
            # Search by name or email
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        User.name.ilike(search_term),
                        User.email.ilike(search_term)
                    )
                )
            
            # Apply pagination
            users = query.offset(skip).limit(limit).all()
            
            logger.debug(f"Retrieved {len(users)} users with filters: role={role}, search={search}")
            return users
            
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        try:
            return self.db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            return self.db.query(User).filter(User.email == email).first()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    def get_users_by_role(
        self,
        role: UserRole,
        skip: int = 0,
        limit: int = 10
    ) -> List[User]:
        """Get users by role with pagination."""
        try:
            users = (
                self.db.query(User)
                .filter(User.role == role)
                .offset(skip)
                .limit(limit)
                .all()
            )
            
            logger.debug(f"Retrieved {len(users)} users with role {role}")
            return users
            
        except Exception as e:
            logger.error(f"Error getting users by role {role}: {e}")
            return []
    
    def update_user_profile(
        self,
        user_id: int,
        user_update: UserUpdate
    ) -> Optional[User]:
        """Update user profile information."""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            # Check if email is being changed and if it's unique
            if user_update.email and user_update.email != user.email:
                existing_user = self.db.query(User).filter(
                    User.email == user_update.email,
                    User.id != user_id
                ).first()
                
                if existing_user:
                    raise ValueError("Email already in use")
            
            # Update fields
            update_data = user_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(user, field) and value is not None:
                    setattr(user, field, value)
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Updated user {user_id} profile")
            return user
            
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            self.db.rollback()
            return None
    
    def update_user_role(self, user_id: int, new_role: UserRole) -> Optional[User]:
        """Update user role."""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            old_role = user.role
            user.role = new_role
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Updated user {user_id} role from {old_role} to {new_role}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating user {user_id} role: {e}")
            self.db.rollback()
            return None
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user account."""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Store user info for logging before deletion
            user_email = user.email
            
            self.db.delete(user)
            self.db.commit()
            
            logger.info(f"Deleted user {user_id} ({user_email})")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            self.db.rollback()
            return False
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics."""
        try:
            # Count users by role
            role_counts = (
                self.db.query(User.role, func.count(User.id))
                .group_by(User.role)
                .all()
            )
            
            role_stats = {role.value: count for role, count in role_counts}
            
            # Total users
            total_users = self.db.query(User).count()
            
            # Recent registrations (last 30 days)
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_registrations = (
                self.db.query(User)
                .filter(User.created_at >= thirty_days_ago)
                .count()
            )
            
            stats = {
                "total_users": total_users,
                "users_by_role": role_stats,
                "recent_registrations": recent_registrations,
                "roles_available": [role.value for role in UserRole]
            }
            
            logger.debug("Generated user statistics")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            return {
                "total_users": 0,
                "users_by_role": {},
                "recent_registrations": 0,
                "roles_available": [role.value for role in UserRole]
            }
    
    def search_users(self, search_term: str, limit: int = 10) -> List[User]:
        """Search users by name or email."""
        try:
            search_pattern = f"%{search_term}%"
            users = (
                self.db.query(User)
                .filter(
                    or_(
                        User.name.ilike(search_pattern),
                        User.email.ilike(search_pattern)
                    )
                )
                .limit(limit)
                .all()
            )
            
            logger.debug(f"Found {len(users)} users matching '{search_term}'")
            return users
            
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return []
    
    def get_active_couriers(self) -> List[User]:
        """Get list of active couriers."""
        try:
            couriers = (
                self.db.query(User)
                .filter(User.role == UserRole.COURIER)
                .all()
            )
            
            logger.debug(f"Retrieved {len(couriers)} active couriers")
            return couriers
            
        except Exception as e:
            logger.error(f"Error getting active couriers: {e}")
            return []
    
    def validate_user_permissions(
        self,
        user: User,
        required_roles: List[UserRole]
    ) -> bool:
        """Validate if user has required permissions."""
        try:
            # Admin has access to everything
            if user.role == UserRole.ADMIN:
                return True
            
            # Check if user role is in required roles
            return user.role in required_roles
            
        except Exception as e:
            logger.error(f"Error validating permissions for user {user.id}: {e}")
            return False