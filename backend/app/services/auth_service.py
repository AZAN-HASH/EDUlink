from flask_jwt_extended import create_access_token, create_refresh_token

from ..extensions import db
from ..models import School, TokenBlocklist, User
from ..utils.validators import sanitize_text


def create_tokens(user):
    return {
        "access_token": create_access_token(identity=str(user.id)),
        "refresh_token": create_refresh_token(identity=str(user.id)),
    }


def register_user(data):
    if User.query.filter((User.username == data["username"]) | (User.email == data["email"])).first():
        return None, "Username or email already exists."

    school = None
    school_name = sanitize_text(data.get("school"))
    if school_name:
        school = School.query.filter(db.func.lower(School.name) == school_name.lower()).first()
        if not school:
            school = School(name=school_name, location=sanitize_text(data.get("location")), created_by_id=None)
            db.session.add(school)
            db.session.flush()

    user = User(
        username=sanitize_text(data["username"]),
        email=sanitize_text(data["email"]).lower(),
        location=sanitize_text(data["location"]),
        role=data.get("role", "student"),
        school=school,
        school_name=school.name if school else school_name,
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return user, None


def authenticate_user(email, password):
    user = User.query.filter(db.func.lower(User.email) == sanitize_text(email).lower()).first()
    if not user or not user.check_password(password):
        return None
    return user


def invalidate_token(jwt_payload):
    blocked = TokenBlocklist(jti=jwt_payload["jti"])
    db.session.add(blocked)
    db.session.commit()
