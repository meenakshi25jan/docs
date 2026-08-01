import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import IngestionStatus, SourceType
from app.db.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.db.models.knowledge_document import KnowledgeDocument

# CHECK constraints enforce allowed values at the DB layer (defense in depth).
# App-level enums (SourceType, IngestionStatus) are the primary API contract.
_SOURCE_TYPES = ", ".join(f"'{v.value}'" for v in SourceType)
_INGESTION_STATUSES = ", ".join(f"'{v.value}'" for v in IngestionStatus)


class KnowledgeSource(TimestampMixin, Base):
    __tablename__ = "knowledge_source"
    __table_args__ = (
        CheckConstraint(
            f"source_type IN ({_SOURCE_TYPES})", name="ck_knowledge_source_source_type"
        ),
        CheckConstraint(
            f"ingestion_status IN ({_INGESTION_STATUSES})",
            name="ck_knowledge_source_ingestion_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    author: Mapped[str | None] = mapped_column(String(200), nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(200), nullable=True)
    license_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ingestion_status: Mapped[str] = mapped_column(
        String(50),
        default=IngestionStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    documents: Mapped[list["KnowledgeDocument"]] = relationship(
        "KnowledgeDocument",
        back_populates="source",
        cascade="all, delete-orphan",
    )
