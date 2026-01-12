"""JWT token utilities and helpers."""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)

class JWTManager:
    """JWT token management utilities."""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.debug(f"Created access token for user: {data.get('sub')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Failed to create access token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create access token"
            )
    
    def create_refresh_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            # Refresh tokens last longer (7 days by default)
            expire = datetime.utcnow() + timedelta(days=7)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.debug(f"Created refresh token for user: {data.get('sub')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Failed to create refresh token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create refresh token"
            )
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {token_type}"
                )
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            logger.debug(f"Verified {token_type} token for user: {payload.get('sub')}")
            return payload
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    def decode_token_without_verification(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode token without verification (for debugging/logging)."""
        try:
            return jwt.get_unverified_claims(token)
        except Exception as e:
            logger.error(f"Failed to decode token: {e}")
            return None
    
    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """Get token expiry time."""
        try:
            payload = self.decode_token_without_verification(token)
            if payload and "exp" in payload:
                return datetime.fromtimestamp(payload["exp"])
            return None
        except Exception as e:
            logger.error(f"Failed to get token expiry: {e}")
            return None
    
    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired."""
        try:
            expiry = self.get_token_expiry(token)
            if expiry:
                return datetime.utcnow() > expiry
            return True
        except Exception:
            return True

# Global JWT manager instance
jwt_manager = JWTManager()