from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .base import TimestampMixin


class Post(TimestampMixin, db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    media_filename: Mapped[str | None] = mapped_column(String(255))
    media_type: Mapped[str | None] = mapped_column(String(20))
    code_snippet: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="published", nullable=False)
    author_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False, index=True)
    club_id: Mapped[int | None] = mapped_column(db.ForeignKey("clubs.id"), index=True)

    author = relationship("User", back_populates="posts")
    club = relationship("Club", back_populates="posts")
    comments = relationship("Comment", back_populates="post", lazy="selectin", cascade="all, delete-orphan")
    likes = relationship("PostLike", back_populates="post", lazy="selectin", cascade="all, delete-orphan")
    bookmarks = relationship("PostBookmark", back_populates="post", lazy="selectin", cascade="all, delete-orphan")
    shares = relationship("PostShare", back_populates="post", lazy="selectin", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "media_filename": self.media_filename,
            "media_type": self.media_type,
            "code_snippet": self.code_snippet,
            "status": self.status,
            "author_id": self.author_id,
            "club_id": self.club_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "author": self.author.to_dict() if self.author else None,
            "club": self.club.to_dict() if self.club else None,
            "likes_count": len(self.likes),
            "comments_count": len(self.comments),
            "shares_count": len(self.shares),
            "bookmarks_count": len(self.bookmarks),
            "comments": [comment.to_dict() for comment in self.comments],
        }


class Comment(TimestampMixin, db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False, index=True)
    post_id: Mapped[int] = mapped_column(db.ForeignKey("posts.id"), nullable=False, index=True)

    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "author_id": self.author_id,
            "post_id": self.post_id,
            "created_at": self.created_at.isoformat(),
            "author": self.author.to_dict() if self.author else None,
        }
