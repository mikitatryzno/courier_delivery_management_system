from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.core.database import Base
import enum

class PackageStatus(str, enum.Enum):
    CREATED = "created"
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    # Sender information
    sender_name = Column(String, nullable=False)
    sender_phone = Column(String, nullable=False)
    sender_address = Column(Text, nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Recipient information
    recipient_name = Column(String, nullable=False)
    recipient_phone = Column(String, nullable=False)
    recipient_address = Column(Text, nullable=False)
    
    # Delivery information
    status = Column(Enum(PackageStatus), default=PackageStatus.CREATED)
    courier_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    estimated_delivery = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_packages")
    courier = relationship("User", foreign_keys=[courier_id], back_populates="courier_packages")