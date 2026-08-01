from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.background_check import CheckStatus, CheckType


class DepartmentHeadcountItem(BaseModel):
    department_id: int
    department_name: str
    active_headcount: int


class EmploymentStatusItem(BaseModel):
    status: str
    count: int


class OutstandingCheckItem(BaseModel):
    check_id: int
    employee_id: int
    employee_number: str
    employee_name: str
    check_type: CheckType
    status: CheckStatus
    requested_at: str


class ExpiringRightToWorkItem(BaseModel):
    check_id: int
    employee_id: int
    employee_number: str
    employee_name: str
    provider_reference: Optional[str] = None
    expiry_date: date
    days_until_expiry: int


class DashboardSummaryResponse(BaseModel):
    total_employees: int
    active_employees: int
    deactivated_employees: int
    total_departments: int
    pending_background_checks: int
    expiring_right_to_work_count: int

    model_config = ConfigDict(from_attributes=True)
