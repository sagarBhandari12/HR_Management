import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class EmployeeStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ON_LEAVE = "ON_LEAVE"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_number = Column(String(50), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    work_email = Column(String(255), unique=True, index=True, nullable=False)
    personal_email = Column(String(255), nullable=True)
    telephone = Column(String(50), nullable=True)
    date_of_birth = Column(Date, nullable=True)

    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    status = Column(Enum(EmployeeStatus), nullable=False, default=EmployeeStatus.ACTIVE)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

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
    deactivated_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    department = relationship("Department", back_populates="employees")
    employment_records = relationship(
        "EmploymentRecord",
        foreign_keys="[EmploymentRecord.employee_id]",
        back_populates="employee",
        cascade="all, delete-orphan",
    )
    background_checks = relationship("BackgroundCheck", back_populates="employee", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Employee id={self.id} emp_num='{self.employee_number}' name='{self.first_name} {self.last_name}'>"
