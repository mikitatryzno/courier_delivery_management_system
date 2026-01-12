from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.core.security import verify_token, extract_user_id_from_token
from src.models.user import User, UserRole
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # Verify token
        payload = verify_token(token, "access")
        
        # Extract user ID
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user from database
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Log successful authentication
        logger.debug(f"User authenticated: {user.email} (ID: {user.id})")
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get the current user if authenticated, otherwise return None."""
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None

def require_role(required_role: UserRole):
    """Decorator to require a specific user role."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            logger.warning(f"Access denied for user {current_user.email}: required {required_role}, has {current_user.role}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role.value}"
            )
        return current_user
    return role_checker

def require_roles(required_roles: List[UserRole]):
    """Decorator to require one of multiple user roles."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles and current_user.role != UserRole.ADMIN:
            logger.warning(f"Access denied for user {current_user.email}: required one of {required_roles}, has {current_user.role}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in required_roles]}"
            )
        return current_user
    return role_checker

def require_admin():
    """Decorator to require admin role."""
    return require_role(UserRole.ADMIN)

def require_courier():
    """Decorator to require courier role."""
    return require_role(UserRole.COURIER)

def require_sender():
    """Decorator to require sender role."""
    return require_role(UserRole.SENDER)

def require_recipient():
    """Decorator to require recipient role."""
    return require_role(UserRole.RECIPIENT)

def require_authenticated():
    """Decorator to require any authenticated user."""
    def auth_checker(current_user: User = Depends(get_current_user)) -> User:
        return current_user
    return auth_checker

class AuthenticationError(Exception):
    """Custom authentication error."""
    def __init__(self, message: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthorizationError(Exception):
    """Custom authorization error."""
    def __init__(self, message: str, status_code: int = status.HTTP_403_FORBIDDEN):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)