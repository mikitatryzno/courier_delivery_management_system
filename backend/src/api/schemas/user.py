from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from src.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    role: UserRole
    phone: Optional[str] = Field(None, max_length=20)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None

class UserRoleUpdate(BaseModel):
    role: UserRole = Field(..., description="New role for the user")

class UserStatusUpdate(BaseModel):
    is_active: bool = Field(..., description="User active status")

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    skip: int
    limit: int

class UserSearchResponse(BaseModel):
    users: List[UserResponse]
    search_term: str
    total_found: int

class UserStatsResponse(BaseModel):
    total_users: int
    users_by_role: dict
    recent_registrations: int
    roles_available: List[str]

# Token-related schemas (already defined but included for completeness)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until expiration
    user: UserResponse

class TokenRefresh(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=100)

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6, max_length=100)

class TokenInfo(BaseModel):
    """Token information for debugging/admin purposes."""
    user_id: int
    email: str
    role: str
    issued_at: datetime
    expires_at: datetime
    token_type: str
    is_expired: bool