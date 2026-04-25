from flask import Blueprint, request
from sqlalchemy import or_

from ..models import Club, Post, School, User
from ..utils.response import error_response, success_response

search_bp = Blueprint("search", __name__, url_prefix="/search")


@search_bp.get("")
def search():
    try:
        query = request.args.get("q", "").strip()
        if not query:
            return success_response({"users": [], "schools": [], "clubs": [], "posts": []})

        pattern = f"%{query}%"
        users = User.query.filter(or_(User.username.ilike(pattern), User.location.ilike(pattern))).limit(10).all()
        schools = School.query.filter(School.name.ilike(pattern)).limit(10).all()
        clubs = Club.query.filter(Club.name.ilike(pattern)).limit(10).all()
        posts = Post.query.filter(or_(Post.title.ilike(pattern), Post.description.ilike(pattern))).limit(10).all()

        return success_response(
            {
                "users": [user.to_dict() for user in users],
                "schools": [school.to_dict() for school in schools],
                "clubs": [club.to_dict() for club in clubs],
                "posts": [post.to_dict() for post in posts],
            }
        )
    except Exception as exc:
        return error_response(str(exc), 500)
