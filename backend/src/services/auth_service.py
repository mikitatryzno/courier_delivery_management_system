"""Authentication service layer."""
from typing import Optional, Tuple
from datetime import timedelta
from sqlalchemy.orm import Session
from src.models.user import User, UserRole
from src.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token
)
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service for handling user authentication operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        try:
            user = self.db.query(User).filter(User.email == email).first()
            
            if not user:
                logger.warning(f"Authentication failed: User not found for email {email}")
                return None
            
            if not verify_password(password, user.hashed_password):
                logger.warning(f"Authentication failed: Invalid password for email {email}")
                return None
            
            logger.info(f"User authenticated successfully: {email}")
            return user
            
        except Exception as e:
            logger.error(f"Authentication error for {email}: {e}")
            return None
    
    def create_user_tokens(self, user: User) -> Tuple[str, str, int]:
        """Create access and refresh tokens for user."""
        try:
            # Create access token
            access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
            access_token = create_access_token(
                data={
                    "sub": str(user.id),
                    "email": user.email,
                    "role": user.role.value
                },
                expires_delta=access_token_expires
            )
            
            # Create refresh token
            refresh_token = create_refresh_token(
                data={
                    "sub": str(user.id),
                    "email": user.email
                }
            )
            
            expires_in = settings.access_token_expire_minutes * 60  # Convert to seconds
            
            logger.debug(f"Tokens created for user: {user.email}")
            return access_token, refresh_token, expires_in
            
        except Exception as e:
            logger.error(f"Token creation error for user {user.email}: {e}")
            raise
    
    def refresh_user_token(self, refresh_token: str) -> Optional[Tuple[str, int]]:
        """Refresh access token using refresh token."""
        try:
            # Verify refresh token
            payload = verify_token(refresh_token, "refresh")
            
            user_id = payload.get("sub")
            if not user_id:
                logger.warning("Invalid refresh token: missing user ID")
                return None
            
            # Get user from database
            user = self.db.query(User).filter(User.id == int(user_id)).first()
            if not user:
                logger.warning(f"Refresh token error: User not found for ID {user_id}")
                return None
            
            # Create new access token
            access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
            access_token = create_access_token(
                data={
                    "sub": str(user.id),
                    "email": user.email,
                    "role": user.role.value
                },
                expires_delta=access_token_expires
            )
            
            expires_in = settings.access_token_expire_minutes * 60
            
            logger.info(f"Token refreshed for user: {user.email}")
            return access_token, expires_in
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return None
    
    def register_user(
        self,
        email: str,
        name: str,
        password: str,
        role: UserRole,
        phone: Optional[str] = None
    ) -> Optional[User]:
        """Register a new user."""
        try:
            # Check if user already exists
            existing_user = self.db.query(User).filter(User.email == email).first()
            if existing_user:
                logger.warning(f"Registration failed: Email already exists {email}")
                return None
            
            # Create new user
            hashed_password = get_password_hash(password)
            user = User(
                email=email,
                name=name,
                hashed_password=hashed_password,
                role=role,
                phone=phone
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"New user registered: {email}")
            return user
            
        except Exception as e:
            logger.error(f"Registration error for {email}: {e}")
            self.db.rollback()
            return None
    
    def change_user_password(self, user: User, current_password: str, new_password: str) -> bool:
        """Change user password."""
        try:
            # Verify current password
            if not verify_password(current_password, user.hashed_password):
                logger.warning(f"Password change failed: Invalid current password for {user.email}")
                return False
            
            # Update password
            user.hashed_password = get_password_hash(new_password)
            self.db.commit()
            
            logger.info(f"Password changed for user: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Password change error for {user.email}: {e}")
            self.db.rollback()
            return False
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        try:
            return self.db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            return self.db.query(User).filter(User.email == email).first()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    def validate_user_permissions(self, user: User, required_roles: list[UserRole]) -> bool:
        """Validate if user has required permissions."""
        try:
            # Admin has access to everything
            if user.role == UserRole.ADMIN:
                return True
            
            # Check if user role is in required roles
            return user.role in required_roles
            
        except Exception as e:
            logger.error(f"Permission validation error for {user.email}: {e}")
            return False