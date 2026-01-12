"""Initialize database with sample data."""
from sqlalchemy.orm import Session
from src.core.database import SessionLocal, engine, Base
from src.models.user import User, UserRole
from src.models.package import Package, PackageStatus
from src.core.security import get_password_hash

def init_db():
    """Initialize database with sample data."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin_user:
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
                db.add(user)
                db.flush()  # Get the ID without committing
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
                db.add(package)
            
            db.commit()
            print("Database initialized with sample data!")
            print("\nSample users created:")
            print("Admin: admin@example.com / admin123")
            print("Courier: courier@example.com / courier123")
            print("Sender: sender@example.com / sender123")
            print("Recipient: recipient@example.com / recipient123")
        else:
            print("Database already initialized!")
    
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()