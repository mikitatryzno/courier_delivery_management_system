from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    
    # Database - Development (SQLite)
    sqlite_database_url: str = "sqlite:///./courier_delivery.db"
    sqlite_database_url_async: str = "sqlite+aiosqlite:///./courier_delivery.db"
    
    # Database - Production (PostgreSQL)
    postgres_server: str = "localhost"
    postgres_user: str = "courier_user"
    postgres_password: str = "courier_password"
    postgres_db: str = "courier_delivery"
    postgres_port: int = 5432
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API
    api_v1_str: str = "/api"
    project_name: str = "Courier Delivery Management System"
    
    # CORS
    backend_cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    @property
    def database_url(self) -> str:
        """Get database URL based on environment."""
        if self.environment == "production":
            return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
        else:
            return self.sqlite_database_url
    
    @property
    def database_url_async(self) -> str:
        """Get async database URL based on environment."""
        if self.environment == "production":
            return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
        else:
            return self.sqlite_database_url_async
    
    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return "sqlite" in self.database_url
    
    @property
    def is_postgres(self) -> bool:
        """Check if using PostgreSQL database."""
        return "postgresql" in self.database_url
    
    class Config:
        env_file = ".env"

settings = Settings()