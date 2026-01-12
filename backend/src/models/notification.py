from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.core.database import Base
import enum


class NotificationType(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ALERT = "alert"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    message = Column(Text, nullable=False)
    type = Column(Enum(NotificationType), default=NotificationType.INFO)
    read = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="notifications")
