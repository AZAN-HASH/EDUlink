from flask import Blueprint
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models import Club, Notification, Post, School, User
from ..utils.decorators import role_required
from ..utils.response import error_response, success_response

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.get("/overview")
@jwt_required()
@role_required("admin")
def overview():
    try:
        return success_response(
            {
                "user_count": User.query.count(),
                "school_count": School.query.count(),
                "club_count": Club.query.count(),
                "post_count": Post.query.count(),
                "notification_count": Notification.query.count(),
            }
        )
    except Exception as exc:
        return error_response(str(exc), 500)


@admin_bp.delete("/users/<int:user_id>")
@jwt_required()
@role_required("admin")
def delete_user(user_id):
    try:
        user = db.session.get(User, user_id)
        if not user:
            return error_response("User not found.", 404)
        db.session.delete(user)
        db.session.commit()
        return success_response(message="User deleted.")
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)


@admin_bp.delete("/posts/<int:post_id>")
@jwt_required()
@role_required("admin")
def delete_any_post(post_id):
    try:
        post = db.session.get(Post, post_id)
        if not post:
            return error_response("Post not found.", 404)
        db.session.delete(post)
        db.session.commit()
        return success_response(message="Post removed.")
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)
