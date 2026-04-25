from marshmallow import ValidationError

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import HTTPException

from ..extensions import db
from ..models import Club, ClubMembership, School
from ..schemas.club import ClubCreateSchema
from ..services.notification_service import create_notification
from ..utils.decorators import get_current_user
from ..utils.response import error_response, success_response
from ..utils.validators import sanitize_text

clubs_bp = Blueprint("clubs", __name__, url_prefix="/clubs")
club_schema = ClubCreateSchema()


@clubs_bp.post("")
@jwt_required()
def create_club():
    try:
        current_user = get_current_user()
        data = club_schema.load(request.get_json() or {})
        school = db.session.get(School, data["school_id"])
        if not school:
            return error_response("School not found.", 404)
        existing = Club.query.filter(
            Club.school_id == school.id, db.func.lower(Club.name) == data["name"].strip().lower()
        ).first()
        if existing:
            return error_response("A club with that name already exists in this school.", 409)

        club = Club(
            name=sanitize_text(data["name"]),
            description=sanitize_text(data.get("description")),
            banner_url=sanitize_text(data.get("banner_url")),
            school_id=school.id,
            leader_id=current_user.id,
        )
        db.session.add(club)
        db.session.flush()

        membership = ClubMembership(user_id=current_user.id, club_id=club.id, role="leader", status="approved")
        db.session.add(membership)
        db.session.commit()
        return success_response(club.to_dict(include_members=True), "Club created successfully.", 201)
    except ValidationError as exc:
        return error_response("Validation failed.", 422, exc.messages)
    except HTTPException as exc:
        return error_response(exc.description, exc.code)
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)


@clubs_bp.get("")
def list_clubs():
    try:
        clubs = Club.query.order_by(Club.created_at.desc()).all()
        return success_response([club.to_dict() for club in clubs])
    except Exception as exc:
        return error_response(str(exc), 500)


@clubs_bp.get("/<int:club_id>")
def get_club(club_id):
    try:
        club = db.session.get(Club, club_id)
        if not club:
            return error_response("Club not found.", 404)
        return success_response(club.to_dict(include_members=True))
    except HTTPException as exc:
        return error_response(exc.description, exc.code)
    except Exception as exc:
        return error_response(str(exc), 500)


@clubs_bp.put("/<int:club_id>")
@jwt_required()
def update_club(club_id):
    try:
        current_user = get_current_user()
        club = db.session.get(Club, club_id)
        if not club:
            return error_response("Club not found.", 404)
        if current_user.id != club.leader_id and current_user.role != "admin":
            return error_response("Only the club leader or an admin can update this club.", 403)

        data = request.get_json() or {}
        if data.get("name"):
            club.name = sanitize_text(data["name"])
        if data.get("description") is not None:
            club.description = sanitize_text(data["description"])
        if data.get("banner_url") is not None:
            club.banner_url = sanitize_text(data["banner_url"])

        db.session.commit()
        return success_response(club.to_dict(include_members=True), "Club updated.")
    except HTTPException as exc:
        return error_response(exc.description, exc.code)
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)


@clubs_bp.post("/<int:club_id>/join")
@jwt_required()
def join_club(club_id):
    try:
        current_user = get_current_user()
        club = db.session.get(Club, club_id)
        if not club:
            return error_response("Club not found.", 404)
        existing = ClubMembership.query.filter_by(user_id=current_user.id, club_id=club.id).first()
        if existing:
            return error_response("Membership request already exists.", 409)

        membership = ClubMembership(
            user_id=current_user.id,
            club_id=club.id,
            status="pending",
            role="member",
        )
        db.session.add(membership)
        db.session.commit()

        create_notification(
            club.leader_id,
            current_user.id,
            "club_join",
            f"{current_user.username} requested to join {club.name}.",
            entity_type="club",
            entity_id=club.id,
        )
        return success_response(membership.to_dict(), "Club join request submitted.")
    except HTTPException as exc:
        return error_response(exc.description, exc.code)
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)


@clubs_bp.post("/<int:club_id>/leave")
@jwt_required()
def leave_club(club_id):
    try:
        current_user = get_current_user()
        membership = ClubMembership.query.filter_by(user_id=current_user.id, club_id=club_id).first()
        if not membership:
            return error_response("Membership not found.", 404)
        if membership.role == "leader":
            return error_response("Club leaders cannot leave their own club.", 400)

        db.session.delete(membership)
        db.session.commit()
        return success_response(message="Club left successfully.")
    except HTTPException as exc:
        return error_response(exc.description, exc.code)
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)


@clubs_bp.post("/<int:club_id>/members/<int:user_id>/approve")
@jwt_required()
def approve_member(club_id, user_id):
    try:
        current_user = get_current_user()
        club = db.session.get(Club, club_id)
        if not club:
            return error_response("Club not found.", 404)
        if current_user.id != club.leader_id and current_user.role != "admin":
            return error_response("Only the club leader or an admin can approve members.", 403)

        membership = ClubMembership.query.filter_by(user_id=user_id, club_id=club_id).first()
        if not membership:
            return error_response("Membership request not found.", 404)

        membership.status = "approved"
        db.session.commit()
        create_notification(
            user_id,
            current_user.id,
            "club_approved",
            f"You have been approved to join {club.name}.",
            entity_type="club",
            entity_id=club.id,
        )
        return success_response(membership.to_dict(), "Member approved.")
    except HTTPException as exc:
        return error_response(exc.description, exc.code)
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)
