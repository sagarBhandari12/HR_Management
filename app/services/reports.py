from datetime import date, timedelta
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.background_check import BackgroundCheck, CheckStatus, CheckType
from app.models.department import Department
from app.models.employee import Employee
from app.schemas.report import (
    DashboardSummaryResponse,
    DepartmentHeadcountItem,
    EmploymentStatusItem,
    ExpiringRightToWorkItem,
    OutstandingCheckItem,
)


class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_summary(self) -> DashboardSummaryResponse:
        total_emp = self.db.query(Employee).count()
        active_emp = self.db.query(Employee).filter(Employee.is_active).count()
        deact_emp = self.db.query(Employee).filter(not Employee.is_active).count()
        total_dept = self.db.query(Department).filter(Department.is_active).count()

        pending_checks = (
            self.db.query(BackgroundCheck)
            .filter(BackgroundCheck.status.in_([CheckStatus.PENDING, CheckStatus.IN_PROGRESS, CheckStatus.REVIEW_REQUIRED]))
            .count()
        )

        cutoff = date.today() + timedelta(days=90)
        expiring_rtw = (
            self.db.query(BackgroundCheck)
            .filter(
                BackgroundCheck.check_type == CheckType.RIGHT_TO_WORK,
                BackgroundCheck.expiry_date is not None,
                BackgroundCheck.expiry_date <= cutoff,
            )
            .count()
        )

        return DashboardSummaryResponse(
            total_employees=total_emp,
            active_employees=active_emp,
            deactivated_employees=deact_emp,
            total_departments=total_dept,
            pending_background_checks=pending_checks,
            expiring_right_to_work_count=expiring_rtw,
        )

    def get_headcount_by_department(self) -> List[DepartmentHeadcountItem]:
        depts = self.db.query(Department).all()
        results = []
        for d in depts:
            count = (
                self.db.query(Employee)
                .filter(Employee.department_id == d.id, Employee.is_active)
                .count()
            )
            results.append(
                DepartmentHeadcountItem(
                    department_id=d.id,
                    department_name=d.name,
                    active_headcount=count,
                )
            )
        return results

    def get_employment_status_report(self) -> List[EmploymentStatusItem]:
        counts = (
            self.db.query(Employee.status, func.count(Employee.id))
            .group_by(Employee.status)
            .all()
        )
        return [EmploymentStatusItem(status=status.value, count=count) for status, count in counts]

    def get_outstanding_checks_report(self) -> List[OutstandingCheckItem]:
        checks = (
            self.db.query(BackgroundCheck)
            .filter(BackgroundCheck.status.in_([CheckStatus.PENDING, CheckStatus.IN_PROGRESS, CheckStatus.REVIEW_REQUIRED]))
            .order_by(BackgroundCheck.requested_at.asc())
            .all()
        )

        results = []
        for c in checks:
            emp = self.db.query(Employee).filter(Employee.id == c.employee_id).first()
            emp_num = emp.employee_number if emp else "UNKNOWN"
            emp_name = f"{emp.first_name} {emp.last_name}" if emp else "Unknown"
            results.append(
                OutstandingCheckItem(
                    check_id=c.id,
                    employee_id=c.employee_id,
                    employee_number=emp_num,
                    employee_name=emp_name,
                    check_type=c.check_type,
                    status=c.status,
                    requested_at=c.requested_at.isoformat(),
                )
            )
        return results

    def get_expiring_right_to_work_report(self, days: int = 90) -> List[ExpiringRightToWorkItem]:
        cutoff = date.today() + timedelta(days=days)
        checks = (
            self.db.query(BackgroundCheck)
            .filter(
                BackgroundCheck.check_type == CheckType.RIGHT_TO_WORK,
                BackgroundCheck.expiry_date is not None,
                BackgroundCheck.expiry_date <= cutoff,
            )
            .order_by(BackgroundCheck.expiry_date.asc())
            .all()
        )

        results = []
        today = date.today()
        for c in checks:
            emp = self.db.query(Employee).filter(Employee.id == c.employee_id).first()
            emp_num = emp.employee_number if emp else "UNKNOWN"
            emp_name = f"{emp.first_name} {emp.last_name}" if emp else "Unknown"
            days_until = (c.expiry_date - today).days if c.expiry_date else 0

            results.append(
                ExpiringRightToWorkItem(
                    check_id=c.id,
                    employee_id=c.employee_id,
                    employee_number=emp_num,
                    employee_name=emp_name,
                    provider_reference=c.provider_reference,
                    expiry_date=c.expiry_date,
                    days_until_expiry=days_until,
                )
            )
        return results
