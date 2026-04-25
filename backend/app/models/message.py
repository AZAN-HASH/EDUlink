from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .base import TimestampMixin


class DirectMessageThread(TimestampMixin, db.Model):
    __tablename__ = "direct_message_threads"
    __table_args__ = (
        UniqueConstraint("participant_one_id", "participant_two_id", name="uq_direct_thread_pair"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    participant_one_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False, index=True)
    participant_two_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False, index=True)

    participant_one = relationship("User", foreign_keys=[participant_one_id], back_populates="direct_threads_as_one")
    participant_two = relationship("User", foreign_keys=[participant_two_id], back_populates="direct_threads_as_two")
    messages = relationship("DirectMessage", back_populates="thread", lazy="selectin", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "participant_one": self.participant_one.to_dict() if self.participant_one else None,
            "participant_two": self.participant_two.to_dict() if self.participant_two else None,
            "created_at": self.created_at.isoformat(),
            "messages": [message.to_dict() for message in self.messages],
        }


class DirectMessage(TimestampMixin, db.Model):
    __tablename__ = "direct_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    thread_id: Mapped[int] = mapped_column(db.ForeignKey("direct_message_threads.id"), nullable=False, index=True)
    sender_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False, index=True)
    recipient_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False, index=True)
    body: Mapped[str] = mapped_column(db.Text, nullable=False)

    thread = relationship("DirectMessageThread", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="direct_messages_sent")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="direct_messages_received")

    def to_dict(self):
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "body": self.body,
            "created_at": self.created_at.isoformat(),
            "sender": self.sender.to_dict() if self.sender else None,
        }


class ClubMessage(TimestampMixin, db.Model):
    __tablename__ = "club_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    club_id: Mapped[int] = mapped_column(db.ForeignKey("clubs.id"), nullable=False, index=True)
    sender_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False, index=True)
    body: Mapped[str] = mapped_column(db.Text, nullable=False)

    club = relationship("Club", back_populates="group_messages")
    sender = relationship("User", back_populates="club_messages")

    def to_dict(self):
        return {
            "id": self.id,
            "club_id": self.club_id,
            "sender_id": self.sender_id,
            "body": self.body,
            "created_at": self.created_at.isoformat(),
            "sender": self.sender.to_dict() if self.sender else None,
        }
