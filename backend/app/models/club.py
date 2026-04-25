from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .base import TimestampMixin


class Club(TimestampMixin, db.Model):
    __tablename__ = "clubs"
    __table_args__ = (UniqueConstraint("school_id", "name", name="uq_school_club_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    banner_url: Mapped[str | None] = mapped_column(String(255))
    school_id: Mapped[int] = mapped_column(db.ForeignKey("schools.id"), nullable=False, index=True)
    leader_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False, index=True)

    school = relationship("School", back_populates="clubs")
    leader = relationship("User", back_populates="led_clubs")
    memberships = relationship("ClubMembership", back_populates="club", lazy="selectin", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="club", lazy="selectin")
    group_messages = relationship("ClubMessage", back_populates="club", lazy="selectin", cascade="all, delete-orphan")

    def to_dict(self, include_members=False):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "banner_url": self.banner_url,
            "school_id": self.school_id,
            "leader_id": self.leader_id,
            "created_at": self.created_at.isoformat(),
            "member_count": len([membership for membership in self.memberships if membership.status == "approved"]),
            "school": self.school.to_dict() if self.school else None,
            "leader": self.leader.to_dict() if self.leader else None,
        }
        if include_members:
            data["members"] = [membership.to_dict() for membership in self.memberships]
        return data
