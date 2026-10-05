from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.models import Notification, User

class NotificationService:
    """
    Central cross-portal notification bus for event broadcasts
    (job matches, status changes, interview invitations, workshops, hackathons).
    """

    def send_notification(
        self,
        db: Session,
        user_id: int,
        title: str,
        message: str,
        notification_type: str = "Info",
        action_url: Optional[str] = None
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            action_url=action_url,
            is_read=False
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif

    def broadcast_to_role(
        self,
        db: Session,
        role: str,
        title: str,
        message: str,
        notification_type: str = "Broadcast",
        action_url: Optional[str] = None
    ) -> int:
        users = db.query(User).filter(User.role == role.upper()).all()
        count = 0
        for u in users:
            notif = Notification(
                user_id=u.id,
                title=title,
                message=message,
                notification_type=notification_type,
                action_url=action_url,
                is_read=False
            )
            db.add(notif)
            count += 1
        db.commit()
        return count

    def get_user_notifications(self, db: Session, user_id: int, limit: int = 20) -> List[Notification]:
        return db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).limit(limit).all()

    def mark_as_read(self, db: Session, notification_id: int, user_id: int) -> bool:
        notif = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        if notif:
            notif.is_read = True
            db.commit()
            return True
        return False

    def mark_all_read(self, db: Session, user_id: int) -> int:
        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        db.commit()
        return count

notification_service = NotificationService()
