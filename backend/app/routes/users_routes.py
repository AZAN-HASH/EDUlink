from marshmallow import ValidationError

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import HTTPException

from ..extensions import db
from ..models import Follow, School, User
from ..schemas.user import UserUpdateSchema
from ..services.notification_service import create_notification
from ..utils.decorators import get_current_user
from ..utils.response import error_response, success_response
from ..utils.validators import sanitize_text

users_bp = Blueprint("users", __name__, url_prefix="/users")
user_update_schema = UserUpdateSchema()


@users_bp.get("")
def list_users():
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return success_response([user.to_dict() for user in users])
    except Exception as exc:
        return error_response(str(exc), 500)


@users_bp.get("/me")
@jwt_required()
def get_me():
    user = get_current_user()
    if not user:
        return error_response("User not found.", 404)
    return success_response(user.to_dict(include_private=True))


@users_bp.get("/<int:user_id>")
def get_user(user_id):
    try:
        user = db.session.get(User, user_id)
        if not user:
            return error_response("User not found.", 404)
        return success_response(user.to_dict())
    except HTTPException as exc:
        return error_response(exc.description, exc.code)
    except Exception as exc:
        return error_response(str(exc), 500)


@users_bp.put("/<int:user_id>")
@jwt_required()
def update_user(user_id):
    try:
        current_user = get_current_user()
        if not current_user:
            return error_response("User not found.", 404)
        if current_user.id != user_id and current_user.role != "admin":
            return error_response("Unauthorized.", 403)

        user = db.session.get(User, user_id)
        if not user:
            return error_response("User not found.", 404)
        data = user_update_schema.load(request.get_json() or {})

        if data.get("username") and data["username"] != user.username:
            duplicate = User.query.filter(User.username == data["username"], User.id != user.id).first()
            if duplicate:
                return error_response("Username already in use.", 409)
            user.username = sanitize_text(data["username"])

        if data.get("school"):
            school_name = sanitize_text(data["school"])
            school = School.query.filter(db.func.lower(School.name) == school_name.lower()).first()
            if not school:
                school = School(name=school_name, created_by_id=current_user.id, location=user.location)
                db.session.add(school)
                db.session.flush()
            user.school = school
            user.school_name = school.name

        if data.get("bio") is not None:
            user.bio = sanitize_text(data["bio"])
        if data.get("location"):
            user.location = sanitize_text(data["location"])
        if data.get("profile_picture") is not None:
            user.profile_picture = sanitize_text(data["profile_picture"])
        if data.get("role") and current_user.role == "admin":
            user.role = data["role"]

        db.session.commit()
        return success_response(user.to_dict(include_private=True), "Profile updated.")
    except ValidationError as exc:
        return error_response("Validation failed.", 422, exc.messages)
    except HTTPException as exc:
        return error_response(exc.description, exc.code)
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)


@users_bp.post("/<int:user_id>/follow")
@jwt_required()
def follow_user(user_id):
    try:
        current_user = get_current_user()
        if not current_user:
            return error_response("User not found.", 404)
        if current_user.id == user_id:
            return error_response("You cannot follow yourself.", 400)

        target = db.session.get(User, user_id)
        if not target:
            return error_response("User not found.", 404)
        existing = Follow.query.filter_by(follower_id=current_user.id, followed_id=target.id).first()
        if existing:
            return error_response("Already following this user.", 409)

        follow = Follow(follower_id=current_user.id, followed_id=target.id)
        db.session.add(follow)
        db.session.commit()
        create_notification(
            target.id,
            current_user.id,
            "follow",
            f"{current_user.username} started following you.",
            entity_type="user",
            entity_id=current_user.id,
        )
        return success_response(message="User followed successfully.")
    except HTTPException as exc:
        return error_response(exc.description, exc.code)
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)


@users_bp.delete("/<int:user_id>/follow")
@jwt_required()
def unfollow_user(user_id):
    try:
        current_user = get_current_user()
        follow = Follow.query.filter_by(follower_id=current_user.id, followed_id=user_id).first()
        if not follow:
            return error_response("You are not following this user.", 404)
        db.session.delete(follow)
        db.session.commit()
        return success_response(message="User unfollowed successfully.")
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)
