from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import StaticPool
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Database engine configuration based on database type
if settings.is_sqlite:
    # SQLite configuration
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.environment == "development"
    )
    
    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
        
else:
    # PostgreSQL configuration
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=settings.environment == "development"
    )

# Session configuration
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async database setup
if settings.is_sqlite:
    async_engine = create_async_engine(
        settings.database_url_async,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.environment == "development"
    )
else:
    async_engine = create_async_engine(
        settings.database_url_async,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=settings.environment == "development"
    )

AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Database health check
def check_database_connection():
    """Check if database connection is working."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info(f"Database connection successful: {settings.database_url}")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

# Initialize database tables
def create_tables():
    """Create all database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

# Drop all tables (for testing/reset)
def drop_tables():
    """Drop all database tables."""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise