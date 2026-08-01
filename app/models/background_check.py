import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class CheckType(str, enum.Enum):
    DBS = "DBS"
    RIGHT_TO_WORK = "RIGHT_TO_WORK"
    CREDIT = "CREDIT"
    BANK_VERIFICATION = "BANK_VERIFICATION"


class CheckStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    FAILED = "FAILED"


class BackgroundCheck(Base):
    __tablename__ = "background_checks"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    check_type = Column(Enum(CheckType), nullable=False, index=True)
    status = Column(Enum(CheckStatus), nullable=False, default=CheckStatus.PENDING, index=True)

    requested_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)
    provider_reference = Column(String(100), nullable=True)
    expiry_date = Column(Date, nullable=True)
    restricted_notes = Column(Text, nullable=True)

    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    employee = relationship("Employee", back_populates="background_checks")
    external_requests = relationship("ExternalRequest", back_populates="background_check", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<BackgroundCheck id={self.id} type='{self.check_type}' status='{self.status}'>"
