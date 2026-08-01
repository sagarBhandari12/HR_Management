from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.employment_record import EmploymentRecordStatus, EmploymentType


class EmploymentRecordCreate(BaseModel):
    job_title: str = Field(..., min_length=2, max_length=150, json_schema_extra={"example": "Senior Lecturer in Software Engineering"})
    employment_type: EmploymentType = Field(default=EmploymentType.PERMANENT, json_schema_extra={"example": EmploymentType.PERMANENT})
    start_date: date = Field(..., json_schema_extra={"example": "2024-09-01"})
    end_date: Optional[date] = Field(None, json_schema_extra={"example": "2026-08-31"})
    salary_band: str = Field(..., min_length=1, max_length=50, json_schema_extra={"example": "Band 7"})
    manager_id: Optional[int] = Field(None, json_schema_extra={"example": 1})
    status: EmploymentRecordStatus = Field(default=EmploymentRecordStatus.ACTIVE, json_schema_extra={"example": EmploymentRecordStatus.ACTIVE})

    @model_validator(mode="after")
    def validate_dates(self) -> "EmploymentRecordCreate":
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValueError("Employment end_date cannot be earlier than start_date.")
        return self


class EmploymentRecordUpdate(BaseModel):
    job_title: Optional[str] = Field(None, min_length=2, max_length=150)
    employment_type: Optional[EmploymentType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    salary_band: Optional[str] = None
    manager_id: Optional[int] = None
    status: Optional[EmploymentRecordStatus] = None

    @model_validator(mode="after")
    def validate_dates(self) -> "EmploymentRecordUpdate":
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValueError("Employment end_date cannot be earlier than start_date.")
        return self


class EmploymentRecordResponse(BaseModel):
    id: int
    employee_id: int
    job_title: str
    employment_type: EmploymentType
    start_date: date
    end_date: Optional[date] = None
    salary_band: str
    manager_id: Optional[int] = None
    status: EmploymentRecordStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
