from flask import request
from flask_jwt_extended import decode_token
from flask_socketio import emit, join_room, leave_room

from .extensions import socketio
from .services.chat_service import send_club_message, send_direct_message

connected_users = {}


def _require_authenticated_user():
    user_id = connected_users.get(request.sid)
    if not user_id:
        emit("socket_error", {"message": "Socket authentication required."})
        return None
    return user_id


def register_socket_events():
    @socketio.on("connect")
    def on_connect():
        emit("connected", {"message": "Socket connected."})

    @socketio.on("disconnect")
    def on_disconnect():
        user_id = connected_users.pop(request.sid, None)
        if user_id:
            socketio.emit("presence", {"user_id": user_id, "online": False})

    @socketio.on("authenticate")
    def on_authenticate(data):
        try:
            payload = decode_token(data.get("token"))
            user_id = int(payload["sub"])
            connected_users[request.sid] = user_id
            join_room(f"user_{user_id}")
            emit("authenticated", {"user_id": user_id})
            socketio.emit("presence", {"user_id": user_id, "online": True})
        except Exception:
            emit("socket_error", {"message": "Socket authentication failed."})

    @socketio.on("join_club")
    def on_join_club(data):
        user_id = _require_authenticated_user()
        if not user_id:
            return
        club_id = data.get("club_id")
        join_room(f"club_{club_id}")
        emit("joined_club", {"club_id": club_id, "user_id": user_id})

    @socketio.on("leave_club")
    def on_leave_club(data):
        user_id = _require_authenticated_user()
        if not user_id:
            return
        club_id = data.get("club_id")
        leave_room(f"club_{club_id}")
        emit("left_club", {"club_id": club_id, "user_id": user_id})

    @socketio.on("direct_message")
    def on_direct_message(data):
        user_id = _require_authenticated_user()
        if not user_id:
            return
        try:
            recipient_id = int(data["recipient_id"])
            body = (data.get("body") or "").strip()
            if not body:
                emit("socket_error", {"message": "Message body is required."})
                return
            message = send_direct_message(user_id, recipient_id, body)
            emit("message_sent", message.to_dict())
        except Exception as exc:
            emit("socket_error", {"message": str(exc)})

    @socketio.on("club_message")
    def on_club_message(data):
        user_id = _require_authenticated_user()
        if not user_id:
            return
        try:
            club_id = int(data["club_id"])
            body = (data.get("body") or "").strip()
            if not body:
                emit("socket_error", {"message": "Message body is required."})
                return
            message = send_club_message(user_id, club_id, body)
            emit("message_sent", message.to_dict())
        except Exception as exc:
            emit("socket_error", {"message": str(exc)})
