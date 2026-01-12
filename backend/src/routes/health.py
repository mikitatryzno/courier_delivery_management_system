"""Health check endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.core.database import get_db, check_database_connection
from src.core.config import settings
from src.utils.database_manager import DatabaseManager

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "database_type": "PostgreSQL" if settings.is_postgres else "SQLite"
    }

@router.get("/database")
def database_health_check(db: Session = Depends(get_db)):
    """Database health check."""
    try:
        # Test database connection
        if not check_database_connection():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection failed"
            )
        
        # Test query execution
        result = db.execute(text("SELECT 1")).fetchone()
        if not result or result[0] != 1:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database query failed"
            )
        
        # Get database info
        with DatabaseManager() as db_manager:
            db_info = db_manager.get_database_info()
            table_counts = db_manager.get_table_counts()
        
        return {
            "status": "healthy",
            "database": db_info,
            "table_counts": table_counts
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database health check failed: {str(e)}"
        )

@router.get("/detailed")
def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with database statistics."""
    try:
        with DatabaseManager() as db_manager:
            if not db_manager.check_connection():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Database connection failed"
                )
            
            db_info = db_manager.get_database_info()
            table_counts = db_manager.get_table_counts()
            
            return {
                "status": "healthy",
                "timestamp": "2024-01-01T00:00:00Z",  # This would be dynamic
                "environment": settings.environment,
                "database": {
                    "type": db_info["type"] if db_info else "Unknown",
                    "version": db_info["version"] if db_info else "Unknown",
                    "connection": "healthy",
                    "tables": table_counts or {}
                },
                "api": {
                    "version": "1.0.0",
                    "endpoints": "operational"
                }
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )