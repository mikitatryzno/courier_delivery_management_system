from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.models.notification import NotificationType


class NotificationCreate(BaseModel):
    user_id: Optional[int]
    message: str
    type: Optional[NotificationType] = NotificationType.INFO


class NotificationRead(BaseModel):
    id: int
    user_id: Optional[int]
    message: str
    type: NotificationType
    read: bool
    created_at: datetime

    class Config:
        orm_mode = True
