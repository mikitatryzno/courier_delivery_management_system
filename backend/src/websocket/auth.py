"""WebSocket authentication utilities."""
import logging
from typing import Optional
from fastapi import WebSocket, status
from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.core.security import verify_token
from src.models.user import User

logger = logging.getLogger(__name__)

async def authenticate_websocket(websocket: WebSocket, token: str) -> Optional[User]:
    """Authenticate WebSocket connection using JWT token."""
    try:
        # Verify token
        payload = verify_token(token, "access")
        
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("WebSocket auth failed: Invalid token payload")
            return None
        
        # Get user from database
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == int(user_id)).first()
            if not user:
                logger.warning(f"WebSocket auth failed: User not found for ID {user_id}")
                return None
            
            logger.debug(f"WebSocket authenticated: {user.email}")
            return user
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        return None

async def close_websocket_with_error(websocket: WebSocket, code: int, reason: str):
    """Close WebSocket connection with error code and reason."""
    try:
        await websocket.close(code=code, reason=reason)
    except Exception as e:
        logger.error(f"Error closing WebSocket: {e}")