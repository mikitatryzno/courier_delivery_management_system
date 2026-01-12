from sqlalchemy import Column, Integer, Enum, ForeignKey, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.core.database import Base
import enum


class DeliveryStatus(str, enum.Enum):
    CREATED = "created"
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False)
    courier_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.CREATED)

    # Current location
    current_lat = Column(Float, nullable=True)
    current_lng = Column(Float, nullable=True)
    last_update = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    package = relationship("Package", backref="delivery", uselist=False)
    courier = relationship("User", backref="deliveries")
