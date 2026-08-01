from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class ExternalRequest(Base):
    __tablename__ = "external_requests"

    id = Column(Integer, primary_key=True, index=True)
    background_check_id = Column(
        Integer, ForeignKey("background_checks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider = Column(String(100), nullable=False)
    request_identifier = Column(String(100), nullable=False)
    outcome = Column(String(50), nullable=False)
    error_code = Column(String(50), nullable=True)

    requested_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship
    background_check = relationship("BackgroundCheck", back_populates="external_requests")

    def __repr__(self) -> str:
        return f"<ExternalRequest id={self.id} provider='{self.provider}' outcome='{self.outcome}'>"
