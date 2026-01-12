"""Database management utilities."""
import logging
from sqlalchemy import text
from src.core.database import engine, SessionLocal, Base, check_database_connection
from src.core.config import settings
from src.models.user import User, UserRole
from src.models.package import Package, PackageStatus
from src.core.security import get_password_hash

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database management operations."""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    def create_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            return False
    
    def drop_tables(self):
        """Drop all database tables."""
        try:
            Base.metadata.drop_all(bind=engine)
            logger.info("Database tables dropped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            return False
    
    def reset_database(self):
        """Reset database by dropping and recreating tables."""
        try:
            self.drop_tables()
            self.create_tables()
            logger.info("Database reset successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            return False
    
    def check_connection(self):
        """Check database connection."""
        return check_database_connection()
    
    def get_database_info(self):
        """Get database information."""
        try:
            with engine.connect() as conn:
                if settings.is_sqlite:
                    result = conn.execute(text("SELECT sqlite_version()"))
                    version = result.fetchone()[0]
                    db_type = "SQLite"
                else:
                    result = conn.execute(text("SELECT version()"))
                    version = result.fetchone()[0]
                    db_type = "PostgreSQL"
                
                return {
                    "type": db_type,
                    "version": version,
                    "url": settings.database_url,
                    "environment": settings.environment
                }
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return None
    
    def seed_sample_data(self):
        """Seed database with sample data."""
        try:
            # Check if data already exists
            existing_user = self.db.query(User).filter(User.email == "admin@example.com").first()
            if existing_user:
                logger.info("Sample data already exists")
                return True
            
            # Create sample users
            users_data = [
                {
                    "email": "admin@example.com",
                    "name": "Admin User",
                    "password": "admin123",
                    "role": UserRole.ADMIN,
                    "phone": "+1234567890"
                },
                {
                    "email": "courier@example.com",
                    "name": "John Courier",
                    "password": "courier123",
                    "role": UserRole.COURIER,
                    "phone": "+1234567891"
                },
                {
                    "email": "sender@example.com",
                    "name": "Alice Sender",
                    "password": "sender123",
                    "role": UserRole.SENDER,
                    "phone": "+1234567892"
                },
                {
                    "email": "recipient@example.com",
                    "name": "Bob Recipient",
                    "password": "recipient123",
                    "role": UserRole.RECIPIENT,
                    "phone": "+1234567893"
                }
            ]
            
            created_users = {}
            for user_data in users_data:
                password = user_data.pop("password")
                hashed_password = get_password_hash(password)
                
                user = User(
                    **user_data,
                    hashed_password=hashed_password
                )
                self.db.add(user)
                self.db.flush()  # Get the ID without committing
                created_users[user_data["role"]] = user
            
            # Create sample packages
            packages_data = [
                {
                    "title": "Important Documents",
                    "description": "Legal documents that need to be delivered urgently",
                    "sender_name": "Alice Sender",
                    "sender_phone": "+1234567892",
                    "sender_address": "123 Sender St, City, State 12345",
                    "recipient_name": "Bob Recipient",
                    "recipient_phone": "+1234567893",
                    "recipient_address": "456 Recipient Ave, City, State 12346",
                    "sender_id": created_users[UserRole.SENDER].id,
                    "status": PackageStatus.CREATED
                },
                {
                    "title": "Electronics Package",
                    "description": "Laptop and accessories for office setup",
                    "sender_name": "Alice Sender",
                    "sender_phone": "+1234567892",
                    "sender_address": "123 Sender St, City, State 12345",
                    "recipient_name": "Charlie Customer",
                    "recipient_phone": "+1234567894",
                    "recipient_address": "789 Customer Blvd, City, State 12347",
                    "sender_id": created_users[UserRole.SENDER].id,
                    "status": PackageStatus.ASSIGNED,
                    "courier_id": created_users[UserRole.COURIER].id
                },
                {
                    "title": "Gift Package",
                    "description": "Birthday gift for family member",
                    "sender_name": "Alice Sender",
                    "sender_phone": "+1234567892",
                    "sender_address": "123 Sender St, City, State 12345",
                    "recipient_name": "Bob Recipient",
                    "recipient_phone": "+1234567893",
                    "recipient_address": "456 Recipient Ave, City, State 12346",
                    "sender_id": created_users[UserRole.SENDER].id,
                    "status": PackageStatus.DELIVERED,
                    "courier_id": created_users[UserRole.COURIER].id
                }
            ]
            
            for package_data in packages_data:
                package = Package(**package_data)
                self.db.add(package)
            
            self.db.commit()
            logger.info("Sample data seeded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to seed sample data: {e}")
            self.db.rollback()
            return False
    
    def get_table_counts(self):
        """Get count of records in each table."""
        try:
            counts = {
                "users": self.db.query(User).count(),
                "packages": self.db.query(Package).count()
            }
            return counts
        except Exception as e:
            logger.error(f"Failed to get table counts: {e}")
            return None
    
    def cleanup_test_data(self):
        """Clean up test data (for testing environments)."""
        try:
            if settings.environment == "production":
                logger.warning("Cannot cleanup data in production environment")
                return False
            
            # Delete test packages
            self.db.query(Package).filter(Package.title.like("Test%")).delete()
            
            # Delete test users (except admin)
            self.db.query(User).filter(
                User.email.like("test%"),
                User.role != UserRole.ADMIN
            ).delete()
            
            self.db.commit()
            logger.info("Test data cleaned up successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup test data: {e}")
            self.db.rollback()
            return False