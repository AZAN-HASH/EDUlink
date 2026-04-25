from marshmallow import ValidationError

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import HTTPException

from ..extensions import db
from ..models import Club, ClubMembership, Comment, Post, PostBookmark, PostLike, PostShare
from ..schemas.post import CommentCreateSchema, PostCreateSchema
from ..services.feed_service import get_club_feed, get_following_feed, get_global_feed
from ..services.file_service import save_media
from ..services.notification_service import create_notification
from ..utils.decorators import get_current_user
from ..utils.response import error_response, success_response
from ..utils.validators import sanitize_text

posts_bp = Blueprint("posts", __name__, url_prefix="/posts")
post_schema = PostCreateSchema()
comment_schema = CommentCreateSchema()


@posts_bp.post("")
@jwt_required()
def create_post():
    try:
        current_user = get_current_user()
        payload = post_schema.load(request.form.to_dict() or request.get_json() or {})
        club_id = payload.get("club_id")
        if club_id:
            membership = ClubMembership.query.filter_by(user_id=current_user.id, club_id=club_id, status="approved").first()
            if not membership:
                return error_response("Only approved club members can post in a club.", 403)

        media_file = request.files.get("media")
        media_filename, media_type = save_media(media_file) if media_file else (None, None)
        post = Post(
            title=sanitize_text(payload["title"]),
            description=sanitize_text(payload["description"]),
            code_snippet=payload.get("code_snippet"),
            media_filename=media_filename,
            media_type=media_type,
            author_id=current_user.id,
            club_id=club_id,
            status="published",
        )
        db.session.add(post)
        db.session.commit()

        if club_id:
            club = db.session.get(Club, club_id)
            create_notification(
                club.leader_id,
                current_user.id,
                "club_post",
                f"{current_user.username} added a new post in {club.name}.",
                entity_type="post",
                entity_id=post.id,
            )
        return success_response(post.to_dict(), "Post created successfully.", 201)
    except ValidationError as exc:
        return error_response("Validation failed.", 422, exc.messages)
    except ValueError as exc:
        return error_response(str(exc), 400)
    except HTTPException as exc:
        return error_response(exc.description, exc.code)
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)


@posts_bp.get("")
def list_posts():
    try:
        feed_type = request.args.get("feed", "global")
        sort = request.args.get("sort", "latest")
        user_id = request.args.get("user_id", type=int)
        club_id = request.args.get("club_id", type=int)

        if feed_type == "following" and user_id:
            data = get_following_feed(user_id, sort)
        elif feed_type == "club" and club_id:
            data = get_club_feed(club_id, sort)
        else:
            data = get_global_feed(sort)
        return success_response(data)
    except Exception as exc:
        return error_response(str(exc), 500)


@posts_bp.get("/<int:post_id>")
def get_post(post_id):
    try:
        post = db.session.get(Post, post_id)
        if not post:
            return error_response("Post not found.", 404)
        return success_response(post.to_dict())
    except HTTPException as exc:
        return error_response(exc.description, exc.code)
    except Exception as exc:
        return error_response(str(exc), 500)


@posts_bp.put("/<int:post_id>")
@jwt_required()
def update_post(post_id):
    try:
        current_user = get_current_user()
        post = db.session.get(Post, post_id)
        if not post:
            return error_response("Post not found.", 404)
        if post.author_id != current_user.id and current_user.role != "admin":
            return error_response("Unauthorized.", 403)

        data = request.get_json() or {}
        if data.get("title"):
            post.title = sanitize_text(data["title"])
        if data.get("description"):
            post.description = sanitize_text(data["description"])
        if "code_snippet" in data:
            post.code_snippet = data["code_snippet"]

        db.session.commit()
        return success_response(post.to_dict(), "Post updated.")
    except HTTPException as exc:
        return error_response(exc.description, exc.code)
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)


