from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import bcrypt, db
from .base import TimestampMixin


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="student", nullable=False)
    profile_picture: Mapped[str | None] = mapped_column(String(255))
    bio: Mapped[str | None] = mapped_column(Text)
    school_name: Mapped[str | None] = mapped_column(String(120))
    location: Mapped[str] = mapped_column(String(120), nullable=False)
    school_id: Mapped[int | None] = mapped_column(db.ForeignKey("schools.id"), index=True)

    school = relationship("School", back_populates="users", foreign_keys=[school_id])
    posts = relationship("Post", back_populates="author", lazy="selectin", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", lazy="selectin", cascade="all, delete-orphan")
    led_clubs = relationship("Club", back_populates="leader", lazy="selectin")
    memberships = relationship("ClubMembership", back_populates="user", lazy="selectin", cascade="all, delete-orphan")
    notifications = relationship(
        "Notification",
        foreign_keys="Notification.user_id",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    follower_relationships = relationship(
        "Follow",
        foreign_keys="Follow.followed_id",
        back_populates="followed",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    following_relationships = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    likes = relationship("PostLike", back_populates="user", lazy="selectin", cascade="all, delete-orphan")
    bookmarks = relationship("PostBookmark", back_populates="user", lazy="selectin", cascade="all, delete-orphan")
    shares = relationship("PostShare", back_populates="user", lazy="selectin", cascade="all, delete-orphan")
    direct_threads_as_one = relationship(
        "DirectMessageThread", foreign_keys="DirectMessageThread.participant_one_id", back_populates="participant_one"
    )
    direct_threads_as_two = relationship(
        "DirectMessageThread", foreign_keys="DirectMessageThread.participant_two_id", back_populates="participant_two"
    )
    direct_messages_sent = relationship(
        "DirectMessage", foreign_keys="DirectMessage.sender_id", back_populates="sender", lazy="selectin"
    )
    direct_messages_received = relationship(
        "DirectMessage", foreign_keys="DirectMessage.recipient_id", back_populates="recipient", lazy="selectin"
    )
    club_messages = relationship("ClubMessage", back_populates="sender", lazy="selectin")

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def approved_clubs(self):
        return [membership.club for membership in self.memberships if membership.status == "approved" and membership.club]

    def to_dict(self, include_private=False):
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email if include_private else None,
            "role": self.role,
            "profile_picture": self.profile_picture,
            "bio": self.bio,
            "school": self.school.to_dict() if self.school else None,
            "school_name": self.school_name,
            "location": self.location,
            "joined_clubs": [
                {"id": club.id, "name": club.name} for club in self.approved_clubs()
            ],
            "projects_posted": len(self.posts),
            "followers_count": len(self.follower_relationships),
            "following_count": len(self.following_relationships),
            "created_at": self.created_at.isoformat(),
        }
        if not include_private:
            data.pop("email")
        return data
