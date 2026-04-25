from flask import Blueprint
from flask_jwt_extended import jwt_required

from ..models import Notification, Post
from ..services.notification_service import unread_count
from ..utils.decorators import get_current_user
from ..utils.response import error_response, success_response

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.get("")
@jwt_required()
def dashboard():
    try:
        current_user = get_current_user()
        recent_posts = (
            Post.query.filter_by(author_id=current_user.id).order_by(Post.created_at.desc()).limit(5).all()
        )
        recent_notifications = (
            Notification.query.filter_by(user_id=current_user.id)
            .order_by(Notification.created_at.desc())
            .limit(5)
            .all()
        )
        return success_response(
            {
                "user": current_user.to_dict(include_private=True),
                "recent_activity": [post.to_dict() for post in recent_posts],
                "joined_clubs": current_user.to_dict()["joined_clubs"],
                "notifications": [item.to_dict() for item in recent_notifications],
                "unread_notifications": unread_count(current_user.id),
            }
        )
    except Exception as exc:
        return error_response(str(exc), 500)
