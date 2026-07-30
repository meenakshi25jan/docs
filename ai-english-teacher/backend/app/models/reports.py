"""Report model — maps to existing reports table (no new migration)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    learner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("learner_profiles.id"), nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    file_url: Mapped[str | None] = mapped_column(String(500))
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
