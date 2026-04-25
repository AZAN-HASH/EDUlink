from ..extensions import db, socketio
from ..models import Notification


def create_notification(user_id, actor_id, event_type, message, entity_type=None, entity_id=None, commit=True):
    notification = Notification(
        user_id=user_id,
        actor_id=actor_id,
        event_type=event_type,
        message=message,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    db.session.add(notification)
    if commit:
        db.session.commit()

    socketio.emit("notification", notification.to_dict(), room=f"user_{user_id}")
    socketio.emit("notification_count", {"count": unread_count(user_id)}, room=f"user_{user_id}")
    return notification


def unread_count(user_id):
    return Notification.query.filter_by(user_id=user_id, is_read=False).count()
