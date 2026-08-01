from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.employee import EmployeeStatus


class EmployeeCreate(BaseModel):
    employee_number: str = Field(..., min_length=3, max_length=50, json_schema_extra={"example": "EMP-1001"})
    first_name: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "David"})
    last_name: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "Miller"})
    work_email: EmailStr = Field(..., json_schema_extra={"example": "david.miller@regent.ac.uk"})
    personal_email: Optional[EmailStr] = Field(None, json_schema_extra={"example": "david.m@example.com"})
    telephone: Optional[str] = Field(None, json_schema_extra={"example": "+447700900077"})
    date_of_birth: Optional[date] = Field(None, json_schema_extra={"example": "1990-05-15"})
    department_id: int = Field(..., json_schema_extra={"example": 1})
    status: EmployeeStatus = Field(default=EmployeeStatus.ACTIVE, json_schema_extra={"example": EmployeeStatus.ACTIVE})


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    work_email: Optional[EmailStr] = None
    personal_email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    date_of_birth: Optional[date] = None
    department_id: Optional[int] = None
    status: Optional[EmployeeStatus] = None


class EmployeeResponse(BaseModel):
    id: int
    employee_number: str
    first_name: str
    last_name: str
    work_email: EmailStr
    personal_email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    date_of_birth: Optional[date] = None
    department_id: int
    department_name: Optional[str] = None
    status: EmployeeStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deactivated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
