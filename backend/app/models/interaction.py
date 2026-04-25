from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .base import TimestampMixin


class Follow(TimestampMixin, db.Model):
    __tablename__ = "follows"
    __table_args__ = (UniqueConstraint("follower_id", "followed_id", name="uq_follow_pair"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    follower_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False, index=True)
    followed_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False, index=True)

    follower = relationship("User", foreign_keys=[follower_id], back_populates="following_relationships")
    followed = relationship("User", foreign_keys=[followed_id], back_populates="follower_relationships")


class ClubMembership(TimestampMixin, db.Model):
    __tablename__ = "club_memberships"
    __table_args__ = (UniqueConstraint("user_id", "club_id", name="uq_club_membership"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False, index=True)
    club_id: Mapped[int] = mapped_column(db.ForeignKey("clubs.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(db.String(20), default="approved", nullable=False)
    role: Mapped[str] = mapped_column(db.String(20), default="member", nullable=False)

    user = relationship("User", back_populates="memberships")
    club = relationship("Club", back_populates="memberships")

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "role": self.role,
            "joined_at": self.created_at.isoformat(),
            "user": self.user.to_dict() if self.user else None,
        }


class PostLike(TimestampMixin, db.Model):
    __tablename__ = "post_likes"
    __table_args__ = (UniqueConstraint("user_id", "post_id", name="uq_post_like"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False, index=True)
    post_id: Mapped[int] = mapped_column(db.ForeignKey("posts.id"), nullable=False, index=True)

    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")


class PostBookmark(TimestampMixin, db.Model):
    __tablename__ = "post_bookmarks"
    __table_args__ = (UniqueConstraint("user_id", "post_id", name="uq_post_bookmark"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False, index=True)
    post_id: Mapped[int] = mapped_column(db.ForeignKey("posts.id"), nullable=False, index=True)

    user = relationship("User", back_populates="bookmarks")
    post = relationship("Post", back_populates="bookmarks")


class PostShare(TimestampMixin, db.Model):
    __tablename__ = "post_shares"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False, index=True)
    post_id: Mapped[int] = mapped_column(db.ForeignKey("posts.id"), nullable=False, index=True)

    user = relationship("User", back_populates="shares")
    post = relationship("Post", back_populates="shares")
