from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database.db import get_db
from app.models.models import User
from app.auth.auth import get_current_user
from app.services.notification_service import notification_service

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

@router.get("")
def get_my_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notifs = notification_service.get_user_notifications(db=db, user_id=current_user.id, limit=30)
    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "notification_type": n.notification_type,
            "action_url": n.action_url,
            "is_read": n.is_read,
            "created_at": n.created_at.strftime("%d %b %Y, %I:%M %p")
        }
        for n in notifs
    ]

@router.post("/{notification_id}/read")
def mark_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = notification_service.mark_as_read(db=db, notification_id=notification_id, user_id=current_user.id)
    return {"success": success}

@router.post("/read-all")
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    count = notification_service.mark_all_read(db=db, user_id=current_user.id)
    return {"marked_count": count}
