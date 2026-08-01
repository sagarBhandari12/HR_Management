from typing import Any, List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_role
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.report import (
    DashboardSummaryResponse,
    DepartmentHeadcountItem,
    EmploymentStatusItem,
    ExpiringRightToWorkItem,
    OutstandingCheckItem,
)
from app.services.reports import ReportService

router = APIRouter(prefix="/reports", tags=["HR Analytics & Reports"])


@router.get(
    "/dashboard",
    response_model=DashboardSummaryResponse,
    status_code=status.HTTP_200_OK,
)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.HR_OFFICER)),
) -> Any:
    """Retrieves high-level HR summary statistics (ADMIN and HR_OFFICER)."""
    report_service = ReportService(db)
    return report_service.get_dashboard_summary()


@router.get(
    "/headcount-by-department",
    response_model=List[DepartmentHeadcountItem],
    status_code=status.HTTP_200_OK,
)
def get_headcount_by_department(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.HR_OFFICER)),
) -> Any:
    """Retrieves active employee headcount breakdown grouped by department (ADMIN and HR_OFFICER)."""
    report_service = ReportService(db)
    return report_service.get_headcount_by_department()


@router.get(
    "/employment-status",
    response_model=List[EmploymentStatusItem],
    status_code=status.HTTP_200_OK,
)
def get_employment_status_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.HR_OFFICER)),
) -> Any:
    """Retrieves distribution of employee employment statuses (ADMIN and HR_OFFICER)."""
    report_service = ReportService(db)
    return report_service.get_employment_status_report()


@router.get(
    "/outstanding-checks",
    response_model=List[OutstandingCheckItem],
    status_code=status.HTTP_200_OK,
)
def get_outstanding_checks_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.HR_OFFICER)),
) -> Any:
    """Retrieves list of pending, in-progress or review-required background checks (ADMIN and HR_OFFICER)."""
    report_service = ReportService(db)
    return report_service.get_outstanding_checks_report()


@router.get(
    "/expiring-right-to-work",
    response_model=List[ExpiringRightToWorkItem],
    status_code=status.HTTP_200_OK,
)
def get_expiring_right_to_work_report(
    days: int = Query(90, ge=1, le=365, description="Expiry threshold in days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.HR_OFFICER)),
) -> Any:
    """Retrieves Right to Work checks expiring within specified days (ADMIN and HR_OFFICER)."""
    report_service = ReportService(db)
    return report_service.get_expiring_right_to_work_report(days=days)
