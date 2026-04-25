from marshmallow import ValidationError

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from ..models import ClubMessage, DirectMessageThread
from ..schemas.chat import MessageSchema
from ..services.chat_service import get_or_create_thread, send_direct_message
from ..utils.decorators import get_current_user
from ..utils.response import error_response, success_response

chat_bp = Blueprint("chat", __name__, url_prefix="/chats")
message_schema = MessageSchema()


@chat_bp.get("/threads")
@jwt_required()
def list_threads():
    try:
        current_user = get_current_user()
        threads = DirectMessageThread.query.filter(
            (DirectMessageThread.participant_one_id == current_user.id)
            | (DirectMessageThread.participant_two_id == current_user.id)
        ).all()
        return success_response([thread.to_dict() for thread in threads])
    except Exception as exc:
        return error_response(str(exc), 500)


@chat_bp.get("/threads/<int:user_id>")
@jwt_required()
def get_thread(user_id):
    try:
        current_user = get_current_user()
        thread = get_or_create_thread(current_user.id, user_id)
        return success_response(thread.to_dict())
    except Exception as exc:
        return error_response(str(exc), 500)


@chat_bp.post("/threads/<int:user_id>/messages")
@jwt_required()
def create_direct_message(user_id):
    try:
        current_user = get_current_user()
        data = message_schema.load(request.get_json() or {})
        message = send_direct_message(current_user.id, user_id, data["body"])
        return success_response(message.to_dict(), "Message sent.", 201)
    except ValidationError as exc:
        return error_response("Validation failed.", 422, exc.messages)
    except Exception as exc:
        return error_response(str(exc), 500)


@chat_bp.get("/clubs/<int:club_id>/messages")
def get_club_messages(club_id):
    try:
        messages = ClubMessage.query.filter_by(club_id=club_id).order_by(ClubMessage.created_at.asc()).all()
        return success_response([message.to_dict() for message in messages])
    except Exception as exc:
        return error_response(str(exc), 500)
