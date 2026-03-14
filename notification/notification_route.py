from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.dependencies import CreateSession
from inventory.inventory_model import Notification
from users.users_model import User
from core.security import verify_token


notification_router = APIRouter(prefix="/notification", tags=["notification"])

@notification_router.get("/notifications")
def get_notifications(session: Session = Depends(CreateSession), user: User = Depends(verify_token)):

    notifications = session.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.created_at.desc()).all()

    return notifications


@notification_router.patch("/notifications/{notification_id}")
def mark_notification_read(notification_id: int, session: Session = Depends(CreateSession)):

    notification = session.query(Notification).filter(Notification.id == notification_id).first()

    notification.is_read = True
    session.commit()

    return {"message": "Notification marked as read"}


@notification_router.get("/notifications/unread-count")
def unread_notifications(session: Session = Depends(CreateSession), user: User = Depends(verify_token)):

    count = session.query(Notification).filter(Notification.user_id == user.id,Notification.is_read == False).count()

    return {"unread": count}