import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.models.schemas import AnalysisStatus


class Base(DeclarativeBase):
    pass


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    keyword: Mapped[str] = mapped_column(String(200), index=True)
    status: Mapped[str] = mapped_column(
        Enum(AnalysisStatus),
        default=AnalysisStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    trending_terms_json: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None
    )
    scored_terms_json: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None
    )
    final_report: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None
    )
    error: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None
    )
