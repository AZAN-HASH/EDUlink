from flask import Blueprint
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models import Notification
from ..services.notification_service import unread_count
from ..utils.decorators import get_current_user
from ..utils.response import error_response, success_response

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


@notifications_bp.get("")
@jwt_required()
def list_notifications():
    try:
        current_user = get_current_user()
        notifications = (
            Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
        )
        return success_response(
            {
                "items": [notification.to_dict() for notification in notifications],
                "unread_count": unread_count(current_user.id),
            }
        )
    except Exception as exc:
        return error_response(str(exc), 500)


@notifications_bp.post("/read-all")
@jwt_required()
def mark_all_read():
    try:
        current_user = get_current_user()
        Notification.query.filter_by(user_id=current_user.id, is_read=False).update({"is_read": True})
        db.session.commit()
        return success_response(message="All notifications marked as read.")
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)


@notifications_bp.post("/<int:notification_id>/read")
@jwt_required()
def mark_read(notification_id):
    try:
        current_user = get_current_user()
        notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first()
        if not notification:
            return error_response("Notification not found.", 404)
        notification.is_read = True
        db.session.commit()
        return success_response(notification.to_dict(), "Notification marked as read.")
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)
