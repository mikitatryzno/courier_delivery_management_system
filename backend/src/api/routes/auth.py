from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.core.security import (
    verify_password, 
    create_access_token, 
    create_refresh_token,
    get_password_hash,
    verify_token,
    is_token_expired
)
from src.core.config import settings
from src.models.user import User
from src.api.schemas.user import (
    UserLogin, 
    Token, 
    UserResponse, 
    UserCreate,
    TokenRefresh,
    RefreshTokenResponse,
    PasswordChange,
    TokenInfo
)
from src.api.middleware.auth import get_current_user, get_current_user_optional
from src.api.schemas.openapi import (
    EXAMPLE_USER_LOGIN,
    EXAMPLE_TOKEN_RESPONSE,
    EXAMPLE_USER_CREATE,
    EXAMPLE_USER_RESPONSE,
    OPENAPI_RESPONSES
)
from src.utils.jwt_utils import jwt_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post(
    "/login", 
    response_model=Token,
    summary="User Login",
    description="Authenticate user with email and password to receive access token",
    responses={
        200: {
            "description": "Successful authentication",
            "content": {
                "application/json": {
                    "example": EXAMPLE_TOKEN_RESPONSE
                }
            }
        },
        **OPENAPI_RESPONSES
    }
)
def login(
    user_credentials: UserLogin = Body(
        ...,
        example=EXAMPLE_USER_LOGIN,
        description="User login credentials"
    ),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access token.
    
    - **email**: Valid email address
    - **password**: User password
    
    Returns JWT access token and user information.
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == user_credentials.email).first()
        
        if not user or not verify_password(user_credentials.password, user.hashed_password):
            logger.warning(f"Failed login attempt for email: {user_credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.value}, 
            expires_delta=access_token_expires
        )
        
        # Create refresh token
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        logger.info(f"User logged in successfully: {user.email}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserResponse.model_validate(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post(
    "/register", 
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="User Registration",
    description="Register a new user account",
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": EXAMPLE_USER_RESPONSE
                }
            }
        },
        400: {
            "description": "Email already registered",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already registered"}
                }
            }
        },
        **OPENAPI_RESPONSES
    }
)
def register(
    user_data: UserCreate = Body(
        ...,
        example=EXAMPLE_USER_CREATE,
        description="User registration data"
    ),
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    - **email**: Valid email address (must be unique)
    - **name**: Full name of the user
    - **password**: Password (minimum 6 characters)
    - **role**: User role (admin, courier, sender, recipient)
    - **phone**: Phone number (optional)
    
    Returns the created user information (without password).
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            name=user_data.name,
            hashed_password=hashed_password,
            role=user_data.role,
            phone=user_data.phone
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"New user registered: {db_user.email}")
        
        return UserResponse.model_validate(db_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.get(
    "/me", 
    response_model=UserResponse,
    summary="Get Current User",
    description="Get information about the currently authenticated user",
    responses={
        200: {
            "description": "Current user information",
            "content": {
                "application/json": {
                    "example": EXAMPLE_USER_RESPONSE
                }
            }
        },
        **OPENAPI_RESPONSES
    }
)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    
    Returns detailed information about the authenticated user.
    Requires valid JWT token in Authorization header.
    """
    return UserResponse.model_validate(current_user)

@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Refresh Access Token",
    description="Get a new access token using refresh token",
    responses={
        200: {
            "description": "New access token generated",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 1800
                    }
                }
            }
        },
        **OPENAPI_RESPONSES
    }
)
def refresh_token(
    token_data: TokenRefresh = Body(
        ...,
        example={"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."},
        description="Refresh token data"
    ),
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token obtained during login
    
    Returns a new access token with extended expiry.
    """
    try:
        # Verify refresh token
        payload = verify_token(token_data.refresh_token, "refresh")
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user from database
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        logger.info(f"Token refreshed for user: {user.email}")
        
        return RefreshTokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )

@router.post(
    "/logout",
    summary="User Logout",
    description="Logout user (client should discard tokens)",
    responses={
        200: {
            "description": "Successfully logged out",
            "content": {
                "application/json": {
                    "example": {"message": "Logged out successfully"}
                }
            }
        },
        **OPENAPI_RESPONSES
    }
)
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout user.
    
    This endpoint invalidates the current session.
    Client should discard all stored tokens.
    """
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Logged out successfully"}


@router.get(
    "/token-info",
    response_model=TokenInfo,
    summary="Token Information",
    description="Return decoded token information for the provided access token",
)
def token_info(request: Request):
    """Return information about the provided JWT access token."""
    auth: str | None = request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    token = auth.split(" ", 1)[1]
    payload = verify_token(token, "access")
    issued_at = payload.get("iat")
    expires_at = payload.get("exp")
    return TokenInfo(
        user_id=int(payload.get("sub")) if payload.get("sub") else 0,
        email=payload.get("email", ""),
        role=payload.get("role", ""),
        issued_at=datetime.utcfromtimestamp(issued_at) if issued_at else datetime.utcnow(),
        expires_at=datetime.utcfromtimestamp(expires_at) if expires_at else datetime.utcnow(),
        token_type=payload.get("type", "access"),
        is_expired=is_token_expired(token)
    )


@router.post(
    "/change-password",
    summary="Change Password",
    description="Change password for the authenticated user",
)
def change_password(
    payload: PasswordChange = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change the password for the authenticated user."""
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect current password")

    try:
        new_hashed = get_password_hash(payload.new_password)
        current_user.hashed_password = new_hashed
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        return {"message": "Password changed successfully"}
    except Exception as e:
        logger.error(f"Password change failed: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to change password")


@router.get(
    "/validate",
    summary="Validate Token",
    description="Validate provided access token and return status",
)
def validate_token(request: Request):
    """Validate the provided access token; return 200 if valid."""
    auth: str | None = request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    token = auth.split(" ", 1)[1]
    # verify_token will raise HTTPException on failure and return payload
    payload = verify_token(token, "access")
    issued_at = payload.get("iat")
    expires_at = payload.get("exp")
    return {
        "valid": True,
        "user_id": int(payload.get("sub")) if payload.get("sub") else None,
        "email": payload.get("email"),
        "role": payload.get("role"),
        "issued_at": datetime.utcfromtimestamp(issued_at) if issued_at else None,
        "expires_at": datetime.utcfromtimestamp(expires_at) if expires_at else None,
        "token_type": payload.get("type", "access"),
        "is_expired": is_token_expired(token)
    }