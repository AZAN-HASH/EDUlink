from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .base import TimestampMixin


class School(TimestampMixin, db.Model):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(120))
    created_by_id: Mapped[int | None] = mapped_column(db.ForeignKey("users.id"))

    users = relationship("User", back_populates="school", lazy="selectin", foreign_keys="User.school_id")
    clubs = relationship("Club", back_populates="school", lazy="selectin", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "location": self.location,
            "created_at": self.created_at.isoformat(),
            "member_count": len(self.users),
            "club_count": len(self.clubs),
        }
