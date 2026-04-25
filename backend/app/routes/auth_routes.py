from marshmallow import ValidationError

from flask import Blueprint, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from ..extensions import db
from ..models import User
from ..schemas.auth import LoginSchema, RegisterSchema
from ..services.auth_service import authenticate_user, create_tokens, invalidate_token, register_user
from ..utils.response import error_response, success_response

auth_bp = Blueprint("auth", __name__)

register_schema = RegisterSchema()
login_schema = LoginSchema()


@auth_bp.post("/register")
def register():
    try:
        data = register_schema.load(request.get_json() or {})
        user, error = register_user(data)
        if error:
            return error_response(error, 409)
        return success_response(
            {"user": user.to_dict(include_private=True), "tokens": create_tokens(user)},
            "Registration successful.",
            201,
        )
    except ValidationError as exc:
        return error_response("Validation failed.", 422, exc.messages)
    except Exception as exc:
        return error_response(str(exc), 500)


@auth_bp.post("/login")
def login():
    try:
        data = login_schema.load(request.get_json() or {})
        user = authenticate_user(data["email"], data["password"])
        if not user:
            return error_response("Invalid email or password.", 401)
        return success_response(
            {"user": user.to_dict(include_private=True), "tokens": create_tokens(user)},
            "Login successful.",
        )
    except ValidationError as exc:
        return error_response("Validation failed.", 422, exc.messages)
    except Exception as exc:
        return error_response(str(exc), 500)


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    try:
        user = db.session.get(User, int(get_jwt_identity()))
        if not user:
            return error_response("User not found.", 404)
        return success_response({"access_token": create_tokens(user)["access_token"]}, "Token refreshed.")
    except Exception as exc:
        return error_response(str(exc), 500)


@auth_bp.post("/logout")
@jwt_required()
def logout():
    try:
        invalidate_token(get_jwt())
        return success_response(message="Logout successful.")
    except Exception as exc:
        return error_response(str(exc), 500)