@posts_bp.delete("/<int:post_id>")
@jwt_required()
def delete_post(post_id):
    try:
        current_user = get_current_user()
        post = db.session.get(Post, post_id)
        if not post:
            return error_response("Post not found.", 404)
        if post.author_id != current_user.id and current_user.role != "admin":
            return error_response("Unauthorized.", 403)

        db.session.delete(post)
        db.session.commit()
        return success_response(message="Post deleted successfully.")
    except HTTPException as exc:
        return error_response(exc.description, exc.code)
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)


@posts_bp.post("/<int:post_id>/like")
@jwt_required()
def like_post(post_id):
    try:
        current_user = get_current_user()
        post = db.session.get(Post, post_id)
        if not post:
            return error_response("Post not found.", 404)
        if PostLike.query.filter_by(user_id=current_user.id, post_id=post.id).first():
            return error_response("Post already liked.", 409)

        like = PostLike(user_id=current_user.id, post_id=post.id)
        db.session.add(like)
        db.session.commit()
        if post.author_id != current_user.id:
            create_notification(
                post.author_id,
                current_user.id,
                "like",
                f"{current_user.username} liked your post.",
                entity_type="post",
                entity_id=post.id,
            )
        return success_response(message="Post liked.")
    except HTTPException as exc:
        return error_response(exc.description, exc.code)
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)


@posts_bp.delete("/<int:post_id>/like")
@jwt_required()
def unlike_post(post_id):
    try:
        current_user = get_current_user()
        like = PostLike.query.filter_by(user_id=current_user.id, post_id=post_id).first()
        if not like:
            return error_response("Like not found.", 404)
        db.session.delete(like)
        db.session.commit()
        return success_response(message="Post unliked.")
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)


@posts_bp.post("/<int:post_id>/comments")
@jwt_required()
def add_comment(post_id):
    try:
        current_user = get_current_user()
        post = db.session.get(Post, post_id)
        if not post:
            return error_response("Post not found.", 404)
        data = comment_schema.load(request.get_json() or {})
        comment = Comment(content=sanitize_text(data["content"]), author_id=current_user.id, post_id=post.id)
        db.session.add(comment)
        db.session.commit()

        if post.author_id != current_user.id:
            create_notification(
                post.author_id,
                current_user.id,
                "comment",
                f"{current_user.username} commented on your post.",
                entity_type="post",
                entity_id=post.id,
            )
        return success_response(comment.to_dict(), "Comment added.", 201)
    except ValidationError as exc:
        return error_response("Validation failed.", 422, exc.messages)
    except HTTPException as exc:
        return error_response(exc.description, exc.code)
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)


@posts_bp.post("/<int:post_id>/share")
@jwt_required()
def share_post(post_id):
    try:
        current_user = get_current_user()
        post = db.session.get(Post, post_id)
        if not post:
            return error_response("Post not found.", 404)
        share = PostShare(user_id=current_user.id, post_id=post_id)
        db.session.add(share)
        db.session.commit()
        return success_response(message="Post shared.")
    except HTTPException as exc:
        return error_response(exc.description, exc.code)
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)


@posts_bp.post("/<int:post_id>/bookmark")
@jwt_required()
def bookmark_post(post_id):
    try:
        current_user = get_current_user()
        post = db.session.get(Post, post_id)
        if not post:
            return error_response("Post not found.", 404)
        existing = PostBookmark.query.filter_by(user_id=current_user.id, post_id=post_id).first()
        if existing:
            return error_response("Post already bookmarked.", 409)
        bookmark = PostBookmark(user_id=current_user.id, post_id=post_id)
        db.session.add(bookmark)
        db.session.commit()
        return success_response(message="Post bookmarked.")
    except HTTPException as exc:
        return error_response(exc.description, exc.code)
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)


@posts_bp.delete("/<int:post_id>/bookmark")
@jwt_required()
def remove_bookmark(post_id):
    try:
        current_user = get_current_user()
        bookmark = PostBookmark.query.filter_by(user_id=current_user.id, post_id=post_id).first()
        if not bookmark:
            return error_response("Bookmark not found.", 404)
        db.session.delete(bookmark)
        db.session.commit()
        return success_response(message="Bookmark removed.")
    except Exception as exc:
        db.session.rollback()
        return error_response(str(exc), 500)
