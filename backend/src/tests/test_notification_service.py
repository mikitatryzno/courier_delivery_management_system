from src.services.notification_service import NotificationService
from src.models.notification import NotificationType
from src.models.user import User, UserRole


def test_create_list_mark_notification(db_session):
    # create user
    user = User(email="nuser@example.com", name="N", hashed_password="x", role=UserRole.SENDER)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    service = NotificationService(db_session)

    notif = service.create_notification(user.id, "Hello", NotificationType.INFO)
    assert notif is not None
    assert notif.user_id == user.id

    notifs = service.list_for_user(user.id)
    assert isinstance(notifs, list)
    assert len(notifs) >= 1

    ok = service.mark_read(notif.id)
    assert ok is True
