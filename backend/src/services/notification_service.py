from typing import Optional, List
from sqlalchemy.orm import Session
from src.models.notification import Notification
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(self, user_id: Optional[int], message: str, ntype) -> Optional[Notification]:
        notif = Notification(user_id=user_id, message=message, type=ntype)
        try:
            self.db.add(notif)
            self.db.commit()
            self.db.refresh(notif)
            return notif
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            self.db.rollback()
            return None

    def mark_read(self, notification_id: int) -> bool:
        notif = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if not notif:
            return False
        notif.read = True
        try:
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def list_for_user(self, user_id: int) -> List[Notification]:
        return self.db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()
