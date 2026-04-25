from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db


class TokenBlocklist(db.Model):
    __tablename__ = "token_blocklist"

    id: Mapped[int] = mapped_column(primary_key=True)
    jti: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
