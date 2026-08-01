import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class EmploymentType(str, enum.Enum):
    PERMANENT = "PERMANENT"
    FIXED_TERM = "FIXED_TERM"
    PART_TIME = "PART_TIME"
    CONTRACTOR = "CONTRACTOR"


class EmploymentRecordStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    TERMINATED = "TERMINATED"


class EmploymentRecord(Base):
    __tablename__ = "employment_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    job_title = Column(String(150), nullable=False)
    employment_type = Column(Enum(EmploymentType), nullable=False, default=EmploymentType.PERMANENT)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    salary_band = Column(String(50), nullable=False)
    manager_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(EmploymentRecordStatus), nullable=False, default=EmploymentRecordStatus.ACTIVE)

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
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="employment_records")
    manager = relationship("Employee", foreign_keys=[manager_id])

    def __repr__(self) -> str:
        return f"<EmploymentRecord id={self.id} title='{self.job_title}' emp_id={self.employee_id}>"
