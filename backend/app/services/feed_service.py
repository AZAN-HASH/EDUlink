from sqlalchemy import func

from ..extensions import db
from ..models import Follow, Post


def feed_query(sort="latest"):
    query = (
        db.session.query(Post)
        .outerjoin(Post.likes)
        .outerjoin(Post.comments)
        .outerjoin(Post.shares)
        .group_by(Post.id)
    )
    if sort == "trending":
        query = query.order_by(
            (
                func.count(db.distinct(Post.likes.property.mapper.class_.id)) * 2
                + func.count(db.distinct(Post.comments.property.mapper.class_.id)) * 3
                + func.count(db.distinct(Post.shares.property.mapper.class_.id))
            ).desc(),
            Post.created_at.desc(),
        )
    else:
        query = query.order_by(Post.created_at.desc())
    return query


def get_global_feed(sort="latest"):
    return [post.to_dict() for post in feed_query(sort).all()]


def get_following_feed(user_id, sort="latest"):
    followed_ids = db.session.query(Follow.followed_id).filter(Follow.follower_id == user_id)
    return [post.to_dict() for post in feed_query(sort).filter(Post.author_id.in_(followed_ids)).all()]


def get_club_feed(club_id, sort="latest"):
    return [post.to_dict() for post in feed_query(sort).filter(Post.club_id == club_id).all()]
