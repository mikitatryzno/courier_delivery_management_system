from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.core.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    COURIER = "courier"
    SENDER = "sender"
    RECIPIENT = "recipient"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    # Optional free-form permissions (comma-separated or JSON string)
    permissions = Column(Text, nullable=True)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    sent_packages = relationship("Package", foreign_keys="Package.sender_id", back_populates="sender")
    courier_packages = relationship("Package", foreign_keys="Package.courier_id", back_populates="courier")