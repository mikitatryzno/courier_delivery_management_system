from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.api.schemas.notification import NotificationCreate, NotificationRead
from src.services.notification_service import NotificationService
from src.api.middleware.auth import get_current_user, require_roles
from src.models.user import User, UserRole
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/", response_model=NotificationRead)
def create_notification(payload: NotificationCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles([UserRole.ADMIN]))):
    service = NotificationService(db)
    notif = service.create_notification(payload.user_id, payload.message, payload.type)
    if not notif:
        raise HTTPException(status_code=400, detail="Failed to create notification")
    return NotificationRead.model_validate(notif)


@router.get("/", response_model=List[NotificationRead])
def list_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = NotificationService(db)
    notifs = service.list_for_user(current_user.id)
    return [NotificationRead.model_validate(n) for n in notifs]


@router.put("/{notification_id}/read")
def mark_read(notification_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = NotificationService(db)
    ok = service.mark_read(notification_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"ok": True}
