from marshmallow import ValidationError

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import HTTPException

from ..extensions import db
from ..models import School
from ..schemas.school import SchoolCreateSchema
from ..utils.decorators import get_current_user
from ..utils.response import error_response, success_response
from ..utils.validators import sanitize_text

schools_bp = Blueprint("schools", __name__, url_prefix="/schools")
school_schema = SchoolCreateSchema()


@schools_bp.post("")
@jwt_required()
def create_school():
    try:
        current_user = get_current_user()
        data = school_schema.load(request.get_json() or {})
        existing = School.query.filter(db.func.lower(School.name) == data["name"].strip().lower()).first()
        if existing:
            return error_response("A school with that name already exists.", 409)

        school = School(
            name=sanitize_text(data["name"]),
            description=sanitize_text(data.get("description")),
            location=sanitize_text(data.get("location")),
            created_by_id=current_user.id,
        )
        db.session.add(school)
        db.session.commit()
        return success_response(school.to_dict(), "School created successfully.", 201)
    except ValidationError as exc:
        return error_response("Validation failed.", 422, exc.messages)
    except HTTPException as exc:
        return error_response(exc.description, exc.code)
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)


@schools_bp.get("")
def list_schools():
    try:
        schools = School.query.order_by(School.name.asc()).all()
        return success_response([school.to_dict() for school in schools])
    except Exception as exc:
        return error_response(str(exc), 500)


@schools_bp.get("/<int:school_id>")
def get_school(school_id):
    try:
        school = db.session.get(School, school_id)
        if not school:
            return error_response("School not found.", 404)
        return success_response(school.to_dict())
    except HTTPException as exc:
        return error_response(exc.description, exc.code)
    except Exception as exc:
        return error_response(str(exc), 500)


@schools_bp.post("/<int:school_id>/join")
@jwt_required()
def join_school(school_id):
    try:
        current_user = get_current_user()
        school = db.session.get(School, school_id)
        if not school:
            return error_response("School not found.", 404)
        current_user.school = school
        current_user.school_name = school.name
        db.session.commit()
        return success_response(current_user.to_dict(include_private=True), "School joined successfully.")
    except HTTPException as exc:
        return error_response(exc.description, exc.code)
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)
