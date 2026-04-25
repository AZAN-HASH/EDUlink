from functools import wraps

from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from ..extensions import db
from ..models import User
from .response import error_response


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = db.session.get(User, int(get_jwt_identity()))
            if not user:
                return error_response("User not found.", 404)
            if user.role not in roles:
                return error_response("You do not have permission to perform this action.", 403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def get_current_user():
    user_id = get_jwt_identity()
    return db.session.get(User, int(user_id)) if user_id else None
